import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_notification():
    try:
        email_from = os.getenv('EMAIL_FROM', '')
        email_password = os.getenv('EMAIL_PASSWORD', '')
        email_to = os.getenv('EMAIL_TO', '')
        
        logger.info(f"Testing email from: {email_from}")
        logger.info(f"Testing email to: {email_to}")
        
        # Crear mensaje de prueba
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = "Test: Balance Alert - Banco Macro"
        
        # Saldo de prueba
        test_balance = 1234567.89
        
        body = f"""
        ¡Prueba de notificación de saldo!
        
        Tu saldo actual es: ${test_balance:,.2f}
        
        Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}
        
        Este es un mensaje de prueba del scraper de Banco Macro.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Enviar email
        logger.info("Connecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        logger.info("Logging in to Gmail...")
        server.login(email_from, email_password)
        
        logger.info("Sending email...")
        server.send_message(msg)
        server.quit()
        
        logger.info("Email sent successfully!")
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        logger.error("Make sure you're using an App Password for Gmail, not your regular password")
        logger.error("Enable 2FA and generate an App Password at: https://myaccount.google.com/apppasswords")

if __name__ == "__main__":
    test_email_notification()