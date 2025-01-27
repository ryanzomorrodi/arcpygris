import arcpy_helpers, helpers
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

def download(geom_type: str, year: str, output_path: str, **kargs):
    with tempfile.TemporaryDirectory() as tempdir:
        req_url = get_url(geom_type, year)
        shape_file_path = helpers.get_shapefile(req_url, tempdir)
        arcpy_helpers.write_feature(shape_file_path, output_path)
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "Tribal Tract",
            year = year,
            req_urls = [req_url],
            geom_type = geom_type
        )

def get_url(geom_type: str, year: str) -> str:
    year_int = int(year)

    if geom_type == "Cartographic":
        if year_int >= 2014:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_ttract_500k.zip"
        elif year_int == 2013:
            req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_ttract_500k.zip"
    else:
        if year_int >= 2013:
            req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TTRACT/tl_{year}_us_ttract.zip"
    
    return req_url
