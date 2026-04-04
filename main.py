import mysql.connector
from flask import Flask, request, jsonify

import bcrypt
import jwt
import datetime

SECRET_KEY = "root123456"

app = Flask(__name__)

# 🔌 KONEKSI DATABASE
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123456",
    database="bank_db"
)

# ======================
# HOME
# ======================
@app.route("/")
def home():
    return "API Banking + MySQL 🔥"

# ======================
# REGISTER (POST + HASH)
# ======================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    nama = data["nama"]
    password = data["password"]

    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE nama=%s", (nama,))
    if cursor.fetchone():
        return "User sudah ada!"

    # 🔐 HASH PASSWORD
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (nama, saldo, password) VALUES (%s, %s, %s)",
        (nama, 0, hashed.decode('utf-8'))
    )
    db.commit()

    return "Register berhasil!"

# ======================
# REGISTER (GET - TEST)
# ======================
@app.route("/register/<nama>/<password>")
def register_test(nama, password):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE nama=%s", (nama,))
    if cursor.fetchone():
        return "User sudah ada!"

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (nama, saldo, password) VALUES (%s, %s, %s)",
        (nama, 0, hashed.decode('utf-8'))
    )
    db.commit()

    return "Register berhasil!"

# ======================
# LOGIN (JWT + HASH CHECK)
# ======================
@app.route("/login/<nama>/<password>")
def login(nama, password):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE nama=%s", (nama,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):

        # 🎟️ GENERATE TOKEN
        token = jwt.encode({
            "user_id": user[0],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "message": "Login berhasil",
            "token": token
        })
    else:
        return "Login gagal!"

# ======================
# CEK SALDO
# ======================
@app.route("/saldo/<int:user_id>")
def saldo(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    if not user:
        return "User tidak ditemukan!"

    return jsonify({
        "id": user[0],
        "nama": user[1],
        "saldo": user[2]
    })

# ======================
# TRANSFER
# ======================
@app.route("/transfer/<int:user_id>/<int:jumlah>")
def transfer(user_id, jumlah):
    cursor = db.cursor()

    cursor.execute("SELECT saldo FROM users WHERE id=%s", (user_id,))
    result = cursor.fetchone()

    if not result:
        return "User tidak ditemukan!"

    saldo = result[0]

    if jumlah > saldo:
        return "Saldo tidak cukup!"

    saldo_baru = saldo - jumlah

    cursor.execute(
        "UPDATE users SET saldo=%s WHERE id=%s",
        (saldo_baru, user_id)
    )
    db.commit()

    return f"Transfer berhasil! Sisa saldo: {saldo_baru}"

# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run(debug=True)