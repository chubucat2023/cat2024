# -*- coding: utf-8 -*-

import bmx055
import math
import time
import SG90


def init():
    bmx055.init_accelerometer_16()


def fail():
    total_acc = 10
    while True:
        loop_start_time = time.time()  # 現在のループの開始時間
        x_acc, y_acc, z_acc = bmx055.read_accelerometer_16()
        total_acc = math.sqrt(x_acc ** 2 + y_acc ** 2 + z_acc ** 2)  # 3軸加速度の合計を計算
        if total_acc > 100:
            SG90.servo_open()
            break
        loop_end_time = time.time()  # 現在のループの終了時間
        temp_time = loop_end_time - loop_start_time  # 現在のループにかかった時間
        time_to_wait = 0.02 - temp_time  # 次のループまでの待機時間
        if time_to_wait > 0:
            time.sleep(time_to_wait)  # 次のループが0.02秒後に始まるように待機
