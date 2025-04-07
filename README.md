# Automatic Job Profile Updater

This script automatically updates job profiles on websites like Naukri.com. It logs in, makes minor edits to text fields (like resume headline and profile summary by toggling a full stop), and mandatorily uploads the latest resume found in a specified folder.

**Features:**

*   Automates login and profile navigation.
*   Edits specified text fields with a simple modification (toggle full stop).
*   Finds the latest resume (.pdf, .doc, .docx) in the `resumes/` folder based on modification time.
*   Uploads the latest resume.
*   Designed to run headlessly (no visible browser window).
*   Uses environment variables for secure credential management.
*   Structured for easy expansion to other job websites.
*   Uses `webdriver-manager` for automatic browser driver management.

**Disclaimer:**

*   Web scraping and automation might be against the Terms of Service of some websites. Use responsibly and at your own risk.
*   Website structures change frequently. The provided Selenium locators (`locators.py`) **will likely need updates** over time. You'll need to inspect the website elements using browser developer tools to fix them if the script breaks.
*   This script handles basic scenarios. Complex JavaScript interactions, CAPTCHAs, or multi-factor authentication might require more advanced techniques or prevent automation entirely.

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd job_profile_updater
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Credentials (Local Development):**
    *   Create a file named `.env` in the project's root directory (`job_profile_updater/`).
    *   Add your credentials to this file (**DO NOT COMMIT THIS FILE TO GIT!** Add `.env` to your `.gitignore` file).
        ```dotenv
        NAUKRI_USERNAME=your_naukri_email@example.com
        NAUKRI_PASSWORD=your_naukri_password
        # Add other site credentials if needed
        # LINKEDIN_USERNAME=your_linkedin_email@example.com
        # LINKEDIN_PASSWORD=your_linkedin_password
        ```

5.  **Add Resumes:**
    *   Place your resume files (e.g., `my_resume_v1.pdf`, `my_resume_v2.docx`) inside the `resumes/` folder. The script will automatically pick the one modified most recently.

6.  **Verify Locators:**
    *   **CRITICAL STEP:** Open `locators.py`. Go to Naukri.com, log in manually, and navigate to your profile edit page. Use your browser's Developer Tools (F12 or right-click -> Inspect) to find the correct IDs, XPaths, or CSS Selectors for each element listed in `NaukriLocators`. Update the values in `locators.py` accordingly. Test thoroughly.

7.  **Run Locally (for Testing):**
    *   Set `HEADLESS_BROWSER = False` in `config.py` to see the browser actions.
    *   Run the script: `python main.py`
    *   Monitor the output and the browser window. Debug any errors, especially locator issues.
    *   Once working, set `HEADLESS_BROWSER = True` back for automated runs.

## Deployment (Free Options for Daily Runs)

Choose **one** of the following free-tier options:

### Option A: PythonAnywhere (Recommended for Simplicity)

PythonAnywhere offers a free tier suitable for one scheduled task per day.

