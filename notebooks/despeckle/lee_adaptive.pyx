# cython: boundscheck=False, wraparound=False
import cython
import numpy as np
cimport numpy as np

# choose the complex / float typedef that matches what you will pass in.
# If you always pass real float32 arrays, you can use float; if you may pass complex64,
# change to np.complex64_t and adjust dtypes when creating arrays in Python.
ctypedef np.float32_t flt_t
ctypedef np.float32_t fltcpl_t  # keep as float32 for performance (intensity)

@cython.boundscheck(False)
@cython.wraparound(False)
def cy_leeimproved_adaptive(
        float[:, :] span,                        # (ny, nx)
        fltcpl_t[:, :, :, :] array,             # (nv, nz, ny, nx)
        float[:, :] looks_arr,                  # (ny, nx)
        float[:, :, :] bounds_arr = None,       # (2, ny, nx) or None
        float[:, :] newsig_arr = None,          # (ny, nx) or None
        float thres=5.0,
        tuple win=(9, 9)):
    """
    Cython implementation of Lee improved sigma with per-pixel looks and optional
    per-pixel bounds/newsig arrays.

    Required shapes:
      - span: (ny, nx) float32
      - array: (nv, nz, ny, nx) float32 (real)
      - looks_arr: (ny, nx) float32
      - bounds_arr: (2, ny, nx) float32  (optional)
      - newsig_arr: (ny, nx) float32     (optional)
    """

    cdef int nv = array.shape[0]
    cdef int nz = array.shape[1]
    cdef int ny = array.shape[2]
    cdef int nx = array.shape[3]
    cdef int ym = win[0] // 2
    cdef int xm = win[1] // 2

    # output buffer (same dtype/shape as array)
    cdef fltcpl_t[:, :, :, :] out = np.zeros_like(array)

    # small working buffers
    cdef int k, l, x, y, v, z, n
    cdef float m2arr, marr, vary, varx, kfac, i1, i2
    cdef float sig2, sfak, nsig2, nsfak, xtilde
    # res holds accumulation for nv x nz small matrix; use numpy and memoryview
    cdef fltcpl_t[:, :] res = np.zeros((nv, nz), dtype=np.float32)

    # main loops
    for k in range(ym, ny - ym):
        for l in range(xm, nx - xm):
            # per-pixel looks
            sig2 = 1.0 / looks_arr[k, l]
            sfak = 1.0 + sig2

            # per-pixel bounds (i1,i2) provided or default
            if bounds_arr is not None:
                i1 = bounds_arr[0, k, l]
                i2 = bounds_arr[1, k, l]
            else:
                i1 = 0.5
                i2 = 2.0

            # per-pixel newsig if provided, else default
            if newsig_arr is not None:
                nsig2 = newsig_arr[k, l]
            else:
                nsig2 = 0.5
            nsfak = 1.0 + nsig2

            # --- 3x3 point-target check ---
            m2arr = 0.0
            marr = 0.0
            n = 0
            for y in range(-1, 2):
                for x in range(-1, 2):
                    m2arr += span[k+y, l+x] * span[k+y, l+x]
                    marr += span[k+y, l+x]
                    if span[k+y, l+x] > thres:
                        n += 1

            if n >= 6:
                # keep the point targets unchanged in output
                for y in range(-1, 2):
                    for x in range(-1, 2):
                        if span[k+y, l+x] > thres:
                            for v in range(nv):
                                for z in range(nz):
                                    out[v, z, k+y, l+x] = array[v, z, k+y, l+x]

            # --- filtering for the center pixel if not already set by point-target logic ---
            if out[0, 0, k, l] == 0.0:
                # compute 3x3 mean/var
                m2arr /= 9.0
                marr /= 9.0
                vary = m2arr - marr * marr
                if vary < 1e-10:
                    vary = 1e-10

                varx = (vary - (marr * marr) * sig2) / sfak
                if varx < 0.0:
                    varx = 0.0
                kfac = varx / vary

                xtilde = (span[k, l] - marr) * kfac + marr

                # scaled bounds for local pixel
                i1 = xtilde * i1
                i2 = xtilde * i2

                # accumulate selected pixels inside window
                # zero accumulator
                for v in range(nv):
                    for z in range(nz):
                        res[v, z] = 0.0
                n = 0
                for y in range(-ym, ym + 1):
                    for x in range(-xm, xm + 1):
                        val = span[k + y, l + x]
                        if (val > i1) and (val < i2):
                            n += 1
                            for v in range(nv):
                                for z in range(nz):
                                    res[v, z] += array[v, z, k + y, l + x]

                if n == 0:
                    # no samples found, set output to zero (same as original behavior)
                    for v in range(nv):
                        for z in range(nz):
                            out[v, z, k, l] = 0.0
                else:
                    # compute mean and var over the selected pixels
                    m2arr = 0.0
                    marr = 0.0
                    for y in range(-ym, ym + 1):
                        for x in range(-xm, xm + 1):
                            val = span[k + y, l + x]
                            if (val > i1) and (val < i2):
                                m2arr += val * val
                                marr += val
                    m2arr /= n
                    marr /= n
                    vary = m2arr - marr * marr
                    if vary < 1e-10:
                        vary = 1e-10

                    varx = (vary - marr * marr * nsig2) / nsfak
                    if varx < 0.0:
                        varx = 0.0
                    kfac = varx / vary

                    for v in range(nv):
                        for z in range(nz):
                            out[v, z, k, l] = (array[v, z, k, l] - res[v, z] / n) * kfac + res[v, z] / n

    return np.asarray(out)
