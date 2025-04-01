# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time


L_motor_pin = 12
R_motor_pin = 13


def init_servo():
    global L_motor  # Declare L_motor as global
    global R_motor  # Declare R_motor as global
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(19, GPIO.OUT)
    GPIO.output(19, 1)
    GPIO.setup(L_motor_pin, GPIO.OUT)
    GPIO.setup(R_motor_pin, GPIO.OUT)
    L_motor = GPIO.PWM(L_motor_pin, 330)
    R_motor = GPIO.PWM(R_motor_pin, 330)
    L_motor.start(0)
    R_motor.start(0)


def forward():
    print("forward")
    L_motor.ChangeDutyCycle(20)
    R_motor.ChangeDutyCycle(80)


def turn_L():
    print("turn_L")
    L_motor.ChangeDutyCycle(20)
    R_motor.ChangeDutyCycle(0)


def turn_R():
    print("turn_R")
    L_motor.ChangeDutyCycle(0)
    R_motor.ChangeDutyCycle(80)


def stop():
    print("stop")
    L_motor.ChangeDutyCycle(0)
    R_motor.ChangeDutyCycle(0)


if __name__ == '__main__':
    print("start")
    init_servo()
    forward()
    time.sleep(2)
    stop()
    print("finish")
