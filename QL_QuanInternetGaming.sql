CREATE DATABASE QL_QuanInternetGaming
USE QL_QuanInternetGaming

CREATE TABLE MayTram (
    MaMay INT PRIMARY KEY IDENTITY(1,1),
    TenMay NVARCHAR(50),
    TrangThai NVARCHAR(20) CHECK (TrangThai IN (N'Trống', N'Đang chơi', N'Bảo trì')),
    GiaTheoGio DECIMAL(18,2) DEFAULT 10000,
    GhiChu NVARCHAR(255)
);


CREATE TABLE TaiKhoanAdmin (
    MaAdmin INT PRIMARY KEY IDENTITY(1,1),
    HoTen NVARCHAR(100),
    TenDangNhap NVARCHAR(50) UNIQUE,
    MatKhau NVARCHAR(100),
    VaiTro NVARCHAR(20) DEFAULT 'Admin' CHECK (VaiTro = 'Admin')
);

CREATE TABLE NhanVien (
    MaNV INT PRIMARY KEY IDENTITY(1,1),
    HoTen NVARCHAR(100),
    VaiTro NVARCHAR(20) CHECK (VaiTro IN ('NhanVien', 'QuanLy'))
);

CREATE TABLE TaiKhoanThanhVien (
    MaTaiKhoan INT PRIMARY KEY IDENTITY(1,1),
	HoTen NVARCHAR(100),
    SoDienThoai NVARCHAR(20),
    TenDangNhap NVARCHAR(50) UNIQUE,
    MatKhau NVARCHAR(100),
    SoDu DECIMAL(18,2) DEFAULT 0,
    NgayTao DATETIME DEFAULT GETDATE()
);

CREATE TABLE PhienChoi (
    MaPhien INT PRIMARY KEY IDENTITY(1,1),
    MaMay INT FOREIGN KEY REFERENCES MayTram(MaMay),
	MaTaiKhoan INT FOREIGN KEY REFERENCES TaiKhoanThanhVien(MaTaiKhoan),
    GioBatDau DATETIME,
    GioKetThuc DATETIME,
    TongTien DECIMAL(18,2)
);


CREATE TABLE SanPhamDichVu (
    MaSP INT PRIMARY KEY IDENTITY(1,1),
    TenSP NVARCHAR(100),
	LoaiSP NVARCHAR(50),
    DonGia DECIMAL(18,2)
);

CREATE TABLE HoaDon (
    MaHD INT PRIMARY KEY IDENTITY(1,1),
    NgayLap DATETIME DEFAULT GETDATE(),
    TongTien DECIMAL(18,2)
);

CREATE TABLE ChiTietHoaDon (
    MaHD INT NOT NULL,
    MaSP INT NOT NULL,
    SoLuong INT NOT NULL CHECK (SoLuong > 0),
    DonGia DECIMAL(18,2) NOT NULL CHECK (DonGia >= 0),
    ThanhTien AS (SoLuong * DonGia) PERSISTED,
    PRIMARY KEY (MaHD, MaSP),
    CONSTRAINT FK_ChiTietHoaDon_HoaDon FOREIGN KEY (MaHD) REFERENCES HoaDon(MaHD),
    CONSTRAINT FK_ChiTietHoaDon_SanPhamDichVu FOREIGN KEY (MaSP) REFERENCES SanPhamDichVu(MaSP)
);
select * from HoaDon
select * from ChiTietHoaDon
select * from TaiKhoanThanhVien
drop table HoaDon
drop table ChiTietHoaDon


CREATE TABLE BaoCaoDoanhThu (
    Ngay DATE PRIMARY KEY,
    TongDoanhThu DECIMAL(18,2),
    TongGioChoi INT,
    SPBanChayNhat NVARCHAR(100)
);




-- MayTram
INSERT INTO MayTram (TenMay, TrangThai, GiaTheoGio, GhiChu) VALUES
(N'Máy 1', N'Trống', 10000, NULL),
(N'Máy 2', N'Đang chơi', 12000, N'Khách chơi game LOL'),
(N'Máy 3', N'Bảo trì', 10000, N'Lỗi phần mềm');

-- NhanVien
INSERT INTO NhanVien (HoTen, VaiTro) VALUES
(N'Ngô Hoàng Minh', N'QuanLy'),
(N'Lê Hoàng Long', N'QuanLy'),
(N'Lê Trần Khánh Duy', N'QuanLy'),
(N'Trần Minh Nam', N'NhanVien');

-- TaiKhoanThanhVien
INSERT INTO TaiKhoanThanhVien (HoTen, SoDienThoai, TenDangNhap, MatKhau, SoDu) VALUES
(N'Ngô Minh Khoa', '0909123456', 'khoa123', '123', 50000),
(N'Phạm Lan Hương', '0909345678', 'huongpl', '123', 75000),
(N'Trịnh Công Sơn', '0909988776', 'sontrinh', '123', 100000);

-- PhienChoi
INSERT INTO PhienChoi (MaMay, MaTaiKhoan, GioBatDau, GioKetThuc, TongTien) VALUES
(1, 1, '2025-05-17 08:00', '2025-05-17 09:00', 10000),
(2, 2, '2025-05-17 09:15', '2025-05-17 10:45', 18000),
(1, 3, '2025-05-17 11:00', NULL, NULL);

-- SanPhamDichVu
INSERT INTO SanPhamDichVu (TenSP, LoaiSP, DonGia) VALUES
(N'Nước suối', N'Đồ uống', 10000),
(N'Mì ly', N'Đồ ăn', 15000),
(N'Cafe đen', N'Đồ uống', 12000),
(N'Trà sữa trân châu', N'Đồ uống', 25000),
(N'Bánh mì chà bông', N'Đồ ăn', 20000),
(N'Nước tăng lực Sting', N'Đồ uống', 15000);

-- HoaDon
INSERT INTO HoaDon (MaPhien, NgayLap, TongTien) VALUES
(1, '2025-05-17', 35000),
(2, '2025-05-17', 12000),
(1, '2025-05-17', 10000);

-- ChiTietHoaDon
INSERT INTO ChiTietHoaDon (MaHD, MaSP, SoLuong, DonGia) VALUES
(1, 1, 1, 10000),
(1, 2, 1, 15000),
(1, 3, 1, 10000),
(2, 3, 1, 12000),
(3, 1, 1, 10000);

-- BaoCaoDoanhThu
INSERT INTO BaoCaoDoanhThu (Ngay, TongDoanhThu, TongGioChoi, SPBanChayNhat) VALUES
('2025-05-15', 50000, 4, N'Nước suối'),
('2025-05-16', 30000, 3, N'Café đen'),
('2025-05-17', 55000, 5, N'Mì ly');
-- TaikhoanAdmin
INSERT INTO TaiKhoanAdmin (HoTen, TenDangNhap, MatKhau) VALUES
(N'Ba Anh Em Nhà Hề', 'admin', '123456');

