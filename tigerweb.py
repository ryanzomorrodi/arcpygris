import asyncio
import hashlib
import json
import nest_asyncio
import os
import re
import tempfile
import tornado.httpclient

nest_asyncio.apply()
base_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/"
CACHE_DIR = os.path.join(tempfile.gettempdir(), "tigerweb_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


cb_server_dict = {
    "Census Divisions": "Region_Division",
    "Census Regions": "Region_Division",
    "States": "State_County",
    "Counties": "State_County",
    "County Subdivisions": "Places_CouSub_ConCity_SubMCD",
    "Census Tracts": "Tracts_Blocks",
    "Census Block Groups": "Tracts_Blocks",
    "Combined New England City and Town Areas": "CBSA",
    "New England City and Town Area Divisions": "CBSA",
    "Metropolitan New England City and Town Areas": "CBSA",
    "Micropolitan New England City and Town Areas": "CBSA",
    "Combined Statistical Areas": "CBSA",
    "Metropolitan Statistical Areas": "CBSA",
    "Micropolitan Statistical Areas": "CBSA",
    "Unified School Districts": "School",
    "Secondary School Districts": "School",
    "Elementary School Districts": "School",
    "Subbarrios": "Places_CouSub_ConCity_SubMCD",
    "Consolidated Cities": "Places_CouSub_ConCity_SubMCD",
    "Incorporated Places": "Places_CouSub_ConCity_SubMCD",
    "Census Designated Places": "Places_CouSub_ConCity_SubMCD",
    "Tribal Census Tracts": "TribalTracts",
    "Tribal Block Groups": "TribalTracts",
    "Alaska Native Regional Corporations": "AIANNHA",
    "Tribal Subdivisions": "AIANNHA",
    "Federal American Indian Reservations": "AIANNHA",
    "Off-Reservation Trust Lands": "AIANNHA",
    "State American Indian Reservations": "AIANNHA",
    "Hawaiian Home Lands": "AIANNHA",
    "Alaska Native Village Statistical Areas": "AIANNHA",
    "Oklahoma Tribal Statistical Areas": "AIANNHA",
    "State Designated Tribal Statistical Areas": "AIANNHA",
    "Tribal Designated Statistical Areas": "AIANNHA",
    "American Indian Joint-Use Areas ": "AIANNHA",
    "Congressional Districts": "Legislative",
    "State Legislative Districts - Upper": "Legislative",
    "State Legislative Districts - Lower": "Legislative",
    "Voting Districts": "Legislative",
}

is_state_subsettable = [
    "States",
    "Counties",
    "County Subdivisions",
    "Census Tracts",
    "Census Block Groups",
    "Census Blocks",
    "Unified School Districts",
    "Secondary School Districts",
    "Consolidated Cities",
    "Incorporated Places",
    "Census Designated Places",
    "Elementary School Districts",
    "Congressional Districts",
    "State Legislative Districts - Upper",
    "State Legislative Districts - Lower",
    "Voting Districts",
]

state_to_fips = {
    "Alabama": "01",
    "Alaska": "02",
    "American Samoa": "60",
    "Arizona": "04",
    "Arkansas": "05",
    "California": "06",
    "Colorado": "08",
    "Commonwealth of the Northern Marina Islands": "69",
    "Connecticut": "09",
    "Deleware": "10",
    "District of Columbia": "11",
    "Florida": "12",
    "Georgia": "13",
    "Guam": "66",
    "Hawaii": "15",
    "Idaho": "16",
    "Illinois": "17",
    "Indiana": "18",
    "Iowa": "19",
    "Kansas": "20",
    "Kentucky": "21",
    "Louisiana": "22",
    "Maine": "23",
    "Maryland": "24",
    "Massachussets": "25",
    "Michigan": "26",
    "Minnesota": "27",
    "Mississippi": "28",
    "Missouri": "29",
    "Montana": "30",
    "Nebraska": "31",
    "Nevada": "32",
    "New Hampshire": "33",
    "New Jersey": "34",
    "New Mexico": "35",
    "New York": "36",
    "North Carolina": "37",
    "North Dakota": "38",
    "Ohio": "39",
    "Oklahoma": "40",
    "Oregon": "41",
    "Pennsylvannia": "42",
    "Puerto Rico": "72",
    "Rhode Island": "44",
    "South Carolina": "45",
    "South Dakota": "46",
    "Tennessee": "47",
    "Texas": "48",
    "United States Virgin Islands": "78",
    "Utah": "49",
    "Vermont": "50",
    "Virginia": "51",
    "Washington": "53",
    "West Virginia": "54",
    "Wisconsin": "55",
    "Wyoming": "56",
}


def get_cache_path(url: str) -> str:
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{url_hash}.json")


async def available_year_services(geo: str, cb: bool) -> dict:
    http_client = tornado.httpclient.AsyncHTTPClient()

    cb_urls = {}
    tigerweb_urls = {}
    census_urls = {}
    if cb:
        cb_urls = await available_year_map_servers(http_client, geo, cb, False)
        in_regex = re.compile(
            rf"^(?:\d{{4}}|\d+(?:st|nd|rd|th))? ?{re.escape(geo)} \d+[A-Z]$"
        )
    else:
        tigerweb_urls, census_urls = await asyncio.gather(
            available_year_map_servers(http_client, geo, cb, False),
            available_year_map_servers(http_client, geo, cb, True),
        )
        in_regex = re.compile(rf"^(?:\d{{4}}|\d+(?:st|nd|rd|th))? ?{re.escape(geo)}$")

    urls = cb_urls | tigerweb_urls | census_urls

    url_list = list(urls.values())
    data_list = await asyncio.gather(
        *[get_json_with_cache(http_client, u) for u in url_list]
    )
    responses = dict(zip(url_list, data_list))

    available_years = {}
    for service_name, url in urls.items():
        data = responses.get(url)
        if not data:
            continue

        matched = {
            layer["layerName"]: layer["layerId"]
            for layer in data.get("layers", [])
            if in_regex.search(layer["layerName"])
        }

        if matched:
            available_years[service_name] = matched

    return available_years


async def available_year_map_servers(
    http_client, geo: str, cb: bool, census: bool
) -> dict:
    if cb:
        url = base_url
        regex = r"Generalized_(?:TAB|ACS)\d{4}"
    else:
        if census:
            url = f"{base_url}Census2020"
            regex = r"tigerWMS_Census\d{4}"
        else:
            url = f"{base_url}TIGERweb"
            regex = r"tigerWMS_ACS\d{4}"
    pattern = re.compile(regex)

    data = await get_json_with_cache(http_client, url)

    if cb:
        service_names = data.get("folders", [])
    else:
        service_names = [s.get("name") for s in data.get("services", [])]

    if cb:
        url = base_url
    else:
        if census:
            url = f"{base_url}Census2020"
        else:
            url = f"{base_url}TIGERweb"

    if cb:
        map_server = cb_server_dict[geo]
    year_services = [
        f"{s}/{map_server}" if cb else s for s in service_names if pattern.search(s)
    ]

    return {s: f"{base_url}{s}/MapServer/legend" for s in year_services}


async def get_json_with_cache(http_client, url: str):
    cache_path = get_cache_path(url)

    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass

    try:
        response = await http_client.fetch(f"{url}?f=pjson")
        if response.code == 200:
            content = response.body.decode()
            with open(cache_path, "w") as f:
                f.write(content)
            return json.loads(content)
    except Exception as e:
        print(f"Error fetching {url}: {e}")

    return None
