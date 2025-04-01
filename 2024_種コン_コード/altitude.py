# -*- coding: utf-8 -*-
import bme280
import bme280_i2c
import time


def init_altitude():
    # 初期化
    bme280_i2c.set_default_i2c_address(0x76)
    bme280_i2c.set_default_bus(1)

    # キャリブレーション
    bme280.setup()
    time.sleep(2)


def read_data():
    # データ取得
    data_all = bme280.read_all()

    data_pressure = data_all.pressure
    # 温度計に誤差があるため補正が入っている
    data_temperature = data_all.temperature
    return data_pressure, data_temperature


if __name__ == "__main__":
    init_altitude()
    for i in range(100):
        pressure = read_data()
        print(pressure)
        time.sleep(0.01)




