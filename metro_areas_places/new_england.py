import arcpy_helpers, helpers
import tempfile

cb_years = [
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

def download(geom_type: str, year: str, resolution, necta_type: str, output_path: str, **kargs):
    with tempfile.TemporaryDirectory() as tempdir:
        req_url = get_url(geom_type, year, resolution, necta_type)
        shape_file_path = helpers.get_shapefile(req_url, tempdir)
        arcpy_helpers.write_feature(shape_file_path, output_path)
    
    if ".gdb" in output_path.lower():
        arcpy_helpers.add_metadata(
            output_path,
            geography = "New England",
            year = year,
            req_urls = [req_url],
            geom_type = geom_type,
            resolution = resolution,
            necta_type = necta_type
        )

def get_url(geom_type: str, year: str, resolution: str, necta_type: str) -> str:
    year_int = int(year)
    year_suffix = year[2:]
    if not resolution:
        resolution = "500k"

    if geom_type == "Cartographic":
        if year_int >= 2014:
                req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_necta_{resolution}.zip"
        elif year_int == 2013:
                req_url = f"https://www2.census.gov/geo/tiger/GENZ{year}/cb_{year}_us_necta_{resolution}.zip"
    else:
        if year_int >= 2010:
            if necta_type == "NECTA":
                req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/NECTA/tl_{year}_us_necta.zip"
            elif necta_type == "Combined NECTA":
                req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CNECTA/tl_{year}_us_cnecta.zip"
            elif necta_type == "NECTA Division":
                req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/NECTADIV/tl_{year}_us_nectadiv.zip"
        elif year_int == 2010:
            if necta_type == "NECTA":
                req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/NECTA/2010/tl_{year}_us_necta.zip"
            elif necta_type == "Combined NECTA":
                req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CNECTA/2010/tl_{year}_us_cnecta.zip"
            elif necta_type == "NECTA Division":
                req_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/NECTADIV/2010/tl_{year}_us_nectadiv.zip"
    
    return req_url
