# -*- coding: utf-8 -*-

import altitude
import bmx055
import SG90
import time
import math
import csv
import numpy as np
from multiprocessing import Process


# センサーの初期化関数
def sensor_init():
    bmx055.init_accelerometer_16()  # 加速度センサーの初期化
    bmx055.init_gyroscope()  # ジャイロスコープの初期化
    altitude.init_altitude()  # 高度センサーの初期化
    print("finish_sensor_initialization")


# 高度を計算する関数
def func_altitude(P0, P, Celsius_T0):
    T0 = Celsius_T0 + 273.15
    h = (T0 / 0.0065) * (1 - (P / P0) ** (8.31447 * 0.0065 / (9.80665 * 0.0289644)))
    return h  # 高度をメートル単位で返す


# センサーデータを読み取る関数
def read_data(default_time):
    # 各センサーからデータを読み取る
    x_acc, y_acc, z_acc = bmx055.read_accelerometer_16()
    x_gyro, y_gyro, z_gyro = bmx055.read_gyroscope()
    pressure, temperature = altitude.read_data()
    tentative_time = time.time()  # 経過時間を計算
    read_time = tentative_time - default_time
    return x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro, pressure, temperature, read_time

class StackedHistogram:
    def __init__(self, bin_width, data_range=None):
        self.bin_width = bin_width
        self.data_range = data_range
        self.histogram_data = self.initialize_histogram()

    def initialize_histogram(self):
        # 初期化時にバケットを等間隔で指定範囲に作成
        if self.data_range is not None:
            start = self.data_range[0]
            end = self.data_range[1]
            bins = np.arange(start, end + self.bin_width, self.bin_width)
            histogram_data = [[bin_start, 0] for bin_start in bins]
            return histogram_data

    def update_histogram(self, value):
        if self.data_range is not None and (value < self.data_range[0] or value > self.data_range[1]):
            # データが指定された範囲外なら無視
            return

        # 実際のデータ点がどのバケットに属するかを判定
        bucket_index = int((value - self.data_range[0]) / self.bin_width)
        
        # データが最後のバケットに含まれていれば、バケットのカウントを増やす
        if 0 <= bucket_index < len(self.histogram_data):
            self.histogram_data[bucket_index][1] += 1

    def get_peak(self):
        # ヒストグラムデータが空であればNoneを返す
        if not self.histogram_data:
            return None

        # NumPy配列に変換
        histogram_data = np.array(self.histogram_data)

        # 最頻値のインデックスを取得
        peak_index = np.argmax(histogram_data[:, 1])

        # 最頻値とその値を返す
        return histogram_data[peak_index, 0], histogram_data[peak_index, 1]

    def get_histogram(self):
        return np.array(self.histogram_data)


class RingBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size
        self.start = 0
        self.end = 0
        self.isFull = False

    def add_value(self, value, data_type):
        self.buffer[self.end] = (data_type, value)
        self.end = (self.end + 1) % self.size
        if self.end == self.start:
            self.isFull = True
            self.start = (self.start + 1) % self.size

    def add_alt_value(self, P0, P, Celsius_T0):
        data_type = 'altitude'
        value = self.func_altitude(P0, P, Celsius_T0)
        self.add_value(value, data_type)

    def get_value(self):
        if self.isFull or self.start != self.end:
            data_type, value = self.buffer[self.start]
            self.start = (self.start + 1) % self.size
            if self.start == self.end:
                self.isFull = False
            return data_type, value
        else:
            return None, None  # The buffer is empty

    def get_end_value(self):
        if self.isFull or self.start != self.end:
            targetIndex = self.end - 1
            if(targetIndex < 0):
                targetIndex = size - 1
            data_type, value = self.buffer[targetIndex]
            self.end = targetIndex
            self.isFull = False
            return data_type, value
        else:
            return None, None  # バッファが空の場合
    
    def printDataRange(self):
        print(self.start, ":", self.end)

alt_rb = RingBuffer(2048)
histPitch = 0.2
histRange = (-5, 15)
stacked_alt_hist = StackedHistogram(histPitch, histRange)

