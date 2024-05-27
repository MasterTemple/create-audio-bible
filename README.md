# Goal

Create an audio Bible by taking out and joining together segments of the Scriptures being read

# Process

1. Input a list of audio or video files
- YouTube Playlist
- YouTube Links
- SermonAudio Series
- SermonAudio Links
1. Download all files in an appropriate location
2. Convert all files to appropriate filetype
3. Transcribe all files into appropriate database
4. Search transcripts for Scripture readings
5. Cut out audio for all matches
6. Display results for user to select and trim
7. Export files

# Requirements

## `.env`

```env
SERMON_AUDIO_API_KEY="" # necessary for using SermonAudio
```

# CLI

Note: `cab` (`c`reate `a`udio `b`ible) is a shell script that just means you don't need to type `python cli.py`

**Create Project:** `cab create "project-name" "book" "sources.txt"`
- `sources.txt` should be a list of URLs separated by newlines (more input methods will be created later)

**Switch to Project:** `cab use "project-name"`
