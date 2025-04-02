#!/usr/bin/env python3
# This script deletes specific files in a given directory and its subdirectories.

import os


def delete_files(target_dir, extensions, specific_files):
    """
    Deletes files with given extensions and specific filenames in the target directory (recursively).
    Prints the path of each deleted file.

    Args:
        target_dir (str): The root directory to search.
        extensions (list): List of file extensions to delete (e.g., [".qlog", ".sbatch"]).
        specific_files (list): List of exact filenames to delete (e.g., ["fort.7"]).
    """
    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist.")
        return

    deleted_count = 0

    for root, _, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)

            # Check if the file matches any of the extensions or specific filenames
            if any(file.endswith(ext) for ext in extensions) or file in specific_files:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

    print(f"\nTotal files deleted: {deleted_count}")


if __name__ == "__main__":
    # Define the target directory
    TARGET_DIR = "/scratch/akhanna2/teraChem_jobs/tests/pi_cisborn"

    # Define file extensions and specific filenames to delete
    EXTENSIONS = [".qlog", ".sbatch", ".sub"]
    SPECIFIC_FILES = ["fort.7"]

    delete_files(TARGET_DIR, EXTENSIONS, SPECIFIC_FILES)
