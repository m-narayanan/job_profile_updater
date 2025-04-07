# Automatic Job Profile Updater

This script automatically updates job profiles on websites like Naukri.com. It logs in, makes minor edits to text fields (like resume headline and profile summary by toggling a full stop), and mandatorily uploads the latest resume found in a specified folder.

**Features:**

*   Automates login and profile navigation.
*   Handles potential cookie banners and dynamic pop-ups.
*   Edits specified text fields with a simple modification (toggle full stop).
*   Updates Profile Summary (configurable via `config.py`).
*   Finds the latest resume (.pdf, .doc, .docx) in the `resumes/` folder based on modification time.
*   Uploads the latest resume (Mandatory).
*   Designed to run headlessly (no visible browser window).
*   Uses environment variables / GitHub Secrets for secure credential management.
*   Structured for easy expansion to other job websites.
*   Uses `webdriver-manager` for automatic browser driver management.
*   Includes debugging features (screenshots on error).
*   Provides GitHub Actions workflow for free daily automation.

**Disclaimer:**

*   Web scraping and automation might be against the Terms of Service of some websites. Use responsibly and at your own risk.
*   **Website structures change frequently.** The provided Selenium locators (`locators.py`) **WILL LIKELY NEED UPDATES** over time. This is the most common cause of script failure. You must verify them using browser developer tools.
*   This script handles common scenarios. Complex JavaScript interactions, CAPTCHAs, or multi-factor authentication might require more advanced techniques or prevent automation entirely.

## Local Setup and Testing

Before deploying, test the script thoroughly on your local machine.

