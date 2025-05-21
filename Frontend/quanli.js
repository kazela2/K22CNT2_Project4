function dangXuat() {
    // Xóa thông tin admin khỏi localStorage
    localStorage.removeItem("admin");
  
    // Chuyển về trang đăng nhập
    window.location.href = "login.html";
  }
  
  // Kiểm tra nếu không có admin thì chuyển hướng
window.addEventListener("DOMContentLoaded", function () {
    const admin = localStorage.getItem("admin");
    if (!admin) {
      alert("⚠️ Vui lòng đăng nhập trước.");
      window.location.href = "login.html";
    }
  });
  