import arcpy_helpers, helpers
import fips
import tempfile

cb_years = [
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

tg_years = [
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

years = sorted(list(set(cb_years + tg_years)), reverse=True)

def download(geom_type: str, year: str, states: list[str], output_path: str, **kargs):
    if not states:
        state_geoids = ["us"]
    else:
        state_geoids = [fips.state_to_fips[state] for state in states]

    with tempfile.TemporaryDirectory() as tempdir:
        shape_file_paths = []
        req_urls = []
        for state_geoid in state_geoids:
            req_url = get_url(geom_type, year, state_geoid)
            req_urls.append(req_url)
            shape_file_paths.append(helpers.get_shapefile(req_url, tempdir))

        arcpy_helpers.merge_features(shape_file_paths, output_path)
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "Place",
            year = year,
            req_urls = req_urls,
            geom_type = geom_type,
            states = states
        )

def get_url(geom_type: str, year: str, state_geoid: str) -> str:
    year_int = int(year)
    year_suffix = year[2:]

    if geom_type == "Cartographic":
        req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state_geoid}_place_500k.zip"
    else:
        req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/PLACE/tl_{year}_{state_geoid}_place.zip"
    
    return req_url
