from flask import Flask, render_template, jsonify  # type: ignore
import mysql.connector
import json

app = Flask(__name__)

def connect_to_db():
    """Membuat koneksi ke database MySQL."""
    try:
        conn = mysql.connector.connect(
            host="localhost",  # Ganti dengan host Anda
            user="root",  # Ganti dengan username Anda
            password="",  # Ganti dengan password Anda
            database="iot",  # Ganti dengan nama database Anda
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error saat menghubungkan ke database: {e}")
        return None

def fetch_data(conn, query):
    """Mengambil data dari database berdasarkan query yang diberikan."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()  # Menarik semua hasil query
        return rows
    except mysql.connector.Error as e:
        print(f"Error saat mengambil data: {e}")
        return []

def load_json_data(file_path):
    """Memuat data dari file JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File {file_path} tidak ditemukan.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}

@app.route("/cuaca.json")
def show_json_data():
    """Endpoint untuk menampilkan data cuaca dari file JSON."""
    data = load_json_data('cuaca.json')  # Ganti 'cuaca.json' dengan path file yang benar

    if data:
        return jsonify(data)
    else:
        return jsonify({"message": "Data JSON tidak tersedia atau terjadi kesalahan."}), 404

@app.route("/")
def index():
    """Menampilkan data suhu, kelembapan, dan waktu di template HTML."""
    query = "SELECT * FROM tb_cuaca;"  # Ganti dengan query yang sesuai dengan kebutuhan Anda

    # Terhubung ke database
    conn = connect_to_db()

    if conn:
        # Menarik data
        data = fetch_data(conn, query)

        if data:
            # Mengambil suhu, kelembapan, dan waktu
            suhu_data = [row[2] for row in data]  # Kolom suhu (misalnya kolom ke-3)
            kelembapan_data = [row[3] for row in data]  # Kolom kelembapan (misalnya kolom ke-4)
            waktu_data = [row[1] for row in data]  # Kolom waktu (misalnya kolom ke-2)

            suhu_tertinggi = max(suhu_data)
            suhu_terendah = min(suhu_data)
            rata_rata_suhu = sum(suhu_data) / len(suhu_data) if suhu_data else 0

            # Menutup koneksi ke database
            conn.close()

            # Mengirim data ke template HTML
            return render_template(
                "index.html",
                suhu_max=suhu_tertinggi,
                suhu_min=suhu_terendah,
                suhu_avg=rata_rata_suhu,
                waktu_data=waktu_data,
                suhu_data=suhu_data,
                kelembapan_data=kelembapan_data,
            )
        else:
            return "Tidak ada data yang ditemukan."

    else:
        return "Gagal terhubung ke database."

if __name__ == "__main__":
    app.run(debug=True)
