@echo off
chcp 65001 >nul
echo ===================================================
echo     PPE Vision System - 一鍵自動打包與更新工具
echo ===================================================

echo.
echo [1/4] 正在清理舊有的暫存檔與快取...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist detect.spec del /q detect.spec

echo.
echo [2/4] 開始進行 PyInstaller 乾淨編譯...
echo (過程可能需要幾分鐘，請耐心等候，不要關閉視窗)
pyinstaller --noconsole --clean --collect-all ultralytics detect.py

echo.
echo [3/4] 正在將模型檔案與測試影片整合進發布資料夾...
if exist v11s_kd_v18s_best.pt (
    copy v11s_kd_v18s_best.pt dist\detect\ >nul
    echo [OK] 成功複製模型檔 (v11s_kd_v18s_best.pt)
) else (
    echo [警告] 找不到 v11s_kd_v18s_best.pt！請確認模型與 detect.py 放在同一個資料夾。
)

if exist test.mp4 (
    copy test.mp4 dist\detect\ >nul
    echo [OK] 成功複製測試影片 (test.mp4)
)

echo.
echo [4/4] 重新命名資料夾...
if exist dist\detect (
    ren dist\detect PPE_Vision_System
    echo [OK] 最終執行檔已準備就緒，位於 dist\PPE_Vision_System 目錄中！
)

echo.
echo ===================================================
echo 更新與打包已全部完成！您可以將 dist 裡面的資料夾壓成 ZIP 帶走了。
echo ===================================================
pause