<script>
	import { read } from '$app/server';
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';

	const domain = 'http://127.0.0.1:5000';
	const bookTree = writable({});
	const config = writable({
		book: 'Loading...',
		name: 'Loading...'
	});
	const openChapter = writable('');
	const openReference = writable('');
	const openReading = writable('');


	/**
	 * @param {string} reference
	*/
	function openFirstReading(reference) {
		// openReference.set(reference);
		const readingId = document
			.getElementById(asId(reference))
			?.querySelector('div.content.reading')?.id;
		// some references have no readings
		if(readingId)
			openReading.set(readingId);
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

	function centerElement(childElement) {
		const mainContent = document.querySelector('div.main-content');
		const childHeight = childElement.offsetHeight;
		const mainContentHeight = mainContent.clientHeight;

		// Calculate the scroll position to center the element
		const scrollTop = (mainContentHeight - childHeight) / 2 + childHeight;

		// Update the scrollTop property
		mainContent.scrollTop += scrollTop;
	}

	/**
	 *
	 * @param {string} id
	 */
	async function scrollIntoMiddle(id) {
		const element = document.getElementById(id);
		console.log({id, element})
		// console.log({ id, element });
		if (element != null) {
			const mainContent = document.querySelector('div.main-content');
			const chaptersBefore = parseInt($openChapter.match(/\d+$/g)[0]);
			const chapterSize = document.querySelector(".button-content.chapter").scrollHeight;

			const versesBefore = parseInt($openReference.match(/\d+$/g)[0]) - 1;
			// const verseSize = document.querySelector(`#${asId($openChapter)} .button-content.verse`).scrollHeight;
			const verseSize = [...document.querySelectorAll(`.button-content.verse`)].find((r) => r?.scrollHeight && r?. scrollHeight > 0)?.scrollHeight;
			// const verseSize = 70;

			const readingsBefore = $bookTree[$openChapter][$openReference].findIndex((r) => r.sid == id);
			// const readingsSize = document.querySelector(`#${asId($openReference)} .button-content.reading`).scrollHeight;
			const readingsSize = [...document.querySelectorAll(`.button-content.reading`)].find((r) => r?.scrollHeight && r?. scrollHeight > 0)?.scrollHeight;
			// const readingsSize = 81;

			if(!verseSize || !readingsSize) {
				setTimeout(() => scrollIntoMiddle(id), 100)
				return;
			}

			const newScroll = (chaptersBefore * chapterSize) + (versesBefore * verseSize) + (readingsBefore * readingsSize);

			// console.log({chaptersBefore, chapterSize, versesBefore, verseSize, readingsBefore, readingsSize, currentScroll: mainContent.scrollTop, newScroll: mainContent.scrollTop + newScroll, $openChapter, $openReference})
			// console.log({versesBefore, verseSize, readingsBefore, readingsSize, currentScroll: mainContent.scrollTop, newScroll: mainContent.scrollTop + newScroll})
			const oldScroll = mainContent.scrollTop;
			mainContent.scrollTop = newScroll

			// console.log({versesBefore, oldScroll, currentScroll: mainContent.scrollTop, newScroll})
			// console.log(document.querySelector(".main-content").scrollTop)
			// setTimeout(() => {
			// 	console.log(document.querySelector(".main-content").scrollTop)
			// 	mainContent.scrollTop = newScroll;
			// }, 250)

			const interval = setInterval(() => {
				console.log(document.querySelector(".main-content").scrollTop)
				mainContent.scrollTop = newScroll;
				}, 50)
			setTimeout(() => {
				clearInterval(interval)
			}, 300)


			// centerElement(element)
			// document.querySelector("div.main-content").scrollTop += 150
			// element.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
			// window.scrollBy(0, 150)
			// const element = document.getElementById(asId(id));
			// const elementRect = element.getBoundingClientRect();
			// const absoluteElementTop = elementRect.top + window.pageYOffset;
			// const middle = absoluteElementTop - window.innerHeight / 2;
			// window.scrollTo(0, middle);
			// Element.prototype.documentOffsetTop = function () {
			// 		return this.offsetTop + ( this.offsetParent ? this.offsetParent.documentOffsetTop() : 0 );
			// };
			//
			// var top = element.documentOffsetTop() - ( window.innerHeight / 2 );
			// window.scrollTo( 0, top );
			// element.scrollIntoView();
		}
	}

	/**
	 * @param {string} - endpoint
	 * @returns {Object} - json
	 */
	async function json_get(endpoint) {
		const res = await fetch(domain + endpoint, {
			headers: {
				'Access-Control-Allow-Origin': domain,
				'Content-Type': 'application/json'
			}
		});
		const json = await res.json();
		return json;
	}

	/**
	 * @param {string} - endpoint
	 * @param {Object} - data
	 * @returns {Object} - json
	 */
	async function json_post(endpoint, data = {}) {
		const res = await fetch(domain + endpoint, {
			method: 'POST',
			body: JSON.stringify(data),
			headers: {
				'Access-Control-Allow-Origin': domain,
				'Content-Type': 'application/json'
			}
		});
		const json = await res.json();
		return json;
	}

	/**
	 * @param {string} - endpoint
	 * @param {Object} - data
	 * @returns {Object} - json
	 */
	async function download_post(endpoint, data = {}) {
		const res = await fetch(domain + endpoint, {
			method: 'POST',
			body: JSON.stringify(data),
			headers: {
				'Access-Control-Allow-Origin': domain,
				'Content-Type': 'application/zip'
			}
		});
		const blob = await res.blob();
		const filename =
			res.headers.get('Content-Disposition')?.split('filename=')[1] || 'download.zip'; // Try to extract filename from headers or use a default

		const url = window.URL.createObjectURL(blob);
		const link = document.createElement('a');
		link.href = url;
		link.download = filename;
		link.click();
	}

	// /**
	//  * @param {PointerEvent} e - event of user clicking expandable/collapsible region
	//  */
	// function toggleChildren(e) {
	// 	const button = e.target;
	// 	button.classList.toggle('active');
	// 	const content = button.nextElementSibling;
	// 	if (content.style.display === 'block') {
	// 		content.style.display = 'none';
	// 	} else {
	// 		content.style.display = 'block';
	// 	}
	// }

	/**
	 * @param {str} content -
	 */
	function asId(content) {
		return content.replace(/[^A-z0-9]/g, '-') + '-content';
	}

	// /**
	//  * @param {str} id -
	//  */
	// function toggleContent(id) {
	// 	const content = document.getElementById(asId(id));
	// 	if (content.style.display === 'block') {
	// 		content.style.display = 'none';
	// 	} else {
	// 		content.style.display = 'block';
	// 	}
	// }

	/**
	 * @param {string} id - file id
	 */
	function openFile(id) {
		// doesn't work right now
		window.open(domain + `/file?id=${id}`);
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
		download_post('/export', data);
	}

	/**
	 * @returns {void}
	 */
	async function saveBookTree() {
		const data = { book_tree: $bookTree };
		const json = await json_post('/save', data);
	}

	/**
	 * @param {string} id - file id
	 */
	function deleteReading(id) {}

	/**
	 * @param {Object} reading
	 */
	function audioUrl(reading) {
		// reading.autoplay = true;
		return `${domain}/audio?file_id=${reading.id}&start_time=${reading.start_time}&end_time=${reading.end_time}&volume=${reading?.volume || 1.0}`;
	}

	// * @param {string} id - file id
	// * @param {string} reference - file id
	/**
	 * @param {Object} reading
	 */
	function editReading(reading) {
		// console.log({ reading });
		reading.audio.preload = 'auto';
		reading.audio.autoplay = true;
		reading.audio.load();
		// reading.audio.load();
		saveBookTree();
	}

	/**
	 * @param {Object} reading
	 */
	function useReading(reading) {
		// unuse other reading
		const chapter = reading.reference.replace(/:\d+$/, '');
		const data = $bookTree;
		data[chapter][reading.reference] = data[chapter][reading.reference].map((r) => {
			return {
				...r,
				use: r.sid == reading.sid
			};
		});
		bookTree.set(data);
		// save selection?
		saveBookTree();
		// move on to next verse
		openNextReading(reading.reference)
		// // or
		// // is in same chapter
		// const chapterKeys = Object.keys($bookTree)
		// const referenceKeys = Object.keys($bookTree[chapter]);
		// console.log({chapterKeys, referenceKeys})
		// const referenceIndex = referenceKeys.findIndex((r) => r == reading.reference);
		// // if next verse is in same chapter
		// if(referenceIndex + 1 < referenceKeys.length) {
		// 	const nextReference = referenceKeys[referenceIndex + 1];
		// 	openReference.set(nextReference);
		// }
		// // verse is in the next chapter
		// else {
		// 	const chapterIndex = chapterKeys.findIndex((c) => c == chapter);
		// 	if(chapterIndex + 1 < chapterKeys.length) {
		// 		const nextChapter = chapterKeys[chapterIndex + 1];
		// 		openChapter.set(nextChapter);
		// 		// first verse of that new chapter
		// 		openReference.set(nextChapter + ":1")
		// 	}
		// }
		// console.log({
		// 	$openChapter,
		// 	$openReference,
		// 	$openReading
		// })
	}

	const esv = writable({});

	/**
	 * @param {string} book - book in the Bible
	 */
	async function getReferences(book) {
		const data = { book };
		const json = await json_post('/esv', data);
		esv.set(json);
	}

	/**
	 * @param {string} reference - Bible reference
	 * @returns {string} content
	 */
	async function getReference(reference) {
		const book = reference.match(/.*(?= \d+:)/g)[0];
		const chapter = reference.match(/\d+(?=:)/g)[0];
		const verse = reference.match(/\d+$/g)[0];
		const { content } = await json_post('/esv', {
			book,
			chapter,
			verse
		});
		return content;
	}

	async function setConfig() {
		const json = await json_get('/config');
		config.set(json);
	}

	async function setBookTree() {
		const json = await json_get('/readings');
		const tree = {};
		const references = Object.keys(json);
		const chapters = [...new Set(references.map((reference) => reference.match(/.*(?=:)/g)[0]))];
		for (let chapter of chapters) {
			tree[chapter] = {};
		}
		for (let [reference, readings] of Object.entries(json)) {
			const chapter = reference.match(/.*(?=:)/g)[0];
			// const chapterNumber = parseInt(reference.match(/\d+(?=:)/g)[0]);
			// console.log({chapter, reference, chapterNumber, bool: chapterNumber > 2})
			let oneIsUsed = false;
			tree[chapter][reference] = readings.slice(0, 5).map((r) => {
				if (r.use) oneIsUsed = true;
				return {
					...r,
					reference,
					url: audioUrl(r),
					volume: r.volume || 1.0,
					use: r.use || false,
					sid: `${r.id}-${r.start_seg}-${r.end_seg}`
				};
			});
			if (!oneIsUsed && tree[chapter][reference].length > 0) {
				tree[chapter][reference][0].use = true;
			}
		}
		bookTree.set(tree);
		console.log({$bookTree})
	}

	/**
	* @param {Array<string>} arr 
	* @returns {Array<Array<string>>}
	*/
	function as2DArray(arr, maxRowLength = 20) {
		let rowCount = Math.floor(arr.length/maxRowLength);
		if (arr.length > (maxRowLength * rowCount)) {
			rowCount++;
		}
		maxRowLength = Math.round(arr.length / rowCount);
		const result = [];
		let temp = [];
		for (let i = 0; i < arr.length; i++) {
			if (temp.length === maxRowLength) {
				result.push(temp);
				temp = [];
			}
			temp.push(arr[i]);
		}
		if (temp.length > 0) {
			result.push(temp);
		}
		return result;
	}

	onMount(async () => {
		// get project name & config
		await setConfig();

		// set ESV book data
		await getReferences($config.book);

		// get reading info
		await setBookTree();

		openChapter.subscribe((c) => {
			openReference.set(c + ":1");
		})
		openReference.subscribe((r) => {
			// scrollIntoMiddle()
			openFirstReading(r)
		})
		// when a new reading is opened
		openReading.subscribe((r) => {
			console.log({newOpenReading: r})
			// stop all other audios/previous audio
			Object.values($bookTree).forEach((referencesToReadings) => Object.values(referencesToReadings).forEach((readings) => readings.forEach((reading) => reading.audio.pause())))
			// play audio of reading
			const audio = document.querySelector(`#audio-${r}`);
			// restart audio from beginning
			const autoPlay = true;
			if(audio && autoPlay) {
				audio.currentTime = 0;
				audio.play()
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
					<h1>{$config?.name}</h1>
					<!-- chapter list? -->
					<!-- <div class="row"> -->
					<!-- make a drop-down to select export audio files in verses, chapters, or the whole book -->
					<!-- 	<button id="save-button" on:click={saveBookTree}>Save</button> -->
					<!-- 	<button on:click={() => exportPrompt('verses')}>Export Verses</button> -->
					<!-- 	<button on:click={() => exportPrompt('chapters')}>Export Chapters</button> -->
					<!-- 	<button on:click={() => exportPrompt('book')}>Export Book</button> -->
					<!-- </div> -->
					<div class="row chapter-select-row">
						{#each Object.keys($bookTree) as chapter}
								<button class:chapter-selected={$openChapter == chapter} class="chapter-select" on:click={() => openChapter.set(chapter)}>{chapter.match(/\d+$/g)[0]}</button>
						{/each}
					</div>
					<div class="col verse-select-row">
						{#if $openChapter != ""}
							{#each as2DArray(Object.entries($bookTree[$openChapter]).sort((a, b) => a[0].match(/\d+$/g)[0] - b[0].match(/\d+$/g)[0])) as referenceRow}
								<div class="row">
									{#each referenceRow as [reference, readings]}
										<button disabled={readings.length == 0} class:verse-selected={$openReference == reference} class="verse-select" on:click={() => openReference.set(reference)}>{reference.match(/\d+$/g)[0]}</button>
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
										<button
											class="collapsible button-content reading"
											on:click={() =>
												openReading.set($openReading != reading.sid ? reading.sid : '')}
											class:selected-reading={reading.use}
										>
											<h4>Reading {i + 1}</h4>
											<p>{reading.content || 'No audio content...'}</p>
										</button>
										<div
											id={reading.sid}
											class="content reading"
											style="display:{$openReading == reading.sid ? 'block' : 'none'};"
										>
											<div class="top-row row">
												<audio id={'audio-' + reading.sid} preload="none" bind:this={reading.audio} controls>
													<!-- <source src={audioUrl(reading)} type="audio/mpeg" /> -->
													<source src={reading.url} type="audio/mpeg" />
												</audio>
												<div class="start_time">
													Start:
													<input
														type="number"
														bind:value={reading.start_time}
														on:input={() => {
															reading.url = audioUrl(reading);
														}}
													/>
												</div>
												<div class="end_time">
													End:
													<input
														type="number"
														bind:value={reading.end_time}
														on:input={() => {
															reading.url = audioUrl(reading);
														}}
													/>
												</div>
												<div class="volume">
													Volume:
													<input
														type="number"
														bind:value={reading.volume}
														on:input={() => {
															reading.url = audioUrl(reading);
														}}
													/>
												</div>
											</div>
											<div class="bottom-row row">
												<div class="source">
													Source:
													<input type="text" value={`${reading.id}.mp3`} disabled />
												</div>
												<button class="open-button" on:click={() => openFile(reading.id)}
													>Open File</button
												>
												<button class="delete-button" on:click={() => deleteReading(reading.id)}
													>Delete</button
												>
												<button class="edit-button" on:click={() => editReading(reading)}
													>Apply</button
												>
												<!-- <button class="use-button" on:click={() => reading.use = true}>{reading.use ? "Using": "Use"}</button> -->
												<button class="use-button" on:click={() => useReading(reading)}
													>{reading.use ? 'Using' : 'Use'}</button
												>
											</div>
										</div>
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
	:root {
		--white: #ffffff;
		--primary: #008cff;
		--secondary: #0051ff;
		--tertiary: #0031cf;
		--action: #00af35;
		--info: #a100c2;
		--accent: #ff5e00;
		--warning: #ff4a53;

		--black: #000000;
		--dark0: #111111;
		--dark1: #1e2124;
		--dark2: #282b30;
		--dark3: #36393e;
		--dark4: #424549;
		--dark5: #525559;
		--dark6: #626569;
		--dark7: #727579;

		--border-radius: 5px;

		/*
		h = hint
		*/
		--hy: #fff3bf;
		--hr: #ffe3e3;
		--hb: #d0ebff;
		--hg: #e9fac8;

		/*
		p = pastel
		*/
		--py: #ffec99;
		--pr: #ffc9c9;
		--pb: #a5d8ff;
		--pg: #b2f2bb;

		--y: #ffd43b;
		--r: #ff8787;
		--b: #4dabf7;
		--g: #69db7c;
	}

	body {
		font-family: Arial, sans-serif;
		margin: 20px;
	}

	.container {
		max-width: 80vw;
		max-height: 90vh;
		/* overflow-y: scroll; */
		margin: 0 auto;
		border: 2px solid #ccc;
		padding: 10px;
		border-radius: 12px;
	}

	.header {
		width: 100%;
		display: flex;
		justify-content: center;
		text-align: center;
		align-items: center;
	}

	.header h1 {
		margin: 0;
	}

	.header .center .row,
	.header .center {
		display: flex;
		align-content: center;
		justify-content: center;
	}

	.collapsible {
		cursor: pointer;
		padding: 10px;
		border: none;
		outline: none;
		text-align: left;
		width: 100%;
		background-color: #f9f9f9;
		border-bottom: 1px solid #ccc;
		border-radius: 12px;
	}

	.collapsible:hover {
		background-color: var(-hb);
	}

	.collapsible:focus,
	.collapsible:active {
		background-color: var(-pb);
	}

	.content {
		padding: 0 15px;
		/* overflow: hidden; */
		/* border-radius: 12px; */
		margin-bottom: 10px;
	}
	.main-content,
	.content {
		border-left: 3px solid #000;
	}

	.container {
		overflow-y: hidden;
	}

	.main-content {
		max-height: 95vh;
		/* width: 80vw; */
		overflow-y: scroll;
		overflow-x: hidden;
	}

	.main-content,
	.content.chapter,
	.content.verse,
	.content.reading {
		border-color: var(--pb);
	}

	.content {
		display: none;
	}

	.content.active {
		display: block;
	}

	/* .buttons { */
	/* 	margin-top: 10px; */
	/* } */
	/**/
	/* .buttons button { */
	/* 	margin-right: 5px; */
	/* } */

	.source,
	.timestamps,
	.volume {
		margin-right: 10px;
	}

	/* button.chapter { */
	/* 	background: var(--hr); */
	/* } */
	/**/
	/* button.verse { */
	/* 	background: var(--hg); */
	/* } */
	/**/
	/* button.reading { */
	/* 	background: var(--hb); */
	/* } */

	.button-content {
		display: flex;
		align-items: center;
		text-align: center;
	}

	.button-content > div > h3,
	.button-content > h4 {
		margin-right: 2rem;
	}

	.button-content.verse > div.col > h3,
	.button-content.verse > div.col > h4,
	.button-content.verse > div.col > p {
		margin-top: 0;
		margin-bottom: 0;
	}

	.verse-results {
		margin-left: 2ch;
		text-align: left;
		color: var(--dark4);
	}

	.esv {
	}

	.row {
		display: flex;
	}

	.col {
		display: flex;
		flex-direction: column;
	}

	.top-row,
	.bottom-row {
		align-items: center;
		padding-top: 1rem;
		padding-bottom: 1rem;
	}

	.top-row > div,
	.top-row > div > input,
	.bottom-row > div > input {
		padding: 1ch;
		text-align: center;
		align-content: center;
		font-size: 1rem;
	}

	.top-row > div {
	}

	.top-row > div > input {
		border-radius: 8px;
		border: 1px solid black;
		width: 9ch;
	}

	.bottom-row > div > input {
		border-radius: 8px;
		border: 1px solid black;
		width: 22ch;
		text-align: center;
		align-content: center;
		background: #e9ecef;
	}

	#save-button {
		margin-left: 0rem;
	}

	button {
		padding: 0.5rem;
		font-size: 1rem;
		margin-left: 1rem;
		width: 12ch;
		border-radius: 8px;
	}

	.verse-select-row,
	.verse-select-row > div.row,
	.chapter-select-row {
		margin-top: 0.25rem;
		margin-bottom: 0.25rem;
	}
	
	button.chapter-select,
	button.verse-select {
		width: 4ch;
		padding: 0.25rem;
	}

	button.chapter-select {
		/* margin-left: ; */
		font-size: 1.25rem;
	}

	button.verse-select {
		margin-left: 0.25rem;
		/* font-size: 1.0rem; */
	}

	input:hover,
	input:focus,
	button:hover {
		background: var(--hb);
	}

	.open-button {
		background: var(--py);
	}

	.delete-button {
		background: var(--pr);
	}

	.edit-button {
		background: var(--pb);
	}

	.use-button {
		background: var(--pg);
	}

	.open-button:hover {
		background: var(--y);
	}

	.delete-button:hover {
		background: var(--r);
	}

	.edit-button:hover {
		background: var(--b);
	}

	.use-button:hover {
		background: var(--g);
	}

	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}

	/* Firefox */
	input[type='number'] {
		-moz-appearance: textfield;
	}

	.verse-selected,
	.chapter-selected,
	.selected-reading {
		background-color: var(--pg);
	}
</style>
