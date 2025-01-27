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
    '2011',
    '2010'
]

years = sorted(list(set(cb_years + tg_years)), reverse = True)

def download(geom_type: str, resolution: str, year: str, states: list[str], output_path: str, **kargs):
    if not states:
        state_geoids = ["us"]
    else:
        state_geoids = [fips.state_to_fips[state] for state in states]

    with tempfile.TemporaryDirectory() as tempdir:
        if geom_type == "TIGER" and int(year) >= 2023:
            req_urls = []
            shape_file_paths = []
            for state_geoid in state_geoids:
                req_url, _ = get_url(geom_type, resolution, year, state_geoid)
                req_urls.append(req_url)
                shape_file_paths.append(helpers.get_shapefile(req_url, tempdir))

            arcpy_helpers.merge_features(shape_file_paths, output_path)
        else:
            req_url, where_exp = get_url(geom_type, resolution, year, "us")
            req_urls = [req_url]
            shape_file_path = helpers.get_shapefile(req_url, tempdir)
            if state_geoids == ["us"]:
                arcpy_helpers.write_feature(shape_file_path, output_path)
            else:
                where_exp += "(" + ",".join("'" + state_geoid + "'" for state_geoid in state_geoids) + ")"
                arcpy_helpers.write_feature(shape_file_path, output_path, where_exp)
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "Congressional District",
            year = year,
            req_urls = req_urls,
            geom_type = geom_type,
            resolution = resolution,
            states = states
        )
            

def get_url(geom_type: str, resolution: str, year: str, state_geoid: str) -> tuple[str, str]:
    year_int = int(year)
    congress = year_to_congress(year_int)

    if geom_type == "Cartographic":
        if year_int >= 2014:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_cd{congress}_{resolution}.zip"
            where_exp = "STATEFP IN "
        elif year_int == 2013:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_cd{congress}_{resolution}.zip"
            where_exp = "STATEFP IN "
    else:
        if year_int >= 2023:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CD/tl_{year}_{state_geoid}_cd{congress}.zip"
            where_exp = "STATEFP IN "
        elif year_int >= 2011:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CD/tl_{year}_us_cd{congress}.zip"
            where_exp = "STATEFP IN "
        elif year_int == 2010:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CD/{congress}/tl_{year}_us_cd{congress}.zip"
            where_exp = "STATEFP10 IN "
    
    return (req_url, where_exp)

def year_to_congress(year: int) -> str:
    if year == 2024:
        return "119"
    elif year in [2022, 2023]:
        return "118"
    elif year >= 2018 and year <= 2021:
        return "116"
    elif year in [2016, 2017]:
        return "115"
    elif year in [2014, 2015]:
        return "114"
    elif year == 2013:
        return "113"
    elif year in [2011, 2012]:
        return "112"
    elif year == 2010:
        return "111"