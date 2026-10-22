"""暗い空スポット(Bortle<=2)の日本全域データ dark_alljp を作る。"""
import json

import pandas as pd
import reverse_geocoder as rg


def _load_dark(path, max_bortle, bbox=None):
    """JSON を読み、Bortle<=max_bortle(と bbox)の点だけを DataFrame にする。

    全点の DataFrame は作らない(メモリ節約)。bbox = (lat_min, lat_max, lon_min, lon_max)
    """
    with open(path) as f:
        points = json.load(f)
    keep = [p for p in points if p["bortle"] <= max_bortle]
    del points
    if bbox:
        la0, la1, lo0, lo1 = bbox
        keep = [p for p in keep if la0 <= p["lat"] <= la1 and lo0 <= p["lon"] <= lo1]
    return pd.DataFrame(keep)


def _add_place(df):
    """lat/lon から country / prefecture / city 列を付ける。"""
    results = rg.search(list(zip(df["lat"], df["lon"])))
    df["country"] = [r["cc"] for r in results]
    df["prefecture"] = [r["admin1"] for r in results]
    df["city"] = [r["name"] for r in results]
    return df


def load_dark_jp(path="JPN.json", max_bortle=2):
    """本土: JPN.json から Bortle<=2 かつ JP のみ。"""
    dark = _add_place(_load_dark(path, max_bortle))
    return dark[dark["country"] == "JP"].copy()


def load_okinawa(path="CHN.json", max_bortle=2):
    """沖縄: CHN.json の沖縄エリアから Bortle<=2。"""
    return _add_place(_load_dark(path, max_bortle, bbox=(24, 27, 122, 131)))


def build_dark_alljp():
    dark_jp = load_dark_jp()
    okinawa = load_okinawa()
    dark_alljp = pd.concat([dark_jp, okinawa], ignore_index=True)
    print(f"本土{len(dark_jp)} + 沖縄{len(okinawa)} = 合計{len(dark_alljp)}")
    return dark_alljp
