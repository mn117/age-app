import os, shutil
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from PIL import Image
import torch

# モデル用インポート
from transformers import ViTImageProcessor
from model import predict_age_gender  # age-gender-prediction の helper 関数

UPLOAD_FOLDER = "./static/images/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
    if "file" not in request.files:
        return redirect(url_for("index"))
    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return redirect(url_for("index"))

    # 保存フォルダをリセット
    if os.path.isdir(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    image = Image.open(filepath).convert("RGB")

    # age-gender-prediction の helper 関数を使って推定
    result_dict = predict_age_gender(filepath)  # または image object を渡すバージョン
    print(result_dict)
    age = result_dict.get("age")
    gender = result_dict.get("gender")
    if gender == "Male": 
        gender_jp = "男性" 
    elif gender == "Female": 
        gender_jp = "女性"
    gender_conf = result_dict.get("gender_confidence", None)

    return render_template(
        "result.html",
        age=age,
        gender=gender_jp,
        gender_confidence=gender_conf,
        filepath=filepath
    )

if __name__ == "__main__":
    app.run(debug=True)

