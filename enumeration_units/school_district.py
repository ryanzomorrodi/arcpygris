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
    '2016'
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

def download(geom_type: str, year: str, sd_type: str, states: list[str], output_path: str, **kargs):
    if not states:
        state_geoids = ["us"]
    else:
        state_geoids = [fips.state_to_fips[state] for state in states]
    
    with tempfile.TemporaryDirectory() as tempdir:
        req_urls = []
        shape_file_paths = []
        for state_geoid in state_geoids:
            req_url = get_url(geom_type, year, sd_type, state_geoid)
            req_urls.append(req_url)
            shape_file_paths.append(helpers.get_shapefile(req_url, tempdir))

        arcpy_helpers.merge_features(shape_file_paths, output_path)
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "School District",
            year = year,
            req_urls = req_urls,
            geom_type = geom_type,
            sd_type = sd_type,
            states = states
        )

def get_url(geom_type: str, year: str, sd_type: str, state_geoid: str) -> str:
    year_int = int(year)
    year_suffix = year[2:]

    if sd_type == "Unified":
        sd_type_abbrv = "sldu"
    elif sd_type == "Elementary":
        sd_type_abbrv = "elsd"
    else:
        sd_type_abbrv = "scsd"
    
    if geom_type == "Cartographic":
        req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state_geoid}_{sd_type_abbrv}_500k.zip"
    else:
        req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/{sd_type_abbrv.upper()}/tl_{year}_{state_geoid}_{sd_type_abbrv}.zip"

    return req_url
