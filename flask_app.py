from flask import Flask, render_template, jsonify, request, send_file
import json
import calendar as cal
from datetime import datetime
import matplotlib.pyplot as plt
import io
import os
import matplotlib
from count_footfall.process import process_video

matplotlib.use('Agg')

app = Flask(__name__)

FILE_NAME = 'data/footfall_data.json'
# 影片上傳資料夾
VIDEO_UPLOAD_FOLDER = './clients_video'
# 人流資料上傳資料夾
UPLOAD_FOLDER = './uploads'

# 從JSON讀取人流量數據的函式
def read_data(filename=FILE_NAME):
    try:
        with open(filename, 'r') as jsonfile:
            data = json.load(jsonfile)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    total = sum(sum(day_data.values()) for day_data in data.values())
    return data, total

# 將數據寫入JSON的函式
def write_data(data, filename=FILE_NAME):
    with open(filename, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)

# API端點來獲取所有人流量數據
@app.route('/api/footfall', methods=['GET'])
def api_get_footfall():
    data, total = read_data()
    return jsonify({"data": data, "total": total})

# API端點來新增人流量數據
@app.route('/api/footfall', methods=['POST'])
def api_add_footfall():
    new_entry = request.json
    data, _ = read_data()
    
    date = new_entry['date']
    hour = int(new_entry['hour'])
    footfall = new_entry['footfall']
    
    if date not in data:
        data[date] = {}
    data[date][str(hour)] = footfall
    
    write_data(data)
    return jsonify({"message": "Data added successfully", "data": new_entry}), 201


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 確保上傳資料夾存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# 處理文件上傳的 API 端點
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and file.filename.endswith('.json'):
        # 將檔案儲存到指定目錄
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # 如果檔案是 JSON 格式，讀取並合併到現有資料中
        with open(filepath, 'r') as jsonfile:
            new_data = json.load(jsonfile)
        
        data, _ = read_data()
        for date, hourly_data in new_data.items():
            if date not in data:
                data[date] = hourly_data
            else:
                for hour, footfall in hourly_data.items():
                    data[date][hour] = footfall
        
        write_data(data)
        
        return jsonify({"message": "File uploaded successfully and data merged"}), 201
        
    return jsonify({"error": "Invalid file format or other error"}), 400

# API端點來根據日期和小時刪除人流量數據
@app.route('/api/footfall/<date>/<hour>', methods=['DELETE'])
def api_delete_footfall(date, hour):
    data, _ = read_data()
    if date in data and str(hour) in data[date]:
        data[date][str(hour)] = 0
    else:
        return jsonify({"error": "Date or hour not found"}), 404
    
    write_data(data)
    return jsonify({"message": "Data deleted successfully", "date": date, "hour": hour}), 200

# API端點來根據日期和小時獲取人流量數據
@app.route('/api/footfall/<date>/<hour>', methods=['GET'])
def api_get_footfall_by_date_hour(date, hour):
    data, _ = read_data()
    hour = str(hour)
    if date in data and hour in data[date] and data[date][hour] != 0:
        return jsonify({"date": date, "hour": hour, "footfall": data[date][hour]})
    else:
        return jsonify({"error": "Date or hour not found"}), 404
    
# API端點來根據日期獲取人流量數據
@app.route('/api/footfall/<date>', methods=['GET'])
def api_get_footfall_by_date_api(date):
    data, _ = read_data()
    if date in data:
        return jsonify({"date": date, "footfall": data[date]})
    else:
        return jsonify({"error": "Date not found"}), 404

# API端點來根據日期和小時修改人流量數據
@app.route('/api/footfall/<date>/<hour>', methods=['PUT'])
def api_update_footfall(date, hour):
    updated_entry = request.json
    data, _ = read_data()
    hour = str(hour)
    
    if date in data:
        data[date][hour] = updated_entry['footfall']
    else:
        return jsonify({"error": "Date not found"}), 404

    write_data(data)
    return jsonify({"message": "Data updated successfully", "date": date, "hour": hour, "footfall": updated_entry['footfall']}), 200

@app.route('/')
def index():
    current_date = datetime.now()
    year = int(request.args.get('year', current_date.year))
    month = int(request.args.get('month', current_date.month))
    data, _ = read_data()
    month_data = {}
    for date in data:
        date_parts = date.split('-')
        if int(date_parts[0]) == year and int(date_parts[1]) == month:
            day = int(date_parts[2])
            month_data[day] = sum(data[date].values())
    
    cal.setfirstweekday(cal.SUNDAY)
    cal_data = cal.monthcalendar(year, month)
    
    return render_template('index.html', year=year, month=month, data=month_data, cal=cal_data)

@app.route('/api/footfall/<year>/<month>/<day>', methods=['GET'])
def api_get_footfall_by_date(year, month, day):
    data, _ = read_data()
    date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
    if date in data:
        return jsonify({"date": date, "footfall": data[date]})
    else:
        return jsonify({"error": "尚無資料"}), 404

# 生成並返回人流量圖表
@app.route('/footfall_chart/<year>/<month>/<day>.png')
def footfall_chart(year, month, day):
    data, _ = read_data()
    date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
    
    if date not in data:
        return jsonify({"error": "Date not found"}), 404
    
    footfall = [data[date].get(str(hour), 0) for hour in range(24)]
    hours = list(range(24))

    plt.figure(figsize=(10, 6))
    plt.bar(hours, footfall, color='blue')
    plt.xlabel('Hour')
    plt.ylabel('Footfall')
    plt.title(f'Footfall for {date}')
    plt.xticks(hours)
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png')

# 確保影片上傳資料夾存在
app.config['VIDEO_UPLOAD_FOLDER'] = VIDEO_UPLOAD_FOLDER

if not os.path.exists(VIDEO_UPLOAD_FOLDER):
    os.makedirs(VIDEO_UPLOAD_FOLDER)

# 處理影片上傳的 API 端點
@app.route('/api/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file uploaded"}), 400

    video = request.files['video']

    if video.filename == '':
        return jsonify({"error": "No video file selected"}), 400

    # 檢查檔案類型，確保是影片檔案
    allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
    file_ext = os.path.splitext(video.filename)[1].lower()

    if file_ext not in allowed_extensions:
        return jsonify({"error": "Invalid video file format"}), 400
    
    # 為檔名新增日期時間
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # 格式: YYYYMMDD_HHMMSS
    original_name = os.path.splitext(video.filename)[0]
    new_filename = f"{original_name}_{timestamp}{file_ext}"

    # 儲存影片檔案到指定資料夾
    filepath = os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], new_filename)
    video.save(filepath)

    print("Processing video...")
    try:
        # process_video 回傳計算到的人數
        footfall_count = process_video(filepath)
    except Exception as e:
        # 當處理影片失敗時，回傳錯誤訊息和 500 狀態碼
        print("Error processing video:", str(e))
        return jsonify({"error": "Video processing failed", "details": str(e)}), 500

    print("Video processed successfully")
    return jsonify({
        "message": "Video uploaded successfully",
        "file_path": filepath,
        "footfall": footfall_count
    }), 201

if __name__ == '__main__':
    app.run(debug=True)
