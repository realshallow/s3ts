from pathlib import Path

from pydub import AudioSegment


class Converter:
    def __init__(self) -> None:
        pass

    def convert(self, src_path: Path, dst_path: Path):
        src = "transcript.mp3"
        dst = "test.wav"

        # convert wav to mp3
        sound = AudioSegment.from_mp3(src)
        sound.set_channels(1)
        sound.export(dst, format="wav")
