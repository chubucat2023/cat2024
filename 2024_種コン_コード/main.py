#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import touka
import DF_15RSMG
import bmx055
import gnssRaspberryPiModel3
import finish_LED
import math
import time
import rover_cam
import touka_worst


def sensor_init(start_time):
    bmx055.init_magnetometer()
    print(f"{time.time() - start_time:.2f} seconds: Magnetometer initialized")

    bmx055.init_accelerometer_4()
    print(f"{time.time() - start_time:.2f} seconds: Accelerometer initialized")

    DF_15RSMG.init_servo()
    print(f"{time.time() - start_time:.2f} seconds: Servo initialized")


def set_rover_degrees(start_time, target_degree):
    while True:
        time.sleep(1)
        current_degree = bmx055.read_magnetometer()
        print(f"{time.time() - start_time:.2f} seconds: Current rover degree: {current_degree}")

        error_angle = target_degree - current_degree
        print(f"{time.time() - start_time:.2f} seconds: Error angle: {error_angle}")

        if error_angle > 180:
            error_angle -= 360
        elif error_angle < -180:
            error_angle += 360
        print(f"{time.time() - start_time:.2f} seconds: Normalized error angle: {error_angle}")

        if abs(error_angle) < 15:
            print(f"{time.time() - start_time:.2f} seconds: Error angle is small enough, stopping adjustment")
            break

        if abs(error_angle) > 90:
            if error_angle > 0:
                DF_15RSMG.turn_R()
            else:
                DF_15RSMG.turn_L()
            print(f"{time.time() - start_time:.2f} seconds: Turned rover for large error adjustment")
            time.sleep(1.5)
            DF_15RSMG.stop()
            print(f"{time.time() - start_time:.2f} seconds: Stopped rover after large turn")
            continue

        if error_angle > 0:
            DF_15RSMG.turn_R()
        else:
            DF_15RSMG.turn_L()
        print(f"{time.time() - start_time:.2f} seconds: Minor adjustment based on error angle")
        time.sleep(0.1)
        DF_15RSMG.stop()
        print(f"{time.time() - start_time:.2f} seconds: Stopped rover after minor adjustment")


def calculate_bearing(start_time):
    DF_15RSMG.stop()
    print(f"{time.time() - start_time:.2f} seconds: Stopped rover for bearing calculation")
    while True:
        try:
            tentative_latitude, tentative_longitude = gnssRaspberryPiModel3.main()
            print(f"{time.time() - start_time:.2f} seconds: Acquired tentative coordinates")
            break
        except:
            print(f"{time.time() - start_time:.2f} seconds: Failed to acquire GNSS data, retrying")

    goal_latitude = 30.3742616666666
    goal_longitude = 130.960021666666

    lat1, lon1 = math.radians(tentative_latitude), math.radians(tentative_longitude)
    lat2, lon2 = math.radians(goal_latitude), math.radians(goal_longitude)

    delta_lon = lon2 - lon1
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    print(f"{time.time() - start_time:.2f} seconds: Calculated bearing: {bearing}")

    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    earth_radius = 6371.0  # kilometers
    distance = earth_radius * c * 1000  # meters
    print(f"{time.time() - start_time:.2f} seconds: Calculated distance: {distance}")

    return bearing, distance


def func_error_angle(start_time, rover_degrees, bearing_degree):
    error_angle = bearing_degree - rover_degrees
    if error_angle > 180:
        error_angle -= 360
    elif error_angle < -180:
        error_angle += 360
    print(f"{time.time() - start_time:.2f} seconds: Calculated functional error angle: {error_angle}")
    return error_angle


