from cnn_landslide_mapping.predictor import detect_landslides

import os


def generateLandsideMap(model_path: str, pre_path: str, post_path: str, dem_path: str, save_path: str, aoi_path: str,  debug=False):

    raw_data_dict = dict()

    raw_data_dict["dem_path"] = os.path.join(dem_path, "download.DSM.tif")
    raw_data_dict["hs_path"] = os.path.join(
        dem_path, "download.hillshade.tif")
    raw_data_dict["slope_path"] = os.path.join(dem_path, "download.slope.tif")

    raw_data_dict["post_image_path"] = dict()
    raw_data_dict["post_image_path"]["B2"] = os.path.join(
        post_path, "download.B2_uint8.tif")
    raw_data_dict["post_image_path"]["B3"] = os.path.join(
        post_path, "download.B3_uint8.tif")
    raw_data_dict["post_image_path"]["B4"] = os.path.join(
        post_path, "download.B4_uint8.tif")

    raw_data_dict["pre_image_path"] = dict()
    raw_data_dict["pre_image_path"]["B2"] = os.path.join(
        pre_path, "download.B2_uint8.tif")
    raw_data_dict["pre_image_path"]["B3"] = os.path.join(
        pre_path, "download.B3_uint8.tif")
    raw_data_dict["pre_image_path"]["B4"] = os.path.join(
        pre_path, "download.B4_uint8.tif")

    raw_data_dict["no_data_mask"] = None

    detect_landslides(model_path=model_path, output_path=save_path,
                      raw_data_dict=raw_data_dict, roi_path=aoi_path, debug=debug)
