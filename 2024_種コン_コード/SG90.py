# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time


GPIO.setwarnings(False)


# サーボモーターを90度に移動する関数
def move_servo_90_degrees(servo_pin):
    pwm_frequency = 50  # PWMの周波数（Hz）

    # PWMの初期化
    pwm = GPIO.PWM(servo_pin, pwm_frequency)
    pwm.start(0)

    i = 180
    dc = (1.0 + i / 180.0) / 20.0 * 100.0
    pwm.ChangeDutyCycle(dc)
    time.sleep(2)

    i = 0
    dc = (1.0 + i / 180.0) / 20.0 * 100.0
    pwm.ChangeDutyCycle(dc)
    time.sleep(0.4)

    pwm.stop()


def servo_open():
    # GPIOピンの設定
    servo_pin = 13  # このピン番号はSG90を接続したGPIOピンに合わせて変更してください
    servo_set_pin = 20   # このピンを出力したいサーボが接続されているフォトリレーのGPIOピンに合わせて変更

    # GPIOの初期化
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setup(servo_set_pin, GPIO.OUT)
    GPIO.output(servo_set_pin, 1)
    move_servo_90_degrees(servo_pin)
    GPIO.output(servo_set_pin, 0)

    # 後片付け
    GPIO.cleanup()


if __name__ == "__main__":
    servo_open()