import os
import mysql.connector
from flask import Flask, request, jsonify
import bcrypt
import jwt
import datetime

app = Flask(__name__)

# ======================
# SECRET KEY
# ======================
SECRET_KEY = "root123456"

# ======================
# KONEKSI DATABASE (ANTI CRASH)
# ======================
try:
    db = mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )
    print("✅ Database connected")
except Exception as e:
    print("❌ Database error:", e)
    db = None


# ======================
# HOME
# ======================
@app.route("/")
def home():
    return "API Banking + MySQL + JWT 🔥"


# ======================
# REGISTER
# ======================
@app.route("/register/<nama>/<password>")
def register(nama, password):
    if not db:
        return "Database tidak terhubung!"

    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE nama=%s", (nama,))
    if cursor.fetchone():
        return "User sudah ada!"

    # HASH PASSWORD 🔐
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (nama, saldo, password) VALUES (%s, %s, %s)",
        (nama, 0, hashed_pw.decode('utf-8'))
    )
    db.commit()

    return "Register berhasil!"


# ======================
# LOGIN + JWT
# ======================
@app.route("/login/<nama>/<password>")
def login(nama, password):
    if not db:
        return "Database tidak terhubung!"

    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE nama=%s", (nama,))
    user = cursor.fetchone()

    if user:
        hashed_pw = user[3]

        # CEK PASSWORD HASH
        if bcrypt.checkpw(password.encode('utf-8'), hashed_pw.encode('utf-8')):
            token = jwt.encode({
                "user_id": user[0],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, SECRET_KEY, algorithm="HS256")

            return jsonify({
                "message": "Login berhasil",
                "token": token
            })

    return "Login gagal!"


# ======================
# CEK SALDO (PROTECTED)
# ======================
@app.route("/saldo/<int:user_id>")
def saldo(user_id):
    if not db:
        return "Database tidak terhubung!"

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
    if not db:
        return "Database tidak terhubung!"

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
# RUN (WAJIB UNTUK RAILWAY)
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)