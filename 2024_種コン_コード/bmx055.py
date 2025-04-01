# -*- coding: utf-8 -*-

import smbus
import time
import math

# Get I2C bus
bus = smbus.SMBus(1)


def init_accelerometer_4():
    # BMX055 Accl address, 0x18(24)
    # Select PMU_Range register, 0x0F(15)
    #  0x03(03) Range = +/- 4g
    bus.write_byte_data(0x19, 0x0F, 0x05)
    # BMX055 Accl address, 0x18(24)
    # Select PMU_BW register, 0x10(16)
    #  0x08(08) Bandwidth = 250 Hz
    bus.write_byte_data(0x19, 0x10, 0x0F)
    # BMX055 Accl address, 0x18(24)
    # Select PMU_LPW register, 0x11(17)
    #  0x00(00) Normal mode, Sleep duration = 0.5ms
    bus.write_byte_data(0x19, 0x11, 0x00)

    time.sleep(1)


def init_accelerometer_16():
    # BMX055 Accl address, 0x18(24)
    # Select PMU_Range register, 0x0F(15)
    #  0x03(03) Range = +/- 16g
    bus.write_byte_data(0x19, 0x0F, 0x0C)
    # BMX055 Accl address, 0x18(24)
    # Select PMU_BW register, 0x10(16)
    #  0x08(08) Bandwidth = 250 Hz
    bus.write_byte_data(0x19, 0x10, 0x0F)
    # BMX055 Accl address, 0x18(24)
    # Select PMU_LPW register, 0x11(17)
    #  0x00(00) Normal mode, Sleep duration = 0.5ms
    bus.write_byte_data(0x19, 0x11, 0x00)

    time.sleep(1)


def read_accelerometer_4():
    data = bus.read_i2c_block_data(0x19, 0x02, 6)
    xAccl = ((data[1] * 256) + (data[0] & 0xF0)) / 16
    if xAccl > 2047: xAccl -= 4096
    yAccl = ((data[3] * 256) + (data[2] & 0xF0)) / 16
    if yAccl > 2047: yAccl -= 4096
    zAccl = ((data[5] * 256) + (data[4] & 0xF0)) / 16
    if zAccl > 2047: zAccl -= 4096
    x_acc = xAccl * 0.009580078125 * 2
    y_acc = yAccl * 0.009580078125 * 2
    z_acc = zAccl * 0.009580078125 * 2
    return x_acc, y_acc, z_acc


def read_accelerometer_16():
    data = bus.read_i2c_block_data(0x19, 0x02, 6)
    xAccl = ((data[1] * 256) + (data[0] & 0xF0)) / 16
    if xAccl > 2047: xAccl -= 4096
    yAccl = ((data[3] * 256) + (data[2] & 0xF0)) / 16
    if yAccl > 2047: yAccl -= 4096
    zAccl = ((data[5] * 256) + (data[4] & 0xF0)) / 16
    if zAccl > 2047: zAccl -= 4096
    x_acc = xAccl * 0.0625
    y_acc = yAccl * 0.0625
    z_acc = zAccl * 0.0625
    return x_acc, y_acc, z_acc


def init_gyroscope():
    # BMX055 Gyro address, 0x68(104)
    # Select Range register, 0x0F(15)
    #  0x04(04) Full scale = +/- 1000 degree/s
    bus.write_byte_data(0x69, 0x0F, 0x01)
    # BMX055 Gyro address, 0x68(104)
    # Select Bandwidth register, 0x10(16)
    #  0x07(07) ODR = 2000 Hz, Filter bandwidth = 523 Hz
    bus.write_byte_data(0x69, 0x10, 0x06)
    # BMX055 Gyro address, 0x68(104)
    # Select LPM1 register, 0x11(17)
    #  0x00(00) Normal mode, Sleep duration = 2ms
    bus.write_byte_data(0x69, 0x11, 0x00)

    time.sleep(1)


def read_gyroscope():
    data = bus.read_i2c_block_data(0x69, 0x02, 6)
    xGyro = data[1] * 256 + data[0]
    if xGyro > 32767: xGyro -= 65536
    yGyro = data[3] * 256 + data[2]
    if yGyro > 32767: yGyro -= 65536
    zGyro = data[5] * 256 + data[4]
    if zGyro > 32767: zGyro -= 65536
    x_gyro = xGyro / 11.37743
    y_gyro = yGyro / 11.37743
    z_gyro = zGyro / 11.37743
    return x_gyro, y_gyro, z_gyro


