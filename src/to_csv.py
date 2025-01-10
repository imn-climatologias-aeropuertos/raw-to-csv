from datetime import datetime
from typing import Tuple, Optional, Literal

from aeromet_py import Metar
from aeromet_py.reports.models import Cloud, CloudList, GroupList, MetarWeather


def parse_line(l: str) -> Tuple[str, str]:
    l = l.replace("=", "")

    date = l[0:12]
    metar = l[13:]

    return date, metar


def create_metar(t: Tuple[str, str]) -> Metar:
    date = datetime.strptime(t[0], "%Y%m%d%H%M")
    metar = Metar(t[1], year=date.year, month=date.month)

    return metar


header = [
    "Year",
    "Month",
    "Day",
    "Hour",
    "Minute",
    "Station",
    "Wind_direction",
    "Wind_speed",
    "Wind_gust",
    "Visibility",
    "Cavok",
    "Weather_intensity",
    "Weather_description",
    "Weather_precipitation",
    "Weather_obscuration",
    "Sky_layer1_cover",
    "Sky_layer1_height",
    "Sky_layer1_cloud",
    "Sky_layer2_cover",
    "Sky_layer2_height",
    "Sky_layer2_cloud",
    "Sky_layer3_cover",
    "Sky_layer3_height",
    "Sky_layer3_cloud",
    "Sky_layer4_cover",
    "Sky_layer4_height",
    "Sky_layer4_cloud",
    "Temperature",
    "Dewpoint",
    "Pressure",
]


def num_to_str(num: Optional[float], sig: Literal[1, 2] = 1) -> str:
    if num is None:
        return "null"
    if sig == 1:
        return f"{num:.1f}"
    return f"{num:.2f}"


def process_intensity(i: Optional[str]) -> str:
    match i:
        case "nearby":
            return "VC"
        case _:
            return i


def process_description(d: Optional[str]) -> str:
    match d:
        case "thunderstorm":
            return "TS"
        case "showers":
            return "SH"
        case _:
            return d


def process_precipitation(p: Optional[str]) -> str:
    match p:
        case "rain":
            return "RA"
        case "drizzle":
            return "DZ"
        case _:
            return p


def process_obscuration(o: Optional[str]) -> str:
    match o:
        case "fog":
            return "FG"
        case "mist":
            return "BR"
        case _:
            return o


def process_weather(weathers: GroupList[MetarWeather]) -> str:
    s = ""
    ints = "null"
    desc = "null"
    prec = "null"
    obsc = "null"

    for i in range(3):
        try:
            w = weathers[i]
            ints = process_intensity(w.intensity)
            desc = process_description(w.description)
            prec = process_precipitation(w.precipitation)
            obsc = process_obscuration(w.obscuration)
        except IndexError:
            break

    s += f"{ints},{desc},{prec},{obsc}"

    return s


def cavok_to_bin(cavok: bool) -> str:
    if cavok:
        return "1"
    return "0"


def process_cover(c: str) -> str:
    match c:
        case "a few":
            return "FEW"
        case "scattered":
            return "SCT"
        case "broken":
            return "BKN"
        case "overcast":
            return "OVC"
        case "indefinite ceiling":
            return "VV"
        case "clear":
            return "NSC"


def process_cloud_layer(c: Cloud) -> str:
    cover = c.cover if c.cover else "null"
    h = c.height_in_feet
    type = c.cloud_type if c.cloud_type else "null"

    return f"{process_cover(cover)},{num_to_str(h)},{type}"


def process_clouds(clouds: CloudList) -> str:
    s = ""

    for i in range(4):
        try:
            c = clouds[i]
            s += f"{process_cloud_layer(c)},"
        except IndexError:
            s += "null,null,null"

    return s


def metar_to_csv(m: Metar) -> str:
    s = ""

    s += f"{m.time.time.year}"
    s += f",{m.time.time.month}"
    s += f",{m.time.time.day}"
    s += f",{m.time.time.hour}"
    s += f",{m.time.time.minute}"
    s += f",{m.station.code}"
    s += f",{num_to_str(m.wind.direction_in_degrees)}"
    s += f",{num_to_str(m.wind.speed_in_knot)}"
    s += f",{num_to_str(m.wind.gust_in_knot)}"
    s += f",{num_to_str(m.prevailing_visibility.in_meters)}"
    s += f",{cavok_to_bin(m.prevailing_visibility.cavok)}"
    s += f",{process_weather(m.weathers)}"
    s += f",{process_clouds(m.clouds)}"
    s += f",{num_to_str(m.temperatures.temperature_in_celsius)}"
    s += f",{num_to_str(m.temperatures.dewpoint_in_celsius)}"
    s += f",{num_to_str(m.pressure.in_inHg, sig=2)}"
    s += "\n"

    return s
