# -*- coding: utf-8 -*-

import cv2
import numpy as np


image_width = 640
horizontal_fov = 62.2
pixels_per_degree = 10.2893891


def calculate_angle(point1, point2, point3):
    vector1 = point1 - point2
    vector2 = point3 - point2
    dot_product = np.dot(vector1, vector2)
    magnitude_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
    cos_theta = dot_product / magnitude_product
    angle_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)
    return angle_deg


def detect_red_cone(img):

    LOW_COLOR1 = np.array([0, 50, 50])
    HIGH_COLOR1 = np.array([10, 255, 255])
    LOW_COLOR2 = np.array([160, 100, 100])
    HIGH_COLOR2 = np.array([180, 255, 255])

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    bin_img1 = cv2.inRange(hsv, LOW_COLOR1, HIGH_COLOR1)
    bin_img2 = cv2.inRange(hsv, LOW_COLOR2, HIGH_COLOR2)

    blue_channel_int = img[:, :, 0].astype(np.int32)
    red_channel_int = img[:, :, 2].astype(np.int32)

    # 赤チャンネルから青チャンネルを引いた結果を0未満の値を0にクリップ
    red_minus_blue = np.clip(red_channel_int - blue_channel_int, 0, 255).astype(np.uint8)

    # グレースケール画像に変換
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # グレースケール画像での最も白いピクセルの位置を取得
    white_pixel_pos = np.column_stack(np.where(gray_img == 255))

    # 強調用の画像を作成
    emphasis_gray = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

    # 最も白いピクセルを赤で強調
    for pos in white_pixel_pos:
        emphasis_gray[pos[0], pos[1]] = [0, 0, 255]  # 赤で強調

    mask = bin_img2
    # 赤い領域かあ青い領域を引いた画像を二値化
    ret, bin_redblue = cv2.threshold(red_minus_blue, 90, 255, cv2.THRESH_BINARY)
    # モーフォロジー変換（クロージング）を適用してノイズを低減
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    result = cv2.bitwise_and(img, img, mask=closed_mask)

    max_red_ratio = 0.0  # 最大の赤の比率
    best_contour = None  # 最大の赤の比率を持つ輪郭

    contours, _ = cv2.findContours(closed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = np.zeros_like(img)

    for contour in contours:
        cv2.drawContours(contour_img, [contour], 0, (255, 255, 255), 2)
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(contour_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cx, cy = x + w // 2, y + h // 2

        cv2.circle(contour_img, (cx, cy), 2, (0, 255, 255), -1)
        cv2.putText(contour_img, f"({cx},{cy})", (cx, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

        area = cv2.contourArea(contour)
        if 1 < area < 30000000:
            epsilon = 0.1 * cv2.arcLength(contour, True)  # %の周囲兆を基準に近似
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                cx, cy = x + w // 2, y + h // 2

                # カラーコーンに四角形の枠を描画
                cv2.drawContours(result, [approx], 0, (0, 255, 0), 2)
                cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(result, (cx, cy), 2, (0, 255, 255), -1)
                cv2.putText(result, f"({cx}, {cy})", (cx, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                cv2.drawContours(result, [approx], 0, (255, 0, 0), 2)

                vertex1 = np.array(approx[0][0])
                vertex2 = np.array(approx[1][0])
                vertex3 = np.array(approx[2][0])

                angle1 = calculate_angle(vertex2, vertex1, vertex3)
                angle2 = calculate_angle(vertex3, vertex2, vertex1)
                angle3 = calculate_angle(vertex1, vertex3, vertex2)

                # 少なくとも一つの角度が90度以下の場合のみ処理
                if any(angle <= 100.0 for angle in [angle1, angle2, angle3]):
                    # カラーコーン内の赤の比率を計算
                    red_pixels = np.sum(bin_img1[y:y + h, x:x + w] == 255)
                    total_pixels = w * h
                    red_ratio = red_pixels / total_pixels

                    # 最大の赤の比率を更新
                    if red_ratio > max_red_ratio:
                        max_red_ratio = red_ratio
                        best_contour = contour

    if best_contour is not None:
        # カラーコーンに四角形の枠を描画
        x, y, w, h = cv2.boundingRect(best_contour)
        cv2.drawContours(result, [best_contour], 0, (0, 255, 0), 2)
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(result, (x + w // 2, y + h // 2), 2, (0, 255, 255), -1)
        cv2.putText(result, f"({x + w // 2}, {y + h // 2})", (x + w // 2, y + h // 2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        angle_horizontal = (x+w//2-image_width/2)/pixels_per_degree

        contour_gray = cv2.cvtColor(contour_img, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(contour_gray, 50, 150)
        # Hough変換を使用して輪郭に線を追加
        lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)

        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))

                if 0 <= x1 < contour_img.shape[1] and 0 <= y1 < contour_img.shape[0] and \
                   0 <= x2 < contour_img.shape[1] and 0 <= y2 < contour_img.shape[0]:
                    cv2.line(contour_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        return img, result, bin_redblue, angle_horizontal
    else:
        return img, result, bin_redblue, None


def calculate_average_x(contours):
    total_x = 0
    count = 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        total_x += x + w // 2
        count += 1

    if count > 0:
        average_x = int(total_x / count)
        return average_x
    else:
        return None


def cap(frame):
    contour_img = np.zeros_like(frame)

    # detect_red_cone関数は img, result, bin_redblue, angle_horizontal を返しますが、
    # img はここでは使用していません。
    _, result, bin_redblue, angle_horizontal = detect_red_cone(frame)

    # 輪郭の描画と平均X座標の計算、表示
    contours, _ = cv2.findContours(bin_redblue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    average_x = calculate_average_x(contours)
    if average_x is not None:
        cv2.line(contour_img, (average_x, 0), (average_x, frame.shape[0]), (0, 255, 0), 2)
        cv2.putText(contour_img, f"Avg X:{average_x}", (average_x, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    if angle_horizontal is not None:
        print("物体までの水平方向の角度:", angle_horizontal, "degrees")
    return angle_horizontal