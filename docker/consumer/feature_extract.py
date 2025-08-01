import re
from urllib.parse import unquote
from collections import Counter
from math import log2

def shannon_entropy(data):
    """Tính entropy (độ hỗn loạn) của chuỗi, càng cao càng lạ."""
    if not data: return 0
    p, lns = Counter(data), float(len(data))
    return -sum((count/lns) * log2(count/lns) for count in p.values())

def features(row):
    uri = unquote(row["uri"].lower())
    
    # Đếm ký tự encode phổ biến & số lần xuất hiện
    pct_total = uri.count("%")
    pct27 = uri.count("%27")  # dấu nháy đơn
    pct22 = uri.count("%22")  # nháy kép
    pct3c = uri.count("%3c")  # <
    pct3e = uri.count("%3e")  # >
    pct2f = uri.count("%2f")  # /
    pct_hex = len(re.findall(r"%[0-9a-f]{2}", uri))  # số ký tự encode hex bất kỳ

    # Thống kê dấu hiệu về tham số, cấu trúc path
    param_count = uri.count("=")
    question_mark = uri.count("?")
    slash_count = uri.count("/")
    path_depth = len([x for x in uri.split("/") if x])

    # Đặc trưng độ dài, entropy, tỷ lệ ký tự lạ, số chữ số
    total_len = len(uri)
    entropy = shannon_entropy(uri)
    non_alnum_ratio = sum(1 for c in uri if not c.isalnum()) / (total_len or 1)
    digit_count = sum(c.isdigit() for c in uri)

    # Method HTTP (nếu parse được)
    method = row.get("method", "GET")
    
    # Keyword & pattern flags – phát hiện dấu hiệu tấn công
    keywords = [
        "select", "union", "drop", "insert", "update", "delete", "from",
        "script", "<img", "onerror", "alert", "eval", "base64", "admin", "passwd", "shadow",
        "exec", "system", "cmd", "wget", "curl"
    ]
    features_dict = {f"kw_{k}": int(k in uri) for k in keywords}

    # Đặc trưng tấn công nổi bật
    features_dict.update({
        "has_script_tag": int(bool(re.search(r"<\s*script", uri))),
        "has_iframe": int("<iframe" in uri),
        "has_js_event": int(bool(re.search(r"on\w+\s*=", uri))),
        "has_dotdot": len(re.findall(r"\.\.", uri)) + len(re.findall(r"%2e%2e", uri)),
        "has_sql_comment": int("--" in uri or "#" in uri),
        "has_or": int(" or " in uri),
        "has_and": int(" and " in uri),
        "has_semicolon": uri.count(";"),
        "has_pipe": uri.count("|"),
        "has_backtick": uri.count("`"),
        "has_dollar": uri.count("$"),
        "has_curl": int("curl" in uri),
        "has_wget": int("wget" in uri),
    })

    # Gộp đặc trưng về cấu trúc, encode, ký tự
    features_dict.update({
        "uri_len": total_len,
        "digit_count": digit_count,
        "non_alnum_ratio": non_alnum_ratio,
        "pct_total": pct_total,
        "pct27": pct27,
        "pct22": pct22,
        "pct3c": pct3c,
        "pct3e": pct3e,
        "pct2f": pct2f,
        "pct_hex": pct_hex,
        "eq": param_count,
        "question_mark": question_mark,
        "slash_count": slash_count,
        "path_depth": path_depth,
        "entropy": entropy,
        "method_get": int(method == "get"),
        "method_post": int(method == "post"),
        "http_status": row.get("status", 200),
    })

    return features_dict
