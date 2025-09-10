"""
Pure-Python implementation of Lee's Improved Sigma speckle filter.
Accepts per-pixel looks array (2D) or scalar looks.

Dependencies:
    numpy, scipy, rasterio (optional, for GeoTIFF I/O)

Example usage at bottom shows reading image and looks from GeoTIFFs.
"""
import numpy as np
import scipy as sp
import scipy.special
import scipy.integrate
import scipy.optimize
import rasterio    # optional; used in example IO
from rasterio import Affine
from rasterio.enums import Resampling
import warnings

# -------------------------
# Probability helper funcs
# -------------------------
def specklepdf(i, looks=1.0):
    if i < 0.0:
        return 0.0
    # Gamma(looks) might be large; use scipy.special.gamma
    return ((looks ** looks) * (i ** (looks - 1.0))) / sp.special.gamma(looks) * np.exp(-looks * i)

def meanpdf(i, looks=1.0):
    if i < 0.0:
        return 0.0
    return specklepdf(i, looks=looks) * i

def sigpdf(i, looks=1.0):
    # integrand used for "newsig" calculation
    return (i - 1.0) ** 2 * specklepdf(i, looks=looks)

def sigmarange(i1, i2, looks=1.0):
    val = sp.integrate.quad(lambda x: specklepdf(x, looks), i1, i2)[0]
    return np.clip(val, 1e-10, 1.0)

def intmean(i1, i2, looks=1.0):
    denom = sigmarange(i1, i2, looks)
    num = sp.integrate.quad(lambda x: meanpdf(x, looks), i1, i2)[0]
    return num / denom

def newsig_integral(i1, i2, sigrng=0.9, looks=1.0):
    """Compute newsig = 1/sigrng * integral(sigpdf, i1, i2)"""
    integral = sp.integrate.quad(lambda x: sigpdf(x, looks), i1, i2)[0]
    return (1.0 / sigrng) * integral

def optf_for_bounds(i, looks, sigr):
    # objective identical to class.optf in your code
    i1, i2 = i
    return (sigmarange(i1, i2, looks) - sigr) ** 2 + (intmean(i1, i2, looks) - 1.0) ** 2

