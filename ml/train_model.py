import pandas as pd
import joblib
import glob
import os
from sklearn.ensemble import IsolationForest
from feature_extract import parse, features

# Đường dẫn log, cho phép đổi nhanh
LOG_DIR = os.path.join("..", "docker", "flask", "logs")
LOG_PATTERN = "access.log*"
CONSUMER_DIR = os.path.join("docker", "consumer")

# Đọc tất cả log files
print("📂 Danh sách file log đang đọc:")
log_files = glob.glob(os.path.join(LOG_DIR, LOG_PATTERN))
if not log_files:
    print("❌ Không tìm thấy file log nào trong", LOG_DIR)
    exit()

for f in log_files:
    print("  -", f)

logs = []
for f in log_files:
    with open(f, "r") as file:
        for line in file:
            p = parse(line)
            if p:
                logs.append(p)

print(f"\n🔍 Số dòng log parse được: {len(logs)}")
if not logs:
    print("❌ Không có log hợp lệ để huấn luyện. Vui lòng kiểm tra file logs/access.log.")
    exit()

# DataFrame
df = pd.DataFrame(logs)
X = df.apply(features, axis=1, result_type='expand')

# Thống kê số lượng truy cập có dấu hiệu tấn công (dựa vào feature)
def is_anomaly(feats):
    return feats.get('quote') or feats.get('script') or feats.get('dotdot') or feats.get('union')

anomaly_flags = X.apply(is_anomaly, axis=1)
num_anomaly = anomaly_flags.sum()
num_normal = len(X) - num_anomaly
print(f"🛑 Số dòng log nghi ngờ tấn công: {num_anomaly}")
print(f"✅ Số dòng log bình thường: {num_normal}")

if num_anomaly < 10:
    print("⚠️ Cảnh báo: Số log tấn công quá ít! Hệ thống có thể khó phát hiện bất thường thực tế.")
    print("👉 Gợi ý: Bổ sung thêm log truy cập có dấu hiệu tấn công vào file log trước khi train.")

if X.empty:
    print("❌ Không có đặc trưng hợp lệ để train model.")
    exit()

# Thống kê đặc trưng bất thường (xem lại)
print("\n📈 30 dòng feature cuối cùng:")
print(X.tail(30))
print("\n📋 Feature các dòng có dấu hiệu bất thường:")
print(X.loc[anomaly_flags].tail(30))  # Dùng loc để lọc dòng theo điều kiện

# Điều chỉnh contamination: tỷ lệ tối thiểu là 0.05, tối đa 0.2 (tuỳ số lượng mẫu bất thường)
auto_contamination = max(0.05, min(num_anomaly / len(X) + 0.01, 0.2))
print(f"\n⚙️ Dùng contamination = {auto_contamination:.3f} cho Isolation Forest.")

# Train Isolation Forest
model = IsolationForest(contamination=auto_contamination, random_state=42)
model.fit(X)

# Đảm bảo thư mục model tồn tại
os.makedirs(CONSUMER_DIR, exist_ok=True)
joblib.dump(model, os.path.join(CONSUMER_DIR, "model.pkl"))
print(f"\n✅ Đã lưu thành công model.pkl vào {CONSUMER_DIR}/")

# ==== BỔ SUNG: LƯU FEATURE LIST ĐỂ ĐỒNG BỘ VỚI REALTIME ====
feature_list = X.columns.tolist()
joblib.dump(feature_list, os.path.join(CONSUMER_DIR, "feature_list.pkl"))
print(f"✅ Đã lưu thành công feature_list.pkl vào {CONSUMER_DIR}/")

print("\n🚩 Đã hoàn thành train model! Nếu vẫn chưa phát hiện được truy cập bất thường, hãy bổ sung thêm log tấn công vào file log rồi train lại.")
