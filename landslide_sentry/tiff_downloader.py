from landslide_sentry.cache_manager.cache_loader import downloadFromWeb, extractZip

import ee
from tqdm import tqdm
import os
import math
import requests
import zipfile

EARTH_RADIUS = 6371  # km

# Initialize GEE API.
ee.Authenticate()
ee.Initialize()


def latLongDifferenceFromDistance(distance):
    deg_rad = distance / EARTH_RADIUS
    deg_deg = math.degrees(deg_rad)

    return deg_deg


def getROIFromTargetPoint(longitude, latitude, width, height):

    del_lat = latLongDifferenceFromDistance(0.5 * height)
    del_lang = latLongDifferenceFromDistance(0.5 * width)

    bottom = latitude - del_lat
    top = latitude + del_lat
    left = longitude - del_lang
    right = longitude + del_lang

    roi = ee.Geometry.Rectangle(left, bottom, right, top)

    return roi


def getMosaicImgFromGeeImgCollec(aoi, img_collection: str, bands: list, start_date: str, end_date: str, cloud_percent: int = None):
    img_collec = (ee.ImageCollection(img_collection)
                  .select(bands)
                  .filter(ee.Filter.date(start_date, end_date))
                  .filterBounds(aoi))

    if cloud_percent is not None:
        img_collec = img_collec.filter(ee.Filter.lt(
            'CLOUDY_PIXEL_PERCENTAGE', cloud_percent))

    img = img_collec.filter(ee.Filter.date(
        start_date, end_date)).mosaic().clip(aoi)

    return img


def downloadImg(img, aoi, save_path, scale):

    download_url = img.getDownloadURL({
        'region': aoi,
        'scale': scale
    })

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    downloadFromWeb(download_url, save_path)


def get_s2_sr_cld_col(aoi, start_date, end_date, cloud_filter):
    # Import and filter S2 SR.
    s2_sr_col = (ee.ImageCollection('COPERNICUS/S2_SR')
                 .filterBounds(aoi)
                 .filterDate(start_date, end_date)
                 .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloud_filter)))

    # Import and filter s2cloudless.
    s2_cloudless_col = (ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
                        .filterBounds(aoi)
                        .filterDate(start_date, end_date))

    # Join the filtered s2cloudless collection to the SR collection by the 'system:index' property.
    return ee.ImageCollection(ee.Join.saveFirst('s2cloudless').apply(**{
        'primary': s2_sr_col,
        'secondary': s2_cloudless_col,
        'condition': ee.Filter.equals(**{
            'leftField': 'system:index',
            'rightField': 'system:index'
        })
    }))


def add_cloud_bands(img, cld_prb_thresh=50):
    # Get s2cloudless image, subset the probability band.
    cld_prb = ee.Image(img.get('s2cloudless')).select('probability')

    # Condition s2cloudless by the probability threshold value.
    is_cloud = cld_prb.gt(cld_prb_thresh).rename('clouds')

    # Add the cloud probability layer and cloud mask as image bands.
    return img.addBands(ee.Image([cld_prb, is_cloud]))


