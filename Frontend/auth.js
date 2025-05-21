document.addEventListener("DOMContentLoaded", () => {
    const thanhVien = JSON.parse(localStorage.getItem('taiKhoanThanhVien') || '{}');
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const logoutBtn = document.getElementById('logoutBtn');
  
    if (thanhVien.MaTaiKhoan) {
      if (loginBtn) loginBtn.classList.add('d-none');
      if (registerBtn) registerBtn.classList.add('d-none');
      if (logoutBtn) logoutBtn.classList.remove('d-none');
    } else {
      if (loginBtn) loginBtn.classList.remove('d-none');
      if (registerBtn) registerBtn.classList.remove('d-none');
      if (logoutBtn) logoutBtn.classList.add('d-none');
    }
  
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('taiKhoanThanhVien');
        localStorage.removeItem('phienDangChoi');
        location.reload();
      });
    }
  });
  