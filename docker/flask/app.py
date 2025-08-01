from flask import Flask, request, Response
import logging, os, time

app = Flask(__name__)

# Tạo thư mục logs nếu chưa tồn tại
log_path = "logs/access.log"
os.makedirs("logs", exist_ok=True)

# Cấu hình logger
logger = logging.getLogger("web")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(log_path)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Middleware log sau mỗi request
@app.after_request
def log_request(response: Response):
    log_line = f'{request.remote_addr} - - [{time.strftime("%d/%b/%Y:%H:%M:%S %z")}] "{request.method} {request.path} HTTP/1.1" {response.status_code}'
    logger.info(log_line)
    return response

# Routes
@app.route("/")
def home():
    return "Home page"

@app.route("/product")
def product():
    pid = request.args.get("id", "")
    return f"Product page for id: {pid}"

@app.route("/search")
def search():
    q = request.args.get("q", "")
    return f"Search result for: {q}"

@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("username")
    return "Login failed", 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
