import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔌 KONEKSI DATABASE
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123456",  # ✅ sudah diganti sesuai kamu
    database="bank_db"
)

# ======================
# HOME
# ======================
@app.route("/")
def home():
    return "API Banking + MySQL 🔥"

# ======================
# REGISTER (POST)
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

    cursor.execute(
        "INSERT INTO users (nama, saldo, password) VALUES (%s, %s, %s)",
        (nama, 0, password)
    )
    db.commit()

    return "Register berhasil!"

# ======================
# REGISTER (GET - TEST CEPAT)
# ======================
@app.route("/register/<nama>/<password>")
def register_test(nama, password):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE nama=%s", (nama,))
    if cursor.fetchone():
        return "User sudah ada!"

    cursor.execute(
        "INSERT INTO users (nama, saldo, password) VALUES (%s, %s, %s)",
        (nama, 0, password)
    )
    db.commit()

    return "Register berhasil!"

# ======================
# LOGIN
# ======================
@app.route("/login/<nama>/<password>")
def login(nama, password):
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE nama=%s AND password=%s",
        (nama, password)
    )
    user = cursor.fetchone()

    if user:
        return jsonify({
            "message": "Login berhasil",
            "id": user[0],
            "nama": user[1]
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