# -------------------------
# Core filtering routine
# -------------------------
def lee_sigma_improved(image, looks=1.0, win=(9, 9), sigma=0.9, perc=0.02, data_type='amplitude', verbose=False):
    """
    Lee's improved sigma speckle filter (pure python).
    Parameters:
        image : ndarray
            2D (single-channel) or 3D (channels, rows, cols) or complex. 
            If complex or data_type == 'amplitude' then amplitude squared is used (i.e. intensity),
            following the logic in your Cython code.
        looks : scalar or 2D ndarray (rows, cols)
            Number of looks. If array supplied, per-pixel looks are used inside the algorithm.
        win : tuple (rows, cols)
            sliding window used for selection (e.g. (9,9)).
        sigma : float
            sigma range (0..1) used for computing newsig bounds.
        perc : float
            point target percentile (0..1) used to pick threshold (converted to a percentile).
        data_type : 'amplitude' or 'intensity'
            If 'amplitude' the output will be amplitude (sqrt of intensity) like original.
    Returns:
        filtered : ndarray same shape as input image (channels preserved)
    """
    # --- normalize input shapes to (nv, nz, y, x) as cython expected ---
    arr = np.asarray(image)
    orig_shape = arr.shape
    # Determine span and array format
    if arr.ndim == 3:
        # assume multi-channel with shape (channels, rows, cols) OR a 3-vector polarimetric (nv=3)
        # We'll treat first axis as "vector" (nv) and then z=1 (no extra covariance dim)
        if np.iscomplexobj(arr) or data_type == 'amplitude':
            span = np.sum(np.abs(arr) ** 2, axis=0)
        else:
            span = np.sum(np.abs(arr), axis=0)
        # reshape to nv,nz,y,x with nz=1
        array = np.expand_dims(arr, axis=1)
        nv = array.shape[0]
        nz = 1
    elif arr.ndim == 4:
        # covariance data: assume shape (nv, nz, y, x) already
        # span is trace
        span = np.abs(np.trace(arr, axis1=0, axis2=1))
        array = arr
        nv = array.shape[0]
        nz = array.shape[1]
    elif arr.ndim == 2:
        # single channel
        if np.iscomplexobj(arr) or data_type == 'amplitude':
            span = np.abs(arr) ** 2
        else:
            span = np.abs(arr)
        array = arr[np.newaxis, np.newaxis, ...]  # shape (1,1,y,x)
        nv = 1
        nz = 1
    else:
        raise ValueError("Unsupported input array shape: {}".format(arr.shape))

    # ensure looks is either scalar or 2D array same size as span
    if np.isscalar(looks):
        looks_arr = np.full_like(span, float(looks), dtype=float)
    else:
        looks_arr = np.asarray(looks, dtype=float)
        if looks_arr.shape != span.shape:
            raise ValueError("If looks is array it must match image y,x shape. got {} vs {}".format(looks_arr.shape, span.shape))

    ny, nx = span.shape
    ym = win[0] // 2
    xm = win[1] // 2

    # compute bounds using mean looks (mirrors original approach)
    looks_mean = float(np.mean(looks_arr))
    # starting guess [0.5, 2.0]
    try:
        bounds = sp.optimize.fmin(optf_for_bounds, [0.5, 2.0], args=(looks_mean, sigma), disp=False)
    except Exception:
        # fall back to default if optimization fails
        bounds = np.array([0.5, 2.0])
    if verbose:
        print("Bounds:", bounds)

    # compute point-target threshold: use perc -> percentile
    # original code: perc = 100 - self.perc * 100; pthreshold = mean(layer_accumulate(...))
    pct = 100.0 - perc * 100.0
    try:
        pthreshold = np.percentile(span, pct)
    except Exception:
        pthreshold = np.mean(span)  # fallback
    if verbose:
        print("Point-target threshold (global percentile):", pthreshold)

    # prepare output
    out = np.zeros_like(array, dtype=float)

    # convenience: get view for reading/writing
    # array shape (nv, nz, ny, nx)
    # We'll cast 'array' to float for arithmetic; keep complex support by using abs/power earlier so it's fine.
    array_float = array.astype(float, copy=False)

    # main nested loops (pure python). Will be slower than Cython.
    # We'll follow Cython logic exactly where possible.
    # iterate center positions skipping borders
    y_range = range(ym, ny - ym)
    x_range = range(xm, nx - xm)

    # Pre-allocate small buffers to avoid repeated allocation
    res = np.zeros((nv, nz), dtype=float)

    for k in y_range:
        for l in x_range:
            # compute 3x3 m2arr and marr and check point-target counts
            m2_3 = 0.0
            m_3 = 0.0
            n_pt = 0
            for yy in range(-1, 2):
                for xx in range(-1, 2):
                    val = span[k + yy, l + xx]
                    m2_3 += val * val
                    m_3 += val
                    if val > pthreshold:
                        n_pt += 1

            # if many point-target pixels in 3x3, copy them (in C code they copy out for those positions)
            if n_pt >= 6:
                for yy in range(-1, 2):
                    for xx in range(-1, 2):
                        if span[k + yy, l + xx] > pthreshold:
                            for v in range(nv):
                                for z in range(nz):
                                    out[v, z, k + yy, l + xx] = array_float[v, z, k + yy, l + xx]
                # Note: still continue and apply center filtering only if out at center is still zero (matching C code)

            if out[0, 0, k, l] == 0.0:
                # compute mean/var over 3x3
                m2_3 /= 9.0
                m_3 /= 9.0
                vary = (m2_3 - m_3 * m_3)
                if vary < 1e-10:
                    vary = 1e-10

                # local looks for center pixel
                looks_center = float(looks_arr[k, l])
                sig2 = 1.0 / looks_center
                sfak = 1.0 + sig2

                varx = ((vary - (m_3 ** 2) * sig2) / sfak)
                if varx < 0.0:
                    varx = 0.0
                kfac = varx / vary

                xtilde = (span[k, l] - m_3) * kfac + m_3
                i1 = xtilde * bounds[0]
                i2 = xtilde * bounds[1]

                # compute per-pixel newsig using local looks (potentially expensive)
                try:
                    nsig2 = newsig_integral(i1, i2, sigrng=sigma, looks=looks_center)
                except Exception:
                    # fallback to a small positive to keep formulas sane
                    nsig2 = 0.5

                nsfak = 1.0 + nsig2

                # reset accumulators over window
                for v in range(nv):
                    for z in range(nz):
                        res[v, z] = 0.0
                n = 0

                # gather samples inside the window that fall between i1 and i2
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
                    # compute stats from the selected pixels
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

                    # varx with nsig2 (note: both nsig2 and nsfak are scalars for center pixel)
                    varx2 = ((vary2 - marr ** 2 * nsig2) / nsfak)
                    if varx2 < 0.0:
                        varx2 = 0.0
                    kfac2 = varx2 / vary2

                    for v in range(nv):
                        for z in range(nz):
                            out[v, z, k, l] = (array_float[v, z, k, l] - (res[v, z] / n)) * kfac2 + (res[v, z] / n)

    # postprocess output: handle non-finite, and transform back to amplitude if requested
    out = np.asarray(out)
    out[~np.isfinite(out)] = 0.0
    if data_type == 'amplitude':
        out[out < 0] = 0.0
        out = np.sqrt(out)

    # squeeze back to original shape: reverse the earlier reshaping
    # original mapping: 2D -> (1,1,y,x), 3D -> (nv,1,y,x), 4D -> unchanged
    if arr.ndim == 2:
        return np.squeeze(out)  # (1,1,y,x) -> (y,x)
    elif arr.ndim == 3:
        # we expanded to (nv,1,y,x) -> squeeze second axis
        return np.squeeze(out, axis=1)
    else:
        return out

