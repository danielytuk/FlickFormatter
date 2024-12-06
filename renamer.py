import os
import re
import random
import tkinter as tk
from tkinter import filedialog
import shutil
import requests
import datetime
from pathlib import Path

# Configurations
# Configuration dictionary to store multiple TMDB API keys for redundancy.
CONFIG = {
    "TMDB_API_KEYS": [
        "516adf1e1567058f8ecbf30bf2eb9378",
        "3fd2be6f0c70a2a598f084ddfb75487c",
        "aa8b43b8cbce9d1689bef3d0c3087e4d",
        "b0d65862c66030895d7983da2bd70edd",
        "eaa6c99bdd160a89bc0a44998ead7bca",
        "0f79586eb9d92afa2b7266f7928b055c",
        "d3449ff6ec0c027623bf6b6f5fff78b3",
        "94a2f36cd4e27626b6a7a07766a76196",
        "9e59d7e445e31611f16d8971a4277825",
        "6b4357c41d9c606e4d7ebe2f4a8850ea",
        "6bfaa39b0a3a25275c765dcaddc7dae7",
        "1155f6c239cb4332df695fcf245eaffd",
        "d3449ff6ec0c027623bf6b6f5fff78b3",
        "94a2f36cd4e27626b6a7a07766a76196",
        "6b4357c41d9c606e4d7ebe2f4a8850ea",
        "cfe422613b250f702980a3bbf9e90716",
        "94a2f36cd4e27626b6a7a07766a76196",
        "2c106eb9d82d561f7090feb22090c32d",
        "a07e22bc18f5cb106bfe4cc1f83ad8ed",
        "c47afb8e8b27906bca710175d6e8ba68",
        "befc21d948862259da6f029c54831a9c",
        "3aa350912efdcc79b7c8fddde2759632",
        "1bb03dcadd1803cf79af629648c59d38",
        "97058a18f3b899a2e57452cec18ee321",
        "137ae6e9c8732b7ea556dcfb16a57a90",
        "d5377a22f42e52f7751e9f670fdc59d8",
        "9eecc30ae89f253bce3cec4140734493",
        "7f8da833ce630e3dc28ae7d33c4c1e74",
        "224e333f115738001bf7d78be3c219f4",
    ]
}

# Utility functions for colored output
# These functions provide colored terminal output for success, error, and info messages.

def print_success(message):
    """Print a success message in green."""
    print(f"\033[92m[SUCCESS]\033[0m {message}")

def print_error(message):
    """Print an error message in red."""
    print(f"\033[91m[ERROR]\033[0m {message}")

def print_info(message):
    """Print an informational message in blue."""
    print(f"\033[94m[INFO]\033[0m {message}")

# Get a random API key
def get_random_api_key():
    """Retrieve a random TMDB API key from the configuration."""
    return random.choice(CONFIG["TMDB_API_KEYS"])

# File extension validation
# List of allowed video file extensions for processing.
ALLOWED_EXTENSIONS = {
    ".webm", ".mkv", ".flv", ".vob", ".ogv", ".ogg", ".mov", ".avi", ".qt", ".wmv",
    ".yuv", ".rm", ".asf", ".amv", ".mp4", ".m4p", ".m4v", ".mpg", ".mpeg", ".mpe",
    ".mpv", ".svi", ".3gp", ".3g2", ".mxf", ".roq", ".nsv", ".f4v", ".f4p", ".f4a", ".f4b"
}

# Check if the file is a TV show
def is_tv_show(filename):
    """
    Determine if a file name matches the pattern of a TV show episode.
    Example pattern: S01E01 (Season 1, Episode 1).
    """
    return bool(re.search(r"S\d{2}E\d{2}", filename, re.IGNORECASE))

# Sanitize filenames
def sanitize_name(name, keep_special_characters=True):
    """
    Clean up and standardize file or folder names.
    - Removes extra spaces, trailing dashes, or year information in parentheses.
    - Optionally removes special characters.
    """
    name = name.strip().rstrip('-').strip()
    name = re.sub(r"\s?\(\d{4}\)\s?-?$", "", name)  # Remove year in parentheses
    if not keep_special_characters:
        name = re.sub(r"[^\w\s]", "", name)  # Remove special characters
    name = re.sub(r"\s+", " ", name).strip()  # Replace multiple spaces with one
    return name

# Update file creation and modification date
def update_file_date(file_path, release_date):
    """
    Update the file's creation and modification date to match the release date.
    - Uses `os.utime` to set the timestamps.
    """
    try:
        date_obj = datetime.datetime.strptime(release_date, "%Y-%m-%d")
        mod_time = date_obj.timestamp()
        os.utime(file_path, (mod_time, mod_time))
        print_success(f"Updated file date to {release_date} for: {file_path}")
    except Exception as e:
        print_error(f"Could not update file date: {e}")

