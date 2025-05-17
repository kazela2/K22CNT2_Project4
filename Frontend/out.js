const loginBtn = document.getElementById("loginBtn");
const logoutBtn = document.getElementById("logoutBtn");
const registerBtn = document.getElementById("registerBtn");

function updateLoginStatus() {
  const admin = JSON.parse(localStorage.getItem("admin"));
  if (admin) {
    loginBtn?.classList.add("d-none");
    registerBtn?.classList.add("d-none");
    logoutBtn?.classList.remove("d-none");
  } else {
    loginBtn?.classList.remove("d-none");
    registerBtn?.classList.remove("d-none");
    logoutBtn?.classList.add("d-none");
  }
}

// Gắn sự kiện đăng xuất nếu tồn tại logoutBtn
logoutBtn?.addEventListener("click", function () {
  localStorage.removeItem("admin");
  updateLoginStatus();
  alert("✅ Đã đăng xuất");
  window.location.reload();
});

window.addEventListener("DOMContentLoaded", updateLoginStatus);

function batDau(maMay) {
    localStorage.setItem('maMayDangChon', maMay);
    window.location.href = 'loginthanhvien.html';
  }

  function ketThuc(maMay) {
    const phienDangChoi = JSON.parse(localStorage.getItem('phienDangChoi'));
  
    if (!phienDangChoi || phienDangChoi.MaMay !== maMay) {
      alert("Không tìm thấy phiên chơi đang hoạt động.");
      return;
    }
  
    const maPhien = phienDangChoi.MaPhien; // giả sử có mã phiên lưu trong localStorage
    const thoiGianKetThuc = new Date().toISOString();
  
    fetch('http://127.0.0.1:5000/PhienChoi/ketthuc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        MaPhien: maPhien,
        MaMay: maMay,
        ThoiGianKetThuc: thoiGianKetThuc
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          alert('Kết thúc phiên chơi thành công!');
          localStorage.removeItem('phienDangChoi');
          location.reload();
        } else {
          alert('Lỗi khi kết thúc phiên chơi: ' + data.message);
        }
      })
      .catch(err => {
        alert('Lỗi kết nối server');
        console.error(err);
      });
  }
  
  
  function napTien(maMay) {
    // Chuyển tới trang nạp tiền (bạn tự tạo)
    localStorage.setItem('maMayDangChon', maMay);
    window.location.href = 'naptiensodu.html';
  }
  