def init_magnetometer():
    # BMX055 Mag address, 0x10(16)
    # Soft reset
    bus.write_byte_data(0x13, 0x4B, 0x01)
    time.sleep(1)
    # Normal Mode, ODR = 10 Hz
    bus.write_byte_data(0x13, 0x4C, 0x00)
    # X, Y, Z-Axis enabled
    bus.write_byte_data(0x13, 0x4E, 0x84)
    # No. of Repetitions for X-Y Axis = 9
    bus.write_byte_data(0x13, 0x51, 0x04)
    # No. of Repetitions for Z-Axis = 15
    bus.write_byte_data(0x13, 0x52, 0x16)
    time.sleep(1)


def calculate_tilt_correction(x_acc, y_acc, z_acc):
    # ピッチとロールの計算
    pitch = -math.atan2(y_acc, math.sqrt(x_acc ** 2 + z_acc ** 2))
    roll = - math.atan2(-x_acc, math.sqrt(y_acc ** 2 + z_acc ** 2))
    return pitch, roll


def cal_pitch():
    x_acc, y_acc, z_acc = read_accelerometer_4()
    if z_acc > 0:
        return True
    return False


def read_magnetometer():

    # 磁気センサーからデータを取得
    data = bus.read_i2c_block_data(0x13, 0x42, 6)
    xMag_raw = ((data[1] * 256) + (data[0] & 0xF8)) / 8
    yMag_raw = ((data[3] * 256) + (data[2] & 0xF8)) / 8
    zMag_raw = ((data[5] * 256) + (data[4] & 0xFE)) / 2
    if xMag_raw > 4095: xMag_raw -= 8192
    if yMag_raw > 4095: yMag_raw -= 8192
    if zMag_raw > 16383: zMag_raw -= 32768

    # 地磁気センサーの値をuT単位に変換
    xMag1 = xMag_raw * (2600 / 8192)
    yMag1 = yMag_raw * (2600 / 8192)
    zMag1 = zMag_raw * (5000 / 32768)

    # return (xMag1, yMag1, zMag1)

    xMag1 -= 63.31787109375
    yMag1 -= 16.8212890625
    zMag1 -= -25.32958984375
    # 地上方向に存在する磁力
    # return (xMag1, yMag1, zMag1)
    earth_mag = 14.22882080078125

    xMag, yMag, zMag = -xMag1, -yMag1, zMag1

    x_acc, y_acc, z_acc = read_accelerometer_4()
    adjusted_x_acc, adjusted_y_acc, adjusted_z_acc = x_acc, y_acc, z_acc
    pitch, roll = calculate_tilt_correction(adjusted_x_acc, adjusted_y_acc, adjusted_z_acc)

    # 方位角を正の度数法で返す
    sin_pitch = math.sin(pitch)
    cos_pitch = math.cos(pitch)
    x_mag_adjusted = (xMag - (earth_mag * sin_pitch)) * cos_pitch + (zMag - (zMag - earth_mag)) * sin_pitch

    # 方位角を正の度数法で返す
    azimuth = math.atan2(-yMag, x_mag_adjusted)

    azimuth_degrees = math.degrees(azimuth)
    if azimuth_degrees < 0:
        azimuth_degrees += 360  # 負の値の場合は360度を加算して正の角度に変換

    # return pitch * 180 / math.pi, roll * 180 / math.pi, adjusted_x_acc, adjusted_y_acc, adjusted_z_acc, xMag, yMag, zMag, azimuth_degrees
    return azimuth_degrees


if __name__ == '__main__':

    """
    init_magnetometer()
    time.sleep(1)
    x, y, z = 0, 0, 0
    for i in range(4):
        xmag, ymag, zmag = read_magnetometer()
        x += xmag
        y += ymag
        z += zmag
        print("read")
        a = input()
    print("x", "y", "z", x/4, y/4, z/4)
    """

    init_magnetometer()
    init_accelerometer_4()
    print(read_magnetometer())
    pitch, roll,  adjusted_x_acc, adjusted_y_acc, adjusted_z_acc, xMag, yMag, zMag, azimuth_degrees = read_magnetometer()
    print("Pitch =", pitch)
    print("Roll =", roll)
    print("Adjustedx, y, z=", adjusted_x_acc, adjusted_y_acc, adjusted_z_acc)
    print("Mag x,y,z =", xMag, yMag, zMag)
    print("Azimuth=", azimuth_degrees)
