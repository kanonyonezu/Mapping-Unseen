"""日本の月別気候データ weather_jp を作る。"""
import pandas as pd


def load_weather_jp(path="sunshine-atlas-monthly-climate.csv"):
    weather = pd.read_csv(path)
    return weather[weather["country_code"] == "JP"]
