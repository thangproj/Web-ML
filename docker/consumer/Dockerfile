# Base image Python
FROM python:3.10-slim

# Cài đặt thư mục làm việc
WORKDIR /app

# Copy mã nguồn
COPY . /app

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Command mặc định khi container chạy
CMD ["python", "realtime_detect.py"]
