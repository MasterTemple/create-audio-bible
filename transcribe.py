import sys
import json
import os
from dotenv import load_dotenv
from vars import DOWNLOADS_DIR, TRANSCRIPTS_DIR

original_stdout = sys.stdout
null_device = open(os.devnull, "w")

print("Importing model")
# suppress whisper output
sys.stdout = null_device
import whisperx
# allow for output again
sys.stdout = original_stdout
# load_dotenv()
# # i want to do this just once
# # WHISPER_MODEL = os.getenv('WHISPER_MODEL')
WHISPER_MODEL = "medium.en"
device = "cuda"
batch_size = 16  # reduce if low on GPU mem
# # change to "int8" if low on GPU mem (may reduce accuracy)
compute_type = "float16"
print("Loading model")
model = whisperx.load_model(WHISPER_MODEL, device, compute_type=compute_type)

def transcribe_project_files(project_name: str) -> None:
    pass

def transcribe_all_files() -> None:

    files = os.listdir(DOWNLOADS_DIR)
    for i, file in enumerate(files):
        # its a dir
        if not file.endswith(".mp3"):
            continue
        id, _ = file.split(".")
        print(f"[{i+1}/{len(files)}] Transcribing '{id}.mp3'")
        transcribe_file(id)

def transcribe_file(id):
    audio_file = os.path.join(DOWNLOADS_DIR, f"{id}.mp3")
    output_file = os.path.join(TRANSCRIPTS_DIR, f"{id}.json")
    if os.path.exists(output_file):
        print(f"'{id}.mp3' already transcribed!")
        return

    # suppress whisper output
    sys.stdout = null_device
    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)

    # delete model if low on GPU resources
    # import gc; gc.collect(); torch.cuda.empty_cache(); del model

    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a,
                            metadata, audio, device, return_char_alignments=False)

    result['id'] = id
    result['model'] = WHISPER_MODEL
    result['compute_type'] = compute_type

    with open(output_file, "w") as f:
        f.write(json.dumps(result))

    # allow for output again
    sys.stdout = original_stdout

if __name__ == "__main__":
    transcribe_all_files()
