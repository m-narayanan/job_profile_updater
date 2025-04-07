# naukri_updater.py
import logging
import time
import os
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

from web_updater import WebUpdater
from locators import NaukriLocators
import config # Import config to access the new flag

class NaukriUpdater(WebUpdater):
    """Specific implementation for updating Naukri profile."""

    def __init__(self, username, password, headless=True):
        super().__init__(username, password, headless)
        self.locators = NaukriLocators

    # --- login method remains the same ---
    def login(self):
        # (Keep the robust login logic from the previous answer)
        logging.info("Attempting to log into Naukri...")
        try:
            self.driver.get(config.NAUKRI_LOGIN_URL)
            time.sleep(2) # Allow page initial load

            # --- Optional Cookie Banner Handling ---
            try:
                if hasattr(self.locators, 'COOKIE_BANNER_ACCEPT_BUTTON'):
                    logging.info("Checking for and clicking potential cookie banner...")
                    banner_button = WebDriverWait(self.driver, 7).until(
                        EC.element_to_be_clickable(self.locators.COOKIE_BANNER_ACCEPT_BUTTON) # Verify locator
                    )
                    banner_button.click()
                    logging.info("Clicked cookie banner accept button.")
                    time.sleep(1)
                else:
                    logging.debug("COOKIE_BANNER_ACCEPT_BUTTON locator not defined, skipping check.")
            except (NoSuchElementException, TimeoutException):
                logging.info("Cookie banner not found or not clickable within timeout.")
            except AttributeError:
                 logging.debug("COOKIE_BANNER_ACCEPT_BUTTON locator missing, skipping check.")
            # --- END: Optional Cookie Banner Handling ---

            logging.info("Attempting to enter username...")
            self.safe_send_keys(self.locators.USERNAME_INPUT, self.username) # Verify locator

            logging.info("Attempting to enter password...")
            self.safe_send_keys(self.locators.PASSWORD_INPUT, self.password) # Verify locator

            logging.info("Attempting to click login button...")
            self.safe_click(self.locators.LOGIN_BUTTON) # Verify locator
            logging.info("Submitted login credentials.")

            WebDriverWait(self.driver, config.EXPLICIT_WAIT_TIME).until(
                 EC.any_of(
                     EC.presence_of_element_located(self.locators.VIEW_PROFILE_LINK), # Verify locator
                     EC.presence_of_element_located(self.locators.PROFILE_MENU_ICON)  # Verify locator
                 )
            )
            logging.info("Naukri login successful.")
            time.sleep(2)

        except TimeoutException as e:
            context = "login_timeout_failure"
            if hasattr(self.locators, 'USERNAME_INPUT') and self.locators.USERNAME_INPUT[1] in str(e):
                 logging.error(f"Login failed: Timeout finding/interacting with USERNAME ({self.locators.USERNAME_INPUT}). Verify locator.", exc_info=False)
            elif hasattr(self.locators, 'PASSWORD_INPUT') and self.locators.PASSWORD_INPUT[1] in str(e):
                 logging.error(f"Login failed: Timeout finding/interacting with PASSWORD ({self.locators.PASSWORD_INPUT}). Verify locator.", exc_info=False)
            elif hasattr(self.locators, 'LOGIN_BUTTON') and self.locators.LOGIN_BUTTON[1] in str(e):
                 logging.error(f"Login failed: Timeout finding/interacting with LOGIN BUTTON ({self.locators.LOGIN_BUTTON}). Verify locator.", exc_info=False)
            else:
                 logging.error("Login submitted, but timed out waiting for dashboard confirmation.")
                 context = "login_confirmation_timeout"
            self._log_debug_info(context)
            raise RuntimeError("Login process failed due to timeout.") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred during Naukri login: {e}", exc_info=True)
            self._log_debug_info("login_unexpected_error")
            raise RuntimeError("Login process failed unexpectedly.") from e

    # --- navigate_to_profile method remains the same (using simplified confirmation) ---
    def navigate_to_profile(self):
        # (Keep the navigate_to_profile logic from the previous answer,
        #  which confirms using only EDIT_RESUME_HEADLINE_ICON)
        logging.info("Navigating to Naukri profile edit page...")
        nav_action_done = False
        try:
            # Try direct navigation
            try:
                profile_link = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(self.locators.VIEW_PROFILE_LINK) # Verify locator
                )
                profile_url = profile_link.get_attribute('href')
                if profile_url and 'mnjuser/profile' in profile_url:
                     logging.info(f"Attempting direct navigation using href: {profile_url}")
                     self.driver.get(profile_url)
                     nav_action_done = True
                     logging.info("Direct navigation attempt complete.")
            except (TimeoutException, NoSuchElementException):
                 logging.info("Profile link for direct navigation not found quickly, will try clicking.")

            if not nav_action_done:
                logging.info("Attempting navigation by clicking profile link element.")
                self.safe_click(self.locators.VIEW_PROFILE_LINK, timeout=15) # Verify locator
                nav_action_done = True
                logging.info("Click navigation attempt complete.")

            time.sleep(2)
            self.check_and_close_popup() # Verify locator for popup close

            # --- SIMPLIFIED Page Load Confirmation (using headline icon) ---
            logging.info("Confirming profile page primary element is loaded...")
            primary_element_locator = self.locators.EDIT_RESUME_HEADLINE_ICON # Assumes this locator is correct now
            try:
                wait = WebDriverWait(self.driver, config.EXPLICIT_WAIT_TIME + 5)
                wait.until(EC.visibility_of_element_located(primary_element_locator))
                logging.info(f"Primary profile page element confirmed ({primary_element_locator}).")
            except TimeoutException as confirm_e:
                logging.error(f"Failed to confirm presence/visibility of the primary profile element ({primary_element_locator}).")
                logging.error(">>> ACTION: Check the saved screenshot and use browser DevTools (F12) to verify the locator for EDIT_RESUME_HEADLINE_ICON.")
                self._log_debug_info("profile_load_confirmation_failure")
                raise RuntimeError("Profile page did not load expected primary element.") from confirm_e
            # --- END OF Confirmation ---

            logging.info("Navigation actions and confirmation completed.")
            time.sleep(1)

        except Exception as e:
            logging.error(f"Failed during navigation/popup/confirmation steps: {e}", exc_info=True)
            self._log_debug_info("navigation_error")
            raise RuntimeError("Navigation to profile page failed definitively.") from e

    # --- check_and_close_popup method remains the same ---
    def check_and_close_popup(self):
        # (Keep the logic from the previous answer - VERIFY POPUP_CLOSE_BUTTON locator)
        if not hasattr(self.locators, 'POPUP_CLOSE_BUTTON'):
             logging.debug("POPUP_CLOSE_BUTTON locator not defined, skipping check.")
             return
        logging.info("Checking for profile help pop-up...")
        try:
            close_button = WebDriverWait(self.driver, 7).until(
                 EC.element_to_be_clickable(self.locators.POPUP_CLOSE_BUTTON) # Verify locator
             )
            logging.info("Profile help pop-up detected. Attempting to close.")
            self.driver.execute_script("arguments[0].click();", close_button)
            logging.info("Clicked pop-up close button via JS.")
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            logging.info("Profile help pop-up not found or not clickable within timeout.")
        except Exception as e:
            logging.warning(f"An error occurred while checking/closing profile help pop-up: {e}", exc_info=True)


    def update_optional_fields(self):
        """Updates Resume Headline and optionally Profile Summary."""
        logging.info("Updating optional fields on Naukri profile...")

        # --- Update Resume Headline (Confirmed Working) ---
        try:
            logging.info("Attempting to update Resume Headline...")
            self.edit_text_field_with_toggle(
                self.locators.EDIT_RESUME_HEADLINE_ICON,
                self.locators.RESUME_HEADLINE_TEXTAREA,
                self.locators.SAVE_RESUME_HEADLINE_BUTTON
            )
            logging.info("Resume Headline update process attempted successfully.") # Changed log level
        except (TimeoutException, NoSuchElementException) as e:
             # Should not happen if it's working, but keep for robustness
             logging.error(f"Failed to find/interact with Resume Headline elements (unexpected): {e}", exc_info=False)
             self._log_debug_info("headline_edit_failure_unexpected")
        except Exception as e:
            logging.warning(f"Could not complete Resume Headline update (unexpected error): {e}", exc_info=True)
            self._log_debug_info("headline_edit_unexpected_error")


        # --- Update Profile Summary (Now Optional) ---
        if config.UPDATE_PROFILE_SUMMARY:
            try:
                 logging.info("Attempting to update Profile Summary (if enabled)...")
                 summary_edit_icon_locator = self.locators.EDIT_PROFILE_SUMMARY_ICON # Verify locator!
                 summary_icon_element = self.safe_find_element(summary_edit_icon_locator, timeout=config.EXPLICIT_WAIT_TIME)
                 self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", summary_icon_element)
                 time.sleep(1)
                 WebDriverWait(self.driver, config.EXPLICIT_WAIT_TIME).until(
                     EC.element_to_be_clickable(summary_edit_icon_locator)
                 )
                 self.edit_text_field_with_toggle(
                     summary_edit_icon_locator,
                     self.locators.PROFILE_SUMMARY_TEXTAREA,    # Verify locator (in edit mode)!
                     self.locators.SAVE_PROFILE_SUMMARY_BUTTON # Verify locator (in edit mode)!
                 )
                 logging.info("Profile Summary update process attempted.")
            except (TimeoutException, NoSuchElementException) as e:
                 logging.error(f"Failed to find/interact with Profile Summary elements. Check locators.", exc_info=False)
                 self._log_debug_info("summary_edit_failure")
            except Exception as e:
                logging.warning(f"Could not complete Profile Summary update (unexpected error): {e}", exc_info=True)
                self._log_debug_info("summary_edit_unexpected_error")
        else:
            logging.info("Skipping Profile Summary update as per configuration.")


    def update_resume(self, resume_path: str):
        """Uploads the new resume file."""
        logging.info(f"Attempting to update Naukri resume with: {os.path.basename(resume_path)}")
        try:
            # --- CRITICAL: Verify this locator for the <input type="file"> element ---
            file_input_locator = self.locators.UPDATE_RESUME_BUTTON
            logging.debug(f"Looking for resume file input element: {file_input_locator}")
            # Use safe_find_element which waits for visibility. Note: Hidden inputs might not become "visible".
            # If it fails here, the locator is wrong OR the input is truly hidden AND not interactable.
            try:
                # Try finding with visibility check first
                file_input = self.safe_find_element(file_input_locator, timeout=config.EXPLICIT_WAIT_TIME)
            except TimeoutException:
                 # If visibility fails, try finding just by presence for hidden inputs
                 logging.warning(f"Could not find visible file input {file_input_locator}. Trying presence check...")
                 try:
                      file_input = WebDriverWait(self.driver, 5).until(
                          EC.presence_of_element_located(file_input_locator)
                      )
                      logging.info(f"Found file input by presence: {file_input_locator}")
                 except TimeoutException as presence_e:
                     logging.error(f"Failed to find file input element {file_input_locator} even by presence.")
                     raise presence_e # Re-raise the specific error

            # Scroll into view (use fallback if needed)
            try:
                 self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", file_input)
                 time.sleep(0.5)
            except Exception:
                 logging.debug("Scrolling input failed, trying alternative scroll target.")
                 try:
                     visible_nearby_element = self.safe_find_element(self.locators.VISIBLE_UPLOAD_AREA, timeout=5) # Verify locator
                     self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", visible_nearby_element)
                     time.sleep(0.5)
                 except Exception as scroll_err:
                     logging.warning(f"Could not scroll resume upload area into view: {scroll_err}")
            time.sleep(1)

            # --- Send file path directly to the input element ---
            logging.info(f"Sending file path '{resume_path}' to the file input element.")
            file_input.send_keys(resume_path)
            logging.info("File path sent to input element.")

            # --- Wait for upload confirmation ---
            # --- CRITICAL: Verify this locator for the success message/state ---
            success_locator = self.locators.RESUME_UPLOAD_SUCCESS_INDICATOR
            logging.debug(f"Waiting for resume upload success indicator: {success_locator}")
            wait = WebDriverWait(self.driver, 90) # Long timeout for upload process
            wait.until(
                EC.visibility_of_element_located(success_locator) # Wait for visibility of the confirmation
            )
            logging.info("Naukri resume update confirmed by success indicator.")
            time.sleep(3)

        except (TimeoutException, NoSuchElementException) as e:
            logging.error(f"Failed during resume upload (finding input or waiting for confirmation). Check locators.", exc_info=False)
            logging.error(f">>> Check locator for INPUT: {self.locators.UPDATE_RESUME_BUTTON}")
            logging.error(f">>> Check locator for SUCCESS: {self.locators.RESUME_UPLOAD_SUCCESS_INDICATOR}")
            self._log_debug_info("resume_upload_failure")
            raise RuntimeError("Resume upload process failed.") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred during Naukri resume upload: {e}", exc_info=True)
            self._log_debug_info("resume_upload_unexpected_error")
            raise RuntimeError("Resume upload failed unexpectedly.") from e

    # --- _log_debug_info method remains the same ---
    def _log_debug_info(self, error_context="general_error"):
        # (Keep the _log_debug_info logic from the previous answer)
        if not self.driver:
            logging.error("Driver not available, cannot log debug info.")
            return
        try:
            current_url = self.driver.current_url
            logging.info(f"DEBUG: Current URL at error ({error_context}): {current_url}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_screenshot_{error_context}_{timestamp}.png"
            if self.driver.save_screenshot(filename):
                 logging.info(f"DEBUG: Saved screenshot: {filename}")
            else:
                 logging.warning("DEBUG: Failed to save screenshot (driver.save_screenshot returned False).")
        except Exception as debug_err:
            logging.error(f"Failed to log debug info: {debug_err}", exc_info=True)