def display_frequency_above_threshold(data4histogram, threshold):

    # 階級ごとの度数を計算
    stacked_alt_hist.update_histogram(data4histogram)
    peak_value, peak_count = stacked_alt_hist.get_peak()
    #hist, bins = np.histogram(data4histogram, bins=range(min(data4histogram), max(data4histogram) + bin_width, bin_width))

    if(peak_count > threshold):
        print(peak_value)


# 引き上げが終了したかどうかを検出し、引き上げ時のデータを記録する関数
def detect_lift_end(default_time, threshold):
    _, _, _, _, _, _, initial_pressure, initial_temperature, _ = read_data(default_time)  # 初期値の読み取り
    lift_data = []  # 引き上げ中のデータを保存するリスト
    start_time = time.time()  # 監視開始時刻

    #size =2048
    #addValue, getValue, display = createRingBuffer(size)
    
    # 15メートルの引き上げまでデータ取得
    while True:
        loop_start_time = time.time()  # 現在のループの開始時間
        x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro, pressure, temperature, read_time = read_data(default_time)
        tentative_height = func_altitude(initial_pressure, pressure, initial_temperature)
        data_type = 'altitude'
        alt_rb.add_value(tentative_height, data_type)

        #createRingBuffer.tacreate


        # lift_data.append([x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro, pressure, temperature, read_time, tentative_height])z

        if tentative_height > 5:
            start_height = tentative_height
            break

        loop_end_time = time.time()  # 現在のループの終了時間
        temp_time = loop_end_time - loop_start_time  # 現在のループにかかった時間
        time_to_wait = 0.5 - temp_time  # 次のループまでの待機時間
        if time_to_wait > 0:
            time.sleep(time_to_wait)  # 次のループが0.02秒後に始まるように待機+++++++++

    # 15メートル引き上げ後、引き上げ終了（15秒間で1メートル以上の高度変化）がなくなるまで待機
    start_height = 0
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro, pressure, temperature, read_time = read_data(default_time)
        tentative_height = func_altitude(initial_pressure, pressure, initial_temperature)  # 現在の高度を計算
        print("tentative_height", tentative_height)
        lift_data.append([x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro, pressure, temperature, read_time, tentative_height])

        if abs(tentative_height - start_height) < 1:  # 10秒間での高度の変化が1メートル未満なら
            if elapsed_time > 15:
                break  # 引き上げが終了したと判断
        else:
            start_time = current_time  # 監視開始時刻をリセット
            start_height = tentative_height  # 初期高度を更新

    loop_end_time = time.time()  # 現在のループの終了時間
    temp_time = loop_end_time - current_time  # 現在のループにかかった時間
    time_to_wait = 0.5 - temp_time  # 次のループまでの待機時間
    if time_to_wait > 0:
        time.sleep(time_to_wait)  # 次のループが0.5秒後に始まるように待機

    # peak_count = 0
    peak_value = 0
    top_alt = tentative_height
    # debugcounter = 0
    # alt_rb.printDataRange()
    print("alt")
    while True:
        # print("index:", debugcounter)
        tagdata, enddata = alt_rb.get_end_value()
        print(enddata)
        if(enddata == None):
            break
        stacked_alt_hist.update_histogram(enddata)
        peak_value, peak_count = stacked_alt_hist.get_peak()
        if(peak_count > threshold):
            break
    peak_alt = peak_value + histPitch*0.5
    print("peak_alt = ", peak_alt)
    height = top_alt - peak_alt
    print("height", height)

    # 最終的なヒストグラムを取得
    final_histogram = stacked_alt_hist.get_histogram()
    print(final_histogram)

    lift_data.append(["lift_end", "lift_end", "lift_end", "lift_end", "lift_end", "lift_end", "lift_end", "lift_end", "lift_end"])
    print("detect_lift_end")
    return lift_data, height  # 引き上げ中のデータ、投下高度を返す