# Rename a file
def rename_file(old_path, new_path, release_date=None):
    """
    Rename a file and optionally update its creation/modification date.
    - Ensures the destination directory exists before renaming.
    """
    try:
        # Convert paths to Path objects for consistent handling
        old_path = Path(old_path)
        new_path = Path(new_path)

        # Ensure the destination directory exists
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Perform the file rename
        shutil.move(str(old_path), str(new_path))
        print_success(f"Renamed: {old_path} -> {new_path}")
        if release_date:
            update_file_date(new_path, release_date)
    except Exception as e:
        print_error(f"Error renaming {old_path} -> {new_path}: {e}")

# Fetch episode or movie details from TMDB
def fetch_tmdb_data(endpoint, params):
    """
    Fetch data from the TMDB API.
    - `endpoint`: API endpoint to query (e.g., "search/tv").
    - `params`: Dictionary of query parameters.
    """
    try:
        api_key = get_random_api_key()
        params["api_key"] = api_key
        response = requests.get(f"https://api.themoviedb.org/3/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print_error(f"TMDB API error: {e}")
        return None

# Fetch episode name and release date
def fetch_episode_details(show_name, season, episode):
    """
    Retrieve episode details (name and air date) from TMDB.
    - First, searches for the TV show by name.
    - Then, fetches specific episode details.
    """
    search_data = fetch_tmdb_data("search/tv", {"query": sanitize_name(show_name, False)})
    if not search_data or not search_data.get("results"):
        print_error(f"Show not found: {show_name}")
        return None, None

    show_id = search_data["results"][0]["id"]
    episode_data = fetch_tmdb_data(f"tv/{show_id}/season/{season}/episode/{episode}", {})
    if episode_data:
        return episode_data.get("name"), episode_data.get("air_date")
    return None, None

# Handle TV show files
def process_tv_show(file_name, file_path, file_ext, save_path):
    """
    Process TV show files:
    - Extract show name, season, and episode number from the file name.
    - Fetch episode details from TMDB.
    - Rename the file in a standardized format and organize it into folders.
    """
    match = re.match(r"(.*?)[. ]S(\d{2})E(\d{2})", file_name, re.IGNORECASE)
    if not match:
        return

    show_name, season, episode = match.groups()
    episode_name, release_date = fetch_episode_details(show_name, season, episode)
    episode_name = episode_name or f"Episode {episode}"

    # Sanitize episode name and construct new path
    episode_name = sanitize_name(episode_name, keep_special_characters=False)
    new_name = f"S{season}E{episode} - {episode_name}{file_ext}"

    show_folder = Path(save_path) / sanitize_name(show_name)
    season_folder = show_folder / f"Season {int(season)}"
    new_path = season_folder / new_name

    rename_file(file_path, new_path, release_date)

# Handle movie files
def process_movie(file_name, file_path, file_ext, save_path):
    """
    Process movie files:
    - Sanitize the movie name.
    - Rename and move the file to the save path.
    """
    sanitized_name = sanitize_name(file_name, keep_special_characters=False)
    new_name = f"{sanitized_name}{file_ext}"
    new_path = Path(save_path) / new_name
    rename_file(file_path, new_path)

# Process files
def rename_files(file_paths, save_path):
    """
    Process a list of files:
    - Identify whether each file is a TV show or a movie.
    - Rename and organize the files accordingly.
    """
    for file_path in file_paths:
        file_path = Path(file_path)
        file_name, file_ext = file_path.stem, file_path.suffix

        if file_ext.lower() in ALLOWED_EXTENSIONS:
            if is_tv_show(file_name):
                process_tv_show(file_name, str(file_path), file_ext, save_path)
            else:
                process_movie(file_name, str(file_path), file_ext, save_path)

    print_success("Renaming completed!")

# Folder selection using Tkinter
def select_files_or_folder():
    """
    Use Tkinter to allow the user to select files or a directory for processing.
    Returns the selected file paths or folder path.
    """
    root = tk.Tk()
    root.withdraw()

    while True:
        print_info("Enter the option you want:\n\n> 1: Select files.\n> 2: Select directory.")
        choice = input("> ").strip()

        if choice == "1":
            file_paths = filedialog.askopenfilenames(title="Select Files")
            return list(file_paths), None
        elif choice == "2":
            folder_path = filedialog.askdirectory(title="Select Directory")
            return None, folder_path
        else:
            print_error("Invalid input. Please enter 1 or 2.")

# Main function
def main():
    """
    Main entry point for the program:
    - Handles user input for selecting files or folders.
    - Processes and renames the selected files.
    """
    print_info("Welcome to FlickFormatter!")
    file_paths, folder_path = select_files_or_folder()

    if file_paths:
        save_path = Path(file_paths[0]).parent  # Use the folder of the selected files
        print_info(f"Processing files: {file_paths}")
        rename_files(file_paths, save_path)
    elif folder_path:
        print_info(f"Processing directory: {folder_path}")
        rename_files(Path(folder_path).rglob("*"), folder_path)  # Recursive search
    else:
        print_error("No files or folder selected. Exiting.")

# Run the program
if __name__ == "__main__":
    main()
