REGISTERED_FILE = []

EAST_TEXT_DETECTOR = {
    "key": "M_ALL_006.hdf5",
    "download_name": "M_ALL_006.hdf5",
    "name": "M_ALL_006.hdf5",
    "dir_path": "model",
    "url": "https://drive.google.com/u/0/uc?id=1SCPfjFTn3f6-Ofzx1tgV0xnJkixXLhsN&export=download",
    "compression_method": None,
    "from_google_drive": True,
    "google_drive_id": "1SCPfjFTn3f6-Ofzx1tgV0xnJkixXLhsN",
}
REGISTERED_FILE.append(EAST_TEXT_DETECTOR)

EAST_TEXT_DETECTOR = {
    "key": "NASA_Landslide_Catalog_2008_2021.html",
    "download_name": "NASA_Landslide_Catalog_2008_2021.html",
    "name": "NASA_Landslide_Catalog_2008_2021.html",
    "dir_path": "HTML",
    "url": "https://drive.google.com/u/0/uc?id=1zttpFp3vrHMqCk6jkQOTAX_cFd1NoxIG&export=download",
    "compression_method": None,
    "from_google_drive": True,
    "google_drive_id": "1zttpFp3vrHMqCk6jkQOTAX_cFd1NoxIG&export",
}
REGISTERED_FILE.append(EAST_TEXT_DETECTOR)

EAST_TEXT_DETECTOR = {
    "key": "nasa_global_landslide_catalog_point.csv",
    "download_name": "nasa_global_landslide_catalog_point.csv",
    "name": "nasa_global_landslide_catalog_point.csv",
    "dir_path": "data",
    "url": "https://maps.nccs.nasa.gov/arcgis/sharing/content/items/eec7aee8d2e040c7b8d3ee5fd0e0d7b9/data",
    "compression_method": None,
    "from_google_drive": False,
    "google_drive_id": None,
}
REGISTERED_FILE.append(EAST_TEXT_DETECTOR)

def getResourceRecord(key: str, registry=REGISTERED_FILE):
    """
    Find the file record in the registry with matching key
    INPUTS:
        key - str: the file (record) key. The complete list of registered keys can be
            found in mmxai/utils/cache_manager/file_registry.py
        registry - list: list containing the record of registered files.
    
    RETURNS:
        dict: record dict with matching key
    """

    for entry in registry:
        if entry["key"] == key:
            return entry
    
    raise ValueError(f"Incorrect file key: {key} is not in mmxai cache registry!")