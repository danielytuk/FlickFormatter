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
# Store a list of TMDB API keys for redundancy in case one API key is exhausted or fails.
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
# Functions to display colored messages in the terminal for success, error, or info.
def print_success(message):
    print(f"\033[92m[SUCCESS]\033[0m {message}")

def print_error(message):
    print(f"\033[91m[ERROR]\033[0m {message}")

def print_info(message):
    print(f"\033[94m[INFO]\033[0m {message}")

# Get a random API key (optimized for reuse)
# Fetches a random TMDB API key, but caches the key to avoid frequent re-fetching.
api_key_cache = None
def get_api_key():
    global api_key_cache
    if not api_key_cache:
        api_key_cache = random.choice(CONFIG["TMDB_API_KEYS"])  # Cache the API key for future use
    return api_key_cache

# File extension validation
# Set of allowed video file extensions for processing.
ALLOWED_EXTENSIONS = {".webm", ".mkv", ".flv", ".vob", ".ogv", ".ogg", ".mov", ".avi", ".qt", ".wmv",
                       ".yuv", ".rm", ".asf", ".amv", ".mp4", ".m4p", ".m4v", ".mpg", ".mpeg", ".mpe",
                       ".mpv", ".svi", ".3gp", ".3g2", ".mxf", ".roq", ".nsv", ".f4v", ".f4p", ".f4a", ".f4b"}

# Check if a file is a TV show based on its name
# Uses a regex to identify file names in the format SxxExx (Season and Episode).
def is_tv_show(filename):
    return bool(re.search(r"S\d{2}E\d{2}", filename, re.IGNORECASE))

# Sanitize file or folder names by removing special characters and unnecessary whitespaces
def sanitize_name(name, keep_special_characters=True):
    # Removes any trailing spaces, dashes, or year information (like "(2020)")
    name = re.sub(r"\s?\(\d{4}\)\s?-?$", "", name.strip().rstrip('-').strip())
    
    # Optionally remove special characters
    if not keep_special_characters:
        name = re.sub(r"[^\w\s]", "", name)
    
    # Replace multiple spaces with one
    return re.sub(r"\s+", " ", name).strip()

# Update file creation and modification dates to match the provided release date
def update_file_date(file_path, release_date):
    try:
        # Convert release date string to timestamp
        mod_time = datetime.datetime.strptime(release_date, "%Y-%m-%d").timestamp()
        os.utime(file_path, (mod_time, mod_time))  # Update file timestamps
        print_success(f"Updated file date to {release_date} for: {file_path}")
    except Exception as e:
        print_error(f"Could not update file date: {e}")

# Rename a file and move it to a new path
def rename_file(old_path, new_path, release_date=None):
    try:
        # Convert paths to Path objects for better handling
        old_path, new_path = Path(old_path), Path(new_path)
        
        # Ensure destination directory exists
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rename and move the file
        shutil.move(str(old_path), str(new_path))
        print_success(f"Renamed: {old_path} -> {new_path}")
        
        # Optionally update file creation/modification date if provided
        if release_date:
            update_file_date(new_path, release_date)
    except Exception as e:
        print_error(f"Error renaming {old_path} -> {new_path}: {e}")

# Fetch data from TMDB API (with optimized error handling)
def fetch_tmdb_data(endpoint, params):
    try:
        params["api_key"] = get_api_key()  # Add API key to the request
        response = requests.get(f"https://api.themoviedb.org/3/{endpoint}", params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Return the JSON response
    except Exception as e:
        print_error(f"TMDB API error: {e}")  # Handle API request errors
        return None

# Fetch episode details from TMDB by first searching for the show and then retrieving episode info
def fetch_episode_details(show_name, season, episode):
    # Search for the TV show by its name
    search_data = fetch_tmdb_data("search/tv", {"query": sanitize_name(show_name, False)})
    if not search_data or not search_data.get("results"):
        print_error(f"Show not found: {show_name}")
        return None, None

    # Get the show ID from the search results
    show_id = search_data["results"][0]["id"]
    
    # Fetch specific episode details
    episode_data = fetch_tmdb_data(f"tv/{show_id}/season/{season}/episode/{episode}", {})
    if episode_data:
        return episode_data.get("name"), episode_data.get("air_date")  # Return episode name and release date
    return None, None

# Process TV show files: Extract show, season, and episode from file name, fetch details, and rename
def process_tv_show(file_name, file_path, file_ext, save_path):
    match = re.match(r"(.*?)[. ]S(\d{2})E(\d{2})", file_name, re.IGNORECASE)
    if not match:
        return  # If the file name doesn't match the TV show pattern, return

    # Extract show name, season, and episode from the file name
    show_name, season, episode = match.groups()
    
    # Fetch episode details (name and release date) from TMDB
    episode_name, release_date = fetch_episode_details(show_name, season, episode)
    episode_name = episode_name or f"Episode {episode}"  # Default to "Episode X" if no name is found

    # Sanitize episode name and construct the new file name
    episode_name = sanitize_name(episode_name, keep_special_characters=False)
    new_name = f"S{season}E{episode} - {episode_name}{file_ext}"

    # Organize into show folder, season folder, and new file path
    show_folder = Path(save_path) / sanitize_name(show_name)
    season_folder = show_folder / f"Season {int(season)}"
    new_path = season_folder / new_name

    # Rename the file to the new path and update its date
    rename_file(file_path, new_path, release_date)

# Process movie files: Sanitize movie name and rename the file
def process_movie(file_name, file_path, file_ext, save_path):
    sanitized_name = sanitize_name(file_name, keep_special_characters=False)
    new_name = f"{sanitized_name}{file_ext}"
    new_path = Path(save_path) / new_name
    rename_file(file_path, new_path)

# Main function to rename and organize files
def rename_files(file_paths, save_path):
    for file_path in file_paths:
        file_path = Path(file_path)  # Convert to Path object for better handling
        file_name, file_ext = file_path.stem, file_path.suffix

        if file_ext.lower() in ALLOWED_EXTENSIONS:  # Process only allowed video files
            if is_tv_show(file_name):  # If it's a TV show, process accordingly
                process_tv_show(file_name, str(file_path), file_ext, save_path)
            else:  # Otherwise, process as a movie
                process_movie(file_name, str(file_path), file_ext, save_path)

    print_success("Renaming completed!")  # Print completion message

# Folder or file selection using Tkinter GUI
def select_files_or_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    while True:
        print_info("Enter the option you want:\n\n> 1: Select files.\n> 2: Select directory.")
        choice = input("> ").strip()

        if choice == "1":
            # Allow the user to select multiple files
            file_paths = filedialog.askopenfilenames(title="Select Files")
            return list(file_paths), None
        elif choice == "2":
            # Allow the user to select a directory
            folder_path = filedialog.askdirectory(title="Select Directory")
            return None, folder_path
        else:
            print_error("Invalid input. Please enter 1 or 2.")

# Main entry point for the program
def main():
    print_info("Welcome to FlickFormatter!")  # Display welcome message
    file_paths, folder_path = select_files_or_folder()  # Get user input for files or folder

    if file_paths:
        save_path = Path(file_paths[0]).parent  # Save path is the directory of the first file
        print_info(f"Processing files: {file_paths}")
        rename_files(file_paths, save_path)  # Rename and organize selected files
    elif folder_path:
        print_info(f"Processing directory: {folder_path}")
        rename_files(Path(folder_path).rglob("*"), folder_path)  # Process all files in the selected directory
    else:
        print_error("No files or folder selected. Exiting.")  # Handle case where no files/folder is selected

# Entry point for executing the script
if __name__ == "__main__":
    main()  # Run the main function when the script is executed
