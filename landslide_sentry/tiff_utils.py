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

if __name__ == "__main__":
    pass