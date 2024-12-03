# FlickFormatter

**Coded and Tested on Windows 11 24H2**

## Features
- Automatically renames TV shows and movies based on metadata from TMDB.
- Supports a wide variety of video file formats.
- Updates file creation and modification dates to match the release dates.
- Organizes TV shows into folders by show and season.

## Installation

1. Download the executable from the [Releases](https://github.com/danielytuk/FlickFormatter/releases) page.
2. Run the executable to launch the application.

## Usage

1. **Select Folder**: When you run the program, a file dialog will appear. Select the folder containing your media files.
2. The program will automatically process the files, renaming them based on metadata fetched from TMDB.
3. TV shows will be organized into folders by show and season, and movie files will be renamed with their proper titles.
4. The program will update the creation and modification dates of the files to match the release dates (if available).

### Example of File Renaming:

- Before: `Superman.and.Lois.S01E01.1080p.WEB.h264-EDITH.mkv`
- After: `S01E01 - Pilot.mkv` (organized in a folder structure like `Superman & Lois (2021)/Season 1/`)

## How It Works

1. **TV Shows**: The program detects TV show episodes by looking for patterns like `S01E01` in the filename. It then fetches episode details such as the name and air date using the TMDB API.
   
2. **Movies**: For movie files, the program cleans up the filename and uses the TMDB API to ensure the movie's name is properly formatted.

3. **API Keys**: The program uses multiple TMDB API keys for load balancing. It randomly selects an API key for each request to avoid hitting rate limits.

## Requirements

- The executable includes all necessary dependencies, so no additional installation is required.
- An active internet connection is required to fetch metadata from TMDB.

## Building from Source

If you want to build the program from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/danielytuk/FlickFormatter.git
   cd yourrepo
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the program:
   ```bash
   python renamer.py
   ```

## Contributing

Feel free to submit issues or pull requests if you want to contribute to the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Note: This project uses the TMDB API but is not endorsed or certified by TMDB.*
