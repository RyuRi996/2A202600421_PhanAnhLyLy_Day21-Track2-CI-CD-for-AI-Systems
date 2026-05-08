# Báo Cáo Thực Hành Lab MLOps

## 1. Lựa Chọn Siêu Tham Số (Hyperparameters)
Trong Bước 1, sau nhiều lần chạy thử nghiệm với MLflow, bộ siêu tham số tốt nhất mang lại chỉ số accuracy và f1_score cao nhất (vượt ngưỡng 0.70) là:
- `n_estimators = 200`: Tăng số lượng cây quyết định giúp mô hình học được nhiều đặc trưng hơn và giảm phương sai (variance).
- `max_depth = 10`: Giới hạn độ sâu của cây ở mức vừa phải để tránh hiện tượng overfitting trên tập huấn luyện (train_phase1.csv).
- `min_samples_split = 2`: Cho phép chia tách các nút nhánh nhỏ để phân loại chi tiết hơn.

## 2. Những Khó Khăn Gặp Phải và Cách Khắc Phục
Trong quá trình triển khai CI/CD và cấu hình máy ảo, em đã gặp một số lỗi và giải quyết như sau:

- **Khó khăn 1: Cấu hình khóa SSH không thành công (`Error: missing server host` / `No such file or directory`)**
  - *Vấn đề:* Em quên tạo khóa SSH và nhập sai zone của máy ảo (tạo ở `asia-southeast1-a` thay vì `us-central1-a` như hướng dẫn). 
  - *Giải pháp:* Dùng lệnh `gcloud compute ssh` để tự động đẩy lại public key lên máy ảo, sau đó trích xuất private key bằng lệnh `cat ~/.ssh/mlops_deploy` và lưu đúng vào GitHub Secrets (`VM_HOST`, `VM_USER`, `VM_SSH_KEY`).

- **Khó khăn 2: Máy ảo không khởi chạy được service (`Unit mlops-serve.service not found`)**
  - *Vấn đề:* Do em chưa thiết lập đầy đủ môi trường trên VM (thiếu thư viện, chưa copy mã nguồn và chưa tạo systemd service).
  - *Giải pháp:* Kết nối SSH vào máy ảo, chạy lệnh `apt install` các thư viện cần thiết, đẩy file `sa-key.json` và `serve.py` lên bằng lệnh `scp` sử dụng đường dẫn tuyệt đối, sau đó tạo file cấu hình `/etc/systemd/system/mlops-serve.service` để service tự động chạy ẩn.

- **Khó khăn 3: Lỗi Health Check Timeout (`Process exited with status 1`)**
  - *Vấn đề:* Github Actions script báo lỗi khi chạy lệnh `curl` kiểm tra sức khỏe máy ảo do máy ảo khởi động quá chậm (tải mô hình từ Google Cloud Storage mất khoảng 6-7 giây).
  - *Giải pháp:* Em đã sửa lại script `.github/workflows/mlops.yml` và tăng thời gian đợi từ `sleep 5` lên `sleep 15`. Sau đó tiến trình Deploy đã hoàn thành 100% màu xanh.
