import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from typing import Dict
import json
import os

class EmailVerifier:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        """
        初始化郵件驗證系統
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.verification_codes: Dict[str, tuple] = {}
        self.storage_file = "verification_codes.json"
        self._load_verification_codes()  # 載入已存儲的驗證碼
    
    def _load_verification_codes(self):
        """從文件載入驗證碼"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    stored_data = json.load(f)
                    # 轉換時間戳和驗證碼為元組
                    self.verification_codes = {
                        email: (code, float(exp_time)) 
                        for email, (code, exp_time) in stored_data.items()
                    }
                    # 清理過期的驗證碼
                    self._cleanup_expired_codes()
        except Exception as e:
            print(f"載入驗證碼時出錯: {e}")
            self.verification_codes = {}

    def _save_verification_codes(self):
        """將驗證碼保存到文件"""
        try:
            # 先清理過期的驗證碼
            self._cleanup_expired_codes()
            # 將驗證碼資料轉換為可序列化的格式
            data_to_save = {
                email: [code, str(exp_time)]
                for email, (code, exp_time) in self.verification_codes.items()
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data_to_save, f)
        except Exception as e:
            print(f"保存驗證碼時出錯: {e}")

    def _cleanup_expired_codes(self):
        """清理過期的驗證碼"""
        current_time = time.time()
        expired_emails = [
            email for email, (_, exp_time) 
            in self.verification_codes.items() 
            if current_time > exp_time
        ]
        for email in expired_emails:
            del self.verification_codes[email]

    def generate_verification_code(self, length: int = 6) -> str:
        """生成指定長度的隨機驗證碼"""
        return ''.join(random.choices(string.digits, k=length))
   
    def send_verification_email(self, to_email: str) -> tuple[bool, str]:
        """發送驗證郵件"""
        try:
            verification_code = self.generate_verification_code()
            expiration_time = time.time() + 600  # 10分鐘後過期
            
            # 創建郵件內容
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = to_email
            message["Subject"] = "您的驗證碼"
            
            body = f"""
            您好！
            
            您的驗證碼是：{verification_code}
            
            該驗證碼將在10分鐘內有效。請勿將驗證碼分享給他人。
            
            如果這不是您請求的驗證碼，請忽略此郵件。
            """
            
            message.attach(MIMEText(body, "plain"))
            
            # 發送郵件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            # 儲存驗證碼和過期時間
            self.verification_codes[to_email] = (verification_code, expiration_time)
            self._save_verification_codes()  # 保存到文件
            
            return True, "驗證碼已發送"
            
        except Exception as e:
            return False, f"發送失敗: {str(e)}"

    def verify_code(self, email: str, code: str) -> tuple[bool, str]:
        """驗證用戶輸入的驗證碼"""
        self._load_verification_codes()  # 重新載入驗證碼確保最新
        
        if email not in self.verification_codes:
            return False, "未發送驗證碼或驗證碼已過期"
            
        stored_code, expiration_time = self.verification_codes[email]
        
        if time.time() > expiration_time:
            del self.verification_codes[email]
            self._save_verification_codes()
            return False, "驗證碼已過期"
            
        if code != stored_code:
            return False, "驗證碼不正確"
            
        # 驗證成功後刪除驗證碼
        del self.verification_codes[email]
        self._save_verification_codes()
        return True, "驗證成功"





