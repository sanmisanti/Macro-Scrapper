import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_navigation():
    try:
        # Configuración mínima de Chrome
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome driver initialized successfully")
        
        # Probar con URL simple primero
        logger.info("Testing Google...")
        driver.get("https://www.google.com")
        logger.info(f"Google loaded successfully. Title: {driver.title}")
        
        # Ahora probar con la URL del banco
        bank_url = os.getenv('BANK_URL', '')
        logger.info(f"Testing bank URL: {bank_url}")
        
        if bank_url:
            driver.get(bank_url)
            logger.info(f"Bank page loaded successfully. Title: {driver.title}")
            logger.info(f"Current URL: {driver.current_url}")
        else:
            logger.error("No BANK_URL found in environment variables")
        
        input("Press Enter to close browser...")
        driver.quit()
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_basic_navigation()