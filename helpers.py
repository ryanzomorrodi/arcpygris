import requests
import os
from zipfile import ZipFile

def get_shapefile(req_url: str, output_dir: str) -> str:
    resp = requests.get(req_url)
    temp_zip_path = os.path.join(output_dir, "temp.zip")

    with open(temp_zip_path, "wb") as f:
        f.write(resp.content)
    
    with ZipFile(temp_zip_path, 'r') as zip_ref:
        zfiles = zip_ref.namelist()
        zip_ref.extractall(output_dir)

    shape_file = [file for file in zfiles if file.endswith('.shp')][0]
    shape_file_path = os.path.join(output_dir, shape_file)

    return shape_file_path