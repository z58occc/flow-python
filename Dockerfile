# 使用官方 Python 映像
FROM python:3.10-slim

# 安裝系統層級依賴 (含 ffmpeg + opencv 需要的庫)
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    && apt-get clean

# 建立工作目錄
WORKDIR /app

# 複製所有檔案進容器
COPY . .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 開放 Flask 預設的 5000 port
EXPOSE 5000

# 啟動指令
CMD ["python", "flask_app.py"]
