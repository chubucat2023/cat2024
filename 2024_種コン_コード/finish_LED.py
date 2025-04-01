# -*- coding: utf-8 -*-

# LED点灯用

import RPi.GPIO as GPIO
import time


def main():
    led_pin = 26
    # GPIOの初期化
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_pin, GPIO.OUT)

    # LEDを点灯
    for i in range(30):
        GPIO.output(led_pin, GPIO.HIGH)
        # 指定した時間だけ点灯
        time.sleep(0.5)
        # LEDを消灯
        GPIO.output(led_pin, GPIO.LOW)
        time.sleep(0.5)

    # GPIOをクリーンアップ
    GPIO.cleanup()


if __name__ == '__main__':
    main()
