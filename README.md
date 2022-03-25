# Automating custom voice Text-To-Speech with Speech-To-Text

## Installation

1. Create a virtual environment with `conda create -n s3tsenv python=3.8`.

2. Activate the environment with `conda activate s3tsenv`.

3. Install the requirements with `pip3 install -r requirements.txt`

3. Install TTS models - for French:
    - Vosk small model https://alphacephei.com/vosk/models/vosk-model-small-fr-pguyot-0.3.zip
    - LINTO large and accurate model https://alphacephei.com/vosk/models/vosk-model-fr-0.6-linto-2.2.0.zip
    For other languages, check https://alphacephei.com/vosk/models.

4. Put the model in a `models` directory

5. Unzip the model

6. Install Coqui TTS with the following commands:

    - `cd ..`

    - `git clone https://github.com/coqui-ai/TTS`

    - `pip install -e .`
    
    - You might have to change the version of PyTorch if you have a modern GPU

7. Change the parameters in `main.py`

8. Change the variables and execute `main.py` to create the database

## Other requirements

You should have a version of python inferior to 3.10. If it is not the case, do not hesitate to create conda environment.

The package ffmepg is necessary for the audio processings.

## Acknoledgments

Thanks to VOSK and Coqui TTS for their open-source software