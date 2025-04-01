# -*- coding: utf-8 -*-

import math
import gnssRaspberryPiModel3  # 必要なモジュールをインポートします。


def haversine(lat1, lon1, lat2, lon2):
    # 地球の半径 (km)
    R = 6371.0

    # 緯度経度をラジアンに変換
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # 緯度と経度の差
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # ハバーサイン公式
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 総距離をメートル単位で返す
    distance = R * c * 1000
    return distance


def measure_gps_errors(iterations=10):
    latitudes = []
    longitudes = []

    while len(latitudes) < iterations:
        try:
            latitude, longitude = gnssRaspberryPiModel3.main()
            latitudes.append(latitude)
            longitudes.append(longitude)
        except:  # 通信エラーまたはその他の例外をキャッチ
            continue  # エラーが発生した場合、次の繰り返しを続ける

    # 最小値と最大値を見つける
    min_latitude = min(latitudes)
    max_latitude = max(latitudes)
    min_longitude = min(longitudes)
    max_longitude = max(longitudes)

    # 最小値と最大値の間の距離を計算する
    error_distance = haversine(min_latitude, min_longitude, max_latitude, max_longitude)

    # 結果を返します。
    return {
        'min_latitude': min_latitude,
        'max_latitude': max_latitude,
        'min_longitude': min_longitude,
        'max_longitude': max_longitude,
        'error_distance': error_distance
    }


# 関数を実行して結果を表示します。
errors = measure_gps_errors()
for key, value in errors.items():
    print(f"{key}: {value}")
