import asyncio
import hashlib
import json
import nest_asyncio
import os
import re
import tempfile
import tornado.httpclient
from typing import TypedDict

nest_asyncio.apply()
base_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/"
CACHE_DIR = os.path.join(tempfile.gettempdir(), "tigerweb_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


class GeoInfo(TypedDict):
    cb_server: str | None
    is_state_subsettable: bool


geo_groups: dict[str, dict[str, GeoInfo]] = {
    "Primary Nested Geographies": {
        "Census Divisions": {
            "cb_server": "Region_Division",
            "is_state_subsettable": False,
        },
        "Census Regions": {
            "cb_server": "Region_Division",
            "is_state_subsettable": False,
        },
        "States": {"cb_server": "State_County", "is_state_subsettable": True},
        "Counties": {"cb_server": "State_County", "is_state_subsettable": True},
        "County Subdivisions": {
            "cb_server": "Places_CouSub_ConCity_SubMCD",
            "is_state_subsettable": True,
        },
        "Census Tracts": {"cb_server": "Tracts_Blocks", "is_state_subsettable": True},
        "Census Block Groups": {
            "cb_server": "Tracts_Blocks",
            "is_state_subsettable": True,
        },
        "Census Blocks": {"cb_server": None, "is_state_subsettable": True},
        "Zip Code Tabulation Areas": {"cb_server": None, "is_state_subsettable": False},
    },
    "Places": {
        "Subbarrios": {
            "cb_server": "Places_CouSub_ConCity_SubMCD",
            "is_state_subsettable": False,
        },
        "Consolidated Cities": {
            "cb_server": "Places_CouSub_ConCity_SubMCD",
            "is_state_subsettable": True,
        },
        "Incorporated Places": {
            "cb_server": "Places_CouSub_ConCity_SubMCD",
            "is_state_subsettable": True,
        },
        "Census Designated Places": {
            "cb_server": "Places_CouSub_ConCity_SubMCD",
            "is_state_subsettable": True,
        },
    },
    "Legislative": {
        "Congressional Districts": {
            "cb_server": "Legislative",
            "is_state_subsettable": True,
        },
        "State Legislative Districts - Upper": {
            "cb_server": "Legislative",
            "is_state_subsettable": True,
        },
        "State Legislative Districts - Lower": {
            "cb_server": "Legislative",
            "is_state_subsettable": True,
        },
        "Voting Districts": {
            "cb_server": "Legislative",
            "is_state_subsettable": True,
        },
    },
    "Schools": {
        "Unified School Districts": {
            "cb_server": "School",
            "is_state_subsettable": True,
        },
        "Secondary School Districts": {
            "cb_server": "School",
            "is_state_subsettable": True,
        },
        "Elementary School Districts": {
            "cb_server": "School",
            "is_state_subsettable": True,
        },
    },
    "Core-Based Statistical Areas": {
        "Combined Statistical Areas": {
            "cb_server": "CBSA",
            "is_state_subsettable": False,
        },
        "Metropolitan Statistical Areas": {
            "cb_server": "CBSA",
            "is_state_subsettable": False,
        },
        "Micropolitan Statistical Areas": {
            "cb_server": "CBSA",
            "is_state_subsettable": False,
        },
        "Metropolitan New England City and Town Areas": {
            "cb_server": "CBSA",
            "is_state_subsettable": False,
        },
        "Micropolitan New England City and Town Areas": {
            "cb_server": "CBSA",
            "is_state_subsettable": False,
        },
        "Combined New England City and Town Areas": {
            "cb_server": "CBSA",
            "is_state_subsettable": False,
        },
        "New England City and Town Area Divisions": {
            "cb_server": "CBSA",
            "is_state_subsettable": False,
        },
    },
    "American Indian, Alaska Native, and Native Hawaiian Areas": {
        "Tribal Census Tracts": {
            "cb_server": "TribalTracts",
            "is_state_subsettable": False,
        },
        "Tribal Block Groups": {
            "cb_server": "TribalTracts",
            "is_state_subsettable": False,
        },
        "Tribal Subdivisions": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
        "Tribal Designated Statistical Areas": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
        "State Designated Tribal Statistical Areas": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
        "Oklahoma Tribal Statistical Areas": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
        "Federal American Indian Reservations": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
        "State American Indian Reservations": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
        "American Indian Joint-Use Areas": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
        "Off-Reservation Trust Lands": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
        "Alaska Native Regional Corporations": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
        "Alaska Native Village Statistical Areas": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
        "Hawaiian Home Lands": {
            "cb_server": "AIANNHA",
            "is_state_subsettable": False,
        },
    },
}
geo_info = {k: v for sub in geo_groups.values() for k, v in sub.items()}

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

    map_server = geo_info.get(geo).get("cb_server")
    year_services = [
        f"{s}/{map_server}" if cb else s for s in service_names if pattern.search(s)
    ]

    return {s: f"{base_url}{s}/MapServer/legend" for s in year_services}


async def get_json_with_cache(http_client, url: str) -> dict:
    cache_path = get_cache_path(url)

    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)

    response = await http_client.fetch(f"{url}?f=pjson")
    content = response.body.decode()
    with open(cache_path, "w") as f:
        f.write(content)
    return json.loads(content)
