# DJ Library Tool
An open-source audio library tool that helps DJs avoid compatibility issues between different software.

## Features
- BPM and Key estimation with Essentia's pre-trained CNN models – similar accuracy to Rekordbox, better than Serato DJ.
- The estimations are automatically added to the songs' title and meta (e.g. `[123-06A] audiofilename.mp3`).
- The key estimation is in camelot key notation by default for easy usage.
- Converts everything to mp3. It keeps the original files and move them into a separate folder (default: /originals).
- Supported formats: wav, mp3, flac, aif

## Installation
Create and activate a virtual environment

```bash
pip install -r requirements.txt
```

## Usage
```bash
run.py --dir path/to/music/directory
```

## Parameters
```md
options:
  -h, --help            show this help message and exit
  --dir DIR             Directory to analyze.
  --no_camelot          Add this to keep the musical notation for key estimation.
  --model MODEL         Path to the TempoCNN model file.
  --bpm_limits MIN MAX  Specify min and max BPM to help the estimations, e.g. --bpm_limits 90 180
  --safe_folder SAFE_FOLDER
                        Folder where all original files will be moved, this
                        won't be analized.
  --bitrate BITRATE     Bitrate for MP3 conversion, e.g. --bitrate 320k
```
