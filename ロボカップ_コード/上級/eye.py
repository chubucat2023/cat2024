import RPi.GPIO as GPIO
import time

# ピンの定義
TRIG = 17
ECHO = 27


def init():
    GPIO.setmode(GPIO.BCM)  # GPIO モード設定
    GPIO.setup(TRIG, GPIO.OUT)  # トリガーピンを出力に設定
    GPIO.setup(ECHO, GPIO.IN)  # エコーピンを入力に設定
    GPIO.output(TRIG, False)  # トリガーをリセット
    time.sleep(0.2)  # センサーが安定するまで少し待つ


def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150

    if distance > 50:
        distance = 50

    time.sleep(0.01)
    return round(distance, 2)


def main():
    distance = measure_distance()
    print(f"Distance: {distance} cm")
    return distance


if __name__ == "__main__":
    init()  # センサー初期化
    for i in range(500):
        distance = main()  # 距離測定
        print(f"Distance: {distance} cm")
        time.sleep(0.1)