def before_fail(default_time):
    total_acc = 10  # 加速度の合計を初期化
    data = []  # 収集するデータのリスト
    initial_pressure = 1013  # 初期圧力を設定
    initial_temperature = 20  # 初期気温を設定
    while total_acc > 3:  # 加速度の合計が5未満になるまでループ
        loop_start_time = time.time()  # 現在のループの開始時間
        loop_end_time = time.time()  # 現在のループの終了時間
        temp_time = loop_end_time - loop_start_time  # 現在のループにかかった時間
        time_to_wait = 0.02 - temp_time  # 次のループまでの待機時間
        if time_to_wait > 0:
            time.sleep(time_to_wait)  # 次のループが0.02秒後に始まるように待機
    data.append(["touka", "touka", "touka", "touka", "touka", "touka", "touka", "touka", "touka", "touka"])  # マーカーとしてデータを追加
    print("start falling")  # 開始マーカーを出力
    return data, initial_pressure, initial_temperature


def after_fail(default_time, initial_height, open_height, initial_pressure, initial_temperature, servo_task):
    data = []  # 収集するデータのリスト
    servo_task_started = False  # サーボタスクが開始されたかどうかを追跡するフラグ

    for i in range(1500):  # データを収集
        loop_start_time = time.time()  # 現在のループの開始時間

        x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro, pressure, temperature, read_time = read_data(default_time)
        total_acc = math.sqrt(x_acc ** 2 + y_acc ** 2 + z_acc ** 2)  # 3軸加速度の合計を計算
        data.append([x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro, initial_pressure, initial_temperature, read_time, "N/A"])  # データをリストに追加
        if total_acc > 100:
            servo_task.start()
            servo_task_started = True
            print("servo_task_started")
        tentative_height = - func_altitude(initial_pressure, pressure, initial_temperature)  # 高度を計算
        if tentative_height > (initial_height-open_height) / 2 and not servo_task_started:  # サーボタスクがまだ開始されていない場合
            servo_task_started = True
            print("servo_task_started")
            servo_task.start()  # サーボを動かすプロセスを開始
        data.append([x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro, pressure, temperature, read_time, tentative_height])  # データをリストに追加

        loop_end_time = time.time()  # 現在のループの終了時間
        temp_time = loop_end_time - loop_start_time  # 現在のループにかかった時間
        time_to_wait = 0.02 - temp_time  # 次のループまでの待機時間
        if time_to_wait > 0:
            time.sleep(time_to_wait)  # 次のループが0.02秒後に始まるように待機

    servo_task.start()  # サーボを動かすプロセスを開始
    if servo_task_started:  # サーボタスクが開始されていた場合のみjoinを呼び出す
        servo_task.join()  # サーボのプロセスが終了するまで待機
    return data


# データをCSVファイルに書き込む関数
def write_fail_data(data):
    filename = 'fail_data.csv'  # CSVファイル名
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ['X_Acc', 'Y_Acc', 'Z_Acc', 'X_Gyro', 'Y_Gyro', 'Z_Gyro', 'Pressure', 'temperature', 'Read_Time', "height"]  # CSVヘッダー
        writer.writerow(header)  # ヘッダーを書き込み
        for block in data:
            for row in block:
                writer.writerow(row)  # データをCSVに書き込み


# メイン関数
def main():
    open_height = 2.5
    sensor_init()  # センサーの初期化2
    # 階級の幅を設定（適宜幅を調整してください）
    bin_width = 20
    # 閾値を設定（適宜閾値を変更してください）
    threshold = 20

    # initial_pressure = 1
    # pressure = 2
    # initial_temperature = 3

    # data4histogram = func_altitude(initial_pressure, pressure, initial_temperature)
    # #閾値以上の度数を持つ階級を表示
    # display_frequency_above_threshold(data4histogram, threshold) 
    default_time = time.time()  # 開始時間を記録
    servo_task = Process(target=SG90.servo_open)  # サーボ操作のためのプロセス
    data = []  # データのリスト
    lift_data, height = detect_lift_end(default_time, threshold)
    data.append(lift_data)
    before_data, initial_pressure, initial_temperature = before_fail(default_time)  # 投下前のデータ収集
    data.append(before_data)
    after_data = after_fail(default_time, height, open_height, initial_pressure, initial_temperature, servo_task)  # 投下後のデータ収集
    data.append(after_data)
    write_fail_data(data)  # データをCSVに書き込み


if __name__ == "__main__":
    print("code start")
    main()
    print("code end")

