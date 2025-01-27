import arcpy_helpers, helpers
import fips
import tempfile

cb_years = [
    '2020'
]

tg_years = [
    '2020',
    '2012'
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
            geography = "Voting District",
            year = year,
            req_urls = req_urls,
            geom_type = geom_type,
            states = states
        )

def get_url(geom_type: str, year: str, state_geoid: str) -> str:
    year_int = int(year)

    if geom_type == "Cartographic":
        if year_int == 2020:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_{state_geoid}_vtd_500k.zip"
    else:
        if year_int == 2020:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER2020PL/LAYER/VTD/2020/tl_2020_{state_geoid}_vtd20.zip"
        elif year_int == 2012:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER2012/VTD/tl_2012_{state_geoid}_vtd10.zip"

    return req_url