<script>
	import { openChapter, openReference, openReading, bookTree } from './stores';
	import {
		audioUrl, getAudioSegment, json_post,
	} from './functions';
	import { writable } from 'svelte/store';
	import { onMount } from 'svelte';

	export let reading = {};
	export let deleteChild = () => {};
	export let updateChild = () => {};
	export let sid;
	// export let updateTranscriptFromChild = () => {};

	let url = writable("")
	function updateValue() {
		reading.url = audioUrl(reading);
		url.set(reading.url);
		reading.audio.preload = "auto"
		reading.audio.load()
		console.log({reading, $url})
		updateChild(reading)
	}
	onMount(() => {
		reading.url = audioUrl(reading);
		url.set(reading.url)
	})
	async function updateChildTranscript() {
		reading.content = await getAudioSegment(reading.id, reading.start_time, reading.end_time)
		// updateTranscriptFromChild()
		updateChild(reading)
	}

	async function createReading() {
		let res = await json_post("/create_reading", {
			source_id: reading.id,
			start_time: reading.start_time,
			end_time: reading.end_time,
			reference: $openReference
		})
		reading = {
			...reading,
			...res.reading,
			// audio: reading.audio,
			// sid: `${reading.id}-${res.reading.start_seg}-${res.reading.end_seg}`,
			// reference: $openReference,
		}
		// reading.content = words.join(" ");
		$bookTree[$openChapter][$openReference] = [reading]
		saveBookTree()
	}

</script>

<div class="child-content verse">

<div
	id="{sid}-child-{reading.i}"
	class="child-content reading"
>
	<div class="top-row row">
		<audio id={`audio-${sid}-${reading.i}`} preload="none" bind:this={reading.audio} controls>
			<source src={$url} type="audio/mpeg" />
		</audio> <div class="start_time">
			Start:
			<input
				type="number"
				bind:value={reading.start_time}
					on:input={async() => updateChildTranscript}
				/> <!-- on:input={updateValue} /> -->
		</div>
		<div class="end_time">
			End:
			<input
				type="number"
				bind:value={reading.end_time}
					on:input={async() => updateChildTranscript}
				/> <!-- on:input={updateValue} /> -->
		</div>
		<div class="volume">
			Volume:
			<input
				type="number"
				bind:value={reading.volume}
				/> <!-- on:input={updateValue} /> -->
		</div>
		<div class="source">
			Source:
			<input type="text" bind:value={reading.id}
				/> <!-- on:input={updateValue} /> -->
		</div>
		<!-- <button class="add-button" on:click={() => { -->
		<!-- 	updateValue() -->
		<!-- }} -->
		<!-- 	>Refresh</button -->
		<!-- > -->
		<button class="remove-button" on:click={() => {
			deleteChild(reading)
		}}
			>Remove</button
		>
	</div>
</div>
</div>

<style>
	@import './style.css';
</style>
