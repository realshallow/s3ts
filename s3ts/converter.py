from pathlib import Path

from pydub import AudioSegment


class Converter:
    def __init__(self, frame_rate: int = 16000, mono: bool = True) -> None:
        self.frame_rate = frame_rate
        self.mono = mono

    def std_convert(self, src_path: Path, dst_path: Path):
        sound = self.read(src_path=src_path)
        sound = self.set_framerate(sound=sound)
        if self.mono:
            sound = self.to_mono(sound=sound)
        self.export(sound, dst_path=dst_path)

    def read(self, src_path: Path):
        return AudioSegment.from_mp3(src_path)

    def set_framerate(self, sound):
        return sound.set_frame_rate(self.frame_rate)

    def to_mono(self, sound):
        return sound.set_channels(1)

    def export(self, sound, dst_path: Path):
        sound.export(dst_path, format="wav")
