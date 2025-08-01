# Web Anomaly Detector

Hệ thống phát hiện truy cập bất thường (Anomaly Detection) trên log HTTP bằng Machine Learning (Isolation Forest)  
Triển khai Docker hóa – dễ dàng chạy real-time, mở rộng và nâng cấp.

---

## 1. Tổng quan kiến trúc

- **Flask App:** Giả lập web server, sinh log truy cập vào file `logs/access.log`.
- **Train Model:** Trích xuất feature từ log, huấn luyện Isolation Forest, lưu model và feature_list.
- **Consumer (Real-time detect):** Theo dõi log mới, extract feature, phát hiện bất thường và ghi ra `anomaly.log`.
- **Docker Compose:** Quản lý và khởi động các thành phần hệ thống.

```
[Flask App] --> [logs/access.log] --> [Consumer detect bất thường]
                    ↑                        |
            [Train Model offline]     [anomaly.log]
```

---

## 2. Cây thư mục dự án

```
web-anomaly-detector/
├── docker-compose.yml
├── logs/
│   └── access.log                # Log truy cập sinh ra bởi Flask App
├── docker/
│   ├── flask/
│   │   ├── Dockerfile
│   │   └── app.py                # Flask app ghi log truy cập
│   └── consumer/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── realtime_detect.py    # Script detect real-time
│       ├── feature_extract.py    # Hàm trích xuất đặc trưng
│       ├── model.pkl             # Mô hình Isolation Forest đã train
│       ├── feature_list.pkl      # Danh sách các feature dùng trong model
│       └── anomaly.log           # Log các truy cập bất thường
├── ml/
│   ├── train_model.py            # Script train model, extract feature
│   └── ...                      # Các script phụ trợ (nếu có)
└── README.md
```

---

## 3. Hướng dẫn sử dụng

### **Bước 1: Train model (ngoài Docker)**

- Chạy script train:
  ```bash
  cd ml
  python train_model.py
  ```
- File `model.pkl` và `feature_list.pkl` sẽ xuất ra `docker/consumer/`.

### **Bước 2: Build và chạy Docker**

- Quay lại thư mục gốc, build và start hệ thống:
  ```bash
  docker-compose build
  docker-compose up -d
  ```
- **Check logs:**
  ```bash
  docker-compose logs -f flask-app
  docker-compose logs -f consumer
  ```

### **Bước 3: Kiểm tra phát hiện bất thường**

- Các truy cập bất thường sẽ được ghi vào file:
  ```
  docker/consumer/anomaly.log
  ```

---

## 4. Tùy biến/Update model

- Khi muốn cập nhật model mới:
  1. Train lại model bằng script `train_model.py`.
  2. Ghi đè file `model.pkl` và `feature_list.pkl` vào `docker/consumer/`.
  3. Khởi động lại container consumer:
     ```bash
     docker-compose restart consumer
     ```

---

## 5. Các feature hỗ trợ phát hiện bất thường

- Độ dài URL, entropy, tỷ lệ ký tự đặc biệt, pattern XSS/SQLi/Directory Traversal/Command Injection...
- Số lượng ký tự encode, tham số, path depth, từ khóa nguy hiểm...
- Dễ mở rộng thêm feature hoặc đổi mô hình ML (Autoencoder, One-Class SVM, ...).

---

## 6. Đóng góp & phát triển thêm

- Có thể tích hợp thêm Filebeat/ELK để visualize log.
- Bổ sung dashboard thống kê tấn công.
- Kết hợp cảnh báo (email, Slack, Telegram...) khi phát hiện truy cập lạ.

---

## 7. Yêu cầu hệ thống

- Docker & Docker Compose
- Python 3.8+
- Các thư viện: pandas, joblib, scikit-learn, flask

---

## 8. Liên hệ

- Author: [Tên của bạn]
- Email: [Email liên hệ]

---
