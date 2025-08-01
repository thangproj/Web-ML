import time
import joblib
import os
import pandas as pd        # Thêm import này để dùng DataFrame
from feature_extract import parse, features

model = joblib.load("docker/consumer/model.pkl")
log_file = "../docker/flask/logs/access.log"

# Load danh sách tên cột feature đã lưu khi train
feature_list = joblib.load("docker/consumer/feature_list.pkl")

print("🟢 Đang giám sát truy cập...")

with open(log_file, "r") as f, open("docker/consumer/anomaly.log", "a") as anomaly_f:
    f.seek(0, 2)  # Nhảy tới cuối file ban đầu (tail)
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.5)
            continue
        p = parse(line)
        if not p:
            continue
        x = features(p)

        # Chuyển dict x thành DataFrame và ép về đúng số cột/thứ tự
        X_df = pd.DataFrame([x])
        X_df = X_df.reindex(columns=feature_list, fill_value=0)

        try:
            pred = model.predict(X_df)[0]
            score = model.decision_function(X_df)[0]
        except Exception as e:
            print(f"❌ Lỗi dự đoán: {e}")
            continue

        label = "✅ Bình thường" if pred == 1 else "❌ Bất thường"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        print(f"{timestamp} [{label}] score={score:.4f} {line.strip()}")
        print("    Real-time Feature:", x)

        if pred == -1:
            anomaly_f.write(f"{timestamp}\t{line.strip()}\tFEATURE={x}\tSCORE={score:.4f}\n")
            anomaly_f.flush()
