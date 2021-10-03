from pyna.rasterlib import Raster

import numpy as np
import os


def convTiffUint16ToUint8(in_path, out_path):
    arr, tr, pr, _ = Raster().load_image(in_path)

    assert arr.dtype == np.uint16

    arr_uint8 = (arr/256.0).astype('uint8')

    Raster().write_image(arr_uint8, out_path, tr, pr)


def duplicateUint16AsUint8(tiff_path):
    name, ext = os.path.splitext(tiff_path)
    out_path = name + "_uint8" + ext
    convTiffUint16ToUint8(tiff_path, out_path)


def convtToUint8(tiff_folder):
    duplicateUint16AsUint8(os.path.join(tiff_folder, "download.B2.tif"))
    duplicateUint16AsUint8(os.path.join(tiff_folder, "download.B3.tif"))
    duplicateUint16AsUint8(os.path.join(tiff_folder, "download.B4.tif"))


def generateRoiFromS2(S2_path, out_dir):
    arr, tr, pr, _ = Raster().load_image(S2_path)
    out_path = os.path.join(out_dir, "aoi_S2.tif")
    Raster().write_image(np.ones_like(arr, dtype=np.uint8), out_path, tr, pr)


def combineCloudMask(pre_path: str, post_path: str, out_dir: str):

    arrs = list()
    trs = list()
    prs = list()

    pre_mask_path = os.path.join(pre_path, "download.clouds.tif")
    post_mask_path = os.path.join(post_path, "download.clouds.tif")

    combine_mask_path = os.path.join(out_dir, "clouds.tif")

    if os.path.exists(pre_mask_path):
        arr, tr, pr, _ = Raster().load_image(pre_mask_path)

        arrs.append(arr)
        trs.append(tr)
        prs.append(pr)

    if os.path.exists(post_mask_path):
        arr, tr, pr, _ = Raster().load_image(post_mask_path)

        arrs.append(arr)
        trs.append(tr)
        prs.append(pr)

    num_of_mask = len(arrs)

    if num_of_mask == 1:
        Raster().write_image(arrs[0], combine_mask_path, trs[0], prs[0])
    elif num_of_mask == 2:
        mask_union = np.logical_or(*arrs)
        combined_arr = np.zeros_like(mask_union, dtype=np.uint8)
        combined_arr[mask_union] = 1
        Raster().write_image(combined_arr, combine_mask_path, trs[0], prs[0])


def preprocessTiffs(pre_path: str, post_path: str, aoi_dir: str):

    convtToUint8(pre_path)
    convtToUint8(post_path)

    generateRoiFromS2(os.path.join(pre_path, "download.B2_uint8.tif"), aoi_dir)

    combineCloudMask(pre_path, post_path, aoi_dir)


if __name__ == "__main__":
    pass
