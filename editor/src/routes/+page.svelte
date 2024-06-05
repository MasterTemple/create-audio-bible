<script>
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';
	import EditableReading from './EditableReading.svelte';
	import { openChapter, openReference, openReading, bookTree, config, esv } from "./stores"
	import { asId, download_post, audioUrl, domain, json_get, json_post, saveBookTree, editReading, useReading, getReferences, setConfig, setBookTree, as2DArray } from "./functions"
	import Reading from './Reading.svelte';

	/**
	 * @param {string} reference
	 */
	function openFirstReading(reference) {
		// openReference.set(reference);
		const readingId = document
			.getElementById(asId(reference))
			?.querySelector('div.content.reading')?.id;
		// some references have no readings
		if (readingId) openReading.set(readingId);
	}

	/**
	 * @param {string} reference
	 */
	function openNextReading(reference) {
		const chapter = reference.replace(/:\d+$/, '');
		const b = reference.match(/.*(?= \d+:)/g)[0];
		const ch = reference.match(/\d+(?=:)/g)[0];
		const v = reference.match(/\d+$/g)[0];
		const nextReference = `${b} ${ch}:${parseInt(v) + 1}`;
		const nextChapter = `${b} ${parseInt(ch) + 1}`;
		const nextChapterReference = `${nextChapter}:1`;
		// is in same chapter
		if (Object.keys($bookTree[chapter]).find((r) => r == nextReference)) {
			openReference.set(nextReference);
			const nextReadingId = document
				.getElementById(asId(nextReference))
				?.querySelector('div.content.reading').id;
			openReading.set(nextReadingId);
		}
		// is in same chapter
		else if (Object.keys($bookTree).find((c) => c == nextChapter)) {
			openChapter.set(nextChapter);
			openReference.set(nextChapterReference);
			const nextReadingId = document
				.getElementById(asId(nextChapterReference))
				?.querySelector('div.content.reading').id;
			openReading.set(nextReadingId);
		}
	}

	/**
	 *
	 * @param {string} id
	 */
	async function scrollIntoMiddle(id) {
		const element = document.getElementById(id);
		console.log({ id, element });
		// console.log({ id, element });
		if (element != null) {
			const mainContent = document.querySelector('div.main-content');

			const chaptersBefore = parseInt($openChapter.match(/\d+$/g)[0]);
			const chapterSize = document.querySelector('.button-content.chapter').scrollHeight;

			const versesBefore = parseInt($openReference.match(/\d+$/g)[0]) - 1;
			const verseSize = [...document.querySelectorAll(`.button-content.verse`)].find(
				(r) => r?.scrollHeight && r?.scrollHeight > 0
			)?.scrollHeight;

			const readingsBefore = $bookTree[$openChapter][$openReference].findIndex((r) => r.sid == id);
			const readingsSize = [...document.querySelectorAll(`.button-content.reading`)].find(
				(r) => r?.scrollHeight && r?.scrollHeight > 0
			)?.scrollHeight;
			console.log({
				chaptersBefore, chapterSize,
				versesBefore, verseSize,
				readingsBefore, readingsSize,
			})

			if (!verseSize || !readingsSize) {
				setTimeout(() => scrollIntoMiddle(id), 100);
				return;
			}

			const margin = ((chaptersBefore - 1) * 20) + ((versesBefore - 1) * 20) + ((readingsBefore - 1) * 20)
			const newScroll =
				chaptersBefore * chapterSize + versesBefore * verseSize + readingsBefore * (readingsSize) + margin


			const interval = setInterval(() => {
				// console.log(document.querySelector('.main-content').scrollTop);
				mainContent.scrollTop = newScroll;
			}, 50);
			setTimeout(() => {
				clearInterval(interval);
			}, 500);

		}
	}

	/**
	 * @param {string} exportType
	 * @returns {void}
	 */
	async function exportPrompt(exportType = 'verses') {
		// ill make a prompt later, for now export verses
		const data = {
			book_tree: $bookTree,
			export_type: exportType
		};
		// download_post('/export', data);
		json_post('/export', data);
	}

	function pauseAllAudio() {
		Object.values($bookTree).forEach((referencesToReadings) =>
			Object.values(referencesToReadings).forEach((readings) =>
				readings.forEach((reading) => {
					reading?.audio?.pause()
					reading?.mergedAudio?.pause()
					reading?.extra?.forEach((r) => r?.audio?.pause())
				})
			)
		);
	}

	onMount(async () => {
		document.addEventListener('keydown', (e) => {
			if (e.key == ' ') {
				// pauseAllAudio()
				let audio = document.querySelector(`#audio-${$openReading}-merged`);
				if(!audio)
					audio = document.querySelector(`#audio-${$openReading}`);
				if (audio.paused) audio.play();
				else audio.pause();

				e.preventDefault();
			}
		});
		// get project name & config
		await setConfig();

		// set ESV book data
		await getReferences($config.book);

		// get reading info
		await setBookTree();

		openChapter.subscribe((c) => {
			openReference.set(c + ':1');
		});
		openReference.subscribe((r) => {
			// scrollIntoMiddle()
			openFirstReading(r);
		});
		// when a new reading is opened
		openReading.subscribe((r) => {
			// console.log({ newOpenReading: r });
			// stop all other audios/previous audio
			pauseAllAudio();
			// play audio of reading
			// const audio = document.querySelector(`#audio-${r}`);
			let audio = document.querySelector(`#audio-${r}-merged`);
			if(!audio)
				audio = document.querySelector(`#audio-${r}`);
			// restart audio from beginning
			const autoPlay = true;
			if (audio && autoPlay) {
				audio.currentTime = 0;
				audio.play();
			}
			// openFirstReading(r)
			// scroll to new reading
			scrollIntoMiddle(r);
		});
	});
