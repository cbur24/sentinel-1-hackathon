import numpy as np
import scipy as sp
import scipy.optimize
import xarray as xr
import dask.array as da
from typing import Union

def lee_sigma_improved_xr(
    img: xr.Dataset,                         # or xr.DataArray with bands as data variables
    band_name: str = "VH_gamma0",
    nlooks: Union[str, float] = "number_of_looks",
    win=(9, 9),
    sigma=0.9,
    perc=0.02,
    data_type="amplitude",
    verbose=False,
    round_step: float = 0.5,                # round nlooks to nearest step (0.5 by default)
) -> xr.DataArray:
    """
    xarray-compatible Lee's improved sigma filter that precomputes bounds/newsig
    for rounded number-of-looks values (supports Dask or NumPy arrays).

    Parameters
    ----------
    img : xr.Dataset or xr.DataArray
        Dataset containing SAR band and nlooks band.
    band_name : str
        Name of SAR band to filter (data variable in ds).
    nlooks : str or float
        Name of looks band (in dataset) or scalar number-of-looks.
    win : tuple
        Window size (rows, cols).
    sigma : float
        sigma range parameter for optf_for_bounds/newsig calculation.
    perc : float
        point-target percentile (0..1).
    data_type : 'amplitude' or 'intensity'
    verbose : bool
    round_step : float
        rounding step used for looks (e.g., 0.5). Smaller -> more unique values -> slower.

    Returns
    -------
    xr.DataArray
        Filtered image (2D) for the first time slice.
    """

    # -----------------------
    # Helper: get DataArray and underlying array (dask or numpy)
    # -----------------------
    # select band's DataArray (if img is a Dataset)
    if isinstance(img, xr.Dataset):
        if band_name not in img:
            raise KeyError(f"Band '{band_name}' not found in dataset")
        sar_da = img[band_name]
    elif isinstance(img, xr.DataArray):
        sar_da = img
    else:
        raise TypeError("img must be xarray.Dataset or xarray.DataArray")

    # for now operate on the first time slice if time exists
    if "time" in sar_da.dims:
        sar_da0 = sar_da.isel(time=0)
    else:
        sar_da0 = sar_da

    # get the underlying array (may be dask)
    sar_data = sar_da0.data

    # nlooks extraction
    if isinstance(nlooks, str):
        if isinstance(img, xr.Dataset) and (nlooks in img):
            nlooks_da = img[nlooks]
            if "time" in nlooks_da.dims:
                nlooks_da0 = nlooks_da.isel(time=0)
            else:
                nlooks_da0 = nlooks_da
            looks_data = nlooks_da0.data
        else:
            raise KeyError(f"nlooks band '{nlooks}' not found in dataset")
    else:
        # scalar
        looks_data = float(nlooks)

    # -----------------------
    # Compute/convert arrays into NumPy (just the arrays used in loops).
    # We'll try to compute only what is necessary: unique rounded looks (if dask),
    # but because the main loop indexes pixel-by-pixel we ultimately convert the
    # image and looks arrays to NumPy here.
    # -----------------------

    # Convert SAR array to NumPy (compute if Dask)
    if hasattr(sar_data, "compute"):
        arr_np = sar_data.compute()
    else:
        arr_np = np.asarray(sar_data)

    # Convert looks to NumPy if it's a Dask array or xarray DataArray
    if hasattr(looks_data, "compute"):
        looks_np = looks_data.compute()
    else:
        looks_np = np.asarray(looks_data)

    # ensure numeric dtypes
    arr_np = np.asarray(arr_np)
    looks_np = np.asarray(looks_np, dtype=float)

    # -----------------------
    # Expand shapes and compute span as in your original code
    # -----------------------
    if arr_np.ndim == 2:
        if np.iscomplexobj(arr_np) or data_type == "amplitude":
            span = np.abs(arr_np) ** 2
        else:
            span = np.abs(arr_np)
        array4d = arr_np[np.newaxis, np.newaxis, :, :]  # nv=1, nz=1
    elif arr_np.ndim == 3:
        if np.iscomplexobj(arr_np) or data_type == "amplitude":
            span = np.sum(np.abs(arr_np) ** 2, axis=0)
        else:
            span = np.sum(np.abs(arr_np), axis=0)
        array4d = np.expand_dims(arr_np, axis=1)
    elif arr_np.ndim == 4:
        span = np.abs(np.trace(arr_np, axis1=0, axis2=1))
        array4d = arr_np
    else:
        raise ValueError(f"Unsupported image array shape: {arr_np.shape}")

    # Make sure arrays are float32 / contiguous for speed
    span = np.ascontiguousarray(span.astype(np.float32))
    array4d = np.ascontiguousarray(array4d.astype(np.float32))
    looks_np = np.ascontiguousarray(looks_np.astype(float))

    ny, nx = span.shape[-2:]
    ym, xm = win[0] // 2, win[1] // 2

    # -----------------------
    # Round looks and compute unique rounded values (efficiently)
    # -----------------------
    def _round_looks_array(a, step):
        # works for numpy array a
        return np.round(a / step) * step

    rounded_looks_np = _round_looks_array(looks_np, round_step)
    unique_rounded = np.unique(rounded_looks_np)

    # ensure unique_rounded is finite and sorted
    unique_rounded = np.asarray([u for u in unique_rounded.flatten() if np.isfinite(u)])
    unique_rounded = np.unique(unique_rounded)

    if verbose:
        print(f"Rounded looks unique values (count={len(unique_rounded)}): {unique_rounded}")

    # -----------------------
    # Precompute bounds + newsig for each unique rounded look value
    # -----------------------
    bounds_lookup = {}   # maps look_value -> (i1,i2)
    newsig_lookup = {}   # maps look_value -> nsig2

    # We'll use your optf_for_bounds and newsig_integral from the previous code.
    # They should be available in the same module; otherwise define them above.
    for lk in unique_rounded:
        try:
            # compute bounds for this looks (uses scipy optimize as before)
            b = sp.optimize.fmin(optf_for_bounds, [0.5, 2.0], args=(float(lk), sigma), disp=False)
            # ensure valid numeric result
            if not np.all(np.isfinite(b)):
                b = np.array([0.5, 2.0], dtype=float)
        except Exception:
            b = np.array([0.5, 2.0], dtype=float)
        bounds_lookup[lk] = (float(b[0]), float(b[1]))

        try:
            ns = newsig_integral(bounds_lookup[lk][0], bounds_lookup[lk][1], sigrng=sigma, looks=float(lk))
            if not np.isfinite(ns):
                ns = 0.5
        except Exception:
            ns = 0.5
        newsig_lookup[lk] = float(ns)

    if verbose:
        print("Precomputation complete: bounds & newsig for rounded looks.")

    # -----------------------
    # Point-target threshold
    # -----------------------
    pct = 100.0 - perc * 100.0
    try:
        pthreshold = np.percentile(span, pct)
    except Exception:
        pthreshold = float(np.mean(span))
    if verbose:
        print("Point-target threshold:", pthreshold)

    # -----------------------
    # Filtering main loop (same logic as original, but uses rounded_looks_np)
    # -----------------------
    nv, nz = array4d.shape[0], array4d.shape[1]
    out = np.zeros_like(array4d, dtype=float)
    array_float = array4d.astype(float, copy=False)
    res = np.zeros((nv, nz), dtype=float)

    for k in range(ym, ny - ym):
        for l in range(xm, nx - xm):
            # 3x3 pre-check for point targets
            m2_3 = 0.0
            m_3 = 0.0
            n_pt = 0
            for yy in range(-1, 2):
                for xx in range(-1, 2):
                    v = span[k + yy, l + xx]
                    m2_3 += v * v
                    m_3 += v
                    if v > pthreshold:
                        n_pt += 1

            # copy point-targets if enough count
            if n_pt >= 6:
                for yy in range(-1, 2):
                    for xx in range(-1, 2):
                        if span[k + yy, l + xx] > pthreshold:
                            for v in range(nv):
                                for z in range(nz):
                                    out[v, z, k + yy, l + xx] = array_float[v, z, k + yy, l + xx]

            if out[0, 0, k, l] == 0.0:
                m2_3 /= 9.0
                m_3 /= 9.0
                vary = (m2_3 - m_3 * m_3)
                if vary < 1e-10:
                    vary = 1e-10

                # take rounded look
                looks_center = float(rounded_looks_np[k, l])
                if looks_center <= 0.0:
                    looks_center = 1.0  # safeguard

                sig2 = 1.0 / looks_center
                sfak = 1.0 + sig2

                varx = (vary - (m_3 * m_3) * sig2) / sfak
                if varx < 0.0:
                    varx = 0.0
                kfac = varx / vary

                xtilde = (span[k, l] - m_3) * kfac + m_3

                # lookup bounds and newsig
                lk = float(rounded_looks_np[k, l])
                b0, b1 = bounds_lookup.get(lk, (0.5, 2.0))
                i1 = xtilde * b0
                i2 = xtilde * b1

                nsig2 = newsig_lookup.get(lk, 0.5)
                nsfak = 1.0 + nsig2

                # accumulate samples between i1 and i2
                for v in range(nv):
                    for z in range(nz):
                        res[v, z] = 0.0
                n = 0
                for yy in range(-ym, ym + 1):
                    for xx in range(-xm, xm + 1):
                        val = span[k + yy, l + xx]
                        if (val > i1) and (val < i2):
                            n += 1
                            for v in range(nv):
                                for z in range(nz):
                                    res[v, z] += array_float[v, z, k + yy, l + xx]

                if n == 0:
                    for v in range(nv):
                        for z in range(nz):
                            out[v, z, k, l] = 0.0
                else:
                    m2arr = 0.0
                    marr = 0.0
                    for yy in range(-ym, ym + 1):
                        for xx in range(-xm, xm + 1):
                            val = span[k + yy, l + xx]
                            if (val > i1) and (val < i2):
                                m2arr += val * val
                                marr += val
                    m2arr /= n
                    marr /= n
                    vary2 = (m2arr - marr * marr)
                    if vary2 < 1e-10:
                        vary2 = 1e-10

                    varx2 = (vary2 - marr * marr * nsig2) / nsfak
                    if varx2 < 0.0:
                        varx2 = 0.0
                    kfac2 = varx2 / vary2

                    for v in range(nv):
                        for z in range(nz):
                            out[v, z, k, l] = (array_float[v, z, k, l] - res[v, z] / n) * kfac2 + res[v, z] / n

    # -----------------------
    # Postprocess and return as xarray
    # -----------------------
    out = np.asarray(out)
    out[~np.isfinite(out)] = 0.0
    if data_type == "amplitude":
        out[out < 0] = 0.0
        out = np.sqrt(out)

    # restore coords / dims using original DataArray
    # sar_da0 is the xarray DataArray for the selected band and first time slice
    if arr_np.ndim == 2:
        da_out = xr.DataArray(out[0, 0], coords=sar_da0.coords, dims=sar_da0.dims, attrs=sar_da0.attrs)
    elif arr_np.ndim == 3:
        da_out = xr.DataArray(np.squeeze(out, axis=1), coords=sar_da0.coords, dims=sar_da0.dims, attrs=sar_da0.attrs)
    else:
        da_out = xr.DataArray(out, coords=sar_da0.coords, dims=sar_da0.dims, attrs=sar_da0.attrs)

    return da_out
