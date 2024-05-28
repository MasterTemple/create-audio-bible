import sys
import json
import os
from dotenv import load_dotenv
# from whisperx.asr import FasterWhisperPipeline
from vars import CURRENT_PROJECT_FILE, DATA_DIR, PROJECT_DIR, PROJECT_DIR_AUDIO, PROJECT_DIR_EXPORT, PROJECT_DIR_EXPORT_VERSES, PROJECT_DIR_EXPORT_CHAPTERS, PROJECT_CONFIG_FILE_NAME, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_TRANSCRIPTS_DIR, PROJECT_DOWNLOADS_DIR, PROJECT_TEMP_DOWNLOADS_DIR

original_stdout = sys.stdout
null_device = open(os.devnull, "w")

# load_dotenv()
# # i want to do this just once
# # WHISPER_MODEL = os.getenv('WHISPER_MODEL')
WHISPER_MODEL = "medium.en"
device = "cuda"
batch_size = 16  # reduce if low on GPU mem
# # change to "int8" if low on GPU mem (may reduce accuracy)
compute_type = "float16"

# to use whisperx module without huge load time because it is imported by cli.py
wx = None
model = None

def import_and_load_model():
    global wx
    global model
    print("Importing model")
    sys.stdout = null_device
    import whisperx
    wx = whisperx
    sys.stdout = original_stdout

    print("Loading model")
    sys.stdout = null_device
    model = wx.load_model(WHISPER_MODEL, device, compute_type=compute_type)
    sys.stdout = original_stdout

def transcribe_project_files(project_name: str) -> None:
    import_and_load_model()
    files = os.listdir(os.path.join(PROJECT_DIR, project_name, PROJECT_DOWNLOADS_DIR))
    for i, file in enumerate(files):
        # its a dir
        if not file.endswith(".mp3"):
            continue
        id, _ = file.split(".")
        print(f"[{i+1}/{len(files)}] Transcribing '{id}.mp3'")
        transcribe_file(project_name, id)

# def transcribe_all_files() -> None:
#
#     files = os.listdir(DOWNLOADS_DIR)
#     for i, file in enumerate(files):
#         # its a dir
#         if not file.endswith(".mp3"):
#             continue
#         id, _ = file.split(".")
#         print(f"[{i+1}/{len(files)}] Transcribing '{id}.mp3'")
#         transcribe_file(id)

def transcribe_file(project_name, id):

    os.path.join(PROJECT_DIR, project_name, PROJECT_DOWNLOADS_DIR)
    audio_file = os.path.join(PROJECT_DIR, project_name, PROJECT_DOWNLOADS_DIR, f"{id}.mp3")
    output_file = os.path.join(PROJECT_DIR, project_name, PROJECT_TRANSCRIPTS_DIR, f"{id}.json")
    if os.path.exists(output_file):
        print(f"'{id}.mp3' already transcribed!")
        return

    # suppress whisper output
    sys.stdout = null_device
    audio = wx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)

    # delete model if low on GPU resources
    # import gc; gc.collect(); torch.cuda.empty_cache(); del model

    # 2. Align whisper output
    model_a, metadata = wx.load_align_model(
        language_code=result["language"], device=device)
    result = wx.align(result["segments"], model_a,
                            metadata, audio, device, return_char_alignments=False)

    result['id'] = id
    result['model'] = WHISPER_MODEL
    result['compute_type'] = compute_type

    with open(output_file, "w") as f:
        f.write(json.dumps(result, indent=2))

    # allow for output again
    sys.stdout = original_stdout

if __name__ == "__main__":
    # transcribe_all_files()
    import_and_load_model()
