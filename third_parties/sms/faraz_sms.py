import requests
import os
from django.core.exceptions import ValidationError



class SMSHandler:
    BASE_URL = "https://edge.ippanel.com/v1"
    
    def __init__(self):
        self.api_key = os.getenv("FARAZ_SMS_API_KEY", None)
        self.sender_number = os.getenv("FARAZ_SMS_SENDER_NUMBER", None)
        self.login_otp_pattern_code = os.getenv("FARAZ_SMS_LOGIN_OTP_PATTERN_CODE", None)
        self.phone_book_id = os.getenv("FARAZ_SMS_PHONE_BOOK_ID", None)
        self.validate_env_config() 
            
    def validate_env_config(self):
        required_fields = ("api_key", "sender_number", "login_otp_pattern_code", "phone_book_id")
        for field in required_fields:
            if getattr(self, field) is None:
                raise EnvironmentError(f"Faraz sms {field} is not properly set.")
    
    def get_headers(self):
        return {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        
    def send_request(self, method, url, headers, body):
        response = requests.request(
            url=url,
            method=method,
            headers=headers,
            json=body,
        )
        if not (200 <= response.status_code <300):
            raise ValidationError(
                f"Failed to send request to faraz sms, status: {response.status_code},"
                f"body: {response.json()}"
            )
            
        return response.json()
    
    def send_sms_with_pattern(self, recipient_phone_number, otp_code):
        # TODO: validate phone_number
        # TODO: add name to phone book
        url = f"{self.BASE_URL}/api/send"
        headers = self.get_headers()
        body = {
            "sending_type": "pattern",
            "from_number": self.sender_number,
            "code": self.login_otp_pattern_code,
            "recipients": [recipient_phone_number],
            "params": {"verification-code": otp_code,},
            "phonebook": {
                "id": self.phone_book_id,
                "name": "علیرضا",
                "pre": "mr",
                "email": "saeed@gmail.com",
                "options": {"456": "1970/01/01"}
            }
        }
        return self.send_request(
            method="POST",
            url=url,
            headers=headers,
            body=body,
        )
        