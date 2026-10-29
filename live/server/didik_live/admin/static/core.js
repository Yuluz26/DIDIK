// The dashboard's state, its API client and its live connection. Views listen with `on` and never open a socket.

import { setZone } from './ui.js';

export const BASE = document.documentElement.dataset.base;

export const state = {
	me: null,
	live: null,
	liveAt: 0,
	status: 'connecting',
	unread: 0,
	range: Number(sessionStorage.getItem('range')) || 14
};

const listeners = new Map();

export function on(type, fn) {
	if (!listeners.has(type)) listeners.set(type, new Set());
	listeners.get(type).add(fn);
	return () => listeners.get(type).delete(fn);
}

export function emit(type, data) {
	for (const fn of listeners.get(type) || []) {
		try {
			fn(data);
		} catch (error) {
			console.error(error);
		}
	}
}

export function query(params) {
	const out = new URLSearchParams();
	for (const [key, value] of Object.entries(params || {})) {
		if (value !== '' && value != null && value !== false) out.set(key, value);
	}
	const text = out.toString();
	return text ? `?${text}` : '';
}

export async function api(path, { method = 'GET', body } = {}) {
	const response = await fetch(`${BASE}/api${path}`, {
		method,
		headers: { 'x-didik-admin': '1', ...(body ? { 'content-type': 'application/json' } : {}) },
		body: body ? JSON.stringify(body) : undefined,
		credentials: 'same-origin'
	});
	if (response.status === 401) {
		location.reload();
		throw new Error('Sesi tamat. Log masuk semula.');
	}
	if (response.status === 204) return null;
	const data = await response.json().catch(() => ({}));
	if (!response.ok) {
		const error = new Error(data.message || 'Sesuatu tidak kena. Cuba lagi.');
		error.status = response.status;
		throw error;
	}
	return data;
}

export async function loadMe() {
	state.me = await api('/me');
	setZone(state.me.timezone);
	return state.me;
}

export async function refreshUnread() {
	const { unread } = await api('/notifications?show=unread');
	state.unread = unread;
	emit('unread', unread);
}

// ---------------------------------------------------------------- the live connection

let socket;
let attempts = 0;
let reconnect = 0;
const STALE_AFTER = 12_000;

function setStatus(status) {
	if (state.status === status) return;
	state.status = status;
	emit('status', status);
}

export function connect() {
	clearTimeout(reconnect);
	setStatus(attempts ? 'down' : 'connecting');
	const scheme = location.protocol === 'https:' ? 'wss' : 'ws';
	socket = new WebSocket(`${scheme}://${location.host}${BASE}/ws`);
	socket.onmessage = (event) => {
		let message;
		try {
			message = JSON.parse(event.data);
		} catch {
			return;
		}
		attempts = 0;
		switch (message.t) {
			case 'hello':
				setStatus('live');
				break;
			case 'live':
				state.live = message;
				state.liveAt = Date.now();
				setStatus('live');
				emit('live', message);
				break;
			case 'event':
			case 'notification':
			case 'notification-removed':
			case 'notifications-changed':
				emit(message.t, message.event || message.notification || message);
				break;
			case 'bye':
				location.reload();
				break;
		}
	};
	socket.onclose = (event) => {
		if (event.code === 4401) return location.reload();
		setStatus('down');
		attempts += 1;
		reconnect = setTimeout(connect, Math.min(15_000, 1000 * 2 ** Math.min(attempts, 4)));
	};
}

export function reconnectNow() {
	if (socket && socket.readyState <= 1) return;
	attempts = 0;
	connect();
}

// A connection that is open but silent for too long is not "live": say so instead of showing old numbers as current.
setInterval(() => {
	if (state.status === 'live' && state.liveAt && Date.now() - state.liveAt > STALE_AFTER) setStatus('stale');
	else if (state.status === 'stale' && Date.now() - state.liveAt <= STALE_AFTER) setStatus('live');
	emit('tick', Date.now());
}, 1000);

document.addEventListener('visibilitychange', () => {
	if (!document.hidden) reconnectNow();
});
