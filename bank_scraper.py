import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BankScraper:
    def __init__(self):
        self.driver = None
        self.bank_url = os.getenv('BANK_URL', '')
        self.username = os.getenv('BANK_USERNAME', '')
        self.password = os.getenv('BANK_PASSWORD', '')
        self.threshold_amount = float(os.getenv('THRESHOLD_AMOUNT', '1000'))
        self.email_from = os.getenv('EMAIL_FROM', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.email_to = os.getenv('EMAIL_TO', '')
        
    def setup_driver(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {str(e)}")
            raise
        
    def login(self):
        try:
            self.driver.get(self.bank_url)
            
            # Paso 1: Ingresar usuario
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "textField1"))
            )
            username_field.send_keys(self.username)
            
            # Hacer click en el botón de usuario
            user_button = self.driver.find_element(By.ID, "processCustomerLogin")
            user_button.click()
            
            # Paso 2: Esperar a que aparezca el campo de contraseña
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "login_textField1"))
            )
            password_field.send_keys(self.password)
            
            # Hacer click en el botón de login
            login_button = self.driver.find_element(By.ID, "processSystem_UserLogin")
            login_button.click()
            
            # Esperar a que se cargue la página principal
            WebDriverWait(self.driver, 15).until(
                EC.url_changes(self.bank_url)
            )
            
            logger.info("Login successful")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def get_balance(self):
        try:
            # Buscar el elemento td con headers="_Saldo disponible"
            balance_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'td[headers="_Saldo disponible"]'))
            )
            
            balance_text = balance_element.text
            logger.info(f"Raw balance text: '{balance_text}'")
            
            # Limpiar el texto para extraer el número
            # Remover símbolos de moneda, espacios y convertir comas por puntos
            clean_text = balance_text.replace('$', '').replace('ARS', '').replace(' ', '').replace(',', '.')
            
            # Buscar el número en el texto limpio
            import re
            numbers = re.findall(r'[-+]?\d*\.?\d+', clean_text)
            
            if numbers:
                balance_value = float(numbers[0])
                logger.info(f"Parsed balance: ${balance_value}")
                return balance_value
            else:
                logger.error(f"Could not parse balance from text: '{balance_text}'")
                return None
            
        except Exception as e:
            logger.error(f"Could not get balance: {str(e)}")
            return None
    
    def send_notification(self, balance):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = f"Balance Alert: ${balance}"
            
            body = f"""
            ¡Alerta de saldo!
            
            Tu saldo actual es: ${balance:,.2f}
            Este monto es mayor al límite establecido de: ${self.threshold_amount:,.2f}
            
            Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_from, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Notification sent successfully for balance: ${balance}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
    
    def check_balance_and_notify(self, headless=True):
        try:
            self.setup_driver(headless=headless)
            
            if not self.login():
                return False
                
            balance = self.get_balance()
            
            if balance is None:
                return False
                
            if balance > self.threshold_amount:
                logger.info(f"Balance ${balance} exceeds threshold ${self.threshold_amount}")
                self.send_notification(balance)
            else:
                logger.info(f"Balance ${balance} is below threshold ${self.threshold_amount}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error during balance check: {str(e)}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()

def main():
    import sys
    
    # Agregar opción para modo debug (no headless)
    debug_mode = '--debug' in sys.argv
    
    scraper = BankScraper()
    scraper.check_balance_and_notify(headless=not debug_mode)

if __name__ == "__main__":
    main()