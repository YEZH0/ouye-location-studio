"""Built-in coordinate presets used as one-click jump targets in the UI."""

from __future__ import annotations

from typing import TypedDict


class Preset(TypedDict):
    id: str
    name: str
    local_name: str
    country: str
    latitude: float
    longitude: float


PRESETS: list[Preset] = [
    {"id": "nyc", "name": "Times Square", "local_name": "时代广场", "country": "US", "latitude": 40.7570095, "longitude": -73.9859724},
    {"id": "sfo", "name": "Golden Gate Bridge", "local_name": "金门大桥", "country": "US", "latitude": 37.8199286, "longitude": -122.4782551},
    {"id": "madrid", "name": "Puerta del Sol", "local_name": "太阳门广场", "country": "ES", "latitude": 40.4168630, "longitude": -3.7038762},
    {"id": "paris", "name": "Eiffel Tower", "local_name": "埃菲尔铁塔", "country": "FR", "latitude": 48.8583701, "longitude": 2.2944813},
    {"id": "london", "name": "Trafalgar Square", "local_name": "特拉法加广场", "country": "GB", "latitude": 51.5080390, "longitude": -0.1280690},
    {"id": "tokyo", "name": "Shibuya Crossing", "local_name": "涩谷十字路口", "country": "JP", "latitude": 35.6595000, "longitude": 139.7005000},
    {"id": "seoul", "name": "Gwanghwamun", "local_name": "光化门", "country": "KR", "latitude": 37.5759000, "longitude": 126.9769000},
    {"id": "singapore", "name": "Marina Bay Sands", "local_name": "滨海湾金沙", "country": "SG", "latitude": 1.2834000, "longitude": 103.8607000},
    {"id": "sydney", "name": "Sydney Opera House", "local_name": "悉尼歌剧院", "country": "AU", "latitude": -33.8567844, "longitude": 151.2152967},
    {"id": "dubai", "name": "Burj Khalifa", "local_name": "哈利法塔", "country": "AE", "latitude": 25.1971970, "longitude": 55.2743764},
    {"id": "reykjavik", "name": "Hallgrímskirkja", "local_name": "哈尔格林姆教堂", "country": "IS", "latitude": 64.1417000, "longitude": -21.9266000},
    {"id": "beijing", "name": "Tiananmen Square", "local_name": "天安门广场", "country": "中国", "latitude": 39.9055000, "longitude": 116.3976000},
    {"id": "shanghai", "name": "The Bund", "local_name": "外滩", "country": "中国", "latitude": 31.2397000, "longitude": 121.4900000},
    {"id": "shenzhen", "name": "Shenzhen Bay", "local_name": "深圳湾", "country": "中国", "latitude": 22.5176000, "longitude": 113.9477000},
    {"id": "hongkong", "name": "Victoria Harbour", "local_name": "维多利亚港", "country": "中国香港", "latitude": 22.2930000, "longitude": 114.1690000},
    {"id": "taipei", "name": "Taipei 101", "local_name": "台北 101", "country": "中国台湾", "latitude": 25.0339640, "longitude": 121.5644680},
    {"id": "moscow", "name": "Red Square", "local_name": "红场", "country": "RU", "latitude": 55.7539000, "longitude": 37.6208000},
    {"id": "cairo", "name": "Great Pyramid", "local_name": "吉萨金字塔", "country": "EG", "latitude": 29.9792000, "longitude": 31.1342000},
    {"id": "rio", "name": "Christ the Redeemer", "local_name": "基督像", "country": "BR", "latitude": -22.9519160, "longitude": -43.2104870},
    {"id": "capetown", "name": "Table Mountain", "local_name": "桌山", "country": "ZA", "latitude": -33.9628000, "longitude": 18.4098000},
]


def find(preset_id: str) -> Preset | None:
    for preset in PRESETS:
        if preset["id"] == preset_id:
            return preset
    return None


def label(preset: Preset) -> str:
    return f"{preset['local_name']} {preset['name']}（{preset['country']}）"
