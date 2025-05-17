from flask import Flask, jsonify, request
from flask_cors import CORS  # ✅ Bổ sung import
import pyodbc
from datetime import datetime
app = Flask(__name__)
CORS(app)  # ✅ Bật CORS để gọi từ frontend port 5500

# Kết nối CSDL
try:
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=DESKTOP-AM5QF8J;"
        "Database=QL_QuanInternetGaming;"
        "Trusted_Connection=yes"
    )
    con = pyodbc.connect(conn_str)
    print("✅ Kết nối SQL Server thành công!")
except Exception as e:
    con = None
    print("❌ Kết nối CSDL thất bại:", e)

# API lấy toàn bộ dữ liệu từ bảng MayTram
@app.route('/MayTram/getAll', methods=['GET'])
def get_all_may_tram():
    cursor = con.cursor()
    cursor.execute("""
        SELECT MaMay, TenMay, TrangThai, GiaTheoGio, GhiChu
        FROM MayTram
    """)
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "MaMay": row.MaMay,
            "TenMay": row.TenMay,
            "TrangThai": row.TrangThai,
            "GiaTheoGio": float(row.GiaTheoGio),
            "GhiChu": row.GhiChu or ""
        })

    return jsonify(result)

# API lấy thông tin tài khoản Admin
@app.route('/TaiKhoanAdmin/login', methods=['POST'])
def login_admin():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cursor = con.cursor()
    cursor.execute("""
        SELECT MaAdmin, HoTen, TenDangNhap, VaiTro
        FROM TaiKhoanAdmin
        WHERE TenDangNhap = ? AND MatKhau = ?
    """, (username, password))
    
    user = cursor.fetchone()

    if user:
        return jsonify({
            "status": "success",
            "MaAdmin": user.MaAdmin,
            "HoTen": user.HoTen,
            "TenDangNhap": user.TenDangNhap,
            "VaiTro": user.VaiTro
        })
    else:
        return jsonify({"status": "fail", "message": "Sai tài khoản hoặc mật khẩu"}), 401


# API lấy toàn bộ tài khoản thành viên
@app.route('/TaiKhoanThanhVien/register', methods=['POST'])
def register_taikhoan_thanthvien():
    data = request.json
    hoten = data.get('HoTen')
    sodienthoai = data.get('SoDienThoai')
    tendangnhap = data.get('TenDangNhap')
    matkhau = data.get('MatKhau')

    if not all([hoten, sodienthoai, tendangnhap, matkhau]):
        return jsonify({"status": "fail", "message": "Thiếu thông tin đăng ký"}), 400

    cursor = con.cursor()
    cursor.execute("SELECT 1 FROM TaiKhoanThanhVien WHERE TenDangNhap = ?", (tendangnhap,))
    if cursor.fetchone():
        return jsonify({"status": "fail", "message": "Tên đăng nhập đã tồn tại"}), 400

    # ❌ Không mã hóa mật khẩu
    cursor.execute("""
        INSERT INTO TaiKhoanThanhVien (HoTen, SoDienThoai, TenDangNhap, MatKhau)
        VALUES (?, ?, ?, ?)
    """, (hoten, sodienthoai, tendangnhap, matkhau))
    con.commit()

    return jsonify({"status": "success", "message": "Đăng ký thành công"})



# API đăng nhập tài khoản thành viên
@app.route('/TaiKhoanThanhVien/login', methods=['POST'])
def login_taikhoan_thanthvien():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cursor = con.cursor()
    cursor.execute("""
        SELECT MaTaiKhoan, HoTen, TenDangNhap, MatKhau, SoDu
        FROM TaiKhoanThanhVien
        WHERE TenDangNhap = ?
    """, (username,))

    user = cursor.fetchone()
    if user and user.MatKhau == password:
        return jsonify({
            "status": "success",
            "MaTaiKhoan": user.MaTaiKhoan,
            "HoTen": user.HoTen,
            "TenDangNhap": user.TenDangNhap,
            "SoDu": float(user.SoDu)
        })
    else:
        return jsonify({"status": "fail", "message": "Sai tên đăng nhập hoặc mật khẩu"}), 401

