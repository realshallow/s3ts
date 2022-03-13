# Automating custom voice Text-To-Speech with Speech-To-Text

## Installation

1. Create a virtual environment with `python3 -m venv .s3tsenv`.

2. Activate the environment with `source .s3tsenv/bin/activate`.

3. Install TTS models - for French:
    - Vosk small model https://alphacephei.com/vosk/models/vosk-model-small-fr-pguyot-0.3.zip
    - LINTO large and accurate model https://alphacephei.com/vosk/models/vosk-model-fr-0.6-linto-2.2.0.zip
    For other languages, check https://alphacephei.com/vosk/models.

4. Put the model in a `models` directory

5. Unzip the model

6. Install Coqui TTS with the following commands:
    - 1
    - 2

7. Change the parameters in `main.py`

8. Execute `main.py`

## Other requirements

You should have a version of python inferior to 3.10. If it is not the case, do not hesitate to create conda environment.

The package ffmepg is necessary for the audio processings.