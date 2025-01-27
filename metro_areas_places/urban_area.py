import arcpy_helpers, helpers
import tempfile

cb_years = [
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
    '2012'
]

years = sorted(list(set(cb_years + tg_years)), reverse = True)

def download(geom_type: str, year: str, ua_criteria: str, output_path: str, **kargs):
    with tempfile.TemporaryDirectory() as tempdir:
        req_url = get_url(geom_type, year, ua_criteria)
        shape_file_path = helpers.get_shapefile(req_url, tempdir)
        arcpy_helpers.write_feature(shape_file_path, output_path)
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "Urban Area",
            year = year,
            req_urls = [req_url],
            geom_type = geom_type,
            ua_criteria = ua_criteria
        )

def get_url(geom_type: str, year: str, ua_criteria: str) -> str:
    year_int = int(year)
    year_suffix = year[2:]
    ua_criteria_suffix = ua_criteria[2:]

    if geom_type == "Cartographic":
        if year_int == 2020:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_ua20_corrected_500k.zip"
        if year_int >= 2014 and year_int <= 2019:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_ua10_500k.zip"
        elif year_int == 2013:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_ua10_500k.zip"
    else:
        if year_int == 2024:
            req_url = "https://www2.census.gov/geo/tiger/TIGER2024/UAC20/tl_2024_us_uac20.zip"
        if year_int == 2023:
            req_url = "https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip"
        if year_int == 2022:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER2022/UAC/tl_2022_us_uac{ua_criteria_suffix}.zip"
        if year_int == 2021:
            req_url = "https://www2.census.gov/geo/tiger/TIGER2021/UAC/tl_2021_us_uac10.zip"
        if year_int == 2020:
            if ua_criteria == "2020":
                req_url = f"https://www2.census.gov/geo/tiger/TIGER2020/UAC/tl_2020_us_uac20_corrected.zip"
            else:
                req_url = f"https://www2.census.gov/geo/tiger/TIGER2020/UAC/tl_2020_us_uac10.zip"
        if year_int >= 2012 and year_int <= 2019:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/UAC/tl_{year}_us_uac10.zip"
    
    return req_url
