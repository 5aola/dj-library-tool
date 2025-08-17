#! .venv/bin/python

import essentia
essentia.log.infoActive = False

from essentia.standard import TempoCNN, KeyExtractor
import argparse
import os
from tqdm import tqdm
import numpy as np  
import librosa
import shutil
import music_tag
from pydub import AudioSegment
from pathlib import Path
from multiprocessing import Pool


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def conv_to_camelot_key(music_key: str) -> str:
    camelot_wheel = {
        "C major": "08B", "G major": "09B", "D major": "10B", "A major": "11B", "E major": "12B",
        "B major": "01B", "F# major": "02B", "C# major": "03B", "Ab major": "04B", "Eb major": "05B",
        "Bb major": "06B", "F major": "07B",

        "A minor": "08A", "E minor": "09A", "B minor": "10A", "F# minor": "11A", "C# minor": "12A",
        "Ab minor": "01A", "Eb minor": "02A", "Bb minor": "03A", "F minor": "04A", "C minor": "05A",
        "G minor": "06A", "D minor": "07A"
    }
    return camelot_wheel.get(music_key, "NAN")


class Analyzer:
    def __init__(
        self, 
        bpm_limits = (90, 180), 
        safe_folder = "originals",
        sample_rate = 11025,
        bitrate = "320k",
        TempoCNN_path = "deeptemp-k16-3.pb",
        num_threads = 8
        ):
        
        self.supported_extensions = (".wav", ".mp3", ".flac", ".aif")
        self.bitrate = bitrate
        self.num_threads = num_threads
        self.model_path = TempoCNN_path
        self.bpm_limits = bpm_limits
        self.sr = sample_rate
        self.dir = ""
        self.safe_dir = os.path.join(self.dir, safe_folder)
        
        
    def _update_directory(self, dir: str):
        self.dir = dir
        self.safe_dir = os.path.join(self.dir, os.path.basename(self.safe_dir))
        
        
    def _estimate_bpm(self, audio):
        sbpm = TempoCNN(graphFilename=self.model_path)
        bpm, all, conf = sbpm(audio)
        filtered_bpms = [(value, confidence) for value, confidence in zip(all, conf) 
                         if confidence > 0.2 and self.bpm_limits[0] <= value <= self.bpm_limits[1]]
        
        if filtered_bpms:
            unique_values, counts = np.unique([value for value, _ in filtered_bpms], return_counts=True)
            
            if len(unique_values) == len(filtered_bpms):  # All BPMs are unique
                highest_confidence_bpm = max(filtered_bpms, key=lambda x: x[1])[0]
                return highest_confidence_bpm
            
            # sort by frequency
            sorted_indices = np.argsort(-counts)
            sorted_bpms = unique_values[sorted_indices]
            
            return sorted_bpms[0]
        
        return bpm
    
    
    def _estimate_key(self, audio):
        skey = KeyExtractor(
            sampleRate=self.sr,
            profileType='edma',
            hpcpSize=120,
        )
        key, scale, _ = skey(audio)
        return f"{key} {scale}"
    
    
    def _collect_all_files(self):
        all_files = []
        for root, _, files in os.walk(self.dir):
                for file in files:
                    if file.endswith(self.supported_extensions) and root != self.safe_dir:
                        audio_path = os.path.join(root, file)
                        all_files.append(audio_path)
        return all_files
    
    
    def _clean_name(self, name: str):
        while name.startswith('[') and ']' in name:
            name = name.split(']', 1)[-1].lstrip()
        return name

    
    def _conv_2_mp3_and_rename_metadata(self, file_path: str, text: str):        
        f = music_tag.load_file(file_path)
        
        new_title = self._clean_name(str(f['title']))
        if new_title == '':
            new_title = os.path.basename(file_path)
            new_title = os.path.splitext(new_title)[0]
            new_title = self._clean_name(new_title)
        new_title = f"{text} {new_title}"
        
        root, ext = os.path.splitext(file_path)
        if ext != '.mp3':
            os.makedirs(self.safe_dir, exist_ok=True)
            
            # Convert to mp3 and rename metadata
            new_path = root + ".mp3"
            song = AudioSegment.from_file(file_path)
            song.export(new_path, 
                format='mp3', 
                bitrate=self.bitrate, 
                tags={'title': new_title, 
                      'artist': str(f['artist']),
                      'album': str(f['album']),
                      'genre': str(f['genre']),
                      })
            shutil.move(file_path, os.path.join(self.safe_dir, os.path.basename(file_path)))
        else:
            f['title'] = new_title
            f.save()
            
    
    def _rename_file(self, file_path: str, text: str):
        root, file = os.path.split(file_path)
        file = self._clean_name(file)
        new_name = f"{text} {file}"
        new_path = os.path.join(root, new_name)
        os.rename(file_path, new_path)
        return new_path
    
    
    def analyze_one_file(self, full_path):
            audio, sr = librosa.load(full_path, sr=self.sr, mono=True)
            bpm = self._estimate_bpm(audio)
            key = self._estimate_key(audio)
        
            camelot_key = conv_to_camelot_key(key)
            bpm_string = f'0{int(bpm)}' if bpm < 100 else f'{int(bpm)}'
            prepared_name = f"[{bpm_string}-{camelot_key}]"
            
            #file = os.path.basename(full_path)
            #ground_truth = int(file[12:15]) if file[0] != '*' else int(file[13:16])
            #prepared_name = f"{'*'*int(bpm != ground_truth)}[{bpm_string}-{camelot_key}]"
            new_path = self._rename_file(full_path, prepared_name)
            self._conv_2_mp3_and_rename_metadata(new_path, prepared_name)
        

    def analyze_directory(self, directory: str):
        self._update_directory(directory)
        all_files = self._collect_all_files()
        
        if not all_files:
            print("No files found to analyze.")
            return
        
        pool = Pool(processes=self.num_threads)
        for _ in tqdm(pool.imap_unordered(self.analyze_one_file, all_files), total=len(all_files)):
            pass
    

                        
                        
                        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Audio library analyzer tool.")
    parser.add_argument('--dir', type=Path, required=True, help="Directory to analyze.")
    parser.add_argument('--model', type=Path, default="deeptemp-k16-3.pb", help="Path to the TempoCNN model file.")
    parser.add_argument('--bpm_limits', type=int, nargs=2, metavar=('MIN', 'MAX'), default=[90, 180],
                        help="Specify min and max BPM, e.g. --bpm_limits 90 180")
    parser.add_argument('--safe_folder', type=Path, default="originals", help="Folder where all original files will be moved, this won't be analized.")
    parser.add_argument('--bitrate', type=str, default="320k", help="Bitrate for MP3 conversion. Examples: 192k, 256k, 320k")
    parser.add_argument('--num_threads', type=int, default=8, help="Number of threads for multiprocessing.")

    args = parser.parse_args()

    pipeline = Analyzer(
        TempoCNN_path=args.model,
        bpm_limits=tuple(args.bpm_limits),
        safe_folder=args.safe_folder,
        bitrate=args.bitrate,
        num_threads=args.num_threads
    )
    pipeline.analyze_directory(args.dir)
    #pipeline._conv_2_mp3_and_rename_metadata(file_path = "Saola - 67esut ALPARI 2025 EDIT.wav", text="")