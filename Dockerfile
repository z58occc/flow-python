FROM python:3.10

# 安裝 ffmpeg（含 libx264）、OpenCV 所需的依賴
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    && apt-get clean

# 建立工作資料夾
WORKDIR /app

# 複製程式碼進容器
COPY . .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 port（Flask 用）
EXPOSE 5000

# 執行應用
CMD ["python", "flask_app.py"]
