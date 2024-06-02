import { writable } from "svelte/store";

export const esv = writable({});

export const bookTree = writable({});
export const config = writable({
	book: 'Loading...',
	name: 'Loading...'
});

export const openChapter = writable('');
export const openReference = writable('');
export const openReading = writable('');
