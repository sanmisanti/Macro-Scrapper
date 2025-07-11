import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MacroDebugScraper:
    def __init__(self):
        self.driver = None
        self.bank_url = os.getenv('BANK_URL', '')
        
    def setup_driver(self, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def open_bank_page(self):
        try:
            logger.info(f"Opening bank page: {self.bank_url}")
            self.driver.get(self.bank_url)
            
            logger.info("Page loaded successfully")
            logger.info(f"Current URL: {self.driver.current_url}")
            logger.info(f"Page title: {self.driver.title}")
            
            time.sleep(5)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to open bank page: {str(e)}")
            return False
    
    def find_login_elements(self):
        try:
            logger.info("Searching for login elements...")
            
            # Buscar campos de input
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            logger.info(f"Found {len(inputs)} input elements")
            
            for i, input_elem in enumerate(inputs):
                elem_id = input_elem.get_attribute('id')
                elem_name = input_elem.get_attribute('name')
                elem_type = input_elem.get_attribute('type')
                elem_class = input_elem.get_attribute('class')
                
                logger.info(f"Input {i+1}: id='{elem_id}', name='{elem_name}', type='{elem_type}', class='{elem_class}'")
            
            # Buscar botones
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"Found {len(buttons)} button elements")
            
            for i, button in enumerate(buttons):
                button_id = button.get_attribute('id')
                button_class = button.get_attribute('class')
                button_text = button.text
                
                logger.info(f"Button {i+1}: id='{button_id}', class='{button_class}', text='{button_text}'")
            
            # Buscar elementos con type=submit
            submits = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
            logger.info(f"Found {len(submits)} submit elements")
            
            for i, submit in enumerate(submits):
                submit_id = submit.get_attribute('id')
                submit_class = submit.get_attribute('class')
                submit_value = submit.get_attribute('value')
                
                logger.info(f"Submit {i+1}: id='{submit_id}', class='{submit_class}', value='{submit_value}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Error finding login elements: {str(e)}")
            return False
    
    def debug_session(self):
        try:
            self.setup_driver(headless=False)  # Ventana visible para debug
            
            if not self.open_bank_page():
                return False
                
            if not self.find_login_elements():
                return False
                
            logger.info("Debug session completed. Check the logs above for element details.")
            
            input("Press Enter to close the browser...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during debug session: {str(e)}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()

def main():
    scraper = MacroDebugScraper()
    scraper.debug_session()

if __name__ == "__main__":
    main()