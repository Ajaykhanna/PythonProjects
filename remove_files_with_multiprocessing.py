import os
import logging
import argparse
from multiprocessing import Pool
from pathlib import Path
from tqdm import tqdm

# --- Configuration ---
# The base path where all 'frame_*' directories are located
BASE_PATH = "/usr/projects/ml4chem/akhanna2/data/ex_sp"

# The range of frame directories to process
START_FRAME = 1
END_FRAME = 87531

# Number of CPU cores to use for the task
NUM_CORES = 32

# Name of the log file to be created
LOG_FILE = "file_removal.log"
# --- End of Configuration ---


def setup_logging():
    """Configures the logging to file and console."""
    # Overwrite the log file each time
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode="w"),
            logging.StreamHandler(),  # Also print logs to the console
        ],
    )


def process_directory(payload: tuple) -> list[str]:
    """
    Scans a single directory, identifies, and optionally removes target files.
    This function is designed to be sent to a multiprocessing worker.

    Args:
        payload: A tuple containing (dir_path, dry_run_flag).
                 - dir_path (Path): The directory to process.
                 - dry_run_flag (bool): If True, no files will be deleted.

    Returns:
        A list of full paths of the files that were (or would be) removed.
    """
    dir_path, dry_run = payload
    affected_files = []

    # Safety: The script only proceeds if the path is a directory.
    if not dir_path.is_dir():
        return affected_files

    # Use os.scandir for better performance with large directories
    try:
        for entry in os.scandir(dir_path):
            # Safety: We only evaluate files, ignoring subdirectories, symlinks, etc.
            if entry.is_file():
                if entry.name == "coords.xyz" or entry.name.endswith(".out"):
                    # This file matches our criteria.
                    if not dry_run:
                        # --- LIVE DELETION MODE ---
                        try:
                            os.remove(entry.path)
                            affected_files.append(entry.path)
                        except OSError as e:
                            logging.error(f"Could not remove file {entry.path}: {e}")
                    else:
                        # --- DRY RUN MODE ---
                        # We don't delete, just record the file path.
                        affected_files.append(entry.path)
    except Exception as e:
        logging.error(f"Error processing directory {dir_path}: {e}")

    return affected_files


def main():
    """
    Main function to orchestrate the file removal process.
    """
    # Setup command-line argument parsing for the --dry-run flag
    parser = argparse.ArgumentParser(
        description="""A parallel script to remove 'coords.xyz' and '*.out' files 
                     from a range of directories. Always use --dry-run first!"""
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a trial run without deleting any files. Logs what would be removed.",
    )
    args = parser.parse_args()

    setup_logging()
    logging.info("--- Script Started ---")

    # Announce the mode (Dry Run or Live)
    if args.dry_run:
        logging.warning("=" * 50)
        logging.warning("--- DRY RUN MODE ENABLED. NO FILES WILL BE DELETED. ---")
        logging.warning("=" * 50)
    else:
        logging.warning("=" * 50)
        logging.warning(
            "--- LIVE DELETION MODE ENABLED. FILES WILL BE PERMANENTLY REMOVED. ---"
        )
        logging.warning("=" * 50)

    logging.info(f"Using {NUM_CORES} cores to process directories.")
    base_path_obj = Path(BASE_PATH)

    # 1. Verify the base path exists
    logging.info(f"Verifying base path: {base_path_obj}")
    if not base_path_obj.is_dir():
        logging.error(
            f"Error: Base path '{base_path_obj}' does not exist or is not a directory."
        )
        print(f"\nError: Base path '{base_path_obj}' does not exist. Aborting.")
        return

    logging.info("Base path verified successfully.")

    # 2. Generate the tasks for the multiprocessing pool
    # Each task is a tuple: (directory_path, dry_run_status)
    # Safety: By constructing absolute paths, we ensure the script does not
    # wander outside the intended base directory.
    dirs_to_process = [
        base_path_obj / f"frame_{i}" for i in range(START_FRAME, END_FRAME + 1)
    ]
    tasks = [(dir_path, args.dry_run) for dir_path in dirs_to_process]

    logging.info(
        f"Generated {len(tasks)} tasks to scan directories from frame_{START_FRAME} to frame_{END_FRAME}."
    )

    # 3. Use multiprocessing to process directories
    logging.info("Starting parallel file processing...")

    all_affected_files = []

    # Create a pool of worker processes
    with Pool(processes=NUM_CORES) as pool:
        # imap_unordered is efficient as the completion order doesn't matter.
        # tqdm provides a real-time progress bar.
        results_iterator = pool.imap_unordered(process_directory, tasks)

        for result_list in tqdm(
            results_iterator, total=len(tasks), desc="Processing Directories"
        ):
            if result_list:
                all_affected_files.extend(result_list)

    # 4. Log the final results
    logging.info("--- Processing Complete ---")

    total_affected = len(all_affected_files)

    # Tailor the summary message based on the run mode
    if args.dry_run:
        summary_verb = "found for removal"
        log_header = "--- List of Files That Would Be Removed ---"
    else:
        summary_verb = "successfully removed"
        log_header = "--- List of Files That Were Removed ---"

    if total_affected > 0:
        logging.info(f"{summary_verb.title()} a total of {total_affected} files.")
        logging.info(log_header)
        # Log each file path for a complete record
        for file_path in sorted(all_affected_files):
            logging.info(file_path)
    else:
        logging.info("No matching files were found to process.")

    logging.info(f"--- Summary ---")
    logging.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE DELETION'}")
    logging.info(f"Total directories scanned: {len(tasks)}")
    logging.info(f"Total files {summary_verb}: {total_affected}")
    logging.info(f"A detailed log is available at: '{LOG_FILE}'")
    print(f"\nProcess finished. A detailed log is available at: {LOG_FILE}")


if __name__ == "__main__":
    # This check is crucial for multiprocessing to work correctly,
    # especially on Windows and macOS.
    main()
