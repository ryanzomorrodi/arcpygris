import arcpy_helpers, helpers
import tempfile

years = [
    '2024',
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
    '2013',
    '2012',
    '2011'
]

def download(year: str, output_path: str, **kargs):
    with tempfile.TemporaryDirectory() as tempdir:
        req_url = get_url(year)
        shape_file_path = helpers.get_shapefile(req_url, tempdir)
        arcpy_helpers.write_feature(shape_file_path, output_path)
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "Primary Road",
            year = year,
            req_urls = [req_url]
        )

def get_url(year: str) -> str:
    req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/PRIMARYROADS/tl_{year}_us_primaryroads.zip"
    
    return req_url
