import numpy as np
from scipy.ndimage import uniform_filter
import xarray as xr


def lee_filter(img, size):
    """
    Apply a Lee filter to reduce speckle noise in an individual image.

    Adapted from https://stackoverflow.com/questions/39785970/speckle-lee-filter-in-python

    Parameters
    ----------
    img : numpy.ndarray
        Input image to be filtered.
    size : int
        Size of the uniform filter window.

    Returns
    -------
    numpy.ndarray
        The filtered image.
    """
    img_mean = uniform_filter(img, size)
    img_sqr_mean = uniform_filter(img**2, size)
    img_variance = img_sqr_mean - img_mean**2

    overall_variance = np.nanvar(img)

    img_weights = img_variance / (img_variance + overall_variance)
    img_output = img_mean + img_weights * (img - img_mean)
    return img_output


def apply_lee_filter(data_array, size=7):
    """
    Apply a Lee filter to each observation in a provided xarray.DataArray.

    Parameters
    ----------
    data_array : xarray.DataArray
        The data array to be filtered.
    size : int, optional
        Size of the uniform filter window.

    Returns
    -------
    xarray.DataArray
        The filtered data array.
    """
    filtered_data = xr.apply_ufunc(
        lee_filter,
        data_array,
        kwargs={"size": size},
        input_core_dims=[["y", "x"]],
        output_core_dims=[["y", "x"]],
        dask_gufunc_kwargs={"allow_rechunk": True},
        vectorize=True,
        dask="parallelized",
        output_dtypes=[data_array.dtype],
        keep_attrs=True,
    )
    return filtered_data
