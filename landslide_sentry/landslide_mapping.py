from cnn_landslide_mapping.predictor import detect_landslides

import os


def generateLandsideMap(model_path: str, pre_dir: str, post_dir: str, dem_dir: str, save_dir: str, data_dir: str, debug=False):

    raw_data_dict = dict()

    raw_data_dict["dem_path"] = os.path.join(dem_dir, "download.DSM.tif")
    raw_data_dict["hs_path"] = os.path.join(
        dem_dir, "download.hillshade.tif")
    raw_data_dict["slope_path"] = os.path.join(dem_dir, "download.slope.tif")

    raw_data_dict["post_image_path"] = dict()
    raw_data_dict["post_image_path"]["B2"] = os.path.join(
        post_dir, "download.B2_uint8.tif")
    raw_data_dict["post_image_path"]["B3"] = os.path.join(
        post_dir, "download.B3_uint8.tif")
    raw_data_dict["post_image_path"]["B4"] = os.path.join(
        post_dir, "download.B4_uint8.tif")

    raw_data_dict["pre_image_path"] = dict()
    raw_data_dict["pre_image_path"]["B2"] = os.path.join(
        pre_dir, "download.B2_uint8.tif")
    raw_data_dict["pre_image_path"]["B3"] = os.path.join(
        pre_dir, "download.B3_uint8.tif")
    raw_data_dict["pre_image_path"]["B4"] = os.path.join(
        pre_dir, "download.B4_uint8.tif")

    raw_data_dict["no_data_mask"] = os.path.join(data_dir, "clouds.tif")

    aoi_path = os.path.join(data_dir, "aoi_S2.tif")

    detect_landslides(model_path=model_path, output_path=save_dir,
                      raw_data_dict=raw_data_dict, roi_path=aoi_path, debug=debug)
