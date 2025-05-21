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
    cursor = con.cursor()
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

# === DỊCH VỤ & HÓA ĐƠN ===
@app.route('/SanPhamDichVu/getAll', methods=['GET'])
def get_all_sanpham():
    cursor = con.cursor()
    cursor.execute("SELECT MaSP, TenSP, LoaiSP, DonGia FROM SanPhamDichVu")
    rows = cursor.fetchall()
    return jsonify([{
        "MaSP": row.MaSP,
        "TenSP": row.TenSP,
        "LoaiSP": row.LoaiSP,
        "DonGia": float(row.DonGia)
    } for row in rows])


@app.route('/HoaDon/add', methods=['POST'])
def add_hoadon():
    data = request.json
    ngay_lap = datetime.now()
    tong_tien = data.get('TongTien', 0)

    cursor = con.cursor()
    try:
        cursor.execute("""
            INSERT INTO HoaDon (NgayLap, TongTien)
            VALUES (?, ?)
        """, (ngay_lap, tong_tien))
        con.commit()

        # Lấy ID hóa đơn vừa tạo
        cursor.execute("SELECT SCOPE_IDENTITY()")
        ma_hoadon = cursor.fetchone()[0]

        return jsonify({"status": "success", "MaHoaDon": ma_hoadon})
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500


@app.route('/ChiTietHoaDon/add', methods=['POST'])
def add_chitiethoadon():
    data = request.json
    print("Received data:", data)  # Debug xem dữ liệu nhận được

    ma_hoadon = data.get('MaHoaDon')
    ma_sp = data.get('MaSP')
    so_luong = data.get('SoLuong')
    don_gia = data.get('DonGia')

    # Kiểm tra MaHoaDon và MaSP phải có, không None, không chuỗi rỗng
    if not ma_hoadon or not ma_sp:
        return jsonify({"status": "fail", "message": "Thiếu mã hóa đơn hoặc mã sản phẩm"}), 400

    # Kiểm tra so_luong và don_gia có giá trị hợp lệ
    if so_luong is None or don_gia is None:
        return jsonify({"status": "fail", "message": "Thiếu số lượng hoặc đơn giá"}), 400

    try:
        so_luong = int(so_luong)
        don_gia = float(don_gia)
    except:
        return jsonify({"status": "fail", "message": "Số lượng hoặc đơn giá không hợp lệ"}), 400

    thanh_tien = so_luong * don_gia

    cursor = con.cursor()
    try:
        cursor.execute("""
            INSERT INTO ChiTietHoaDon (MaHoaDon, MaSP, SoLuong, DonGia, ThanhTien)
            VALUES (?, ?, ?, ?, ?)
        """, (ma_hoadon, ma_sp, so_luong, don_gia, thanh_tien))
        con.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500


@app.route('/TaiKhoanThanhVien/truSoDu', methods=['POST'])
def tru_so_du():
    data = request.json
    ma_taikhoan = data.get('MaTaiKhoan')
    so_tien = data.get('SoTien')

    if not ma_taikhoan or so_tien is None:
        return jsonify({"status": "fail", "message": "Thiếu thông tin"}), 400

    cursor = con.cursor()
    try:
        # Kiểm tra số dư hiện tại
        cursor.execute("SELECT SoDu FROM TaiKhoanThanhVien WHERE MaTaiKhoan = ?", (ma_taikhoan,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"status": "fail", "message": "Tài khoản không tồn tại"}), 404

        so_du_hien_tai = row[0]
        if so_du_hien_tai < so_tien:
            return jsonify({"status": "fail", "message": "Số dư không đủ"}), 400

        # Trừ số dư
        cursor.execute("UPDATE TaiKhoanThanhVien SET SoDu = SoDu - ? WHERE MaTaiKhoan = ?", (so_tien, ma_taikhoan))
        con.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route('/ChiTietHoaDon/<int:ma_hoadon>', methods=['GET'])
def get_chitiethoadon(ma_hoadon):
    cursor = con.cursor()
    cursor.execute("""
        SELECT MaSP, SoLuong, DonGia, ThanhTien
        FROM ChiTietHoaDon
        WHERE MaHoaDon = ?
    """, (ma_hoadon,))
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "MaSP": row.MaSP,
            "SoLuong": row.SoLuong,
            "DonGia": float(row.DonGia),
            "ThanhTien": float(row.ThanhTien)
        })

    return jsonify(result)

@app.route('/NhanVien/getAll', methods=['GET'])
def get_all_nhanvien():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT MaNV, HoTen, VaiTro FROM NhanVien")
        rows = cursor.fetchall()

        nhanviens = []
        for row in rows:
            nhanviens.append({
                "MaNV": row[0],
                "HoTen": row[1],
                "VaiTro": row[2]
            })
        return jsonify(nhanviens)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/NhanVien/add', methods=['POST'])
def add_nhanvien():
    try:
        data = request.json
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO NhanVien (HoTen, VaiTro) VALUES (?, ?)",
            data['HoTen'], data['VaiTro']
        )
        con.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/NhanVien/delete/<int:maNV>', methods=['DELETE'])
def delete_nhanvien(maNV):
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM NhanVien WHERE MaNV = ?", maNV)
        con.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



# ✅ API: Lấy tất cả báo cáo doanh thu
@app.route('/BaoCaoDoanhThu/getAll', methods=['GET'])
def get_baocao():
    try:
        cursor.execute("SELECT Ngay, TongDoanhThu, TongGioChoi, SPBanChayNhat FROM BaoCaoDoanhThu")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "Ngay": r.Ngay.strftime('%Y-%m-%d'),
                "TongDoanhThu": float(r.TongDoanhThu),
                "TongGioChoi": r.TongGioChoi,
                "SPBanChayNhat": r.SPBanChayNhat
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ✅ API: Thêm báo cáo doanh thu mới
@app.route('/BaoCaoDoanhThu/add', methods=['POST'])
def add_baocao():
    try:
        data = request.get_json()
        ngay = data['Ngay']
        doanhthu = data['TongDoanhThu']
        giochoi = data['TongGioChoi']
        spbanchay = data['SPBanChayNhat']

        cursor.execute("""
            INSERT INTO BaoCaoDoanhThu (Ngay, TongDoanhThu, TongGioChoi, SPBanChayNhat)
            VALUES (?, ?, ?, ?)
        """, (ngay, doanhthu, giochoi, spbanchay))
        con.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# === CHẠY APP ===
if __name__ == '__main__':
    if con:
        app.run(debug=True)
    else:
        print("❌ Không chạy Flask do kết nối SQL thất bại.")
