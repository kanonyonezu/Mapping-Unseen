"""国土地理院のリバースジオコーディングAPIで、緯度経度に日本語住所を付ける。"""
import os
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

URL = "https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress"
CACHE_PATH = "gsi_address_cache.csv"


def get_jp_address(lat, lon):
    """1点分。成功すれば (市区町村コード, 町名)、失敗すれば (None, None)。"""
    try:
        r = requests.get(URL, params={"lat": lat, "lon": lon}, timeout=10)
        res = r.json()["results"]
        return res["muniCd"], res["lv01Nm"]
    except Exception:
        return None, None


def add_jp_address(df, cache_path=CACHE_PATH, max_workers=4):
    """df に muni_cd / address 列を付ける。取得済みの点はキャッシュから読む。"""
    df = df.copy()
    keys = list(zip(df["lat"].round(6), df["lon"].round(6)))

    if os.path.exists(cache_path):
        cache = pd.read_csv(cache_path, dtype={"muni_cd": str})
        cached = {(a, b): (c, d) for a, b, c, d
                  in cache[["lat", "lon", "muni_cd", "address"]].itertuples(index=False)}
    else:
        cached = {}

    todo = [k for k in dict.fromkeys(keys) if k not in cached]
    print(f"キャッシュ済み {len(keys) - len(todo)} / API問い合わせ {len(todo)}")
    if todo:
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            for k, v in zip(todo, ex.map(lambda k: get_jp_address(*k), todo)):
                cached[k] = v
        pd.DataFrame(
            [(a, b, c, d) for (a, b), (c, d) in cached.items()],
            columns=["lat", "lon", "muni_cd", "address"],
        ).to_csv(cache_path, index=False)

    df["muni_cd"] = [cached[k][0] for k in keys]
    df["address"] = [cached[k][1] for k in keys]
    return df