1.  **Prerequisites:**
    *   Python 3.7+ installed.
    *   Git installed ([https://git-scm.com/downloads](https://git-scm.com/downloads)).
    *   Google Chrome browser installed.

2.  **Clone/Download Code:** Get the project files.

3.  **Navigate to Project Directory:** Open your terminal/command prompt and `cd` into the `job_profile_updater` directory.

4.  **Create Virtual Environment & Activate:**
    ```bash
    python -m venv venv
    # Windows: venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate
    ```
    *(You should see `(venv)` in your prompt)*

5.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Configure Credentials (Local `.env` file ONLY):**
    *   Create a file named `.env` in the project root.
    *   Add your credentials:
        ```dotenv
        NAUKRI_USERNAME=your_naukri_email@example.com
        NAUKRI_PASSWORD=your_naukri_password
        ```
    *   **IMPORTANT:** Create/update your `.gitignore` file and add `.env` to it. **NEVER commit your `.env` file.**

7.  **Configure Features (`config.py`):**
    *   Set `HEADLESS_BROWSER = False` for initial visual testing.
    *   Set `UPDATE_PROFILE_SUMMARY = True` or `False` depending on whether you want to update the profile summary.

8.  **Add Resumes:** Place your latest resume file (`.pdf`, `.doc`, `.docx`) inside the `resumes/` folder.

9.  **CRITICAL STEP: Verify Locators (`locators.py`)**
    *   Run the script locally: `python main.py`
    *   Watch the browser window controlled by Selenium.
    *   If it fails (errors like `TimeoutException`, `NoSuchElementException`), **STOP** and:
        *   Check the error message in the terminal to see which element failed.
        *   Look for the `error_screenshot_*.png` file created in the project directory. Does it show the expected page? Is the element visible? Are there unexpected pop-ups?
        *   Open the relevant Naukri page in your regular browser (or use the Selenium window). Use Developer Tools (F12 -> Inspect) to find the correct `id`, `xpath`, or `css selector` for the element that caused the error.
        *   **Update the corresponding locator value in `locators.py`**. Pay special attention to elements needed for login, navigation, edit icons, text areas (in edit mode), save buttons (in edit mode), the resume `<input type="file">` element, and the resume upload success indicator.
    *   Repeat testing and locator updates until the script runs successfully locally.

10. **Final Local Test (Headless):**
    *   Set `HEADLESS_BROWSER = True` in `config.py`.
    *   Run `python main.py` again. Ensure it completes successfully without the visible browser.

## Automated Daily Execution via GitHub Actions (Free)

This method uses GitHub's infrastructure to run your script on a schedule.

1.  **Push to GitHub Repository:**
    *   Make sure your local Git repository is set up and includes your working code and a `.gitignore` file (excluding `venv`, `.env`, logs, screenshots, `.wdm`).
    *   Create a repository on GitHub.com (public or private).
    *   Push your local code to the GitHub repository.

2.  **Set Up GitHub Secrets (Secure Credentials):**
    *   Go to your repository page on GitHub.com.
    *   **Settings** tab -> **Secrets and variables** (left sidebar) -> **Actions**.
    *   Click **New repository secret**.
    *   Create a secret named `NAUKRI_USERNAME` and paste your Naukri email/username as the value. Add secret.
    *   Create another secret named `NAUKRI_PASSWORD` and paste your Naukri password. Add secret.
    *   *(These secrets replace the need for the `.env` file in the deployed environment)*.

3.  **Add the Workflow File:**
    *   Ensure the directory structure `.github/workflows/` exists in your project.
    *   Make sure the file `.github/workflows/naukri_update_schedule.yml` (or your chosen `.yml` filename) exists with the correct workflow definition (as provided in the previous instructions). The key parts are:
        *   `on: schedule: - cron: '0 9 * * *'` (Defines the 9:00 AM UTC daily schedule - adjust time as needed).
        *   `on: workflow_dispatch:` (Allows manual triggering).
        *   `jobs: update_naukri_profile: runs-on: ubuntu-latest` (Specifies the runner).
        *   Steps for `checkout`, `setup-python`, `install Google Chrome`, `install Dependencies`.
        *   The crucial `Run Profile Update Script` step, which uses `env: ${{ secrets.NAUKRI_USERNAME }}` etc., to securely pass credentials.
        *   The optional `Upload logs and screenshot on failure` step.

4.  **Commit and Push the Workflow File:**
    ```bash
    git add .github/workflows/naukri_update_schedule.yml
    git commit -m "Add GitHub Actions workflow"
    git push
    ```

5.  **Monitor Workflow Runs on GitHub:**
    *   Go to the **Actions** tab of your repository on GitHub.com.
    *   You'll see the "Daily Naukri Profile Update" workflow.
    *   **Manual Test:** Click the workflow name, then click "Run workflow" to test it immediately.
    *   **Scheduled Runs:** The workflow will run automatically based on the `cron` schedule.
    *   **Check Logs:** Click on any workflow run, then click the job name (`update_naukri_profile`). Expand each step to see detailed logs. Errors will be visible here.
    *   **Check Artifacts (on Failure):** If a run fails, go to the "Summary" page for that run. Download the `naukri-update-failure-artifacts.zip` from the "Artifacts" section to get the logs and screenshots generated by the script during the failed run.

## Maintenance

*   **Website Changes:** Naukri.com *will* change its website layout over time. When this happens, the script will likely fail (often with `TimeoutException` or `NoSuchElementException`). You will need to:
    1.  Check the GitHub Actions logs and failure artifacts (screenshots).
    2.  Manually inspect the Naukri website using Developer Tools (F12).
    3.  Update the locators in `locators.py`.
    4.  Commit and push the changes to GitHub. The workflow will use the updated code on its next run.
*   **Dependency Updates:** Occasionally update dependencies (`pip install -r requirements.txt --upgrade`) and test locally.

## Expansion

To add support for another website (e.g., LinkedIn):

1.  **Add Credentials:** Add secrets (e.g., `LINKEDIN_USERNAME`, `LINKEDIN_PASSWORD`) to GitHub repository settings. Update `config.py` to load them (using `os.getenv`).
2.  **Add Locators:** Create a `LinkedInLocators` class in `locators.py`.
3.  **Create Updater Class:** Create `linkedin_updater.py` with a `LinkedInUpdater` class inheriting `WebUpdater`, implementing its abstract methods using LinkedIn locators.
4.  **Update `main.py`:** Add LinkedIn to the `updater_classes` dictionary.
5.  **Update Workflow (`.github/workflows/naukri_update_schedule.yml`):** Add the new secrets to the `env:` section of the "Run Profile Update Script" step.
6.  **Test Thoroughly:** Test locally first, then push changes.
