#!/usr/bin/env python3

import math
from pathlib import Path
from typing import List
import numpy as np
from tqdm import tqdm
from vosk import Model, KaldiRecognizer
import pandas as pd
import os
import wave
from pydub import AudioSegment
from pydub.effects import normalize


class DBExtractor:
    def __init__(
        self,
        path: Path,
        min_duration: int = 2000,
        mean_duration: int = 3500,
        max_duration: int = 5000,
        min_confidence: float = 0.65,
        max_silence: int = 700,
        frame_rate: int = 16000,
    ) -> None:
        """
        Default constructor for the Extractor Tool.

        Args:
            path (Path): The path to the dataset.
            min_duration (int, optional): The minimum duration of the audio. Defaults to 2000.
            mean_duration (int, optional): The mean duration of the audio. Defaults to 3500.
            max_duration (int, optional): The max duration of the audio. Defaults to 5000.
            min_confidence (float, optional): The minimum required confidence to be validated. Defaults to 0.65.
            frame_rate (int, optional): The number of samples per second. Defaults to 16000.
        """
        self.min_duration = min_duration
        self.mean_duration = mean_duration
        self.max_duration = max_duration
        self.max_silence = max_silence

        # 3 sigmas
        self.variance = (mean_duration - min_duration) / 3

        self.min_confidence = min_confidence
        self.n_utterance = 0
        self.wav_filenames = []
        self.wav_filesizes = []
        self.transcripts = []

        self.frame_rate = frame_rate

        self.path = path

    def generate_data(
        self, model_path: Path, data_path: Path, verbose: bool = True
    ) -> None:
        self.load_model(model_path)
        # Multiple data files
        if data_path.is_dir():
            source_files = [
                file for file in list(data_path.glob("*")) if file.suffix == ".wav"
            ]
            if verbose:
                print("Found", len(source_files), "audio files to process.")
            i = 1
            for file_path in source_files:
                if verbose:
                    print("Processing", file_path.name)
                    print("Operation", i, "on", len(source_files))
                self.process_file(file_path)
                self.load_model(model_path)
                i += 1

        # Single data file
        elif data_path.is_file():
            self.process_file(data_path)

        # Save the data to csv
        self.to_csv()

    def process_file(self, data_path: Path):
        print("Starting extraction.")
        extraction = self.extract_text(data_path)

        print("Splitting the data and saving metadata.")
        self.split_data(data_path, extraction)

    def extract_text(self, data_path: Path):
        wf = wave.open(str(data_path), "rb")

        if (
            wf.getnchannels() != 1
            or wf.getsampwidth() != 2
            or wf.getcomptype() != "NONE"
        ):
            print("Audio file must be WAV format mono PCM.")
            exit(1)

        pbar = tqdm(total=math.ceil(wf.getnframes() / 1000))
        while True:
            data = wf.readframes(1000)
            if len(data) == 0:
                break
            if self.rec.AcceptWaveform(data):
                pass
            pbar.update(1)
        pbar.close()
        res = self.rec.Result()
        return eval(res)

    def load_model(self, model_path: Path) -> None:
        if not model_path.exists():
            print(
                "Please download the model from https://alphacephei.com/vosk/models and unpack as \
                    'model' in the current folder."
            )
            exit(1)

        self.model = Model(str(model_path))

        self.rec = KaldiRecognizer(self.model, self.frame_rate)
        self.rec.SetWords(True)

    def split_data(
        self, data_path: Path, extraction: dict, random: bool = True
    ) -> None:
        sound = AudioSegment.from_wav(data_path)
        data_folder = Path(data_path.parent, "wavs")
        data_folder.mkdir(parents=True, exist_ok=True)

        words = extraction["result"]
        max_duration = self.max_duration

        n_words = len(words)
        i = 0
        n_accepted = 0
        t_accepted = 0
        n_rejected = 0
        t_rejected = 0
        n_words_accepted = 0
        n_words_rejected = 0
        while i < n_words:
            current_words = []
            start = int(words[i]["start"] * 1000)
            end = start
            if random:
                max_duration = max(
                    min(
                        np.random.normal(self.mean_duration, self.variance),
                        self.max_duration,
                    ),
                    self.min_duration,
                )
            while (
                i < n_words
                and words[i]["start"] * 1000 - end < self.max_silence
                and words[i]["conf"] > self.min_confidence
                and end - start < max_duration
            ):
                current_words.append(words[i]["word"])
                end = int(words[i]["end"] * 1000)
                i += 1

            if end - start > self.min_duration:
                n_accepted += 1
                t_accepted += end - start
                n_words_accepted += len(current_words)
                self.create_utterance(start, end, current_words, sound, data_folder)
            else:
                i += 1
                n_rejected += 1
                t_rejected += end - start
                n_words_rejected += len(current_words)

        print("Number of accepted samples:", n_accepted)
        print("Number of accepted words:", n_words_accepted)
        if t_accepted > 60000:
            print("Duration of accepted samples:", round(t_accepted / 60000, 1), "min")
        else:
            print("Duration of accepted samples:", round(t_accepted / 1000, 1), "s")

        print("Number of rejected samples:", n_rejected)
        print("Number of rejected words:", n_words_rejected)
        if t_rejected > 60000:
            print("Duration of rejected samples:", round(t_rejected / 60000, 1), "min")
        else:
            print("Duration of rejected samples:", round(t_rejected / 1000, 1), "s")

    def create_utterance(
        self, start: int, end: int, list_words: list, sound, data_path: Path
    ) -> None:
        utterance = normalize(sound[start:end])
        utt_path = Path(data_path, "audio_" + str(self.n_utterance) + ".wav")
        self.wav_filenames.append(utt_path.stem)
        self.transcripts.append(" ".join(list_words))
        self.export(utterance, utt_path)
        self.n_utterance += 1

    def export(self, sound, dst_path: Path) -> None:
        sound = sound.set_frame_rate(16000)
        sound.export(dst_path, format="wav")

    def to_csv(self) -> None:
        df = pd.DataFrame(
            {"wav_filename": self.wav_filenames, "transcript": self.transcripts,}
        )
        df.to_csv(Path(self.path, "metadata.txt"), sep="|", index=False, header=False)

    def reset(self) -> None:
        self.n_utterance = 0
        self.wav_filenames = []
        self.transcripts = []
