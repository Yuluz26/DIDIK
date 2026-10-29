// One activity event as a list row. Used by the overview, the live page, the activity log and the security page.

import { ago, h, tile } from './ui.js';

const KINDS = {
	'user.signup': ['user-plus', 'mint', 'Ibu bapa baharu'],
	'user.login': ['user', 'mute', 'Log masuk'],
	'user.suspended': ['ban', 'amber', 'Digantung'],
	'user.restored': ['check', 'mint', 'Dipulihkan'],
	'user.deleted': ['trash', 'red', 'Dipadam'],
	'quiz.created': ['book', 'blue', 'Kuiz'],
	'quiz.updated': ['edit', 'mute', 'Kuiz dikemas kini'],
	'quiz.deleted': ['trash', 'red', 'Kuiz dipadam'],
	'room.opened': ['door', '', 'Bilik dibuka'],
	'room.closed': ['door', 'mute', 'Bilik ditutup'],
	'player.joined': ['smile', 'mint', 'Murid masuk'],
	'game.started': ['play', '', 'Permainan bermula'],
	'game.finished': ['flag', 'blue', 'Permainan tamat'],
	'admin.signin': ['lock', 'mint', 'Log masuk admin'],
	'admin.signin_failed': ['alert', 'red', 'Kod salah'],
	'admin.refused': ['alert', 'amber', 'Emel tidak dibenarkan'],
	'admin.otp_sent': ['mail', 'mute', 'Kod dihantar'],
	'admin.mail_failed': ['alert', 'red', 'Emel gagal'],
	'admin.signout': ['lock', 'mute', 'Log keluar admin'],
	'admin.room_closed': ['door', 'amber', 'Bilik ditutup admin'],
	'admin.quiz_edited': ['edit', 'amber', 'Kuiz disunting admin'],
	'admin.session_revoked': ['shield', 'amber', 'Sesi ditamatkan'],
	'admin.sessions_revoked': ['shield', 'amber', 'Sesi ditamatkan']
};

export const kindLabel = (kind) => (KINDS[kind] || [, , kind])[2];

export function eventRow(event, { fresh = false, detail = false } = {}) {
	const [iconName, tone, label] = KINDS[event.kind] || ['info', 'mute', event.kind];
	const time = h('time', { datetime: event.at, title: new Date(event.at).toLocaleString('ms-MY') }, ago(event.at));
	time.dataset.at = event.at;
	return h(
		'li',
		{ class: fresh ? 'fresh' : '' },
		tile(iconName, tone),
		h('span', { class: 'grow' }, h('span', null, event.summary), h('small', null, detail && event.data?.ip ? `${label} · ${event.data.ip}` : label)),
		time
	);
}

/** Keeps "3 min lalu" honest while the page stays open. */
export function refreshTimes(container) {
	for (const time of container.querySelectorAll('time[data-at]')) time.textContent = ago(time.dataset.at);
}
