# -*- coding: utf-8 -*-

# Raspberry pi model3
# Raspberry pi model4
# 両方とも動作確認済み


import math
import serial

# import csv

GNSS_list = []


def GNSS(serial_port):
    print('class GNSS')
    gnssCount = 5  # 取得するデータの数

    latitudes = []  # 緯度を格納するリスト
    longitudes = []  # 経度を格納するリスト

    serial_port.readline()  # 最初の行は無視
    while True:
        GPSsentence = serial_port.readline()

        try:
            GPSsentence = GPSsentence.decode('utf-8')

            if GPSsentence.startswith('$GNRMC'):
                data = GPSsentence.split(',')

                if len(data) >= 9:
                    latitude = float(data[3])  # 緯度
                    longitude = float(data[5])  # 経度
                    latitudes.append(latitude)
                    longitudes.append(longitude)

                    if len(latitudes) == gnssCount:
                        latitudes.sort()
                        longitudes.sort()
                        mid_index = len(latitudes) // 2  # 中央のインデックス

                        # リストの要素数が奇数の場合は中央の値、偶数の場合は中央の二つの値の平均を取る
                        MEDlatitude = latitudes[mid_index] if len(latitudes) % 2 != 0 else (latitudes[mid_index - 1] + latitudes[mid_index]) / 2.0
                        MEDlongitude = longitudes[mid_index] if len(longitudes) % 2 != 0 else (longitudes[mid_index - 1] + longitudes[mid_index]) / 2.0
                        return MEDlatitude, MEDlongitude

        except:
            print('GNSSError')


def main():
    print('start program')
    UART = serial.Serial('/dev/ttyS0', 9600, timeout=10)  # '/dev/ttyAMA0' or '/dev/serial0' or '/dev/ttyS0'
    print('open port')

    latitude, longitude = GNSS(UART)
    decimal, integer = math.modf(latitude / 100.0)
    gps_latitude = integer + decimal / 60.0 * 100.0
    decimal, integer = math.modf(longitude / 100.0)
    gps_longitude = integer + decimal / 60.0 * 100.0

    print(gps_latitude)
    print(gps_longitude)

    UART.close()

    print('end of communication')

    return gps_latitude, gps_longitude


if __name__ == '__main__':
    main()