def use_gnss(start_time):
    DF_15RSMG.forward()
    print(f"{time.time() - start_time:.2f} seconds: Started moving forward for GNSS guidance")
    time.sleep(10)  # simulate some travel time

    while True:
        DF_15RSMG.stop()
        print(f"{time.time() - start_time:.2f} seconds: Stopped for GNSS reevaluation")
        bearing_degree, distance = calculate_bearing(start_time)
        print(f"{time.time() - start_time:.2f} seconds: GNSS guidance reevaluated")

        if distance < 10:
            print(f"{time.time() - start_time:.2f} seconds: Destination is close enough, ending GNSS guidance")
            break

        if distance < 15:
            for i in range(int(distance - 1)):
                set_rover_degrees(start_time, bearing_degree)
                DF_15RSMG.forward()
                time.sleep(2)
                DF_15RSMG.stop()
                print(f"{time.time() - start_time:.2f} seconds: Moved closer to destination in short bursts")
                rover_degree = bmx055.read_magnetometer()
                error_angle = func_error_angle(start_time, rover_degree, bearing_degree)
                if abs(error_angle) > 15:
                    continue  # Skip the rest if there's a large error

        else:
            set_rover_degrees(start_time, bearing_degree)
            DF_15RSMG.forward()
            print(f"{time.time() - start_time:.2f} seconds: Moving forward for longer distance towards destination")
            start_movement = time.time()
            while time.time() - start_movement < distance / 5:  # Simplified movement time, assuming 5 m/s speed
                continue  # Just wait here for simplicity
            DF_15RSMG.stop()
            print(f"{time.time() - start_time:.2f} seconds: Stopped after long distance movement")


def use_yolo(start_time):
    rover_cam.init()
    print(f"{time.time() - start_time:.2f} seconds: YOLO camera initialized")

    while True:
        pitch = bmx055.cal_pitch()
        print(f"{time.time() - start_time:.2f} seconds: Calculated pitch: {pitch}")
        if pitch:
            DF_15RSMG.forward()
            time.sleep(3)
            DF_15RSMG.stop()
            print(f"{time.time() - start_time:.2f} seconds: Moved forward to adjust for pitch")
            continue

        error_angle, flag, algorithm = rover_cam.main()
        print(f"{time.time() - start_time:.2f} seconds: YOLO detection processed")

        if flag:
            DF_15RSMG.stop()
            rover_cam.cleanup()
            print(f"{time.time() - start_time:.2f} seconds: Stopping due to YOLO flag")
            return

        if error_angle is not None:
            if algorithm:
                if error_angle > 0:
                    DF_15RSMG.turn_R()
                else:
                    DF_15RSMG.turn_L()
                print(f"{time.time() - start_time:.2f} seconds: Adjusted direction based on YOLO error angle")
                time.sleep(0.15)
                DF_15RSMG.forward()
                time.sleep(0.3)
                DF_15RSMG.stop()
                print(f"{time.time() - start_time:.2f} seconds: Moved forward after YOLO direction adjustment")
            else:
                if abs(error_angle) < 5:
                    DF_15RSMG.forward()
                    time.sleep(2)
                    print(f"{time.time() - start_time:.2f} seconds: Moved forward as obstacle is directly ahead")
                else:
                    if error_angle > 0:
                        DF_15RSMG.turn_R()
                    else:
                        DF_15RSMG.turn_L()
                    print(
                        f"{time.time() - start_time:.2f} seconds: Adjusted direction slightly based on YOLO error angle")
                    time.sleep(0.15)
                    DF_15RSMG.forward()
                    time.sleep(0.3)
                    print(
                        f"{time.time() - start_time:.2f} seconds: Moved forward after slight YOLO direction adjustment")
        else:
            DF_15RSMG.turn_L()
            time.sleep(0.3)
            print(f"{time.time() - start_time:.2f} seconds: Turned left as no obstacles detected")
        DF_15RSMG.stop()
        print(f"{time.time() - start_time:.2f} seconds: Stopped for next YOLO cycle")


def main():
    start_time = time.time()
    touka.main()
    print(f"{time.time() - start_time:.2f} seconds: Touka finished")

    sensor_init(start_time)

    use_gnss(start_time)

    use_yolo(start_time)

    DF_15RSMG.stop()
    finish_LED.main()
    print(f"{time.time() - start_time:.2f} seconds: Finish LED sequence executed")


if __name__ == "__main__":
    main()
