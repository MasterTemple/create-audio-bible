import { writable } from "svelte/store";
	import { openChapter, openReference, openReading, bookTree, config, esv } from "./stores"

export const domain = 'http://127.0.0.1:5000';


/**
 * @param {Array<string>} arr
 * @returns {Array<Array<string>>}
 */
export function as2DArray(arr, maxRowLength = 20) {
	let rowCount = Math.floor(arr.length / maxRowLength);
	if (arr.length > maxRowLength * rowCount) {
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

/**
 * @param {string} - endpoint
 * @param {Object} - data
 * @returns {Object} - json
 */
export async function download_post(endpoint, data = {}) {
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

/**
 * @param {Object} reading
 */
export function audioUrl(reading) {
	// reading.autoplay = true;
	return `${domain}/audio?file_id=${reading.id}&start_time=${reading.start_time}&end_time=${reading.end_time}&volume=${reading?.volume || 1.0}`;
}

/**
 * @param {str} content -
 */
export function asId(content) {
	return content.replace(/[^A-z0-9]/g, '-') + '-content';
}

/**
 * @param {string} - endpoint
 * @returns {Object} - json
 */
export async function json_get(endpoint) {
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
 * @param {string} endpoint
 * @param {Object} data
 * @returns {Object} json
 */
export async function json_post(endpoint, data = {}) {
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


let book_tree = {}
bookTree.subscribe(async(bt) => {
	if (Object.entries(bt).length == 0)
		return;
	book_tree = bt
})

/**
 * @returns {void}
 */
export async function saveBookTree() {
	const data = { book_tree };
	const json = await json_post('/save', data);
}


// * @param {string} id - file id
// * @param {string} reference - file id
/**
 * @param {Object} reading
 */
export function editReading(reading) {
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
export function useReading(reading) {
	// unuse other reading
	const chapter = reading.reference.replace(/:\d+$/, '');
	const data = book_tree;
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
	// openNextReading(reading.reference);
}


/**
 * @param {string} id - file id
 */
export function deleteReading(id) {}

/**
 * @param {string} book - book in the Bible
 */
export async function getReferences(book) {
	const data = { book };
	const json = await json_post('/esv', data);
	esv.set(json);
}

/**
 * @param {Number} start_seg
 * @param {Number} end_seg
 * @returns {Array<string>} words
 */
export async function getWords(start_seg, end_seg) {
	const data = { start_seg, end_seg };
	const { words } = await json_post('/words', data);
	return words;
}


/**
 * @param {string} reference - Bible reference
 * @returns {string} content
 */
export async function getReference(reference) {
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

export async function setConfig() {
	const json = await json_get('/config');
	config.set(json);
}


export async function setBookTree() {
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
		if(tree[chapter][reference].length == 0 || tree[chapter][reference][0].id == 0) {
			tree[chapter][reference] = [
				{
					id: 0,
					start_time: 0,
					end_time: 0,
					start_seg: 0,
					end_seg: 0,
					content: "No Audio Content...",
					reference,
					url: "",
					volume: 1.0,
					use: true,
					sid: `0-0-0`,
					blank: true
				}
			]
		}
	}
	bookTree.set(tree);
}
