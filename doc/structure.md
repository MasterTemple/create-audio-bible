# Local Storage Structure

```
data/
├──downloads/
│  ├── temp/
│  └── {id}.{ext}
├──transcripts/
│  └── {id}.json
├──projects/
│  └── {name}/
│      ├── config.json
│      ├── files.json
│      ├── csv/
│      │   ├── searches.csv
│      │   ├── segments.csv
│      │   └── sources.csv
│      ├── downloads/
│      │   ├── temp/
│      │   └── {id}.{ext}
│      ├── transcripts/
│      │   └── {id}.json
│      ├── audio/
│      │   └── {chapter}-{verse}-{id}-{start}-{stop}-{amplification}.{ext}
│      └── export/
│          ├── verses/
│          │   └── {book} {chapter}:{verse}.{ext}
│          └── chapters/
│              └── {book} {chapter}.{ext}
```

# Explanation

`id` corresponds to the YouTube ID or Sermon ID
`.{ext}` corresponds to the final extension to be used (likely constant bit-rate .mp3)
`name` corresponds to the name that the user gives to their project, such as `1 Peter - Samuel Renihan` found in `config.json`
`book` corresponds to the book of the Bible that the user would like to have
`chapter` and `verse` are determined by the book of the Bible
`start`, `stop`, and `amplification` all corresponds to modifications done to the origin file `{id}.{ext}`
`downloads/temp/` is where all non `.{ext}` files go before conversion, post-conversion files belong directly in `downloads`
Example `config.json`
```json
{
	"name": "1 Peter - Samuel Renihan",
	"book": "1 Peter",
	"cover_image": "/path/to/img",
	"sources": [
		"link 1",
		"link 2"
	]
}
```
`sources` can be any of the following:
- YouTube Playlist
- YouTube Links
- SermonAudio Series
- SermonAudio Links
`cover_image` is the image to be on the cover of the exported files
`files.json` lists all the ids of files