1.  **Sign Up:** Create a free account at [PythonAnywhere](https://www.pythonanywhere.com/).
2.  **Upload Code:**
    *   Use the "Files" tab to upload your entire project folder (`job_profile_updater/`).
    *   Alternatively, open a "Bash Console" and `git clone` your repository.
3.  **Create Virtual Environment (in PythonAnywhere Bash Console):**
    ```bash
    cd job_profile_updater
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    *   **Note:** WebDriver Download: `webdriver-manager` *might* have issues downloading the driver within the scheduled task environment due to network restrictions on free accounts. Run it once manually in the console to ensure the driver is cached:
        ```bash
        # Still inside the activated venv
        python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
        # Or for Firefox: python -c "from webdriver_manager.firefox import GeckoDriverManager; GeckoDriverManager().install()"
        ```
        If this still causes issues, you might need to adjust `web_updater.py` to point to a pre-installed browser/driver path provided by PythonAnywhere (check their Selenium help pages). Firefox is often recommended on PA.
4.  **Set Environment Variables:**
    *   Go to the "Account" -> "API token" tab (or find Environment Variables settings if they exist) *OR* set them directly in the scheduled task command (see below). For better security, avoid putting them directly visible in the command if possible. PythonAnywhere consoles might support loading `.env` if you use `python-dotenv` correctly, but task scheduling might differ. Check their docs. A common way is to prefix the command:
5.  **Schedule the Task:**
    *   Go to the "Tasks" tab.
    *   Schedule a new "Daily" task.
    *   Set the time to `09:00` (PythonAnywhere uses UTC by default, adjust if your 9 AM is in a different timezone and PA allows timezone specification).
    *   Enter the command. **Adjust paths carefully based on your username and where you uploaded the code:**
        ```bash
        # Example Command - **ADJUST PATHS!**
        export NAUKRI_USERNAME='your_naukri_email@example.com' && export NAUKRI_PASSWORD='your_naukri_password' && cd /home/YourUsername/job_profile_updater && /home/YourUsername/job_profile_updater/venv/bin/python main.py >> /home/YourUsername/job_profile_updater/updater.log 2>&1
        ```
        *   Replace `YourUsername` with your PythonAnywhere username.
        *   Replace credentials with your actual ones (or use PA's secure env var features if available).
        *   `>> .../updater.log 2>&1` redirects output and errors to a log file for debugging.
6.  **Enable & Monitor:** Save the task. Check the log file (`updater.log` in this example) after 9:00 AM UTC the next day to see if it ran correctly.

### Option B: GitHub Actions (More Powerful, Slightly More Complex Setup)

GitHub Actions provides free minutes for public repositories (and a decent amount for private) which is usually sufficient for a short daily script run.

1.  **Push Code to GitHub:** Make sure your code (excluding `.env`!) is pushed to a GitHub repository.
2.  **Set Repository Secrets:**
    *   Go to your GitHub repository -> Settings -> Secrets and variables -> Actions.
    *   Click "New repository secret".
    *   Create secrets named `NAUKRI_USERNAME` and `NAUKRI_PASSWORD` with your credentials. Add secrets for other sites if needed.
3.  **Create Workflow File:**
    *   Create a directory path in your repository: `.github/workflows/`
    *   Create a file inside it named `update_profile.yml` (or any `.yml` name).
    *   Paste the following content:

    ```yaml
    name: Update Job Profiles Daily

    on:
      schedule:
        # Runs at 09:00 UTC every day
        # CRON syntax: minute hour day(month) month day(week)
        - cron: '0 9 * * *'
      workflow_dispatch: # Allows manual triggering from Actions tab

    jobs:
      update_profiles:
        runs-on: ubuntu-latest # Use a Linux runner

        steps:
        - name: Checkout Repository
          uses: actions/checkout@v3

        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.10' # Choose a Python version

        - name: Install Google Chrome # Needed for ChromeDriver
          run: |
            sudo apt-get update
            sudo apt-get install -y google-chrome-stable

        - name: Install Dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt
            # webdriver-manager will download the correct driver for the installed Chrome

        - name: Run Profile Update Script
          env:
            NAUKRI_USERNAME: ${{ secrets.NAUKRI_USERNAME }}
            NAUKRI_PASSWORD: ${{ secrets.NAUKRI_PASSWORD }}
            # Add other secrets here if needed
            # LINKEDIN_USERNAME: ${{ secrets.LINKEDIN_USERNAME }}
            # LINKEDIN_PASSWORD: ${{ secrets.LINKEDIN_PASSWORD }}
          run: |
            # Ensure resumes folder exists relative to script execution
            ls -l # List files for debugging path issues
            python main.py

        # Optional: Upload logs as artifact for debugging
        # - name: Upload Logs
        #   if: always() # Run even if the script fails
        #   uses: actions/upload-artifact@v3
        #   with:
        #      name: update-logs
        #      path: |
        #        *.log
        #        *.png # Upload error screenshots if you implement them
    ```

4.  **Commit and Push:** Commit the `.github/workflows/update_profile.yml` file and push it to your repository.
5.  **Monitor:** The action will automatically trigger based on the `schedule`. You can check the run logs in the "Actions" tab of your GitHub repository. You can also trigger it manually using "workflow_dispatch".

## Expansion

To add support for another website (e.g., LinkedIn):

1.  **Add Credentials:** Add `LINKEDIN_USERNAME` and `LINKEDIN_PASSWORD` to your `.env` file (local) and environment variables / secrets (deployment). Update `config.py` to load them.
2.  **Add Locators:** Create a `LinkedInLocators` class in `locators.py` with the necessary element locators for LinkedIn.
3.  **Create Updater Class:** Create a new file `linkedin_updater.py`. Define a `LinkedInUpdater` class that inherits from `WebUpdater` and implements the `login`, `navigate_to_profile`, `update_optional_fields`, and `update_resume` methods using LinkedIn's specific locators and page flow.
4.  **Update `main.py`:** Import `LinkedInUpdater` and add a section to instantiate and run it, similar to the Naukri section (potentially checking if credentials exist in config).
5.  **Test Thoroughly:** Test the new updater locally before deploying.