import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_credentials():
    email_from = os.getenv('EMAIL_FROM', '')
    email_password = os.getenv('EMAIL_PASSWORD', '')
    
    logger.info(f"Email: {email_from}")
    logger.info(f"Password length: {len(email_password)} characters")
    logger.info(f"Password (first 4 chars): {email_password[:4]}...")
    logger.info(f"Password (last 4 chars): ...{email_password[-4:]}")
    
    # Verificar que no haya espacios
    if ' ' in email_password:
        logger.error("ERROR: Password contains spaces! Remove all spaces from the app password")
        return False
    
    # Verificar longitud típica de contraseña de aplicación (16 caracteres)
    if len(email_password) != 16:
        logger.warning(f"WARNING: App password should be 16 characters, yours is {len(email_password)}")
    
    return True

if __name__ == "__main__":
    if verify_credentials():
        logger.info("Credentials format looks correct. Try the email test again.")
    else:
        logger.error("Fix the credentials and try again.")