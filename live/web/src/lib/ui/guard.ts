// Keeps the site's art and words in the site: no right-click or long-press menu (so no "save image" or
// "open image in new tab"), no dragging a picture out, no copying the page. What can be typed into (a quiz
// being written, a login form) still works as usual: select, copy, paste and its menu. The pixel art and the
// videos are drawn by the page, and the CSS in app.css stops a phone's long press from offering them.
//
// This keeps a picture from being taken with a tap or a click; it cannot stop someone determined (a
// screenshot, the browser's developer tools), which no web page can.

const FIELD = 'input, textarea, select, [contenteditable]:not([contenteditable="false"])';

const inField = (target: EventTarget | null): boolean => target instanceof Element && target.closest(FIELD) !== null;

/** Starts the guard on the whole document; returns a function that stops it. */
export function guardContent(): () => void {
	const block = (event: Event) => {
		if (!inField(event.target)) event.preventDefault();
	};
	// a copy or cut counts as the field's only while the field is what has the focus
	const blockCopy = (event: ClipboardEvent) => {
		if (!inField(document.activeElement) && !inField(event.target)) event.preventDefault();
	};
	const events: [string, EventListener][] = [
		['contextmenu', block],
		['dragstart', block],
		['selectstart', block],
		['copy', blockCopy as EventListener],
		['cut', blockCopy as EventListener]
	];
	for (const [name, handler] of events) document.addEventListener(name, handler, { capture: true });
	return () => {
		for (const [name, handler] of events) document.removeEventListener(name, handler, { capture: true });
	};
}
