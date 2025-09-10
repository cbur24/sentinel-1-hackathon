@decorators.keep_names
@decorators.keep_attrs
def gamma_map(img, window=7, enl=4.9, keep_bands=["angle"]):
    """Source https://servir-mekong.github.io/hydra-floods/filtering/
    Gamma Map speckle filtering algorithm.
    Algorithm adapted from https://groups.google.com/g/google-earth-engine-developers/c/a9W0Nlrhoq0/m/tnGMC45jAgAJ.

    args:
        img (ee.Image): Earth engine image object. Expects that imagery is a SAR image
        window (int, optional): moving window size to apply filter (i.e. a value of 7 == 7x7 window). default = 7
        enl (float, optional): equivalent number of looks (enl) per pixel from a SAR scan.
            See https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/resolutions/level-1-ground-range-detected.
            default = 4.9
        keep_bands (list[str], optional): list of band names to drop during filtering and include in the result
            default = ["angle"]

    returns:
        ee.Image: filtered SAR image using the Gamma Map algorithm
    """

    band_names = img.bandNames()
    if keep_bands is not None:
        keep_img = img.select(keep_bands)
        proc_bands = band_names.removeAll(keep_bands)
    else:
        proc_bands = band_names

    img = img.select(proc_bands)

    # Square kernel, window should be odd (typically 3, 5 or 7)
    weights = ee.List.repeat(ee.List.repeat(1, window), window)
    midPt = (window // 2) + 1 if (window % 2) != 0 else window // 2

    # ~~(window/2) does integer division in JavaScript
    kernel = ee.Kernel.fixed(window, window, weights, midPt, midPt, False)

    # Convert image from dB to natural values
    nat_img = geeutils.db_to_power(img)

    # Get mean and variance
    mean = nat_img.reduceNeighborhood(ee.Reducer.mean(), kernel)
    variance = nat_img.reduceNeighborhood(ee.Reducer.variance(), kernel)

    # "Pure speckle" threshold
    ci = variance.sqrt().divide(mean)  # square root of inverse of enl

    # If ci <= cu, the kernel lies in a "pure speckle" area -> return simple mean
    cu = 1.0 / math.sqrt(enl)

    # If cu < ci < cmax the kernel lies in the low textured speckle area -> return the filtered value
    cmax = math.sqrt(2.0) * cu

    alpha = ee.Image(1.0 + cu * cu).divide(ci.multiply(ci).subtract(cu * cu))
    b = alpha.subtract(enl + 1.0)
    d = (
        mean.multiply(mean)
        .multiply(b)
        .multiply(b)
        .add(alpha.multiply(mean).multiply(nat_img).multiply(4.0 * enl))
    )
    f = b.multiply(mean).add(d.sqrt()).divide(alpha.multiply(2.0))

    caster = ee.Dictionary.fromLists(
        proc_bands, ee.List.repeat("float", proc_bands.length())
    )
    img1 = (
        geeutils.power_to_db(mean.updateMask(ci.lte(cu)))
        .rename(proc_bands)
        .cast(caster)
    )
    img2 = (
        geeutils.power_to_db(f.updateMask(ci.gt(cu)).updateMask(ci.lt(cmax)))
        .rename(proc_bands)
        .cast(caster)
    )
    img3 = img.updateMask(ci.gte(cmax)).rename(proc_bands).cast(caster)

    # If ci > cmax do not filter at all (i.e. we don't do anything, other then masking)
    output = (
        ee.ImageCollection([img1, img2, img3])
        .reduce(ee.Reducer.firstNonNull())
        .rename(proc_bands)
        .clip(img.geometry())
    )

    if keep_bands is not None:
        output = output.addBands(keep_img)

    # Compose a 3 band image with the mean filtered "pure speckle", the "low textured" filtered and the unfiltered portions
    return output