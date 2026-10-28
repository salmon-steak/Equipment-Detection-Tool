# 🛡️ AI PPE Detection System (工安防護裝備智慧偵測系統)

基於 **Ultralytics YOLO** 與 **OpenCV** 開發的即時、低延遲本地端工安防護裝備違規偵測與警報系統。

---

## ✨ 核心功能特色 (Key Features)

- **即時物件偵測**：精準辨識安全帽佩戴狀況 (`helmet`, `No_Helmet`) 與防護手套狀況 (`Gloves`, `No_Gloves`)。
- **極簡科技介面 (Clean HUD)**：無雜訊的高畫質 1280x720 滿版縮放視窗，即時顯示系統時間、FPS 效能與狀態。
- **動態影像來源切換**：支援即時網路攝影機 (**WebCam**) 與預錄示範影片 (**test.mp4**) 的無縫切換。
- **熱鍵互動控制**：
  - `C` 鍵：切換至網路攝影機。
  - `V` 鍵：切換至預錄影片。
  - `+` / `-` 鍵：即時微調模型信心度閾值 (Confidence Threshold)。
  - `Q` 鍵：安全終止程式。
- **智慧警報與數據記錄**：觸發違規時自動發出音效警報 (`winsound`)，並同步將時間、違規項目與效能寫入輕量化 `.csv` 報表。

---

## 🛠️ 技術堆疊 (Tech Stack)
- **Programming Language**: Python 3.10+
- **Core Vision**: OpenCV, Ultralytics YOLO
- **Audio & Logging**: Winsound, CSV Module
- **Deployment**: PyInstaller

---
