import arcpy_helpers, helpers
import fips
import tempfile
from ftplib import FTP

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

def download(year: str, states: list[str], output_path: str, **kargs):
    if not states:
        state_geoids = ["us"]
    else:
        state_geoids = [fips.state_to_fips[state] for state in states]
    
    ftp = FTP('ftp2.census.gov')
    ftp.login() 

    with tempfile.TemporaryDirectory() as tempdir:
        shape_file_paths = []
        req_urls = []
        for state_geoid in state_geoids:
            state_req_urls = get_urls(year, state_geoid, ftp)
            req_urls = req_urls + state_req_urls
        for req_url in req_urls:
            shape_file_paths.append(helpers.get_shapefile(req_url, tempdir))

        arcpy_helpers.merge_features(shape_file_paths, output_path)

    ftp.quit()
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "Address Range",
            year = year,
            req_urls = req_urls,
            states = states
        )

def get_urls(year: str, state_geoid: str, ftp: FTP) -> list[str]:

    directory = f"geo/tiger/TIGER{year}/ADDRFEAT"
    search_criteria = f"geo/tiger/TIGER{year}/ADDRFEAT/tl_{year}_{state_geoid}"

    req_urls = ["https://www2.census.gov/" + file_name for file_name in ftp.nlst(directory) if search_criteria in file_name]

    return req_urls