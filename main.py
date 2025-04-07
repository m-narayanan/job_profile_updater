import logging
import sys
import os # Added for potential path debugging

import config
from naukri_updater import NaukriUpdater
# Import other updaters here when you add them
# from linkedin_updater import LinkedInUpdater

# Configure logging (ensure it's set up before first log message)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting job profile update process...")
    logging.info(f"Current working directory: {os.getcwd()}") # Log CWD for path context

    try:
        config.validate_config()
    except (ValueError, FileNotFoundError) as e:
        logging.error(f"Configuration error: {e}")
        sys.exit(1) # Exit if essential config is missing

    updater_classes = {
        "Naukri": NaukriUpdater,
        # "LinkedIn": LinkedInUpdater, # Example for expansion
    }

    overall_success = True

    for site_name, UpdaterClass in updater_classes.items():
        logging.info("="*20 + f" Processing {site_name} " + "="*20)
        updater_instance = None # Define outside try block for potential cleanup

        try:
            # Dynamically get credentials from config based on site name (requires convention)
            username = getattr(config, f"{site_name.upper()}_USERNAME", None)
            password = getattr(config, f"{site_name.upper()}_PASSWORD", None)

            if not username or not password:
                logging.warning(f"Credentials for {site_name} not found in config, skipping.")
                continue # Skip to the next site

            updater_instance = UpdaterClass(
                username=username,
                password=password,
                headless=config.HEADLESS_BROWSER
            )

            success = updater_instance.run_update()

            if success:
                logging.info(f"{site_name} update attempt finished successfully.")
            else:
                logging.error(f"{site_name} update attempt finished with errors.")
                overall_success = False # Mark overall process as failed if any site fails

        except Exception as e:
            logging.error(f"A critical error occurred while processing {site_name}: {e}", exc_info=True)
            overall_success = False
            # Ensure driver is quit even if run_update fails before the finally block
            if updater_instance and updater_instance.driver:
                 logging.info(f"Attempting to quit driver for {site_name} after critical error.")
                 updater_instance.driver.quit()

    logging.info("="*50)
    if overall_success:
        logging.info("Job profile update process finished successfully for all configured sites.")
    else:
         logging.error("Job profile update process finished with errors for one or more sites.")
         # sys.exit(1) # Optionally exit with error code if any part failed

if __name__ == "__main__":
    main()