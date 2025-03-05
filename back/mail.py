import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from typing import Dict


class EmailVerifier:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        """
        初始化郵件驗證系統
       
        參數:
        smtp_server: SMTP服務器地址（例如：'smtp.gmail.com'）
        smtp_port: SMTP服務器端口（例如：587）
        sender_email: 發送者郵箱
        sender_password: 發送者郵箱密碼或應用專用密碼
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.verification_codes: Dict[str, tuple] = {}  # 存儲驗證碼和過期時間
       
    def generate_verification_code(self, length: int = 6) -> str:
        """生成指定長度的隨機驗證碼"""
        return ''.join(random.choices(string.digits, k=length))
   
    def send_verification_email(self, to_email: str) -> tuple[bool, str]:
        """
        發送驗證郵件
       
        參數:
        to_email: 接收驗證碼的郵箱地址
       
        返回:
        (bool, str): (是否成功發送, 信息)
        """
        try:
            # 生成驗證碼
            verification_code = self.generate_verification_code()
            expiration_time = time.time() + 300  # 5分鐘後過期
           
            # 創建郵件內容
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = to_email
            message["Subject"] = "郵箱驗證碼"
           
            # 郵件正文
            body = f"""
            您好！
           
            您的驗證碼是：{verification_code}
           
            該驗證碼將在5分鐘內有效。請勿將驗證碼分享給他人。
           
            如果這不是您請求的驗證碼，請忽略此郵件。
            """
           
            message.attach(MIMEText(body, "plain"))
           
            # 連接SMTP服務器並發送郵件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
           
            # 存儲驗證碼和過期時間
            self.verification_codes[to_email] = (verification_code, expiration_time)
           
            return True, "驗證碼已發送"
           
        except Exception as e:
            return False, f"發送失敗: {str(e)}"
   
    def verify_code(self, email: str, code: str) -> tuple[bool, str]:
        """
        驗證用戶輸入的驗證碼
       
        參數:
        email: 用戶郵箱
        code: 用戶輸入的驗證碼
       
        返回:
        (bool, str): (驗證是否成功, 信息)
        """
        if email not in self.verification_codes:
            return False, "未發送驗證碼或驗證碼已過期"
           
        stored_code, expiration_time = self.verification_codes[email]
       
        # 檢查是否過期
        if time.time() > expiration_time:
            del self.verification_codes[email]
            return False, "驗證碼已過期"
           
        # 驗證碼匹配檢查
        if code != stored_code:
            return False, "驗證碼不正確"
           
        # 驗證成功後刪除存儲的驗證碼
        del self.verification_codes[email]
        return True, "驗證成功"





