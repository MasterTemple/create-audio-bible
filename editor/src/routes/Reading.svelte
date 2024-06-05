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
		deleteReading
	} from './functions';
	import { writable } from 'svelte/store';
	import ExtraReading from './ExtraReading.svelte';
	import { onMount } from 'svelte';

	export let reading = {};
	export let i = 1;
	export let openNextReading = () => {};
	const extraReadings = writable(reading.extra);

	function deleteChild(childReading) {
		// console.log({childReading})
		// console.log({filtered: $extraReadings.filter((er) => er.i != childReading.i)})
		// console.log({$extraReadings})
		let i = 0;
		extraReadings.set(
			$extraReadings.filter((er) => er.i != childReading.i).map((er) => {
				return {
					...er,
					i: i++
				}
			})
		);
		reading.extra = $extraReadings;
	}

	function updateChild(childReading) {
		extraReadings.set(
			$extraReadings.map((er) => {
				if (er?.i != childReading?.i) {
					childReading;
				} else {
					return er;
				}
			})
		);
		reading.extra = $extraReadings;
	}

	extraReadings.subscribe((ers) => {
		// console.log({ers, extra: reading.extra})
		// update mergedUrl
		ers = [reading, ...ers]
		const fileIds = ers.map((e) => e.id).join(",")
		const startTimes = ers.map((e) => e.start_time).join(",")
		const endTimes = ers.map((e) => e.end_time).join(",")
		const volumes = ers.map((e) => e.volume).join(",")
		reading.mergedUrl = `${domain}/merged_audio?file_ids=${fileIds}&start_times=${startTimes}&end_times=${endTimes}&volumes=${volumes}`;
	})

	onMount(() => {
		extraReadings.set(reading.extra)
	})

	// console.log({reading})

</script>

<button
	class="collapsible button-content reading"
	on:click={() => openReading.set($openReading != reading.sid ? reading.sid : '')}
	class:using-reading={reading.use}
	class:reading-selected={$openReading == reading.sid}
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
		{#if $extraReadings.length != 0}
			<audio id={'audio-' + reading.sid} preload="none" bind:this={reading.audio} controls>
				<!-- <source src={audioUrl(reading)} type="audio/mpeg" /> -->
				<source src={reading.url} type="audio/mpeg" />
			</audio>
		{/if}
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
		<div class="source">
			Source:
			<input type="text" bind:value={reading.id} on:input={() => {
					reading.url = audioUrl(reading);
					// updateChild(reading)
			}}/>
		</div>
		<button
			class="add-button"
			on:click={() => {
				// addReading(reading)
				reading.extra.push({
					...reading,
					i: $extraReadings.length,
					extra: undefined,
					audio: undefined,
					mergedAudio: undefined,
					mergedUrl: undefined,
				});
				extraReadings.set(reading.extra);
			}}>Add</button
		>
	</div>
	<div class="middle-row col">
		{#each $extraReadings as extraReading}
			<ExtraReading reading={extraReading} {deleteChild} {updateChild} sid={reading.sid} />
		{/each}
	</div>
	<div class="bottom-row row">
		{#if $extraReadings.length == 0}
			<audio id={'audio-' + reading.sid} preload="none" bind:this={reading.audio} controls>
				<source src={reading.url} type="audio/mpeg" />
			</audio>
		{:else}
			<audio id={'audio-' + reading.sid + '-merged'} preload="none" bind:this={reading.mergedAudio} controls>
				<source src={reading.mergedUrl} type="audio/mpeg" />
			</audio>
		{/if}
		<button class="open-button" on:click={() => window.open(domain + `/file?id=${reading.id}`)}
			>Open File</button
		>
		<button class="delete-button" on:click={() => deleteReading(reading.id)}>Delete</button>
		<button class="edit-button" on:click={() => {
			// edit reading
			editReading(reading)
			// edit child readings
			// reading.extra.forEach((r) => editReading(r))
			$extraReadings.forEach((er) => {
				er.audio.preload = "auto"
				er?.audio?.load()
			})
			// $bookTree[$openChapter][$openReference] = [reading]
			$bookTree[$openChapter][$openReference].map((r) => {
				if(r.sid == reading.sid)
					return reading
				else
					return r
			})
			saveBookTree()

		}}>Apply</button>
		<!-- <button class="use-button" on:click={() => reading.use = true}>{reading.use ? "Using": "Use"}</button> -->
		<button
			class="use-button"
			on:click={() => {
				useReading(reading);
				openNextReading(reading.reference);
			}}>{reading.use ? 'Using' : 'Use'}</button
		>
	</div>
</div>

<style>
	@import './style.css';
</style>
