from pathlib import Path

from pydub import AudioSegment


class Converter:
    def __init__(self, frame_rate: int = 16000, mono: bool = True) -> None:
        self.frame_rate = frame_rate
        self.mono = mono

    def std_convert(self, src_path: Path, dst_path: Path, verbose: bool = True):
        if src_path.is_dir() and dst_path.is_dir():
            source_files = list(src_path.glob("*"))
            if verbose:
                print("Found", len(source_files), "audio files to process.")
            for file_path in source_files:
                print(file_path)
                self.process_file(file_path, Path(dst_path, file_path.stem))

        elif src_path.is_file() and dst_path.is_file():
            self.process_file(src_path, dst_path)
        else:
            raise ValueError(
                "The source and destination paths should be both folders or both files."
            )

    def process_file(self, src_path, dst_path):
        sound = self.read(src_path=src_path)
        sound = self.set_framerate(sound=sound)
        if self.mono:
            sound = self.to_mono(sound=sound)
        self.export(sound, dst_path=Path(str(dst_path.with_suffix("")) + ".wav"))

    def read(self, src_path: Path):
        return AudioSegment.from_mp3(src_path)

    def set_framerate(self, sound):
        return sound.set_frame_rate(self.frame_rate)

    def to_mono(self, sound):
        return sound.set_channels(1)

    def export(self, sound, dst_path: Path):
        sound.export(dst_path, format="wav")