# -------------------------
# Example usage (GeoTIFF I/O)
# -------------------------
if __name__ == "__main__":
    # Example: read SAR image and looks map from GeoTIFFs and write filtered result.
    import argparse
    parser = argparse.ArgumentParser(description="Apply Lee improved sigma speckle filter.")
    parser.add_argument("--image", required=True, help="Input SAR GeoTIFF (single band or multi-band).")
    parser.add_argument("--looks", required=True, help="Looks GeoTIFF (single band) or scalar (float).")
    parser.add_argument("--out", required=True, help="Output GeoTIFF path.")
    parser.add_argument("--win", type=int, nargs=2, default=[9,9], help="Window size (rows cols).")
    parser.add_argument("--sigma", type=float, default=0.9)
    parser.add_argument("--perc", type=float, default=0.02)
    parser.add_argument("--dtype", choices=['amplitude','intensity'], default='amplitude')
    parser.add_argument("--verbose", action='store_true')
    args = parser.parse_args()

    # read image (supports multi-band)
    with rasterio.open(args.image) as src:
        meta = src.meta.copy()
        bands = src.count
        # read as (bands, rows, cols)
        img = src.read(out_dtype='float32')  # shape (bands, y, x)

    # read looks; could be a raster or a scalar number
    try:
        looks_num = float(args.looks)
        looks_arr = looks_num
    except Exception:
        with rasterio.open(args.looks) as L:
            looks_arr = L.read(1).astype(float)
            # if shapes mismatch, resample looks to image resolution
            if looks_arr.shape != img.shape[1:]:
                # resample uses rasterio
                data = L.read(
                    out_shape=(1, img.shape[1], img.shape[2]),
                    resampling=Resampling.bilinear
                )[0]
                looks_arr = data.astype(float)

    # call filter
    filtered = lee_sigma_improved(img, looks=looks_arr, win=tuple(args.win), sigma=args.sigma,
                                  perc=args.perc, data_type=args.dtype, verbose=args.verbose)

    # write output: keep number of bands same as input; filtered shape may be (bands, y, x) or (y, x)
    out_meta = meta.copy()
    out_meta.update(dtype='float32', count=(filtered.shape[0] if filtered.ndim == 3 else 1))
    with rasterio.open(args.out, 'w', **out_meta) as dst:
        if filtered.ndim == 3:
            dst.write(filtered.astype('float32'))
        else:
            dst.write(filtered.astype('float32'), 1)

    if args.verbose:
        print("Filtering done. Output saved to", args.out)
