import random
import hashlib
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


def generate_otp() -> str:
    """Generate a random 6-digit OTP code."""
    return str(random.randint(100000, 999999))


def hash_otp(code: str) -> str:
    """Hash the OTP before storing in DB — never store plain text."""
    return hashlib.sha256(code.encode()).hexdigest()


def verify_otp_hash(entered_code: str, stored_hash: str) -> bool:
    """Check if entered code matches the stored hash."""
    return hash_otp(entered_code) == stored_hash


def send_sms(phone: str, otp_code: str) -> bool:
    """
    Send OTP via Twilio SMS.
    Returns True if sent successfully, False if failed.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=f"Your verification code is: {otp_code}. Valid for 10 minutes. Do not share this code.",
            from_=TWILIO_PHONE_NUMBER,
            to=f"+91{phone}"   # +91 for India — change prefix for other countries
        )

        print(f"✅ SMS sent to {phone} — SID: {message.sid}")
        return True

    except Exception as e:
        print(f"❌ SMS failed: {str(e)}")
        return False