</script>

<html lang="en">
	<head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0" />
		<title>{$config.book}</title>
	</head>
	<body>
		<div class="container">
			<div class="header">
				<div class="center col">
					<div class="row">
						<h1>{$config?.name}</h1>
						<div class="col dropdown">
							<button class="dropbtn" on:click={() => exportPrompt('book')}>Export</button>
							<div class="dropdown-content">
								<button on:click={() => exportPrompt('verses')}>Verses</button>
								<button on:click={() => exportPrompt('chapters')}>Chapters</button>
								<button on:click={() => exportPrompt('book')}>Book</button>
							</div>
						</div>
					</div>
					<!-- chapter list? -->
					<!-- <div class="row"> -->
					<!-- make a drop-down to select export audio files in verses, chapters, or the whole book -->
					<!-- 	<button id="save-button" on:click={saveBookTree}>Save</button> -->
					<!-- 	<button on:click={() => exportPrompt('verses')}>Export Verses</button> -->
					<!-- 	<button on:click={() => exportPrompt('chapters')}>Export Chapters</button> -->
					<!-- 	<button on:click={() => exportPrompt('book')}>Export Book</button> -->
					<!-- </div> -->
					<div class="col chapter-select-row">
						{#each as2DArray(Object.keys($bookTree)) as chapterRow}
							<div class="row">
								{#each chapterRow as chapter}
									<button
										class:chapter-selected={$openChapter == chapter}
										class="chapter-select"
										on:click={() => openChapter.set(chapter)}
										>{chapter.match(/\d+$/g)[0]}
									</button>
								{/each}
							</div>
						{/each}
					</div>
					<div class="col verse-select-row">
						{#if $openChapter != ''}
							{#each as2DArray(Object.entries($bookTree[$openChapter]).sort((a, b) => a[0].match(/\d+$/g)[0] - b[0].match(/\d+$/g)[0])) as referenceRow}
								<div class="row">
									{#each referenceRow as [reference, readings]}
										<button
											class:no-readings-available={readings.length == 1 && readings[0].blank}
											class:verse-selected={$openReference == reference}
											class="verse-select"
											on:click={() => openReference.set(reference)}
											>{reference.match(/\d+$/g)[0]}</button
										>
									{/each}
								</div>
							{/each}
						{/if}
					</div>
					<div class="col reading-select-row">
						{#if $openChapter != '' && $openReference != ''}
							{#each as2DArray($bookTree[$openChapter][$openReference]) as readingRow}
								<div class="row">
									{#each readingRow as reading, i}
										<button
											class:reading-selected={$openReading == reading.sid}
											class:using-reading={reading.use}
											class="reading-select"
											on:click={() => openReading.set(reading.sid)}
											>{i + 1}
										</button>
									{/each}
								</div>
							{/each}
						{/if}
					</div>
				</div>
			</div>
			<div class="main-content">
				<div class="collapsible">
					{#each Object.entries($bookTree) as [chapter, referencesToReadings]}
						<button
							class:chapter-selected={$openChapter == chapter}
							class="collapsible button-content chapter"
							on:click={() => openChapter.set($openChapter != chapter ? chapter : '')}
						>
							<h2>{chapter}</h2>
						</button>
						<div
							id={asId(chapter)}
							class="content chapter"
							style="display:{$openChapter == chapter ? 'block' : 'none'};"
						>
							{#each Object.entries(referencesToReadings).sort((a, b) => a[0].match(/\d+$/g)[0] - b[0].match(/\d+$/g)[0]) as [reference, readings]}
								<button
									class:verse-selected={$openReference == reference}
									class="collapsible button-content verse"
									on:click={() => openReference.set($openReference != reference ? reference : '')}
								>
									<div class="col">
										<h3>{reference}</h3>
										<p class="verse-results">Readings: {readings?.length || 0}</p>
									</div>
									<!-- {#await getReference(reference) then content} -->
									<!-- 	<p class="esv">{content}</p> -->
									<!-- {/await} -->
									<p class="esv">{$esv[reference]}</p>
								</button>

								<div
									id={asId(reference)}
									class="content verse"
									style="display:{$openReference == reference ? 'block' : 'none'};"
								>
									{#each readings as reading, i}
										<!-- {#if reading.blank == true} -->
										<!-- 	<EditableReading reading={reading} i={i} openNextReading={openNextReading}/> -->
										<!-- {:else} -->
											<Reading reading={reading} i={i} openNextReading={openNextReading}/>
										<!-- {/if} -->
									{/each}
								</div>
							{/each}
						</div>
					{/each}
				</div>
			</div>
		</div>
	</body>
</html>

<style>
	@import "./style.css";
</style>
