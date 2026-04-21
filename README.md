# CollabLoc Local Receiver

本專案為論文 CollabLoc: Collaborative Information Sharing for Real-Time Multiuser Visual Localization System 的實作。旨在透過手機進行空間定位，並將定位資料即時傳送至本地電腦。此 repo 為專案的本地端接收/視覺化工具，配和 Android AR 應用程式 (`HelloAR Java`) 使用。

## 1. 手機端應用程式：HelloAR Java

本應用程式實作 CollabLoc 論文中的 Client 端，得到目前位置在場景中的 6DOF Pose (六自由度位姿)，並透過 UDP 廣播將資料傳送至同網域的本地裝置。

### 操作流程
1. **啟動**：開啟 Andriod 手機上的 HelloAR Java 應用程式。
2. **網路連線**：啟動時請務必連上網路，並確認與接收端使用相同網路。
3. **定位與資料發送**：
   - 當手機成功與後端伺服器同步後，會顯示「Connect Success !」。
   - **點擊螢幕**進入定位模式，看到「Recording logs」表示手機正在背景持續發送 UDP 封包到 Port 8888。
   - 再次點擊螢幕結束定位模式，停止定位及資訊發送。

### 螢幕提示說明 (Hints)
* **`Connect Success !` (連線成功)**：手機已成功連線至遠端定位伺服器，並獲取初始化的世界座標參考。
* **`Connect Failed ! Retrying...` (連線失敗)**：無法連線至定位伺服器。請檢查手機的網路能否正常存取外部網路（或特定伺服器 IP）。若確認連線正常，可能是我們的定位伺服器斷線，請聯絡我們重啟。
* **`Recording logs` (正在記錄日誌)**：定位系統已啟動，目前正將 `Image Stamp`、`Time Stamp` 與 `Fused World Pose` 持續發送至本地裝置。

---

## 2. 本地裝置端

此 repo 負責接收手機廣播的資料，並在電腦上即時繪製相應的運動軌跡與點雲地圖。

### 環境設定
請確保已安裝 Python 3.8+。

**1. 下載地圖資料（必備）**
在使用視覺化工具前，請先下載我們預先建模好的工五 8 樓點雲地圖：
*   **載點**：[Google Drive 下載連結](https://drive.google.com/file/d/1rw0VvscFCxpE8VOSAvjpF7po0VDg85BV/view?usp=sharing)

**2. 安裝套件**
```bash
# 安裝必要套件
pip install -r requirements.txt
```

### 啟動方式
執行前，請確認**手機與電腦位於同一個區域網路 (Wi-Fi)**。請先將接收端程式碼啟動後再點擊開啟 HelloAR Java 的定位模式。

```bash
# 基本啟動方式 (需指定點雲路徑)
python udp_server.py --point_cloud <點雲檔案路徑>

# 選項與參數說明
# --point_cloud:    下載的地圖點雲檔案路徑 (例如: ee8f/points3D.txt)
# --udp_port:       監聽的 UDP Port (預設為 8888)
# --plot_interval:  繪圖更新頻率，單位為秒 (預設為 0.5)

# 進階啟動範例
python udp_server.py --point_cloud ee8f/points3D.txt --udp_port 8888 --plot_interval 0.1
```

### 技術細節與注意事項
* **通訊協定**：預設使用 UDP Port `8888`，與 HelloAR Java 程式目前發送的 Port 相同(可透過 `--udp_port` 修改)。
* **資料格式**：接收到的格式為 `img_stamp|time_stamp|pose_data`。
* **視覺化**：請透過 `--point_cloud` 參數指定地圖點雲路徑，繪圖器會讀取此路徑來渲染空間點雲。
* **更新頻率**：若覺得繪圖延遲較大，可調低 `--plot_interval` (例如 0.1)。
* **關閉程式**：在終端機按下 `Ctrl + C` 即可停止接收。

### 故障排除

如果你發現 `udp_server.py` 無法接收到手機發送的資料，可以使用內附的 `test_sender.py` 進行交叉測試，確認是否為**接收端電腦防火牆**的問題。

1. **環境準備**：找另一台在相同 Wi-Fi 下的電腦（或在同一台電腦開啟另一個終端機）作為「測試發送端」。
2. **啟動接收端**：執行 `python udp_server.py --point_cloud <路徑>`。
3. **啟動測試發送端**：執行 `python test_sender.py`。

**診斷結果：**
*   **若測試發送端啟動後，接收端有顯示資料**：代表接收端電腦設定正常，問題可能出在手機端，請聯繫我們解決。
*   **若收不到資料**：
    *   請檢查接收端電腦的系統防火牆 (Windows Defender / macOS Firewall)，確認是否已**放行 UDP Port 8888**。
    *   確認兩台設備是否連線至同一個 Wi-Fi 網域。

---
