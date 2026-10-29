// Gambaran: the whole site at a glance. Totals and trends come from the server for the chosen period;
// the live card, the activity feed and the open rooms follow the live connection.

import { api } from './core.js';
import { donut, heatmap, spark, tiles } from './charts.js';
import { eventRow, refreshTimes } from './feed.js';
import { editNote } from './notifications.js';
import { ago, avatar, change, empty, h, icon, num, seg, skeletons, tile } from './ui.js';

const FEED_SIZE = 12;

function statCard({ label, iconName, tone, value, period, previous, series, days, unit }) {
	const diff = change(period, previous);
	return h('section', { class: 'card stat s3' },
		h('div', { class: 'card-head' }, h('h2', null, label), tile(iconName, tone)),
		h('div', { class: 'row' },
			h('div', null, h('div', { class: 'num' }, num(value)), h('p', { class: 'sub' }, unit)),
			h('div', { class: `spark ${tone}` }, spark(series, tone))
		),
		h('div', { class: 'meta' },
			h('span', { class: `delta ${diff.kind}` }, diff.kind === 'up' && icon('up', 12), diff.kind === 'down' && icon('down', 12), diff.text),
			h('span', { class: 'sub' }, `${num(period)} dalam ${days} hari`)
		)
	);
}

export default {
	title: 'Gambaran',
	subtitle: 'Apa yang berlaku di DIDIK, dari ibu bapa hingga murid.',
	range: true,
	action: { label: 'Nota baharu', icon: 'plus', run: () => editNote() },

	async mount(root, ctx) {
		const { state } = ctx;
		const top = h('div', { class: 'grid' });
		const rows = h('div', { class: 'grid' });
		const bottom = h('div', { class: 'grid' });
		root.append(top, rows, bottom);

		// ---- cards that follow the live connection
		const liveNum = h('div', { class: 'num' }, '—');
		const liveRooms = h('b', null, '0');
		const liveKids = h('b', null, '0');
		const livePlaying = h('b', null, '0');
		const liveCard = h('section', { class: 'card stat s3' },
			h('div', { class: 'card-head' }, h('h2', null, 'Dalam talian sekarang'), tile('pulse', 'mint')),
			h('div', null, liveNum, h('p', { class: 'sub' }, 'murid dalam talian')),
			h('div', { class: 'mini' }, h('div', null, 'Bilik terbuka', liveRooms), h('div', null, 'Sedang bermain', livePlaying), h('div', null, 'Murid dalam bilik', liveKids))
		);
		const roomsList = h('ul', { class: 'list' });
		const roomsCard = h('section', { class: 'card s4' }, h('div', { class: 'card-head' }, h('h2', null, 'Bilik terbuka'), h('a', { href: '#/live' }, 'Lihat semua')), roomsList);
		const feed = h('ul', { class: 'list feed' });
		const feedCard = h('section', { class: 'card s4' }, h('div', { class: 'card-head' }, h('h2', null, 'Aktiviti langsung'), h('a', { href: '#/activity' }, 'Lihat semua')), feed);

		const paintLive = (live) => {
			if (!live) return;
			liveNum.textContent = num(live.online);
			liveRooms.textContent = num(live.rooms.length);
			liveKids.textContent = num(live.children);
			livePlaying.textContent = num(live.rooms.filter((room) => room.phase === 'playing').length);
			roomsList.replaceChildren(...(live.rooms.length
				? live.rooms.slice(0, 5).map((room) => h('li', null,
					tile('door', room.phase === 'playing' ? 'mint' : ''),
					h('span', { class: 'grow' }, h('span', null, `${room.modeTitle} · ${room.host}`), h('small', null, `${room.quiz}`)),
					h('span', { class: 'pill info' }, `${room.online}/${room.players}`)))
				: [h('li', null, empty('door', 'Tiada bilik dibuka sekarang.'))]));
		};

		// ---- the cards that come from the server
		const notes = h('ul', { class: 'list notes-mini' });
		const newest = h('div');
		const newestCard = h('section', { class: 'card s4' }, h('div', { class: 'card-head' }, h('h2', null, 'Terbaharu')), newest);
		const notesCard = h('section', { class: 'card s4' }, h('div', { class: 'card-head' }, h('h2', null, 'Notifikasi'), h('a', { href: '#/notifications' }, 'Lihat semua')), notes);

		const heatHost = h('div');
		const donutHost = h('div');
		bottomCards();
		function bottomCards() {
			bottom.append(
				h('section', { class: 'card s5' }, h('div', { class: 'card-head' }, h('h2', null, 'Murid masuk ikut masa'), h('span', { class: 'sub' }, '4 minggu terakhir')), heatHost),
				roomsCard,
				h('section', { class: 'card s3' }, h('div', { class: 'card-head' }, h('h2', null, 'Murid ikut permainan')), donutHost)
			);
		}
		rows.append(feedCard, newestCard, notesCard);

		const feedItems = [];
		const addEvent = (event, fresh) => {
			if (event.kind.startsWith('admin.') || event.kind === 'user.login') return;
			feedItems.unshift(event);
			feedItems.length = Math.min(feedItems.length, FEED_SIZE);
			feed.replaceChildren(...feedItems.map((e, i) => eventRow(e, { fresh: fresh && i === 0 })));
		};

		async function load() {
			const days = state.range;
			top.replaceChildren(h('section', { class: 'card s3' }, skeletons(3)), h('section', { class: 'card s3' }, skeletons(3)), h('section', { class: 'card s3' }, skeletons(3)), liveCard);
			try {
				const [data, activity, notification] = await Promise.all([api(`/overview?days=${days}`), api('/activity?per=30'), api('/notifications')]);
				const total = data.modes.reduce((a, m) => a + m.count, 0);
				top.replaceChildren(
					h('section', { class: 'card s3' }, h('div', { class: 'card-head' }, h('h2', null, 'Permainan dibuka')), h('p', { class: 'sub tight' }, `${num(total)} bilik dalam ${days} hari`), tiles(data.modes, 'bilik')),
					statCard({ label: 'Ibu bapa', iconName: 'users', tone: '', value: data.parents.total, period: data.parents.period, previous: data.parents.previous, series: data.parents.series, days, unit: 'jumlah akaun' }),
					statCard({ label: 'Murid masuk', iconName: 'smile', tone: 'mint', value: data.students.period, period: data.students.period, previous: data.students.previous, series: data.students.series, days, unit: `dalam ${days} hari` }),
					liveCard
				);
				paintLive(state.live);

				feedItems.length = 0;
				for (const event of activity.items.filter((e) => e.kind !== 'user.login').slice(0, FEED_SIZE)) feedItems.push(event);
				feed.replaceChildren(...(feedItems.length ? feedItems.map((e) => eventRow(e)) : [h('li', null, empty('list', 'Belum ada aktiviti.'))]));

				const people = seg([['users', 'Ibu bapa'], ['quizzes', 'Kuiz']], 'users', (value) => drawNewest(value));
				const drawNewest = (kind) => {
					const items = kind === 'users'
						? data.recentUsers.map((u) => h('li', null, avatar(u.name), h('span', { class: 'grow' }, h('b', null, u.name), h('small', null, u.email)), h('time', null, ago(u.createdAt))))
						: data.recentQuizzes.map((q) => h('li', null, tile('book', 'blue'), h('span', { class: 'grow' }, h('b', null, q.title), h('small', null, `${q.owner} · ${q.questions} soalan`)), h('time', null, ago(q.createdAt))));
					list.replaceChildren(...(items.length ? items : [h('li', null, empty('inbox', kind === 'users' ? 'Belum ada ibu bapa.' : 'Belum ada kuiz.'))]));
				};
				const list = h('ul', { class: 'list' });
				drawNewest('users');
				newest.replaceChildren(people, h('div', { class: 'gap' }), list);

				const unread = notification.items.slice(0, 5);
				notes.replaceChildren(...(unread.length
					? unread.map((n) => h('li', { class: n.read ? '' : 'unread' }, tile(n.level === 'success' ? 'check' : n.level === 'info' ? 'info' : 'alert', n.level === 'success' ? 'mint' : n.level === 'warning' ? 'amber' : n.level === 'danger' ? 'red' : ''), h('span', { class: 'grow' }, h('b', null, n.title), n.body && h('small', null, n.body)), h('time', null, ago(n.createdAt))))
					: [h('li', null, empty('bell', 'Tiada notifikasi.'))]));

				heatHost.replaceChildren(heatmap(data.heatmap));
				const parts = data.studentsByMode.slice(0, 5).map((m) => ({ label: m.title, count: m.count }));
				donutHost.replaceChildren(parts.length ? donut(parts, data.students.period, 'murid') : empty('smile', 'Belum ada murid masuk.'));
			} catch (error) {
				top.replaceChildren(h('section', { class: 'card s12' }, h('p', { class: 'error-line' }, error.message), h('button', { class: 'btn sm', type: 'button', onClick: load }, 'Cuba lagi')));
			}
		}

		const stops = [
			ctx.on('live', paintLive),
			ctx.on('event', (event) => addEvent(event, true)),
			ctx.on('range', load),
			ctx.on('tick', () => refreshTimes(feed))
		];
		await load();
		return () => stops.forEach((stop) => stop());
	}
};
