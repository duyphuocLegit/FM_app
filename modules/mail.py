import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Hàm gửi email tới admin khi chi tiêu mới vượt mức
def send_email_to_admin(admin_email, new_expense, limit, user_id):
    # Thông tin tài khoản gửi email (ví dụ sử dụng Gmail)
    sender_email = "carot000199@gmail.com"
    sender_password = "ewao xhjo qjyd mdyd"

    # Tạo nội dung email
    subject = "Cảnh báo: Chi tiêu vượt mức!"
    body = f"Số tiền chi tiêu mới {new_expense} của user {user_id} đã vượt qua giới hạn {limit}.\n\nVui lòng kiểm tra lại."

    # Tạo email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = admin_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Kết nối đến server SMTP của Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Gửi email
        text = msg.as_string()
        server.sendmail(sender_email, admin_email, text)

        # Đóng kết nối với server
        server.quit()

        print("Email đã được gửi thành công!")
    except Exception as e:
        print(f"Không thể gửi email. Lỗi: {e}")

# Hàm kiểm tra chi tiêu mới và gửi email nếu vượt giới hạn
def check_new_expense(new_expense, user_id):
    if new_expense > 500:
        send_email_to_admin("duyyphuoc2@gmail.com", new_expense, 500, user_id)
    else:
        print("Chi tiêu trong giới hạn.")