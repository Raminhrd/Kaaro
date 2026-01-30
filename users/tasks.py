from celery import shared_task
import logging
from third_parties.sms.faraz_sms import SMSHandler

logger = logging.getLogger(__name__)

@shared_task
def send_otp_sms(phone_number, otp_code):
    try:
        sms_hanler = SMSHandler()
        sms_hanler.send_sms_with_pattern(
            recipient_phone_number=phone_number, 
            otp_code=otp_code
        )
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")