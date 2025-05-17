
    const loginForm = document.getElementById('loginForm');
    const messageDiv = document.getElementById('message');

    loginForm.addEventListener('submit', function(e) {
      e.preventDefault();

      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;

      fetch('http://127.0.0.1:5000/TaiKhoanThanhVien/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
      })
      .then(res => res.json())
      .then(data => {
        if(data.status === 'success') {
            // Lưu thông tin tài khoản vào localStorage
  localStorage.setItem('taiKhoanThanhVien', JSON.stringify({
    MaTaiKhoan: data.MaTaiKhoan,
    SoDu: data.SoDu
  }));
          const soDu = data.SoDu;
          const maTaiKhoan = data.MaTaiKhoan;
          const maMay = localStorage.getItem('maMayDangChon');

          if(!maMay) {
            messageDiv.textContent = 'Lỗi: không xác định được máy đã chọn.';
            return;
          }

          if(soDu < 1000) { // giả sử 1000 VND là số dư tối thiểu để chơi
            messageDiv.textContent = 'Số dư không đủ để chơi. Vui lòng nạp thêm tiền.';
            return;
          }

          // Gọi API bắt đầu phiên chơi
          fetch('http://127.0.0.1:5000/PhienChoi/batdau', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ MaMay: parseInt(maMay), MaTaiKhoan: maTaiKhoan })
          })
          .then(res2 => res2.json())
          .then(data2 => {
            if (data2.status === 'success') {
              messageDiv.textContent = 'Phiên chơi đã bắt đầu. Chúc bạn chơi vui vẻ!';
          
              // Lưu trạng thái máy trạm đã bắt đầu vào localStorage
              localStorage.setItem('phienDangChoi', JSON.stringify({
                MaMay: parseInt(maMay),
                MaTaiKhoan: maTaiKhoan,
                MaPhien: data2.MaPhien // Lưu thêm MaPhien từ phản hồi của backend
              }));
          
              // Chuyển về maytram.html
              window.location.href = 'maytram.html';
            } else {
              messageDiv.textContent = 'Lỗi khi bắt đầu phiên chơi: ' + data2.message;
            }
          });
          

        } else {
          messageDiv.textContent = 'Đăng nhập thất bại: ' + data.message;
        }
      })
      .catch(err => {
        messageDiv.textContent = 'Lỗi kết nối server';
        console.error(err);
      });
    });

    