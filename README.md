# DJ Library Tool
An open-source audio library tool that helps DJs avoid compatibility issues between different software.

## Features
- BPM and Key estimation added to the songs title and meta as well (i. e. `[123-06A] audiofilename.mp3`).
- The key estimation is in camelot key notation for easy usage.
- Converts everything to mp3. It keeps the original files and move it to a separate, safe folder (default: originals).
- Supported formats: wav, mp3, flac, aif

## Installation
Create and activate a virtual environment

```bash
pip install -r requirements.txt
```

## Easiest Usage
```bash
run.py --dir path/to/music/directory --model path/to/TempoCNN/model
```

## Optional Parameters
```md
options:
  -h, --help            show this help message and exit
  --dir DIR             Directory to analyze.
  --no_camelot          Add this to not use Camelot notation for key estimation.
  --model MODEL         Path to the TempoCNN model file.
  --bpm_limits MIN MAX  Specify min and max BPM, e.g. --bpm_limits 90 180
  --safe_folder SAFE_FOLDER
                        Folder where all original files will be moved, this
                        won't be analized.
  --bitrate BITRATE     Bitrate for MP3 conversion. e.g. --bitrate 320k
  --num_threads NUM_THREADS
                        Number of threads for multiprocessing.
```
