import os
import re
import random
import tkinter as tk
from tkinter import filedialog
import shutil
import requests
import datetime
from pathlib import Path

# A BOAT LOAD OF KEYS
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

# UTIL FUNCS FOR COLOURED OUTPUT
def print_success(message):
    print(f"\033[92m[SUCCESS]\033[0m {message}")

def print_error(message):
    print(f"\033[91m[ERROR]\033[0m {message}")

def print_info(message):
    print(f"\033[94m[INFO]\033[0m {message}")

# RANDOM KEY
def get_random_api_key():
    return random.choice(CONFIG["TMDB_API_KEYS"])

# EXT VAILDATION
ALLOWED_EXTENSIONS = {
    ".webm", ".mkv", ".flv", ".vob", ".ogv", ".ogg", ".mov", ".avi", ".qt", ".wmv",
    ".yuv", ".rm", ".asf", ".amv", ".mp4", ".m4p", ".m4v", ".mpg", ".mpeg", ".mpe",
    ".mpv", ".svi", ".3gp", ".3g2", ".mxf", ".roq", ".nsv", ".f4v", ".f4p", ".f4a", ".f4b"
}

# TV SHOW CHECK
def is_tv_show(filename):
    return bool(re.search(r"S\d{2}E\d{2}", filename, re.IGNORECASE))

# SANITISE FILENAME
def sanitize_name(name, keep_special_characters=True):
    name = name.strip().rstrip('-').strip()
    name = re.sub(r"\s?\(\d{4}\)\s?-?$", "", name)  # Remove year in parentheses
    return re.sub(r"[^\w\s]" if not keep_special_characters else r"\s+", " ", name).strip()

# UPDATE CREATION/MODIFICATION TO REL DATE
def update_file_date(file_path, release_date):
    try:
        date_obj = datetime.datetime.strptime(release_date, "%Y-%m-%d")
        mod_time = date_obj.timestamp()
        os.utime(file_path, (mod_time, mod_time))
        print_success(f"Updated file date to {release_date} for: {file_path}")
    except Exception as e:
        print_error(f"Could not update file date: {e}")

# RENAMER
def rename_file(old_path, new_path, release_date=None):
    try:
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)
        print_success(f"Renamed: {old_path} -> {new_path}")
        if release_date:
            update_file_date(new_path, release_date)
    except Exception as e:
        print_error(f"Error renaming {old_path} -> {new_path}: {e}")

# FETCH DETAILS TMDB
def fetch_tmdb_data(endpoint, params):
    try:
        api_key = get_random_api_key()
        params["api_key"] = api_key
        response = requests.get(f"https://api.themoviedb.org/3/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print_error(f"TMDB API error: {e}")
        return None

# Fetch EP.NAME & REL DATE
def fetch_episode_details(show_name, season, episode):
    search_data = fetch_tmdb_data("search/tv", {"query": sanitize_name(show_name, False)})
    if not search_data or not search_data.get("results"):
        print_error(f"Show not found: {show_name}")
        return None, None

    show_id = search_data["results"][0]["id"]
    episode_data = fetch_tmdb_data(f"tv/{show_id}/season/{season}/episode/{episode}", {})
    if episode_data:
        return episode_data.get("name"), episode_data.get("air_date")
    return None, None

# PROCESS TV
def process_tv_show(file_name, file_path, file_ext, save_path):
    match = re.match(r"(.*?)[. ]S(\d{2})E(\d{2})", file_name, re.IGNORECASE)
    if not match:
        return

    show_name, season, episode = match.groups()
    episode_name, release_date = fetch_episode_details(show_name, season, episode)
    episode_name = episode_name or f"Episode {episode}"
    new_name = f"S{season}E{episode} - {episode_name}{file_ext}"

    show_folder = os.path.join(save_path, sanitize_name(show_name))
    season_folder = os.path.join(show_folder, f"Season {int(season)}")
    new_path = os.path.join(season_folder, new_name)

    rename_file(file_path, new_path, release_date)

# PROCESS MOVIE
def process_movie(file_name, file_path, file_ext, save_path):
    sanitized_name = sanitize_name(file_name, keep_special_characters=False)
    new_name = f"{sanitized_name}{file_ext}"
    new_path = os.path.join(save_path, new_name)
    rename_file(file_path, new_path)

# START RENAMING
def rename_files(base_path, save_path):
    if not base_path:
        print_error("No folder selected.")
        return

    for root_dir, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root_dir, file)
            file_name, file_ext = os.path.splitext(file)

            if file_ext.lower() in ALLOWED_EXTENSIONS:
                if is_tv_show(file_name):
                    process_tv_show(file_name, file_path, file_ext, save_path)
                else:
                    process_movie(file_name, file_path, file_ext, save_path)

    print_success("Renaming completed!")

# FOLDER SELC w/TKINTER
def select_folder():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Select Folder with Files to Rename")

def main():
    print_info("Select the folder containing your media files.")
    base_path = select_folder()
    if not base_path:
        print_error("No folder selected. Exiting.")
        return

    save_path = base_path
    print_info(f"Processing files in: {base_path}")
    rename_files(base_path, save_path)

if __name__ == "__main__":
    main()
