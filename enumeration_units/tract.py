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
    '2013',
    '2010',
    '2000',
    '1990'
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
    '2011',
    '2010',
    '2000'
]

years = sorted(list(set(cb_years + tg_years)), reverse=True)

def download(geom_type: str, resolution: str, year: str, states: list[str], output_path: str, **kargs):
    if not resolution:
        resolution = "500k"
    if not states:
        state_geoids = ["us"]
    else:
        state_geoids = [fips.state_to_fips[state] for state in states]

    with tempfile.TemporaryDirectory() as tempdir:
        shape_file_paths = []
        req_urls = []
        for state_geoid in state_geoids:
            req_url = get_url(geom_type, resolution, year, state_geoid)
            req_urls.append(req_url)
            shape_file_paths.append(helpers.get_shapefile(req_url, tempdir))

        arcpy_helpers.merge_features(shape_file_paths, output_path)
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "Tract",
            year = year,
            req_urls = req_urls,
            geom_type = geom_type,
            resolution = resolution,
            states = states
        )

def get_url(geom_type: str, resolution: str, year: str, state_geoid: str) -> str:
    year_int = int(year)
    year_suffix = year[2:]

    if geom_type == "Cartographic":
        if year_int >= 2014:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state_geoid}_tract_{resolution}.zip"
        elif year_int == 2013:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_{state_geoid}_tract_500k.zip"
        elif year_int == 2010:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_{state_geoid}_140_00_500k.zip"
        elif year_int in [1990, 2000]:
            req_url = f"https://www2.census.gov/geo/tiger/PREVGENZ/tr/tr{year_suffix}shp/tr{state_geoid}_d{year_suffix}_shp.zip"
    else:
        if year_int >= 2011:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state_geoid}_tract.zip"
        elif year_int in [2000, 2010]:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER2010/TRACT/{year}/tl_2010_{state_geoid}_tract{year_suffix}.zip"
    return req_url