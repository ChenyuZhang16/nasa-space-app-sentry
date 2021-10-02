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


def downloadFromWeb(url, download_path):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        block_size = 1024
        total_size = int(response.headers.get('content-length', 0))

        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

        with open(download_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=block_size):
                progress_bar.update(len(chunk))
                file.write(chunk)

        progress_bar.close()

        if total_size != 0 and progress_bar.n != total_size:
            os.remove(download_path)

            raise Exception(f"Downloaded file size different from the web content length. " +
                            f"Content length is {total_size}B. File size is {progress_bar.n}B. " +
                            "Try re-downloading.")


def downloadImg(img, aoi, save_path, scale):
    download_url = img.getDownloadURL({
        'region': aoi,
        'scale': scale
    })

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    downloadFromWeb(download_url, save_path)


def extractZip(zip_path, dest_path):
    with zipfile.ZipFile(zip_path, 'r') as zip:
        extracted_names = zip.namelist()
        zip.extractall(path=dest_path)

    return extracted_names


def downloadAndExtractS2Data(aoi, start_date: str, end_date: str, cloud_percent: int, download_path: str):
    img = getMosaicImgFromGeeImgCollec(
        aoi, "COPERNICUS/S2", ['B4', 'B3', 'B2'], start_date, end_date, cloud_percent)

    download_file = os.path.join(download_path, "download_S2.zip")

    downloadImg(img, aoi, download_file, scale=10)
    extractZip(download_file, download_path)


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
        extractZip(download_file, download_path)


if __name__ == "__main__":
    pass
