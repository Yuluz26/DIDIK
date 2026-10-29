// What every view shares: building elements, icons, dates, dialogs and toasts.
//
// Text goes into the page through `textContent` only (see `h`). A parent's name, a quiz title and a child's
// nickname are written by strangers; none of them is ever parsed as HTML. The only `innerHTML` in this file
// sets an icon from the constants below.

export function h(tag, attrs, ...kids) {
	const el = document.createElement(tag);
	for (const [name, value] of Object.entries(attrs || {})) {
		if (value == null || value === false) continue;
		if (name === 'class') el.className = value;
		else if (name === 'data') Object.assign(el.dataset, value);
		else if (name.startsWith('on')) el.addEventListener(name.slice(2).toLowerCase(), value);
		else el.setAttribute(name, value === true ? '' : value);
	}
	put(el, kids);
	return el;
}

export function put(el, kids) {
	for (const kid of kids.flat(Infinity)) {
		if (kid == null || kid === false) continue;
		el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
	}
	return el;
}

export const clear = (el) => el.replaceChildren();

// ---------------------------------------------------------------- icons (24px, stroke)

const P = (d) => `<path d="${d}"/>`;
const ICONS = {
	grid: '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
	pulse: P('M22 12h-4l-3 9L9 3l-3 9H2'),
	list: P('M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01'),
	users: P('M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2') + '<circle cx="9" cy="7" r="4"/>' + P('M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75'),
	user: P('M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2') + '<circle cx="12" cy="7" r="4"/>',
	'user-plus': P('M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2') + '<circle cx="9" cy="7" r="4"/>' + P('M19 8v6M22 11h-6'),
	book: P('M4 19.5A2.5 2.5 0 0 1 6.5 17H20M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z'),
	bell: P('M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0'),
	shield: P('M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'),
	logout: P('M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9'),
	menu: P('M3 12h18M3 6h18M3 18h18'),
	search: '<circle cx="11" cy="11" r="7.5"/>' + P('m21 21-4.3-4.3'),
	plus: P('M12 5v14M5 12h14'),
	x: P('M18 6 6 18M6 6l12 12'),
	check: P('M20 6 9 17l-5-5'),
	trash: P('M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2'),
	edit: P('M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z'),
	pin: P('M12 17v5M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z'),
	up: P('m5 12 7-7 7 7M12 19V5'),
	down: P('M12 5v14M19 12l-7 7-7-7'),
	flame: P('M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.07-2.14-.22-4.05 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.15.43-2.29 1-3a2.5 2.5 0 0 0 2.5 2.5z'),
	door: P('M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z') + P('M9 22V12h6v10'),
	flag: P('M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1zM4 22v-7'),
	smile: '<circle cx="12" cy="12" r="10"/>' + P('M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01'),
	lock: '<rect x="3" y="11" width="18" height="11" rx="2"/>' + P('M7 11V7a5 5 0 0 1 10 0v4'),
	alert: P('M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0zM12 9v4M12 17h.01'),
	info: '<circle cx="12" cy="12" r="10"/>' + P('M12 16v-4M12 8h.01'),
	mail: '<rect x="2" y="4" width="20" height="16" rx="2"/>' + P('m22 7-10 5L2 7'),
	device: '<rect x="2" y="3" width="20" height="14" rx="2"/>' + P('M8 21h8M12 17v4'),
	refresh: P('M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16M3 21v-5h5'),
	pause: P('M6 4h4v16H6zM14 4h4v16h-4z'),
	play: P('M6 3l14 9-14 9z'),
	more: '<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>',
	inbox: P('M22 12h-6l-2 3h-4l-2-3H2') + P('M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z'),
	play2: P('M5 3l14 9-14 9z'),
	ban: '<circle cx="12" cy="12" r="10"/>' + P('m4.9 4.9 14.2 14.2')
};

export function icon(name, size = 18) {
	const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
	svg.setAttribute('viewBox', '0 0 24 24');
	svg.setAttribute('width', size);
	svg.setAttribute('height', size);
	svg.setAttribute('fill', 'none');
	svg.setAttribute('stroke', 'currentColor');
	svg.setAttribute('stroke-width', '1.9');
	svg.setAttribute('stroke-linecap', 'round');
	svg.setAttribute('stroke-linejoin', 'round');
	svg.setAttribute('aria-hidden', 'true');
	svg.innerHTML = ICONS[name] || ICONS.info;
	return svg;
}

export function iconsIn(root) {
	for (const el of root.querySelectorAll('[data-icon]')) {
		if (!el.firstChild) el.append(icon(el.dataset.icon, el.classList.contains('icon-btn') ? 20 : 18));
	}
}

// ---------------------------------------------------------------- numbers and dates

let zone = 'Asia/Kuala_Lumpur';
export const setZone = (name) => {
	zone = name;
};

const numbers = new Intl.NumberFormat('ms-MY');
export const num = (n) => numbers.format(n ?? 0);

export function change(now, before) {
	if (!before) return now ? { text: 'baharu', kind: 'up' } : { text: '0%', kind: '' };
	const pct = ((now - before) / before) * 100;
	const text = `${pct > 0 ? '+' : pct < 0 ? '−' : ''}${Math.abs(pct).toLocaleString('ms-MY', { maximumFractionDigits: 1 })}%`;
	return { text, kind: pct > 0 ? 'up' : pct < 0 ? 'down' : '' };
}

