document.addEventListener('DOMContentLoaded', () => {
    renderOrderSummary();
  
    const form = document.getElementById('loginForm');
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
  
      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value;
  
      if (!username || !password) {
        showMessage('Vui lòng nhập đầy đủ thông tin', 'error');
        return;
      }
  
      try {
        // 1. Đăng nhập lấy MaTaiKhoan, SoDu
        const loginRes = await fetch('http://localhost:5000/TaiKhoanThanhVien/login', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ username, password })
        });
  
        const loginData = await loginRes.json();
        if (!loginRes.ok || loginData.status !== 'success') {
          showMessage(loginData.message || 'Đăng nhập thất bại', 'error');
          return;
        }
  
        const maTaiKhoan = loginData.MaTaiKhoan;
        let soDu = loginData.SoDu || 0;
  
        // 2. Lấy giỏ hàng
        const cart = JSON.parse(sessionStorage.getItem('cart')) || [];
        if (cart.length === 0) {
          showMessage('Bạn chưa chọn sản phẩm nào để thanh toán.', 'info');
          return;
        }
  
        // 3. Tính tổng tiền
        const tongTien = cart.reduce((sum, sp) => sum + sp.DonGia * sp.SoLuong, 0);
  
        if (soDu < tongTien) {
          showMessage('Số dư tài khoản không đủ để thanh toán.', 'error');
          return;
        }
  
        // 4. Tạo hóa đơn
        const hoaDonRes = await fetch('http://localhost:5000/HoaDon/add', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ TongTien: tongTien })  // Backend ko cần MaTaiKhoan nữa nhé
        });
  
        const hoaDonData = await hoaDonRes.json();
        if (!hoaDonRes.ok || hoaDonData.status !== 'success') {
          showMessage('Lỗi tạo hóa đơn: ' + (hoaDonData.message || ''), 'error');
          return;
        }
  
        const maHoaDon = hoaDonData.MaHoaDon;
  
        // 5. Lưu chi tiết hóa đơn: kiểm tra kỹ dữ liệu mỗi sp trước khi gửi
        for (const sp of cart) {
          if (!sp.MaSP || !sp.SoLuong || !sp.DonGia) {
            showMessage(`Sản phẩm ${sp.TenSP || ''} thiếu thông tin chi tiết, không thể thanh toán`, 'error');
            return;
          }
  
          const chiTietRes = await fetch('http://localhost:5000/ChiTietHoaDon/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
              MaHoaDon: maHoaDon,
              MaSP: sp.MaSP,
              SoLuong: sp.SoLuong,
              DonGia: sp.DonGia
            })
          });
  
          const chiTietData = await chiTietRes.json();
          if (!chiTietRes.ok || chiTietData.status !== 'success') {
            showMessage(`Lỗi lưu sản phẩm ${sp.TenSP}: ` + (chiTietData.message || ''), 'error');
            return;
          }
        }
  
        // 6. Trừ số dư tài khoản
        const truSoDuRes = await fetch('http://localhost:5000/TaiKhoanThanhVien/truSoDu', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ MaTaiKhoan: maTaiKhoan, SoTien: tongTien })
        });
  
        const truSoDuData = await truSoDuRes.json();
        if (!truSoDuRes.ok || truSoDuData.status !== 'success') {
          showMessage('Lỗi trừ số dư: ' + (truSoDuData.message || ''), 'error');
          return;
        }
  
        // 7. Xóa giỏ hàng, cập nhật UI
        sessionStorage.removeItem('cart');
        renderOrderSummary();
  
        showMessage(`Thanh toán thành công. Mã hóa đơn: ${maHoaDon}`, 'success');
      } catch (err) {
        console.error(err);
        showMessage('Lỗi kết nối hoặc xử lý.', 'error');
      }
    });
  });
  
  function renderOrderSummary() {
    const orderDetailsDiv = document.getElementById('orderDetails');
  
    const cart = JSON.parse(sessionStorage.getItem('cart')) || [];
  
    if (cart.length === 0) {
      orderDetailsDiv.innerHTML = '<p>Chưa có sản phẩm nào trong đơn hàng.</p>';
      return;
    }
  
    let html = `<table class="table table-bordered">
      <thead>
        <tr><th>Tên</th><th>SL</th><th>Giá</th><th>Thành tiền</th></tr>
      </thead><tbody>`;
  
    let total = 0;
    cart.forEach(item => {
      const thanhTien = item.DonGia * item.SoLuong;
      total += thanhTien;
      html += `<tr>
        <td>${item.TenSP}</td>
        <td>${item.SoLuong}</td>
        <td>${item.DonGia.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' })}</td>
        <td>${thanhTien.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' })}</td>
      </tr>`;
    });
  
    html += `<tfoot>
      <tr>
        <th colspan="3" class="text-end">Tổng cộng:</th>
        <th>${total.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' })}</th>
      </tr>
    </tfoot></table>`;
  
    orderDetailsDiv.innerHTML = html;
  }
  
  function showMessage(msg, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = msg;
    messageDiv.style.color = type === 'success' ? 'green' : (type === 'error' ? 'red' : 'blue');
  }
  