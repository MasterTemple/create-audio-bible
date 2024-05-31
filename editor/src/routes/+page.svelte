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
		const res = await fetch(domain + endpoint);
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
	 * @param {PointerEvent} e - event of user clicking expandable/collapsible region
	 */
	function toggleChildren(e) {
		const button = e.target;
		button.classList.toggle('active');
		const content = button.nextElementSibling;
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
		window.open(
			`file:///home/dgmastertemple/Documents/GitHub/create-audio-bible/projects/Ephesians - Tim Conway/downloads/${id}.mp3`
		);
	}

	/**
	 * @param {string} id - file id
	 */
	function deleteReading(id) {}

	/**
	 * @param {string} id - file id
	 */
	function editReading(id) {}

	/**
	 * @param {string} id - file id
	 */
	function useReading(id) {
		// save selection
		// collapse current verse tree and go to next verse
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
			tree[chapter][reference] = readings.slice(0, 5);
		}
		bookTree.set(tree);
		console.log($bookTree);
	}

	onMount(async () => {
		// get project name & config
		await setConfig();

		// get reading info
		await setBookTree();
	});
</script>

<html lang="en">
	<head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0" />
		<title>Ephesians</title>
		<style>
			body {
				font-family: Arial, sans-serif;
				margin: 20px;
			}

			.container {
				max-width: 800px;
				margin: 0 auto;
				border: 1px solid #ccc;
				padding: 10px;
				border-radius: 5px;
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
			}

			.collapsible:hover,
			.collapsible.active {
				background-color: #ddd;
			}

			.content {
				padding: 0 15px;
				display: none;
				overflow: hidden;
				border-left: 3px solid #ccc;
				margin-bottom: 10px;
			}

			.content.active {
				display: block;
			}

			.buttons {
				margin-top: 10px;
			}

			.buttons button {
				margin-right: 5px;
			}

			.source,
			.timestamps,
			.volume {
				margin-right: 10px;
			}
		</style>
	</head>
	<body>
		<div class="container">
			<div class="header">
				<h1>Ephesians - Tim Conway</h1>
				<!-- make a drop-down to select export audio files in verses, chapters, or the whole book -->
				<button>Export</button>
			</div>
			{#each Object.entries($bookTree) as [chapter, referencesToReadings]}
				<button class="collapsible" on:click={toggleChildren}>{chapter}</button>
				<div class="content">
					{#each Object.entries(referencesToReadings).sort((a, b) => a[0].match(/\d+$/g)[0] - b[0].match(/\d+$/g)[0]) as [reference, readings]}
						<button class="collapsible" on:click={toggleChildren}>
							<p>{reference}</p>
							{#await getReference(reference) then content}
								<p>{content}</p>
							{/await}
						</button>

						<div class="content">
							{#each readings as reading, i}
								<button class="collapsible" on:click={toggleChildren}>Reading {i + 1}</button>
								<div class="content">
									<p>{reading.content || 'The verse content...'}</p>
									<div class="source">Source: {reading.id}.mp3</div>
									<div class="timestamps">Start: {reading.start_time} End: {reading.end_time}</div>
									<div class="volume">Volume: 1x</div>
									<div class="buttons">
										<button on:click={() => openFile(reading.id)}>Open File</button>
										<button on:click={() => deleteReading(reading.id)}>Delete</button>
										<button on:click={() => editReading(reading.id)}>Edit</button>
										<button on:click={() => useReading(reading.id)}>Use</button>
									</div>
								</div>
							{/each}
						</div>
					{/each}
				</div>
			{/each}
		</div>
	</body>
</html>
