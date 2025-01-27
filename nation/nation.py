import arcpy_helpers, helpers
import tempfile

years = [
    '2023',
    '2022',
    '2021',
    '2020',
    '2019',
    '2018',
    '2017',
    '2016',
    '2015',
    '2014',
    '2013'
]

def download(year: str, resolution: str, output_path: str, **kargs):
    with tempfile.TemporaryDirectory() as tempdir:
        req_url = get_url(year, resolution)
        shape_file_path = helpers.get_shapefile(req_url, tempdir)
        arcpy_helpers.write_feature(shape_file_path, output_path)
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "Nation",
            year = year,
            req_urls = [req_url],
            resolution = resolution
        )

def get_url(year: str, resolution: str) -> str:
    year_int = int(year)
    if year_int == 2013:
        req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_nation_{resolution}.zip"
    elif year_int >= 2014:
        req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_nation_{resolution}.zip"
    
    return req_url
