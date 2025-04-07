import logging
import time
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
# from selenium.webdriver.firefox.service import Service as FirefoxService # Uncomment if using Firefox
# from webdriver_manager.firefox import GeckoDriverManager # Uncomment if using Firefox
# from selenium.webdriver.firefox.options import Options as FirefoxOptions # Uncomment if using Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException
)
from selenium.webdriver.common.by import By # Import By for locator tuple structure

# Import config and utils later to avoid potential circular dependencies
import config
import utils

class WebUpdater(ABC):
    """Abstract base class for website profile updaters."""

    def __init__(self, username, password, headless=True):
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None

    def _init_driver(self) -> WebDriver:
        """Initializes the Selenium WebDriver."""
        logging.info("Initializing WebDriver...")
        options = ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new") # Recommended new headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_argument("--disable-blink-features=AutomationControlled") # May help avoid detection
        # options.add_experimental_option('useAutomationExtension', False) # May help avoid detection

        try:
            logging.info("Setting up ChromeDriver using webdriver-manager...")
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(config.IMPLICIT_WAIT_TIME)
            logging.info("WebDriver initialized successfully (Chrome).")
            return driver
        except Exception as e:
            logging.error(f"Failed to initialize Chrome WebDriver: {e}", exc_info=True)
            raise RuntimeError("Could not initialize Chrome WebDriver.") from e

    @abstractmethod
    def login(self):
        """Logs into the website."""
        pass

    @abstractmethod
    def navigate_to_profile(self):
        """Navigates to the profile editing section."""
        pass

    @abstractmethod
    def update_optional_fields(self):
        """Updates optional text fields like headline, summary."""
        pass

    @abstractmethod
    def update_resume(self, resume_path: str):
        """Uploads the new resume."""
        pass

    def run_update(self):
        """Executes the full update process."""
        if not self.username or not self.password:
             logging.error(f"Missing username or password for {self.__class__.__name__}.")
             return False

        latest_resume = utils.find_latest_resume(config.RESUME_FOLDER)
        if not latest_resume:
            logging.error("Mandatory step failed: Could not find resume to upload.")
            return False

        self.driver = None
        try:
            self.driver = self._init_driver()
            self.login()
            self.navigate_to_profile()
            self.update_optional_fields()
            self.update_resume(latest_resume)
            logging.info(f"Update process completed successfully for {self.__class__.__name__}.")
            return True
        except Exception as e:
            # Error logging is now more specific within the methods that fail
            # The exception will propagate here if not handled locally
            logging.error(f"An unhandled error occurred during the update process for {self.__class__.__name__}: {e}", exc_info=True)
             # Log debug info here as a final catch-all if not logged earlier
            if hasattr(self, '_log_debug_info'): # Check if subclass has the method
                 self._log_debug_info(f"{self.__class__.__name__}_run_update_error")
            return False
        finally:
            if self.driver:
                logging.info("Closing WebDriver.")
                self.driver.quit()

    # --- Helper methods for subclasses ---
    def safe_find_element(self, locator, timeout=config.EXPLICIT_WAIT_TIME):
        """Finds an element, waiting for visibility."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located(locator))
            logging.debug(f"Found visible element with locator: {locator}")
            return element
        except TimeoutException:
            # Logged with more context in the calling function usually
            raise # Re-raise to be caught by caller

    def safe_click(self, locator, timeout=config.EXPLICIT_WAIT_TIME):
        """Clicks an element safely, waiting for clickability, with retries and JS fallback."""
        retries = 2
        last_exception = None
        for i in range(retries):
            try:
                wait = WebDriverWait(self.driver, timeout)
                element = wait.until(EC.element_to_be_clickable(locator))
                logging.debug(f"Attempting to click element: {locator} (Attempt {i+1})")
                element.click()
                time.sleep(1) # Pause after click
                return # Success
            except StaleElementReferenceException as e:
                logging.warning(f"StaleElementReferenceException clicking {locator}, attempt {i+1}/{retries}. Retrying...")
                last_exception = e
                time.sleep(1)
            except ElementClickInterceptedException as e:
                 logging.warning(f"Element click intercepted for {locator} (Attempt {i+1}). Trying JavaScript click.")
                 last_exception = e
                 try:
                     # Find presence first for JS click
                     element_for_js = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
                     self.driver.execute_script("arguments[0].click();", element_for_js)
                     logging.info(f"JavaScript click executed for {locator}.")
                     time.sleep(1)
                     return # Success
                 except Exception as js_click_err:
                      logging.error(f"JavaScript click also failed for {locator}: {js_click_err}")
                      last_exception = js_click_err
                      time.sleep(1)
            except TimeoutException as e:
                 # Logged with more context by caller
                 last_exception = e
                 time.sleep(1) # Pause before retry
            except Exception as e:
                 logging.error(f"Unexpected error clicking {locator}: {e}", exc_info=True)
                 last_exception = e
                 time.sleep(1)

        # If loop finishes
        logging.error(f"Failed to click {locator} after {retries} retries.")
        if last_exception:
            raise last_exception # Raise the specific error encountered
        else:
            # Should not happen if retries > 0, but safety net
            raise Exception(f"Unknown error clicking {locator} after retries")

    def safe_send_keys(self, locator, text, timeout=config.EXPLICIT_WAIT_TIME, clear_first=True):
        """Sends keys safely, waiting for element readiness, with retries."""
        retries = 2
        last_exception = None
        for i in range(retries):
            try:
                element = self.safe_find_element(locator, timeout) # Ensures visibility first
                element = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator)) # Then check clickability/enabled

                logging.debug(f"Sending keys to element: {locator} (Attempt {i+1})")
                if clear_first:
                    element.clear()
                    time.sleep(0.3) # Pause after clear
                element.send_keys(text)
                time.sleep(0.5) # Pause after sending keys
                return # Success
            except StaleElementReferenceException as e:
                logging.warning(f"StaleElementReferenceException sending keys to {locator}, attempt {i+1}/{retries}. Retrying...")
                last_exception = e
                time.sleep(1)
            except TimeoutException as e:
                # Logged with context by caller
                last_exception = e
                time.sleep(1)
            except Exception as e:
                logging.error(f"Unexpected error sending keys to {locator}: {e}", exc_info=True)
                last_exception = e
                time.sleep(1)

        # If loop finishes
        logging.error(f"Failed to send keys to {locator} after {retries} retries.")
        if last_exception:
            raise last_exception
        else:
            raise Exception(f"Unknown error sending keys to {locator} after retries")

    def edit_text_field_with_toggle(self, edit_icon_locator, text_area_locator, save_button_locator):
        """Helper to click edit, wait for modal/area, toggle full stop, and save."""
        try:
            logging.info(f"Attempting to edit field triggered by clicking: {edit_icon_locator}")
            self.safe_click(edit_icon_locator)
            logging.debug(f"Clicked edit icon: {edit_icon_locator}. Waiting for text area {text_area_locator} to be visible...")

            # Wait explicitly for the text area to appear AND be visible/interactive
            try:
                # Wait for visibility using safe_find_element
                text_element = self.safe_find_element(text_area_locator, timeout=config.EXPLICIT_WAIT_TIME + 5)
                 # Additionally wait for clickability/enabled state
                text_element = WebDriverWait(self.driver, config.EXPLICIT_WAIT_TIME).until(
                     EC.element_to_be_clickable(text_area_locator)
                )
                logging.info(f"Text area {text_area_locator} located and ready.")
            except Exception as e:
                logging.error(f"Failed to find or make ready the text area {text_area_locator} after clicking edit.")
                raise e # Re-raise the original error if not found

            current_text = text_element.get_attribute('value') or text_element.text
            new_text = utils.toggle_full_stop(current_text)
            logging.debug(f"Current text: '{current_text[:50]}...', New text: '{new_text[:50]}...'")

            if current_text != new_text:
                logging.info(f"Updating text field {text_area_locator}")
                self.safe_send_keys(text_area_locator, new_text, clear_first=True)
                time.sleep(0.5)

                logging.debug(f"Attempting to click save button: {save_button_locator}")
                self.safe_click(save_button_locator)
                logging.info(f"Clicked save button for field.")
                # Wait for potential modal close or confirmation message (adjust as needed)
                time.sleep(5)
            else:
                 logging.info(f"No text change needed for field: {text_area_locator}")
                 # Attempt to close the modal - Clicking save might work, or need a Cancel button
                 try:
                    logging.debug(f"Attempting to click save/close button anyway: {save_button_locator}")
                    self.safe_click(save_button_locator)
                    logging.info(f"Clicked 'Save/Close' button for {text_area_locator} (no change made).")
                    time.sleep(3)
                 except Exception as close_err:
                     logging.warning(f"Could not click save/close button ({save_button_locator}) after no change. May need specific 'Cancel' locator. Error: {close_err}")
                     # Add fallback cancel logic if necessary here

        except Exception as e:
            # Error logged by the safe_ methods or here if it's a different step
            logging.error(f"Failed during edit_text_field_with_toggle for {edit_icon_locator}: {e}", exc_info=True)
            raise # Re-raise to be potentially caught by run_update