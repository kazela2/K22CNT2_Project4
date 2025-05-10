CREATE DATABASE QL_QuanInternetGaming
USE QL_QuanInternetGaming

CREATE TABLE MayTram (
    MaMay INT PRIMARY KEY IDENTITY(1,1),
    TenMay NVARCHAR(50),
    TrangThai NVARCHAR(20) CHECK (TrangThai IN ('Trống', 'Đang chơi', 'Bảo trì')),
    GhiChu NVARCHAR(255)
);

CREATE TABLE NhanVien (
    MaNV INT PRIMARY KEY IDENTITY(1,1),
    HoTen NVARCHAR(100),
    VaiTro NVARCHAR(20) CHECK (VaiTro IN ('NhanVien', 'QuanLy'))
);

CREATE TABLE KhachHang (
    MaKH INT PRIMARY KEY IDENTITY(1,1),
    HoTen NVARCHAR(100),
    LoaiKH NVARCHAR(20) CHECK (LoaiKH IN ('VangLai', 'ThanhVien')),
    SoDienThoai NVARCHAR(20),
    DiaChi NVARCHAR(255),
    SoDu DECIMAL(18,2) DEFAULT 0
);

CREATE TABLE TaiKhoanThanhVien (
    MaTaiKhoan INT PRIMARY KEY IDENTITY(1,1),
    MaKH INT FOREIGN KEY REFERENCES KhachHang(MaKH),
    TenDangNhap NVARCHAR(50) UNIQUE,
    MatKhau NVARCHAR(100),
    SoDu DECIMAL(18,2) DEFAULT 0
);

CREATE TABLE PhienChoi (
    MaPhien INT PRIMARY KEY IDENTITY(1,1),
    MaMay INT FOREIGN KEY REFERENCES MayTram(MaMay),
    MaKH INT FOREIGN KEY REFERENCES KhachHang(MaKH),
    GioBatDau DATETIME,
    GioKetThuc DATETIME,
    TongTien DECIMAL(18,2)
);


CREATE TABLE SanPhamDichVu (
    MaSP INT PRIMARY KEY IDENTITY(1,1),
    TenSP NVARCHAR(100),
    DonGia DECIMAL(18,2),
    SoLuongTon INT
);

CREATE TABLE HoaDonDichVu (
    MaHD INT PRIMARY KEY IDENTITY(1,1),
    MaPhien INT FOREIGN KEY REFERENCES PhienChoi(MaPhien),
    NgayLap DATETIME DEFAULT GETDATE(),
    TongTien DECIMAL(18,2)
);

CREATE TABLE ChiTietHoaDonDichVu (
    MaHD INT FOREIGN KEY REFERENCES HoaDonDichVu(MaHD),
    MaSP INT FOREIGN KEY REFERENCES SanPhamDichVu(MaSP),
    SoLuong INT,
    DonGia DECIMAL(18,2),
    ThanhTien AS (SoLuong * DonGia) PERSISTED,
    PRIMARY KEY (MaHD, MaSP)
);


CREATE TABLE LichSuNapTien (
    MaNap INT PRIMARY KEY IDENTITY(1,1),
    MaKH INT FOREIGN KEY REFERENCES KhachHang(MaKH),
    SoTien DECIMAL(18,2),
    NgayNap DATETIME DEFAULT GETDATE()
);

CREATE TABLE LichSuDangNhap (
    MaNV INT FOREIGN KEY REFERENCES NhanVien(MaNV),
    ThoiGianDangNhap DATETIME,
    ThoiGianDangXuat DATETIME
);

CREATE TABLE CauHinhGiaTien (
    MaGia INT PRIMARY KEY IDENTITY(1,1),
    GiaTheoGio DECIMAL(18,2),
    MoTa NVARCHAR(255)
);

CREATE TABLE BaoCaoDoanhThu (
    Ngay DATE PRIMARY KEY,
    TongDoanhThu DECIMAL(18,2),
    TongGioChoi INT,
    SPBanChayNhat NVARCHAR(100)
);

INSERT INTO MayTram (TenMay, TrangThai, GhiChu) VALUES
(N'Máy 01', N'Trống', N'Phòng máy lạnh'),
(N'Máy 02', N'Bảo trì', N'Lỗi màn hình'),
(N'Máy 03', N'Trống', N'')

INSERT INTO NhanVien (HoTen, VaiTro) VALUES
(N'Nguyễn Văn A', N'QuanLy'),
(N'Trần Thị B', N'NhanVien')

INSERT INTO KhachHang (HoTen, LoaiKH, SoDienThoai, DiaChi, SoDu) VALUES
(N'Khách Vãng Lai 1', N'VangLai', NULL, NULL, 0),
(N'Nguyễn Thành Viên', N'ThanhVien', '0912345678', N'Hà Nội', 100000)

INSERT INTO TaiKhoanThanhVien (MaKH, TenDangNhap, MatKhau, SoDu) VALUES
(2, 'nguyen_tv', 'matkhau123', 100000)

INSERT INTO PhienChoi (MaMay, MaKH, GioBatDau, GioKetThuc, TongTien) VALUES
(1, 2, '2025-05-09 08:00', '2025-05-09 09:30', 7500)

INSERT INTO SanPhamDichVu (TenSP, DonGia, SoLuongTon) VALUES
(N'Nước suối', 10000, 50),
(N'Mì tôm trứng', 15000, 30),
(N'Sting', 12000, 40)

INSERT INTO HoaDonDichVu (MaPhien, TongTien) VALUES
(1, 27000)

INSERT INTO ChiTietHoaDonDichVu (MaHD, MaSP, SoLuong, DonGia) VALUES
(1, 1, 1, 10000),
(1, 2, 1, 15000) 

INSERT INTO LichSuNapTien (MaKH, SoTien) VALUES
(2, 100000)

INSERT INTO LichSuDangNhap (MaNV, ThoiGianDangNhap, ThoiGianDangXuat) VALUES
(1, '2025-05-09 08:00', '2025-05-09 17:00')

INSERT INTO CauHinhGiaTien (GiaTheoGio, MoTa) VALUES
(5000, N'Giá bình thường'),
(3000, N'Khuyến mãi giờ vàng (8h-10h)')

INSERT INTO BaoCaoDoanhThu (Ngay, TongDoanhThu, TongGioChoi, SPBanChayNhat) VALUES
('2025-05-09', 345000, 18, N'Nước suối')