@app.route('/PhienChoi/batdau', methods=['POST'])
def bat_dau_phien_choi():
    data = request.json
    ma_may = data.get('MaMay')
    ma_taikhoan = data.get('MaTaiKhoan')

    if not all([ma_may, ma_taikhoan]):
        return jsonify({"status": "fail", "message": "Thiếu thông tin bắt đầu phiên chơi"}), 400

    gio_bat_dau = datetime.now()

    cursor = con.cursor()
    cursor.execute("""
        INSERT INTO PhienChoi (MaMay, MaTaiKhoan, GioBatDau)
        VALUES (?, ?, ?)
    """, (ma_may, ma_taikhoan, gio_bat_dau))
    con.commit()

    return jsonify({"status": "success", "message": "Phiên chơi đã bắt đầu"})


@app.route('/PhienChoi/ketthuc', methods=['POST'])
def ket_thuc_phien_choi():
    data = request.json
    try:
        ma_may = int(data.get('MaMay', 0))
        ma_taikhoan = int(data.get('MaTaiKhoan', 0))
    except (TypeError, ValueError):
        return jsonify({"status": "fail", "message": "Sai định dạng thông tin"}), 400

    if not all([ma_may, ma_taikhoan]):
        return jsonify({"status": "fail", "message": "Thiếu thông tin kết thúc phiên chơi"}), 400

    gio_ket_thuc = datetime.now()
    cursor = con.cursor()

    # Lấy phiên chơi chưa kết thúc
    cursor.execute("""
        SELECT TOP 1 MaPhien, GioBatDau
        FROM PhienChoi
        WHERE MaMay = ? AND MaTaiKhoan = ? AND GioKetThuc IS NULL
        ORDER BY GioBatDau DESC
    """, (ma_may, ma_taikhoan))

    phien = cursor.fetchone()
    if not phien:
        return jsonify({"status": "fail", "message": "Không tìm thấy phiên chơi đang hoạt động"}), 404

    ma_phien, gio_bat_dau = phien
    so_phut = (gio_ket_thuc - gio_bat_dau).total_seconds() / 60

    # Lấy giá theo giờ của máy
    cursor.execute("SELECT GiaTheoGio FROM MayTram WHERE MaMay = ?", (ma_may,))
    may = cursor.fetchone()
    if not may:
        return jsonify({"status": "fail", "message": "Không tìm thấy máy"}), 404

    gia_theo_gio = float(may[0])
    tong_tien = round((gia_theo_gio / 60) * so_phut, 2)

    # Trừ tiền trong tài khoản
    cursor.execute("UPDATE TaiKhoanThanhVien SET SoDu = SoDu - ? WHERE MaTaiKhoan = ?", (tong_tien, ma_taikhoan))

    # Cập nhật kết thúc phiên
    cursor.execute("""
        UPDATE PhienChoi
        SET GioKetThuc = ?, TongTien = ?
        WHERE MaPhien = ?
    """, (gio_ket_thuc, tong_tien, ma_phien))

    con.commit()

    return jsonify({"status": "success", "message": "Kết thúc phiên chơi", "TongTien": tong_tien})


# nạp tiền
@app.route('/TaiKhoanThanhVien/napTien', methods=['POST'])
def nap_tien():
    data = request.json
    ma_taikhoan = data.get('MaTaiKhoan')
    so_tien_nap = data.get('SoTienNap')

    if not ma_taikhoan or not so_tien_nap or so_tien_nap <= 0:
        return jsonify({"status": "fail", "message": "Thông tin nạp tiền không hợp lệ"}), 400

    cursor = con.cursor()

    # Kiểm tra tài khoản tồn tại
    cursor.execute("SELECT SoDu FROM TaiKhoanThanhVien WHERE MaTaiKhoan = ?", (ma_taikhoan,))
    tk = cursor.fetchone()
    if not tk:
        return jsonify({"status": "fail", "message": "Tài khoản không tồn tại"}), 404

    # Cộng số tiền nạp vào số dư hiện tại
    so_du_moi = tk.SoDu + so_tien_nap

    # Cập nhật số dư
    cursor.execute("UPDATE TaiKhoanThanhVien SET SoDu = ? WHERE MaTaiKhoan = ?", (so_du_moi, ma_taikhoan))
    con.commit()

    return jsonify({"status": "success", "SoDuMoi": so_du_moi})

# app run
if __name__ == '__main__':
    if con:
        app.run(debug=True)
    else:
        print("❌ Không chạy Flask do kết nối SQL thất bại.")
