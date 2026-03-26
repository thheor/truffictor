import cv2
import numpy as np
import mediapipe as mp
import math
import time
import requests
import threading
import tkinter as tk

face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
# face_mesh = "multi_face_landmarks.task"


def calculate_distance(point1, point2):
    return math.sqrt((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2)


def send_alert_to_esp32(esp32_ip, buzzer_type):
    try:
        requests.get(f"http://{esp32_ip}/buzzer1")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to ESP32: {e}")


def deteksi_kantuk(esp32_ip):
    cap = cv2.VideoCapture(0)
    drowsiness_start_time = None
    alert_sent = False
    threshold_distance = 0.0151
    detection_time = 2

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks

        frame_h, frame_w, _ = frame.shape

        if landmark_points:
            landmarks = landmark_points[0].landmark
            left_eye_points = [landmarks[145], landmarks[159]]
            right_eye_points = [landmarks[374], landmarks[386]]

            left_eye_distance = calculate_distance(
                left_eye_points[0], left_eye_points[1]
            )
            right_eye_distance = calculate_distance(
                right_eye_points[0], right_eye_points[1]
            )

            for landmark in left_eye_points + right_eye_points:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

            kantuk_terdeteksi = False

            if (
                left_eye_distance < threshold_distance
                and right_eye_distance < threshold_distance
            ):
                if drowsiness_start_time is None:
                    drowsiness_start_time = time.time()
                    alert_sent = False
                elif (
                    time.time() - drowsiness_start_time >= detection_time
                    and not alert_sent
                ):
                    cv2.putText(
                        frame,
                        "KANTUK TERDETEKSI",
                        (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                    )
                    threading.Thread(
                        target=send_alert_to_esp32, args=(esp32_ip, 2)
                    ).start()
                    alert_sent = True
                    kantuk_terdeteksi = True
                else:
                    drowsiness_start_time = None
                    alert_sent = False
                    kantuk_terdeteksi = False

                if kantuk_terdeteksi:
                    cv2.putText(
                        frame,
                        "KANTUK TERDETEKSI",
                        (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                    )

        cv2.imshow("Deteksi Kantuk", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def detect_lines(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    lines = cv2.HoughLinesP(
        edges, rho=1, theta=np.pi / 180, threshold=50, minLineLength=50, maxLineGap=100
    )
    return lines


def draw_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if 300 <= y1 <= 700 and 300 <= y2 <= 700:
                cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 5)
    return cv2.addWeighted(image, 0.8, line_image, 1.0, 0.0)


def draw_sensor_box(image, box):
    (x_min, y_min, x_max, y_max) = box
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 255), 2)


def check_lines_in_box(image, lines, box, esp32_ip, sensor_id):
    (x_min, y_min, x_max, y_max) = box
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if (x_min <= x1 <= x_max and y_min <= y1 <= y_max) or (
                x_min <= x2 <= x_max and y_min <= y2 <= y_max
            ):
                cv2.putText(
                    image,
                    f"MOBIL HILANG KENDALI {sensor_id}",
                    (50, 50 + (sensor_id - 1) * 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )
                requests.get(f"http://{esp32_ip}/buzzer1")
                return True
    return False


def deteksi_hilang_kendali(video_path, esp32_ip):
    cap = cv2.VideoCapture(video_path)

    sensor_box1 = (700, 550, 750, 650)
    sensor_box2 = (600, 550, 650, 650)

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        lines = detect_lines(frame)
        lines_image = draw_lines(frame, lines)

        draw_sensor_box(lines_image, sensor_box1)
        draw_sensor_box(lines_image, sensor_box2)

        check_lines_in_box(lines_image, lines, sensor_box1, esp32_ip, 1)
        check_lines_in_box(lines_image, lines, sensor_box2, esp32_ip, 2)

        cv2.imshow("Deteksi Hilang Kendali", lines_image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def open_detection(detection_type, esp32_ip):
    if detection_type == "Deteksi Kantuk":
        deteksi_kantuk(esp32_ip)
    elif detection_type == "Deteksi Hilang Kendali 1":
        deteksi_hilang_kendali("HILANGKENDALI.mp4", esp32_ip)
    elif detection_type == "Deteksi Hilang Kendali 2":
        deteksi_hilang_kendali("TERKENDALI.mp4", esp32_ip)
    elif detection_type == "Deteksi Hilang Kendali 3":
        deteksi_hilang_kendali("WhatsApp Video 2024-08-30 at 21.27.48.mp4", esp32_ip)


def main():
    root = tk.Tk()
    root.title("Sistem Deteksi")

    tk.Label(root, text="Masukkan IP ESP32:").grid(row=0, column=0, padx=10, pady=10)
    esp32_ip_entry = tk.Entry(root)
    esp32_ip_entry.grid(row=0, column=1, padx=10, pady=10)

    def start_detection(detection_type):
        esp32_ip = esp32_ip_entry.get()
        if esp32_ip:
            open_detection(detection_type, esp32_ip)
        else:
            tk.messagebox.showwarning("Peringatan", "Harap masukkan IP ESP32")

    tk.Button(
        root, text="DETEKSI KANTUK", command=lambda: start_detection("Deteksi Kantuk")
    ).grid(row=1, column=0, padx=10, pady=10)
    tk.Button(
        root,
        text="DETEKSI HILANG KENDALI",
        command=lambda: start_detection("Deteksi Hilang Kendali 1"),
    ).grid(row=1, column=1, padx=10, pady=10)
    tk.Button(
        root,
        text="DETEKSI SESUAI JALUR",
        command=lambda: start_detection("Deteksi Hilang Kendali 2"),
    ).grid(row=2, column=0, padx=10, pady=10)
    tk.Button(
        root, text="X", command=lambda: start_detection("Deteksi Hilang Kendali 3")
    ).grid(row=2, column=1, padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
