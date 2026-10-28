import cv2
import threading
import time
import os
import winsound
import csv
import numpy as np
from ultralytics import YOLO
from datetime import datetime
import ctypes

class CameraStream:
    def __init__(self, src=0):
        self.change_source(src)

    def change_source(self, src):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.stopped = True
            time.sleep(0.1)
            self.cap.release()

        self.src = src
        self.is_file = isinstance(src, str)
        self.cap = cv2.VideoCapture(src)
        
        if not self.is_file:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        
        if not self.is_file:
            threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                self.ret, self.frame = ret, frame

    def read(self):
        if self.is_file:
            self.ret, self.frame = self.cap.read()
            if not self.ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.ret, self.frame = self.cap.read()
        return self.frame

    def stop(self):
        self.stopped = True
        if self.cap.isOpened():
            self.cap.release()

def main():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    csv_file = "logs/violation_log.csv"
    if not os.path.exists(csv_file):
        with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["系統時間", "違規項目", "觸發時信心度閾值", "系統效能(FPS)"])

    model_path = "v11s_kd_v18s_best.pt"
    
    try:
        model = YOLO(model_path)
    except Exception as e:
        error_msg = f"找不到模型檔案！\n請確保 '{model_path}' 與執行檔放在同一個資料夾內。"
        ctypes.windll.user32.MessageBoxW(0, error_msg, "SYSTEM ERROR", 0x10)
        return
    
    violation_classes = ["No_Gloves", "No_Helmet"]
    
    current_source_type = "WEBCAM"
    cam = CameraStream(0)
    time.sleep(1)

    window_name = "PPE VISION SYSTEM"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1100, 700)

    last_alert_time = 0
    alert_cooldown = 3.0  
    prev_time = time.time()
    current_conf = 0.50
    
    COLOR_BG = (12, 12, 16)       # 極致深色背景
    COLOR_CYAN = (230, 216, 173)  # 柔和科技白/藍 (BGR)
    COLOR_RED = (80, 80, 255)     # 質感警報紅
    COLOR_GREEN = (90, 220, 120)  # 柔和正常綠

    while True:
        frame = cam.read()
        if frame is None:
            continue

        results = model.predict(source=frame, imgsz=640, stream=True, verbose=False, conf=current_conf)
        
        for r in results:
            annotated_frame = r.plot() 
            detected_violations = set()
            
            if r.boxes:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id]
                    if cls_name in violation_classes:
                        detected_violations.add(cls_name)
            
            h, w = annotated_frame.shape[:2]
            pad_top, pad_bottom, pad_sides = 60, 50, 20  # 縮小邊距，放大畫面佔比
            
            dashboard = np.full((h + pad_top + pad_bottom, w + pad_sides * 2, 3), COLOR_BG, dtype=np.uint8)
            dashboard[pad_top:pad_top+h, pad_sides:pad_sides+w] = annotated_frame
            
            # 簡潔細外框
            cv2.rectangle(dashboard, (pad_sides, pad_top), (pad_sides+w, pad_top+h), (40, 40, 50), 1)

            # 頂部極簡標題與時間
            sys_time = datetime.now().strftime("%H:%M:%S")
            cv2.putText(dashboard, "AI PPE MONITORING", (pad_sides, 38), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, COLOR_CYAN, 1, cv2.LINE_AA)

            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time

            if detected_violations:
                # 右上角極簡違規提示
                violations_str = ", ".join(detected_violations)
                cv2.putText(dashboard, f"ALERT: {violations_str}", (pad_sides + w - 280, 38), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, COLOR_RED, 1, cv2.LINE_AA)
                
                if curr_time - last_alert_time > alert_cooldown:
                    threading.Thread(target=winsound.Beep, args=(2000, 300), daemon=True).start()
                    with open(csv_file, mode='a', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), violations_str, f"{current_conf:.2f}", f"{fps:.1f}"])
                    last_alert_time = curr_time
            else:
                cv2.putText(dashboard, "STATUS: SECURE", (pad_sides + w - 180, 38), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, COLOR_GREEN, 1, cv2.LINE_AA)

            # 底部極簡狀態列 (一行搞定，絕不互卡)
            bar_y = pad_top + h + 32
            status_text = f"FPS: {fps:.1f}  |  SRC: {current_source_type}  |  CONF: {current_conf:.2f}  |  [C]CAM [V]VID [+/-]CONF [Q]EXIT"
            cv2.putText(dashboard, status_text, (pad_sides, bar_y), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.48, (160, 160, 170), 1, cv2.LINE_AA)

            # 高畫質等比例縮放填滿
            display_frame = cv2.resize(dashboard, (1280, 720), interpolation=cv2.INTER_LINEAR)
            cv2.imshow(window_name, display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('+') or key == ord('='):
            current_conf = min(0.95, current_conf + 0.05)
        elif key == ord('-'):
            current_conf = max(0.05, current_conf - 0.05)
        elif key == ord('c') or key == ord('C'):
            cam.change_source(0)
            current_source_type = "WEBCAM"
        elif key == ord('v') or key == ord('V'):
            if os.path.exists("test.mp4"):
                cam.change_source("test.mp4")
                current_source_type = "TEST.MP4"
            
        try:
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break

    cam.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()