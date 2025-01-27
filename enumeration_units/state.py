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
    if not states:
        state_geoids = ["us"]
    else:
        state_geoids = [fips.state_to_fips[state] for state in states]

    with tempfile.TemporaryDirectory() as tempdir:
        req_url, where_exp = get_url(geom_type, resolution, year)
        shape_file_path = helpers.get_shapefile(req_url, tempdir)
        if state_geoids == ["us"]:
            arcpy_helpers.write_feature(shape_file_path, output_path)
        else:
            where_exp += "(" + ",".join("'" + state_geoid + "'" for state_geoid in state_geoids) + ")"
            arcpy_helpers.write_feature(shape_file_path, output_path, where_exp)
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "State",
            year = year,
            req_urls = [req_url],
            geom_type = geom_type,
            resolution = resolution,
            states = states
        )

def get_url(geom_type: str, resolution: str, year: str) -> tuple[str, str]:
    year_int = int(year)
    year_suffix = year[2:]

    if geom_type == "Cartographic":
        if year_int >= 2014:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_state_{resolution}.zip"
            where_exp = "STATEFP IN "
        elif year_int == 2013:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_state_{resolution}.zip"
            where_exp = "STATEFP IN "
        elif year_int == 2010:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_us_040_00_{resolution}.zip"
            where_exp = "STATE IN "
        elif year_int in [1990, 2000]:
            req_url = f"https://www2.census.gov/geo/tiger/PREVGENZ/st/st{year_suffix}shp/st99_d{year_suffix}_shp.zip"
            where_exp = "ST IN "
    else:
        if year_int >= 2011:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/STATE/tl_{year}_us_state.zip"
            where_exp = "STATEFP IN "
        elif year_int in [2000, 2010]:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER2010/STATE/{year}/tl_2010_us_state{year_suffix}.zip"
            where_exp = f"STATEFP{year_suffix} IN "
    
    return (req_url, where_exp)
