Speech models are downloaded separately by `scripts/download-models.sh` from the Vosk project. They are not bundled in this repository because the model archives are large and have separate licenses. The app expects these directories next to `app.py`:

- `vosk-model-small-en-us-0.15`
- `vosk-model-small-ru-0.22`
