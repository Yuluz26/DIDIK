// The dashboard: boots, routes between views (#/live, #/users …) and keeps the header and sidebar in step.
//
// A view is a module whose default export is { title, subtitle, range?, search?, action?, mount(root, ctx) }.
// `mount` returns a function that undoes what it set up (listeners, timers); the router calls it on leaving.

import { api, connect, emit, loadMe, on, refreshUnread, state } from './core.js';
import { clear, debounce, h, iconsIn, icon, num, toast } from './ui.js';

const ROUTES = {
	'': './overview.js',
	live: './live.js',
	activity: './activity.js',
	users: './users.js',
	quizzes: './quizzes.js',
	notifications: './notifications.js',
	security: './security.js'
};
const NAV = { '': 'overview' };

const $ = (id) => document.getElementById(id);
const root = $('view');
const search = $('search');
const range = $('range');
const action = $('action');
const status = $('status');

let current = null;
let cleanup = null;
let token = 0;

function hash() {
	const [path, query = ''] = location.hash.replace(/^#\/?/, '').split('?');
	return { path: path.replace(/\/$/, ''), params: new URLSearchParams(query) };
}

export function go(path, params) {
	const query = params ? `?${new URLSearchParams(params)}` : '';
	location.hash = `#/${path}${query}`;
}

// ---------------------------------------------------------------- routing

async function route() {
	const { path, params } = hash();
	const file = ROUTES[path] ?? ROUTES[''];
	const mine = ++token;
	cleanup?.();
	cleanup = null;
	closeMenu();

	for (const link of document.querySelectorAll('#nav a')) {
		const active = link.dataset.route === (NAV[path] || (ROUTES[path] ? path : 'overview'));
		if (active) link.setAttribute('aria-current', 'page');
		else link.removeAttribute('aria-current');
	}

	let view;
	try {
		view = (await import(file)).default;
	} catch (error) {
		console.error(error);
		return toast('Halaman ini tidak dapat dimuat.', 'bad');
	}
	if (mine !== token) return;

	current = view;
	document.title = `${view.title} · Bilik kawalan`;
	titleCount();
	range.hidden = !view.range;
	range.value = String(state.range);
	search.placeholder = view.search || 'Cari ibu bapa atau kuiz…';
	search.value = params.get('q') || '';
	if (view.action) {
		action.hidden = false;
		action.replaceChildren(icon(view.action.icon, 17), view.action.label);
	} else {
		action.hidden = true;
	}

	clear(root);
	root.append(
		h('div', { class: 'page-head' }, h('h1', null, view.title), view.subtitle && h('p', null, view.subtitle)),
		h('div', { id: 'stage' })
	);
	const stage = $('stage');
	try {
		cleanup = (await view.mount(stage, { api, state, on, go, params, toast, search: search.value })) || null;
	} catch (error) {
		console.error(error);
		stage.replaceChildren(h('div', { class: 'card' }, h('p', { class: 'error-line' }, error.message || 'Halaman ini gagal dimuat.')));
	}
	if (mine === token) {
		root.focus({ preventScroll: true });
		window.scrollTo(0, 0);
	}
}

// ---------------------------------------------------------------- header and sidebar

search.addEventListener(
	'input',
	debounce(() => current?.onSearch?.(search.value.trim()), 250)
);
search.addEventListener('keydown', (event) => {
	if (event.key === 'Enter' && current && !current.onSearch) {
		event.preventDefault();
		go('users', { q: search.value.trim() });
	}
});
document.addEventListener('keydown', (event) => {
	const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || '');
	if ((event.key === '/' && !typing && !document.querySelector('dialog[open]')) || ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k')) {
		event.preventDefault();
		search.focus();
		search.select();
	}
});

range.addEventListener('change', () => {
	state.range = Number(range.value);
	try {
		sessionStorage.setItem('range', String(state.range));
	} catch {
		/* private window: the choice lasts until the page is closed */
	}
	emit('range', state.range);
});

action.addEventListener('click', () => current?.action?.run({ api, state, on, go, toast }));

const closeMenu = () => {
	document.body.classList.remove('menu-open');
	$('menu').setAttribute('aria-expanded', 'false');
	$('scrim').hidden = true;
};
$('menu').addEventListener('click', () => {
	const open = document.body.classList.toggle('menu-open');
	$('menu').setAttribute('aria-expanded', String(open));
	$('scrim').hidden = !open;
});
$('scrim').addEventListener('click', closeMenu);
document.addEventListener('keydown', (event) => event.key === 'Escape' && closeMenu());

$('logout').addEventListener('click', async () => {
	await api('/logout', { method: 'POST' }).catch(() => {});
	location.reload();
});

// ---------------------------------------------------------------- status, counts, title

const LABELS = { live: 'Langsung', connecting: 'Menyambung…', stale: 'Data lama', down: 'Terputus. Menyambung semula…' };

function paintStatus() {
	status.dataset.state = state.status;
	let text = LABELS[state.status];
	if (state.status === 'live' && state.liveAt) {
		const seconds = Math.round((Date.now() - state.liveAt) / 1000);
		text = `Langsung · ${seconds < 2 ? 'sekarang' : `${seconds} s lalu`}`;
	}
	status.lastElementChild.textContent = text;
	status.title = text;
}
on('status', paintStatus);
on('tick', paintStatus);

on('live', (live) => {
	const badge = $('nav-live');
	badge.hidden = !live.online;
	badge.textContent = num(live.online);
	badge.title = `${live.online} murid dalam talian`;
});

function titleCount() {
	if (current) document.title = `${state.unread ? `(${state.unread}) ` : ''}${current.title} · Bilik kawalan`;
}
on('unread', (count) => {
	const badge = $('nav-unread');
	badge.hidden = !count;
	badge.textContent = count > 99 ? '99+' : String(count);
	badge.title = `${count} belum dibaca`;
	titleCount();
});
const recount = debounce(() => refreshUnread().catch(() => {}), 300);
for (const type of ['notification', 'notification-removed', 'notifications-changed']) on(type, recount);

// ---------------------------------------------------------------- boot

iconsIn(document);
window.addEventListener('hashchange', route);

(async () => {
	try {
		const me = await loadMe();
		$('me-mail').textContent = me.email;
		$('me-av').textContent = me.email[0].toUpperCase();
	} catch (error) {
		console.error(error);
	}
	connect();
	refreshUnread().catch(() => {});
	route();
})();
