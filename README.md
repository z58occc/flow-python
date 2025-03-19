以下是根據您的程式撰寫的 README：

---

# 人流資料可視化系統

此專案提供一個基於 Flask 框架的人流資料可視化平台，允許使用者查看特定日期的人流資料及相關圖表。系統包括數據生成、前端顯示和後端 API 來支援動態數據的呈現。

## 目錄結構

- `data_generation.py` - 用於生成或處理人流數據的程式碼。
- `flask_app.py` - Flask 應用程式的主程式碼，設定路由和 API，提供資料給前端。
- `for_test_upload_data.json` - 測試用的 JSON 檔案，包含模擬人流數據。
- `index.html` - 人流資料的主頁面，顯示日曆、當月資料和按日查詢按鈕。
- `script.js` - 包含前端 JavaScript 邏輯，用於月份切換和人流資料查詢。
- `style.css` - CSS 樣式檔，設定整體頁面的樣式。
- `data` - 資料夾 儲存資料
- `uploads` - 資料夾 暫存上傳資料，上傳新資料會被洗掉

## 功能

### 1. 人流數據生成
`data_generation.py` 負責生成模擬的人流數據，可根據需求修改數據生成邏輯，並輸出為 JSON 檔案，供 Flask 後端使用。

### 2. 前端頁面
`index.html` 提供一個人流數據查詢界面，包括：
- 日曆視圖：顯示每月日期，可點擊日期查詢人流資料。
- 上月、下月按鈕：切換月份，查看歷史人流數據。
- 詳細資訊視窗：顯示查詢日期的人流總數量，並載入對應的圖表。
## 如何執行


 執行 Flask 應用程式：
   ```bash
   python flask_app.py
   ```

### 獲取所有資料

```bash
curl -X GET http://127.0.0.1:5000/api/footfall
```

### 獲取某日某小時的資料

```bash
curl -X GET http://127.0.0.1:5000/api/footfall/2024-07-28/14
```

### 添加某日某小時的資料

```bash
curl -X POST http://127.0.0.1:5000/api/footfall -H "Content-Type: application/json" -d '{"date": "2024-07-29", "hour": 14, "footfall": 150}'
```

### 修改某日某小時的資料

```bash
curl -X PUT http://127.0.0.1:5000/api/footfall/2024-07-28/14 -H "Content-Type: application/json" -d "{\"footfall\": 150}"
```

### 刪除某日某小時的資料

```bash
curl -X DELETE http://127.0.0.1:5000/api/footfall/2024-07-28/14
```

### 上傳檔案到資料庫

```bash
curl -X POST http://127.0.0.1:5000/api/upload -F "file=@data.json"
curl -X POST http://127.0.0.1:5000/api/upload -F "file=@for_test_upload_data.json"
```

### 上傳影片到資料庫 (資料夾clients_video)
```bash
curl -X POST http://127.0.0.1:5000/api/upload_video -F "video=@影片路徑"
```

"# web_and_yolo" 
