<script>
	import { read } from '$app/server';
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';

	const domain = 'http://127.0.0.1:5000';
	const bookTree = writable({});
	const config = writable({});

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

	/**
	 * @param {str} id -
	 */
	function toggleContent(id) {
		const content = document.getElementById(asId(id));
		if (content.style.display === 'block') {
			content.style.display = 'none';
		} else {
			content.style.display = 'block';
		}
	}

	/**
	 * @param {string} id - file id
	 */
	function openFile(id) {
		// doesn't work right now
		window.open(domain + `/file?id=${id}`)
	}

	/**
	 * @returns {void}
	 */
	async function save() {
		const data = { "book_tree": $bookTree };
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
			return `${domain}/audio?file_id=${reading.id}&start_time=${reading.start_time}&end_time=${reading.end_time}&volume=${reading?.volume || 1.0}`
	}

	 // * @param {string} id - file id
	 // * @param {string} reference - file id
	/**
	 * @param {Object} reading
	 */
	function editReading(reading) {
		//! ALRIGHT ADD ID AND REFERENCE TO READING VARIABLE OK YESC
		console.log({reading})
		// const audioId = asId(`${reference} ${i} audio`);
		reading.audio.preload = "auto"
		reading.audio.load()
		// reading.audio.querySelector("source").source = audioUrl(reading);
	}

	/**
	 * @param {string} id - file id
	 */
	function useReading(id) {
		// save selection
		// collapse current verse tree and go to next verse
	}

	const esv = writable({})

	/**
	 * @param {string} book - book in the Bible
	 */
	async function getReferences(book) {
		const data = { book };
		const json = await json_post('/esv', data);
		esv.set(json)
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
			tree[chapter][reference] = readings.slice(0, 5).map((r) => {
				return {
					...r,
					reference,
					url: audioUrl(r)
				}
			});
		}
		bookTree.set(tree);
	}

	onMount(async () => {
		// get project name & config
		await setConfig();

		// set ESV book data
		await getReferences($config.book)

		// get reading info
		await setBookTree();
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
				<h1>{$config.name}</h1>
				<a href="file:///home/dgmastertemple/Documents/GitHub/create-audio-bible/projects/Ephesians - Tim Conway/json" on:click={() => window.open("file:///home/dgmastertemple/Documents/GitHub/create-audio-bible/projects/Ephesians - Tim Conway/json")}>click</a>
				<!-- make a drop-down to select export audio files in verses, chapters, or the whole book -->
				<div class="row">
					<button>Export</button>
					<button on:click={save}>Save</button>
				</div>
			</div>
			<div class="main-content">

			{#each Object.entries($bookTree) as [chapter, referencesToReadings]}
				<button class="collapsible chapter" on:click={() => toggleContent(chapter)}>
					<h2>{chapter}</h2>
				</button>
				<div id={asId(chapter)} class="content chapter">
					{#each Object.entries(referencesToReadings).sort((a, b) => a[0].match(/\d+$/g)[0] - b[0].match(/\d+$/g)[0]) as [reference, readings]}
						<button class="collapsible button-content verse" on:click={() => toggleContent(reference)}>
							<h3>{reference}</h3>
							<!-- {#await getReference(reference) then content} -->
							<!-- 	<p class="esv">{content}</p> -->
							<!-- {/await} -->
								<p class="esv">{$esv[reference]}</p>
						</button>

						<div id={asId(reference)} class="content verse">
							{#each readings as reading, i}
								<button class="collapsible button-content reading" on:click={toggleContent(`${reference} ${i}`)}>
									<h4>Reading {i + 1}</h4>
									<p>{reading.content || 'No audio content...'}</p>
								</button>
								<div id={asId(`${reference} ${i}`)} class="content reading">
									<div class="top-row row">
										<audio
											preload="none"
											bind:this={reading.audio}
											controls
										>
											<!-- <source src={audioUrl(reading)} type="audio/mpeg" /> -->
											<source
												src={reading.url}
												type="audio/mpeg"
											/>
										</audio>
											<div class="start_time">
												Start:
												<input type="number" bind:value={reading.start_time} on:input={() => {reading.url = audioUrl(reading)}}>
											</div>
											<div class="end_time">
												End:
												<input type="number" bind:value={reading.end_time} on:input={() => {reading.url = audioUrl(reading)}}>
											</div>
											<div class="volume">
												Volume:
												<input type="number" value={reading?.volume || 1}>
											</div>
									</div>
									<div class="bottom-row row">
										<div class="source">
												Source: 
												<input type="text" value={`${reading.id}.mp3`} disabled>
											</div>
										<button class="open-button" on:click={() => openFile(reading.id)}>Open File</button>
										<button class="delete-button" on:click={() => deleteReading(reading.id)}>Delete</button>
										<button class="edit-button" on:click={() => editReading(reading)}>Edit</button>
										<button class="use-button" on:click={() => useReading(reading.id)}>Use</button>
									</div>
								</div>
							{/each}
						</div>
					{/each}
				</div>
			{/each}
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
		margin: 0 auto;
		border: 2px solid #ccc;
		padding: 10px;
		border-radius: 12px;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.header h1 {
		margin: 0;
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

	.collapsible:hover,
	.collapsible.active {
		background-color: #ddd;
	}

	.main-content,
	.content {
		padding: 0 15px;
		overflow: hidden;
		border-left: 3px solid #000;
		/* border-radius: 12px; */
		margin-bottom: 10px;
	}

	.main-content {
		border-color: var(--py)
	}

	.content.chapter {
		border-color: var(--pr);
	}

	.content.verse {
		border-color: var(--pb);
	}

	.content.reading {
		border-color: var(--pg);
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

	.button-content > h3,
	.button-content > h4 {
		margin-right: 2rem;
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
		width: 7ch;
	}

	.bottom-row > div > input {
		border-radius: 8px;
		border: 1px solid black;
		width: 18ch;
		text-align: center;
		align-content: center;
		background: #e9ecef;
	}

	.bottom-row > button {
		padding: 0.5rem;
		font-size: 1rem;
		margin-left: 1rem;
		width: 12ch;
		border-radius: 8px;
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


</style>
