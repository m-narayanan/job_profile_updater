import os
import glob
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_latest_resume(folder_path: str) -> str | None:
    """
    Finds the most recently modified resume file (.pdf, .doc, .docx) in a folder.

    Args:
        folder_path: The absolute path to the folder containing resumes.

    Returns:
        The absolute path to the latest resume file, or None if no suitable file is found.
    """
    allowed_extensions = ("*.pdf", "*.doc", "*.docx")
    resume_files = []
    for ext in allowed_extensions:
        # Use recursive=False if you only want files directly in the folder, not subfolders
        resume_files.extend(glob.glob(os.path.join(folder_path, ext), recursive=False))

    if not resume_files:
        logging.warning(f"No resume files (.pdf, .doc, .docx) found directly in {folder_path}")
        return None

    try:
        # Filter out directories just in case glob picks them up somehow
        files_only = [f for f in resume_files if os.path.isfile(f)]
        if not files_only:
            logging.warning(f"No actual resume files found (checked isfile) in {folder_path}")
            return None

        latest_file = max(files_only, key=os.path.getmtime)
        logging.info(f"Found latest resume: {os.path.basename(latest_file)}")
        return os.path.abspath(latest_file) # Ensure absolute path for Selenium
    except ValueError: # Handles case where files_only is empty after filtering
         logging.warning(f"No valid resume files found after isfile check in {folder_path}")
         return None
    except Exception as e:
        logging.error(f"Error finding latest resume: {e}")
        return None

def toggle_full_stop(text: str) -> str:
    """Adds a full stop if one doesn't exist at the end, or removes it if it does."""
    if not text:
        return "." # Add one if empty
    stripped_text = text.strip() # Use strip() to handle leading/trailing whitespace
    if not stripped_text: # If text was only whitespace
        return "."
    if stripped_text.endswith('.'):
        return stripped_text[:-1].strip() # Remove trailing dot and any space before it
    else:
        return stripped_text + '.'