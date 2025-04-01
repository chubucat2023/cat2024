# -*- coding: utf-8 -*-

from picamera2 import Picamera2, Preview
import cv2
import numpy as np
from ultralytics import YOLO
import os
import time

import DF_15RSMG
import nagao_cam

# グローバル変数の定義
model = None
picam2 = None
image_counter = 0  # 画像ファイルの連番を管理する変数


def init():
    global model, picam2
    # YOLOモデルとpicamera2の初期化
    model = YOLO('best_2.pt')
    picam2 = Picamera2()
    preview_config = picam2.create_still_configuration()
    picam2.configure(preview_config)
    picam2.start_preview()
    picam2.start()


def main():
    global model, picam2, image_counter
    time.sleep(3)
    # Picamera2から画像を取得
    frame = picam2.capture_array()
    # BGR形式に変換（OpenCV用）
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    # HSV形式に変換（色検出用）
    frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    # 現在のディレクトリにある 'cam_test' フォルダのパスを取得
    save_directory = os.path.join(os.getcwd(), 'cam_test')
    # 'cam_test' ディレクトリが存在しない場合は作成
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # 画像をJPEG形式で保存（連番をつける）
    filename = os.path.join(save_directory, f'captured_frame_{image_counter:04d}.jpg')
    cv2.imwrite(filename, frame_bgr)
    image_counter += 1  # 画像ファイルのカウンターをインクリメント

    # 赤色の定義
    LOW_COLOR1 = np.array([0, 100, 100])
    HIGH_COLOR1 = np.array([10, 255, 255])
    LOW_COLOR2 = np.array([160, 100, 100])
    HIGH_COLOR2 = np.array([180, 255, 255])

    # 赤色のマスクを作成
    mask1 = cv2.inRange(frame_hsv, LOW_COLOR1, HIGH_COLOR1)
    mask2 = cv2.inRange(frame_hsv, LOW_COLOR2, HIGH_COLOR2)
    mask = cv2.bitwise_or(mask1, mask2)

    # 赤色の面積を計算
    red_area = np.sum(mask) / 255
    total_area = frame.shape[0] * frame.shape[1]
    red_ratio = red_area / total_area

    # 赤色が20%以上の場合はFlagを返す
    if red_ratio > 0.7:
        return 1, True, True
    if red_ratio > 0.1:
        # 元の解像度を四分の一にする
        frame_bgr_resized = cv2.resize(frame_bgr, (frame_bgr.shape[1] // 4, frame_bgr.shape[0] // 4))
        # 圧縮された画像を使用
        error_angle = nagao_cam.cap(frame_bgr_resized)
        return error_angle, False, True

    # 赤色が30%未満の場合は元のオブジェクト検出処理を実行
    results = model(frame_bgr, conf=0.5, imgsz=640)
    class_id = 0
    highest_confidence = 0
    center_x = None
    for box, cls, conf in zip(results[0].boxes.xyxy, results[0].boxes.cls, results[0].boxes.conf):
        if cls == class_id and conf > highest_confidence:
            highest_confidence = conf
            x1, y1, x2, y2 = [int(i) for i in box]
            center_x = (x1 + x2) // 2
            break

    # カメラの水平画角を考慮して、中心からのずれを計算
    if center_x is not None:
        image_width = frame.shape[1]
        angle_per_pixel = 62.2 / image_width  # 水平画角をピクセル数で割る
        deviation = (center_x - (image_width / 2)) * angle_per_pixel  # 中心からのずれを計算
        return deviation, False, False
    else:
        return None, False, False


def cleanup():
    global picam2
    picam2.stop()


# 別のコードからこれを呼び出す例
if __name__ == '__main__':
    init()
    result = main()
    if isinstance(result, str) and result == "Flag":
        print("Red color occupies more than 20% of the image")
    elif result is not None:
        print(f"Object is {result} degrees from center")
    else:
        print("No object found")
    cleanup()
