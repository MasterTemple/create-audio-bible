<script>
	import { openChapter, openReference, openReading, bookTree } from './stores';
	import {
		asId,
		download_post,
		audioUrl,
		domain,
		json_get,
		json_post,
		saveBookTree,
		editReading,
		useReading,
		getReferences,
		setConfig,
		setBookTree,
		as2DArray,
		deleteReading,

		getAudioSegment

	} from './functions';
	import { writable } from 'svelte/store';

	export let reading = {};
	export let i = 1;
	export let openNextReading = () => {};

	async function createReading() {
		reading.blank = undefined;
		let res = await json_post("/create_reading", {
			source_id: reading.id,
			start_time: reading.start_time,
			end_time: reading.end_time,
			reference: $openReference
		})
		reading = {
			...res.reading,
			audio: reading.audio,
			sid: `${reading.id}-${res.reading.start_seg}-${res.reading.end_seg}`,
			reference: $openReference,
		}
		// reading.content = words.join(" ");
		$bookTree[$openChapter][$openReference] = [reading]
		saveBookTree()
	}
</script>

<button
	class="collapsible button-content reading"
	on:click={() => openReading.set($openReading != reading.sid ? reading.sid : '')}
	class:using-reading={reading.use}
	class:reading-selected={$openReading == reading.sid}
>
	<h4>Create Reading</h4>
	<p>{reading.content}</p>
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
					reading.content = getAudioSegment(id, reading.start_time, reading.end_time)
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
					reading.content = getAudioSegment(id, reading.start_time, reading.end_time)
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
			<input type="text" bind:value={reading.id} />
		</div>
		<button class="open-button" on:click={() => window.open(domain + `/file?id=${reading.id}`)}
			>Open File</button
		>
		<button class="delete-button" on:click={() => deleteReading(reading.id)}>Delete</button>
		<button class="edit-button" on:click={() => createReading(reading)}>Apply</button>
		<!-- <button class="use-button" on:click={() => reading.use = true}>{reading.use ? "Using": "Use"}</button> -->
		<button class="use-button" on:click={() => {
			useReading(reading)
			openNextReading(reading.reference);
		}}
			>{reading.use ? 'Using' : 'Use'}</button
		>
	</div>
</div>

<style>
	@import './style.css';
</style>
