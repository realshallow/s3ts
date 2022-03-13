from pathlib import Path
from s3ts.converter import Converter
from s3ts.db_extractor import DBExtractor

convert = False
extract = True

src_path = Path("data/macron_ia.mp3")
dst_path = Path("data/macron_ia.wav")
model_path = Path("models/vosk-model-fr-0.6-linto-2.2.0")

if convert:
    converter = Converter()
    converter.std_convert(src_path=src_path, dst_path=dst_path)

if extract:
    extractor = DBExtractor()
    extractor.generate_data(model_path, dst_path)
