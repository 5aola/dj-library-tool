# dj-library-tool
An open-source audio library tool for electronic music analysis for DJs.

## Features
- BPM and key estimation, the results are added to the title of the audio.
- The key estimation is in camelot key notation for easy usage.
- If it isn't already in MP3 format, it converts to 320kbps MP3. It keeps the originals and move it to a separate folder (default: originals).

## Installation

Create and activate a venv

```bash
pip install -r requirements.txt
```

## Easiest Usage
```bash
run.py --dir path/to/music/directory --model path/to/TempoCNN/model
```

## Parameters
```md
options:
  -h, --help            show this help message and exit
  --dir DIR             Directory to analyze.
  --model MODEL         Path to the TempoCNN model file.
  --bpm_limits MIN MAX  Specify min and max BPM, e.g. --bpm_limits 90 180
  --safe_folder SAFE_FOLDER
                        Folder where all original files will be moved, this
                        won't be analized.
  --bitrate BITRATE     Bitrate for MP3 conversion. Examples: 192k, 256k, 320k
  --num_threads NUM_THREADS
                        Number of threads for multiprocessing.
```
