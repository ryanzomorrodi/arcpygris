import arcpy_helpers, helpers
import fips
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
    '2011',
    '2010',
    '2000'
]

def download(year: str, states: list[str], output_path: str, **kargs):
    if not states:
        state_geoids = ["us"]
    else:
        state_geoids = [fips.state_to_fips[state] for state in states]
    
    with tempfile.TemporaryDirectory() as tempdir:
        req_urls = []
        shape_file_paths = []
        for state_geoid in state_geoids:
            req_url = get_url(year, state_geoid)
            req_urls.append(req_url)
            shape_file_paths.append(helpers.get_shapefile(req_url, tempdir))

        arcpy_helpers.merge_features(shape_file_paths, output_path)

    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "Block",
            year = year,
            req_urls = req_urls,
            states = states
        )

def get_url(year: str, state_geoid: str) -> str:
    year_int = int(year)
    year_suffix = year[2:]
    if year_int >= 2020:
        req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TABBLOCK20/tl_{year}_{state_geoid}_tabblock20.zip"
    elif year_int >= 2014:
        req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TABBLOCK/tl_{year}_{state_geoid}_tabblock10.zip"
    elif year_int >= 2011:
        req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TABBLOCK/tl_{year}_{state_geoid}_tabblock.zip"
    elif year_int in [2000, 2010]:
        req_url = f"https://www2.census.gov/geo/tiger/TIGER2010/TABBLOCK/{year}/tl_2010_{state_geoid}_tabblock{year_suffix}.zip"
    
    return req_url
