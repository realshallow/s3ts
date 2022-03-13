#!/usr/bin/env python3

from pathlib import Path
from typing import List
from vosk import Model, KaldiRecognizer
import pandas as pd
import os
import wave
from pydub import AudioSegment


class DBExtractor:
    def __init__(
        self,
        min_duration: int = 5000,
        max_duration: int = 15000,
        min_confidence: float = 0.65,
    ) -> None:
        self.min_duration = min_duration
        self.max_duration = max_duration

        self.min_confidence = min_confidence
        self.n_utterance = 0
        self.wav_filenames = []
        self.wav_filesizes = []
        self.transcripts = []

        self.path = Path("data")

    def generate_data(self, model_path: Path, data_path: Path) -> None:
        extraction = self.extract_text(model_path, data_path)
        self.split_data(data_path, extraction)
        self.to_csv(data_path)

    def extract_text(self, model_path: Path, data_path: Path):
        self.reset()
        if not os.path.exists(model_path):
            print(
                "Please download the model from https://alphacephei.com/vosk/models and unpack as \
                    'model' in the current folder."
            )
            exit(1)

        wf = wave.open(str(data_path), "rb")

        if (
            wf.getnchannels() != 1
            or wf.getsampwidth() != 2
            or wf.getcomptype() != "NONE"
        ):
            print("Audio file must be WAV format mono PCM.")
            exit(1)

        model = Model(str(model_path))
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                pass

        res = rec.Result()
        return eval(res)

    def split_data(self, data_path: Path, extraction: dict) -> None:
        sound = AudioSegment.from_mp3(data_path)
        data_folder = Path("data", data_path.stem)
        data_folder.mkdir(parents=True, exist_ok=True)

        words = extraction["result"]

        n_words = len(words)
        i = 0
        while i < n_words:
            current_words = []
            start = int(words[i]["start"] * 1000)
            end = start
            while i < n_words and end - start < self.max_duration:
                current_words.append(words[i]["word"])
                end = int(words[i]["end"] * 1000)
                i += 1
            if end - start > self.min_duration:
                self.create_utterance(start, end, current_words, sound, data_path)

    def create_utterance(
        self, start: int, end: int, list_words: list, sound, data_path: Path
    ) -> None:
        utterance = sound[start:end]
        utt_path = Path(
            str(data_path)[:-4], str(data_path.stem) + str(self.n_utterance) + ".wav"
        )
        self.wav_filenames.append(utt_path)
        self.transcripts.append(" ".join(list_words))
        self.export(utterance, utt_path)
        self.wav_filesizes.append(os.path.getsize(utt_path))
        self.n_utterance += 1

    def export(self, sound, dst_path: Path) -> None:
        sound.export(dst_path, format="wav")

    def to_csv(self, data_path) -> None:
        df = pd.DataFrame(
            {
                "wav_filename": self.wav_filenames,
                "wav_filesize": self.wav_filesizes,
                "transcript": self.transcripts,
            }
        )
        df.to_csv(Path(self.path, "metadata_" + str(data_path.stem) + ".csv"))

    def reset(self) -> None:
        self.n_utterance = 0
        self.wav_filenames = []
        self.wav_filesizes = []
        self.transcripts = []