def add_shadow_bands(img, nir_drk_thresh=0.15, cld_prj_dist=1):
    # Identify water pixels from the SCL band.
    not_water = img.select('SCL').neq(6)

    # Identify dark NIR pixels that are not water (potential cloud shadow pixels).
    SR_BAND_SCALE = 1e4
    dark_pixels = img.select('B8').lt(
        nir_drk_thresh*SR_BAND_SCALE).multiply(not_water).rename('dark_pixels')

    # Determine the direction to project cloud shadow from clouds (assumes UTM projection).
    shadow_azimuth = ee.Number(90).subtract(
        ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')))

    # Project shadows from clouds for the distance specified by the CLD_PRJ_DIST input.
    cld_proj = (img.select('clouds').directionalDistanceTransform(shadow_azimuth, cld_prj_dist*10)
                .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
                .select('distance')
                .mask()
                .rename('cloud_transform'))

    # Identify the intersection of dark pixels with cloud shadow projection.
    shadows = cld_proj.multiply(dark_pixels).rename('shadows')

    # Add dark pixels, cloud projection, and identified shadows as image bands.
    return img.addBands(ee.Image([dark_pixels, cld_proj, shadows]))


def add_cld_shdw_mask(img, buffer=50):
    # Add cloud component bands.
    img_cloud = add_cloud_bands(img)

    # Add cloud shadow component bands.
    img_cloud_shadow = add_shadow_bands(img_cloud)

    # Combine cloud and shadow mask, set cloud and shadow as value 1, else 0.
    is_cld_shdw = img_cloud_shadow.select('clouds').add(
        img_cloud_shadow.select('shadows')).gt(0)

    # Remove small cloud-shadow patches and dilate remaining pixels by BUFFER input.
    # 20 m scale is for speed, and assumes clouds don't require 10 m precision.
    is_cld_shdw = (is_cld_shdw.focal_min(2).focal_max(buffer*2/20)
                   .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
                   .rename('cloudmask'))

    # Add the final cloud-shadow mask to the image.
    return img_cloud_shadow.addBands(is_cld_shdw)


def downloadAndExtractS2Data(aoi, start_date: str, end_date: str, cloud_percent: int, download_path: str):

    s2_sr_cld_col_eval = get_s2_sr_cld_col(
        aoi, start_date, end_date, cloud_percent)
    cloud_mask_image = (s2_sr_cld_col_eval.map(add_cld_shdw_mask)).mosaic()

    clouds = cloud_mask_image.select('clouds').selfMask().clip(aoi)
    img_bgr = cloud_mask_image.select(['B2', 'B3', 'B4']).clip(aoi)

    clouds_zip = os.path.join(download_path, "download_cloud.zip")
    s2_zip = os.path.join(download_path, "download_S2.zip")

    try:
        downloadImg(img_bgr, aoi, s2_zip, scale=10)
        downloadImg(clouds, aoi, clouds_zip, scale=10)

        extractZip(s2_zip)
        extractZip(clouds_zip)
    except ee.EEException as e:
        print(f"Encountered exception: {type(e)} - {e}")
        print(f"This could be due to level 2 data not available for the selected dates.")
        print(f"Try downloading alternative level 1 data (cloud mask not avaliable)")

        img = getMosaicImgFromGeeImgCollec(
            aoi, "COPERNICUS/S2", ['B2', 'B3', 'B4'], start_date, end_date, cloud_percent)

        download_file = os.path.join(download_path, "download_S2.zip")

        downloadImg(img, aoi, download_file, scale=10)
        extractZip(download_file)


def downloadAndExtractDemData(aoi, download_path: str):
    dsm_collection = ee.ImageCollection('JAXA/ALOS/AW3D30/V3_2')
    elevation = dsm_collection.select('DSM')

    proj = elevation.first().select(0).projection()
    img = dict()
    img["DEM"] = elevation.mosaic().setDefaultProjection(proj)
    img["slope"] = ee.Terrain.slope(img["DEM"].clip(aoi))
    img["hs"] = ee.Terrain.hillshade(img["DEM"].clip(aoi))

    for key in img:
        download_file = os.path.join(download_path, "download_" + key + ".zip")
        downloadImg(img[key], aoi, download_file, scale=30)
        extractZip(download_file)


def downloadEssentialTifFiles(roi, pre_path: str, post_path: str, dem_path: str, pre_date_1: str, pre_date_2: str, post_date_1: str, post_date_2: str, cloud_percent: int):

    print("Downloading pre-event Sentinel 2 data (RGB, cloud coverage) ...")
    downloadAndExtractS2Data(
        roi, pre_date_1, pre_date_2, cloud_percent, pre_path)

    print("Downloading post-event Sentinel 2 data (RGB, cloud coverage) ...")
    downloadAndExtractS2Data(
        roi, post_date_1, post_date_2, cloud_percent, post_path)
    
    print("Downloading DEM data (elevation, hillshade, slope) ...")
    downloadAndExtractDemData(roi, dem_path)


if __name__ == "__main__":
    pass
