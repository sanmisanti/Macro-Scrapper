import os
import time
import signal
import sys
from datetime import datetime
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
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
            # Buscar todos los elementos td con headers="_Saldo disponible"
            balance_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td[headers="_Saldo disponible"]'))
            )
            
            accounts = []
            total_balance = 0
            
            for i, balance_element in enumerate(balance_elements):
                balance_text = balance_element.text
                logger.info(f"Raw balance text for account {i+1}: '{balance_text}'")
                
                # Limpiar el texto para extraer el número
                # Remover símbolos de moneda, espacios y convertir comas por puntos
                clean_text = balance_text.replace('$', '').replace('ARS', '').replace(' ', '').replace(',', '.')
                
                # Buscar el número en el texto limpio
                import re
                numbers = re.findall(r'[-+]?\d*\.?\d+', clean_text)
                
                if numbers:
                    balance_value = float(numbers[0])
                    account_name = f"Cuenta{i+1}"
                    accounts.append({
                        'name': account_name,
                        'balance': balance_value
                    })
                    total_balance += balance_value
                    logger.info(f"Parsed balance for {account_name}: ${balance_value}")
                else:
                    logger.error(f"Could not parse balance from text for account {i+1}: '{balance_text}'")
            
            if accounts:
                logger.info(f"Total balance across all accounts: ${total_balance}")
                return {
                    'accounts': accounts,
                    'total': total_balance
                }
            else:
                logger.error("No valid balances found")
                return None
            
        except Exception as e:
            logger.error(f"Could not get balance: {str(e)}")
            return None
    
    def logout(self):
        try:
            logout_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "widgetLogoutBtn"))
            )
            logout_button.click()
            logger.info("Logout successful")
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
    
    def send_notification(self, balance_data):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = f"Balance Alert: ${balance_data['total']}"
            
            # Crear detalle de cuentas
            accounts_detail = ""
            for account in balance_data['accounts']:
                accounts_detail += f"  {account['name']}: ${account['balance']:,.2f}\n"
            
            body = f"""
            ¡Alerta de saldo!
            
            Detalle por cuenta:
{accounts_detail}
            Saldo total: ${balance_data['total']:,.2f}
            Este monto es mayor al límite establecido de: ${self.threshold_amount:,.2f}
            
            Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_from, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Notification sent successfully for total balance: ${balance_data['total']}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
    
    def check_balance_and_notify(self, headless=True):
        try:
            self.setup_driver(headless=headless)
            
            if not self.login():
                return False
                
            balance_data = self.get_balance()
            
            if balance_data is None:
                return False
                
            total_balance = balance_data['total']
            
            if total_balance > self.threshold_amount:
                logger.info(f"Total balance ${total_balance} exceeds threshold ${self.threshold_amount}")
                self.send_notification(balance_data)
            else:
                logger.info(f"Total balance ${total_balance} is below threshold ${self.threshold_amount}")
                
            # Cerrar sesión
            self.logout()
            
            return True
            
        except Exception as e:
            logger.error(f"Error during balance check: {str(e)}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()

def run_daemon():
    """Ejecuta el scraper en modo daemon, verificando cada 30 minutos"""
    logger.info("Iniciando Banco Macro Scraper en modo daemon")
    logger.info("Verificaciones cada 30 minutos - Presiona Ctrl+C para detener")
    
    def signal_handler(signum, frame):
        logger.info("Señal de interrupción recibida. Cerrando daemon...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Ejecutar inmediatamente la primera vez
    run_single_check(headless=True)
    
    # Luego ejecutar cada 30 minutos
    while True:
        try:
            logger.info(f"Esperando 30 minutos hasta la próxima verificación...")
            time.sleep(1800)  # 30 minutos = 1800 segundos
            run_single_check(headless=True)
        except KeyboardInterrupt:
            logger.info("Daemon detenido por el usuario")
            break
        except Exception as e:
            logger.error(f"Error inesperado en daemon: {str(e)}")
            logger.info("Continuando con el siguiente ciclo...")
            time.sleep(60)  # Esperar 1 minuto antes del siguiente intento

def run_single_check(headless=True, max_retries=3):
    """Ejecuta una sola verificación con reintentos"""
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"=== Iniciando verificación (intento {attempt}/{max_retries}) ===")
            scraper = BankScraper()
            success = scraper.check_balance_and_notify(headless=headless)
            
            if success:
                logger.info("Verificación completada exitosamente")
                return True
            else:
                logger.warning(f"Verificación falló en intento {attempt}")
                
        except Exception as e:
            logger.error(f"Error en intento {attempt}: {str(e)}")
            
        if attempt < max_retries:
            wait_time = attempt * 60  # Esperar 60, 120, 180 segundos
            logger.info(f"Esperando {wait_time} segundos antes del siguiente intento...")
            time.sleep(wait_time)
    
    logger.error(f"Verificación falló después de {max_retries} intentos")
    return False

def main():
    # Verificar argumentos de línea de comandos
    if '--daemon' in sys.argv:
        run_daemon()
    elif '--debug' in sys.argv:
        # Modo debug: una sola ejecución con ventana visible
        logger.info("Ejecutando en modo debug (una sola vez)")
        run_single_check(headless=False)
    else:
        # Modo normal: una sola ejecución headless
        logger.info("Ejecutando verificación única")
        run_single_check(headless=True)

if __name__ == "__main__":
    main()