export function ago(iso) {
	const seconds = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
	if (seconds < 8) return 'sebentar tadi';
	if (seconds < 60) return `${Math.floor(seconds)} s lalu`;
	if (seconds < 3600) return `${Math.floor(seconds / 60)} min lalu`;
	if (seconds < 86400) return `${Math.floor(seconds / 3600)} j lalu`;
	if (seconds < 7 * 86400) return `${Math.floor(seconds / 86400)} hari lalu`;
	return date(iso);
}

export const date = (iso) => (iso ? new Intl.DateTimeFormat('ms-MY', { timeZone: zone, day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(iso)) : '—');
export const clock = (iso) => new Intl.DateTimeFormat('ms-MY', { timeZone: zone, hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(iso));
export const stamp = (iso) => (iso ? new Intl.DateTimeFormat('ms-MY', { timeZone: zone, day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(iso)) : '—');

export function dayLabel(iso) {
	const key = (d) => new Intl.DateTimeFormat('en-CA', { timeZone: zone }).format(d);
	const then = key(new Date(iso));
	if (then === key(new Date())) return 'Hari ini';
	if (then === key(new Date(Date.now() - 86400000))) return 'Semalam';
	return new Intl.DateTimeFormat('ms-MY', { timeZone: zone, weekday: 'long', day: 'numeric', month: 'long' }).format(new Date(iso));
}

export function duration(seconds) {
	if (seconds < 60) return `${seconds} s`;
	if (seconds < 3600) return `${Math.floor(seconds / 60)} min`;
	return `${Math.floor(seconds / 3600)} j ${Math.floor((seconds % 3600) / 60)} min`;
}

// ---------------------------------------------------------------- small pieces

export function avatar(name, size) {
	let hash = 0;
	for (const ch of name || '?') hash = (hash * 31 + ch.charCodeAt(0)) % 360;
	const el = h('span', { class: 'av', 'aria-hidden': 'true' }, [...(name || '?').trim()][0]?.toUpperCase() || '?');
	el.style.setProperty('--hue', `hsl(${hash} 62% 55%)`);
	if (size) {
		el.style.width = el.style.height = `${size}px`;
	}
	return el;
}

export const pill = (text, kind = '') => h('span', { class: `pill ${kind}` }, text);

export function tile(iconName, tone = '') {
	return h('span', { class: `tile-ic ${tone}` }, icon(iconName, 17));
}

export function empty(iconName, text) {
	return h('div', { class: 'empty' }, icon(iconName, 28), h('p', null, text));
}

export function skeletons(count = 4) {
	return h('ul', { class: 'list', 'aria-hidden': 'true' }, Array.from({ length: count }, () => h('li', null, h('span', { class: 'skeleton' }))));
}

export function seg(options, current, onPick) {
	const wrap = h('div', { class: 'seg', role: 'group' });
	const draw = (now) => {
		clear(wrap);
		for (const [value, label] of options) {
			wrap.append(h('button', { type: 'button', 'aria-pressed': String(value === now), onClick: () => { draw(value); onPick(value); } }, label));
		}
	};
	draw(current);
	return wrap;
}

export function debounce(fn, ms) {
	let timer;
	return (...args) => {
		clearTimeout(timer);
		timer = setTimeout(() => fn(...args), ms);
	};
}

// ---------------------------------------------------------------- toasts and dialogs

export function toast(message, kind = 'ok') {
	const box = document.getElementById('toasts');
	const el = h('div', { class: `toast ${kind}` }, icon(kind === 'ok' ? 'check' : 'alert', 18), h('span', null, message));
	box.append(el);
	setTimeout(() => el.remove(), kind === 'ok' ? 3800 : 6500);
}

/** Opens the page's one <dialog>. `build(close)` returns the sheet's content; the promise ends with close(value). */
export function openDialog(build, { drawer = false } = {}) {
	const dialog = document.getElementById('dialog');
	return new Promise((resolve) => {
		let result;
		const close = (value) => {
			result = value;
			dialog.close();
		};
		const finish = () => {
			dialog.removeEventListener('close', finish);
			dialog.removeEventListener('click', away);
			dialog.replaceChildren();
			resolve(result);
		};
		const away = (event) => {
			if (event.target === dialog) close();
		};
		dialog.className = drawer ? 'drawer' : 'modal';
		dialog.replaceChildren(build(close));
		dialog.addEventListener('close', finish);
		dialog.addEventListener('click', away);
		dialog.showModal();
		dialog.querySelector('[autofocus]')?.focus();
	});
}

export function sheetHead(title, close, sub) {
	return h('div', { class: 'sheet-head' }, h('div', null, h('h2', null, title), sub && h('p', { class: 'sub' }, sub)), h('button', { class: 'icon-btn', type: 'button', 'aria-label': 'Tutup', onClick: () => close() }, icon('x', 20)));
}

export function confirmBox({ title, body, ok = 'Ya', danger = false }) {
	return openDialog((close) =>
		h('div', { class: 'sheet', role: 'alertdialog', 'aria-label': title },
			sheetHead(title, close),
			h('p', { class: 'sheet-text' }, body),
			h('div', { class: 'sheet-foot' },
				h('button', { class: 'btn', type: 'button', onClick: () => close(false), autofocus: true }, 'Batal'),
				h('button', { class: `btn ${danger ? 'danger' : 'primary'}`, type: 'button', onClick: () => close(true) }, ok)
			)
		)
	).then((value) => value === true);
}
