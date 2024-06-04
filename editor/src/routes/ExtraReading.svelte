<script>
	import { openChapter, openReference, openReading, bookTree } from './stores';
	import {
		audioUrl,
	} from './functions';
	import { writable } from 'svelte/store';
	import { onMount } from 'svelte';
	export let reading = {};
	export let deleteChild = () => {};
	export let updateChild = () => {};
	export let sid;
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
</script>

<div
	id="{sid}-child-{reading.i}"
	class="child-content reading"
>
	<div class="top-row row">
		<audio id={`audio-${sid}-${reading.i}`} preload="none" bind:this={reading.audio} controls>
			<source src={$url} type="audio/mpeg" />
		</audio>
		<div class="start_time">
			Start:
			<input
				type="number"
				bind:value={reading.start_time}
				on:input={updateValue} />
		</div>
		<div class="end_time">
			End:
			<input
				type="number"
				bind:value={reading.end_time}
				on:input={updateValue} />
		</div>
		<div class="volume">
			Volume:
			<input
				type="number"
				bind:value={reading.volume}
				on:input={updateValue} />
		</div>
		<div class="source">
			Source:
			<input type="text" bind:value={reading.id}
				on:input={updateValue} />
		</div>
		<button class="remove-button" on:click={() => {
			deleteChild(reading)
		}}
			>Remove</button
		>
	</div>
</div>

<style>
	@import './style.css';
</style>
