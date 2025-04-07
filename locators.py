# locators.py
from selenium.webdriver.common.by import By

# ==============================================================================
# IMPORTANT: Verify locators carefully using browser developer tools (F12).
#            Resume Headline section seems OK based on feedback.
#            Focus verification on PROFILE SUMMARY and RESUME UPLOAD sections.
# ==============================================================================

class NaukriLocators:
    # --- Cookie Banner (Optional) ---
    COOKIE_BANNER_ACCEPT_BUTTON = (By.ID, "cookie-accept-button-id") # <-- UPDATE IF NEEDED

    # --- Login Page ---
    USERNAME_INPUT = (By.ID, "usernameField") # <-- VERIFY/UPDATE
    PASSWORD_INPUT = (By.ID, "passwordField") # <-- VERIFY/UPDATE
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit' and contains(text(),'Login')]") # <-- VERIFY/UPDATE

    # --- Post-Login Dashboard / Navigation ---
    VIEW_PROFILE_LINK = (By.XPATH, "//a[contains(@href,'mnjuser/profile')]") # <-- VERIFY/UPDATE
    PROFILE_MENU_ICON = (By.CSS_SELECTOR, ".nI-gNb-icon-img") # <-- VERIFY/UPDATE (Alternative)

    # --- Profile Page ---
    # Pop-up/Sidebar Help Section
    POPUP_CLOSE_BUTTON = (By.XPATH, "//div[contains(@class,'view-profile-strip')]//span[contains(@class,'cross-icon')]") # <-- UPDATE IF NEEDED

    # Resume Headline Section (Seems OK - using verified locator)
    EDIT_RESUME_HEADLINE_ICON = (By.XPATH, "//div[contains(@class,'resumeHeadline')]//span[contains(@class,'edit') and contains(@class,'icon') and contains(text(),'editOneTheme')]") # Using locator based on feedback
    RESUME_HEADLINE_TEXTAREA = (By.ID, "resumeHeadlineTxt") # Seems OK
    SAVE_RESUME_HEADLINE_BUTTON = (By.XPATH, "//div[contains(@class,'resumeHeadline')]//button[text()='Save']") # Seems OK

    # *** PROFILE SUMMARY SECTION - VERIFY THESE IF ENABLED ***
    EDIT_PROFILE_SUMMARY_ICON = (By.XPATH, "//div[contains(@class,'profileSummary')]//span[contains(@class,'edit') and contains(@class,'icon')]") # <--*** VERIFY/UPDATE! ***
    PROFILE_SUMMARY_TEXTAREA = (By.XPATH, "//textarea[contains(@placeholder,'Profile Summary')]") # <--*** VERIFY/UPDATE (in edit mode)! ***
    SAVE_PROFILE_SUMMARY_BUTTON = (By.XPATH, "//div[contains(@class,'profileSummary')]//button[text()='Save']") # <--*** VERIFY/UPDATE (in edit mode)! ***

    # *** RESUME UPLOAD SECTION - VERIFY THESE CAREFULLY ***
    # The hidden file input element
    UPDATE_RESUME_BUTTON = (By.XPATH, "//input[@id='attachCV']") # <--*** CRITICAL: VERIFY/UPDATE THIS! Find the <input type="file"> ***
    # A visible element in the upload area (useful for scrolling into view)
    VISIBLE_UPLOAD_AREA = (By.XPATH, "//div[contains(@class,'resumeUploadDiv')]") # <--*** VERIFY/UPDATE THIS! Example XPath ***
    # Element indicating successful resume upload
    RESUME_UPLOAD_SUCCESS_INDICATOR = (By.XPATH, "//*[contains(text(),'Resume has been successfully uploaded')]") # <--*** CRITICAL: VERIFY/UPDATE THIS! What confirms success? ***