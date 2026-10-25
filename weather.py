"""気象庁の観測地点データを読み込む。"""
import pandas as pd


def load_weather_station(path="jma_station_active.csv"):
    """現在稼働中の観測地点一覧(観測項目のフラグ付き)。"""
    return pd.read_csv(path)
