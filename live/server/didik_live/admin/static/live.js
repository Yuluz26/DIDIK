// Langsung: every room open right now and the children in it, as it changes. A pause button freezes the
// screen while you read; the connection keeps listening and the page catches up when you resume.

import { api } from './core.js';
import { eventRow, refreshTimes } from './feed.js';
import { clear, confirmBox, duration, empty, h, icon, num, openDialog, pill, sheetHead, tile, toast } from './ui.js';

const PHASES = { lobby: ['Menunggu', 'info'], playing: ['Bermain', 'ok'], ended: ['Tamat', 'warn'] };
const LIVE_KINDS = /^(player|room|game)\./;

function summary(label, value, iconName, tone) {
	const out = h('b', { class: 'num' }, value);
	return [h('section', { class: 'card stat s4' }, h('div', { class: 'card-head' }, h('h2', null, label), tile(iconName, tone)), h('div', { class: 'row' }, out)), out];
}

export default {
	title: 'Langsung',
	subtitle: 'Bilik yang sedang dibuka dan murid di dalamnya.',
	search: 'Cari kod bilik, kuiz atau hos…',

	async mount(root, ctx) {
		let text = '';
		let paused = false;
		let pending = null;
		let open = null; // the room whose drawer is open: { code, refresh }

		const [kidsCard, kidsOut] = summary('Murid dalam talian', '0', 'smile', 'mint');
		const [roomsCard, roomsOut] = summary('Bilik terbuka', '0', 'door', '');
		const [playCard, playOut] = summary('Sedang bermain', '0', 'play', 'blue');
		const grid = h('div', { class: 'rooms' });
		const cards = new Map();
		const pause = h('button', { class: 'btn sm', type: 'button', 'aria-pressed': 'false', onClick: () => setPaused(!paused) });
		const feed = h('ul', { class: 'list feed' });
		const events = [];

		root.append(
			h('div', { class: 'grid kpis' }, kidsCard, roomsCard, playCard),
			h('div', { class: 'gap' }),
			h('div', { class: 'grid' },
				h('section', { class: 's8' }, h('div', { class: 'toolbar' }, h('h2', { class: 'visually-hidden' }, 'Bilik'), h('span', { class: 'grow' }), pause), grid),
				h('section', { class: 'card s4' }, h('div', { class: 'card-head' }, h('h2', null, 'Baru berlaku')), feed)
			)
		);

		function setPaused(on) {
			paused = on;
			pause.setAttribute('aria-pressed', String(on));
			pause.replaceChildren(icon(on ? 'play' : 'pause', 15), on ? 'Sambung kemas kini' : 'Jeda kemas kini');
			if (!on && pending) paint(pending);
		}
		setPaused(false);

		function roomCard(room) {
			const refs = {
				code: h('span', { class: 'code' }),
				phase: h('span'),
				title: h('span', { class: 'title' }),
				sub: h('span', { class: 'sub' }),
				kids: h('span'),
				age: h('span')
			};
			const el = h('button', { class: 'room', type: 'button', onClick: () => details(refs.code.textContent) },
				h('span', { class: 'room-top' }, refs.code, refs.phase),
				refs.title,
				refs.sub,
				h('span', { class: 'sub' }, refs.kids, refs.age)
			);
			return { el, refs };
		}

		function paint(live) {
			pending = live;
			if (paused) return;
			pending = null;
			kidsOut.textContent = num(live.online);
			roomsOut.textContent = num(live.rooms.length);
			playOut.textContent = num(live.rooms.filter((r) => r.phase === 'playing').length);

			const query = text.toLowerCase();
			const shown = live.rooms.filter((r) => !query || `${r.code} ${r.quiz} ${r.host} ${r.modeTitle}`.toLowerCase().includes(query));
			const keep = new Set();
			shown.forEach((room, index) => {
				keep.add(room.code);
				let card = cards.get(room.code);
				if (!card) cards.set(room.code, (card = roomCard(room)));
				const [label, kind] = PHASES[room.phase] || PHASES.lobby;
				card.refs.code.textContent = room.code;
				card.refs.phase.replaceChildren(pill(room.locked ? `${label} · dikunci` : label, kind));
				card.refs.title.textContent = room.quiz;
				card.refs.sub.textContent = `${room.modeTitle} · ${room.host}`;
				card.refs.kids.textContent = `${room.online}/${room.players} murid dalam talian`;
				card.refs.age.textContent = ` · dibuka ${duration(room.age)}`;
				if (grid.children[index] !== card.el) grid.insertBefore(card.el, grid.children[index] || null);
			});
			for (const [code, card] of cards) {
				if (!keep.has(code)) {
					card.el.remove();
					cards.delete(code);
				}
			}
			if (!shown.length) grid.replaceChildren(empty('door', query ? 'Tiada bilik yang sepadan.' : 'Tiada bilik dibuka sekarang. Bilik muncul di sini sebaik sahaja ibu bapa membukanya.'));
			else grid.querySelector('.empty')?.remove();
			open?.refresh();
		}

		async function details(code) {
			let people = h('ul', { class: 'who-list' });
			const facts = h('dl', { class: 'kv' });
			const render = (room) => {
				const [label, kind] = PHASES[room.phase] || PHASES.lobby;
				facts.replaceChildren(
					...[['Permainan', room.modeTitle], ['Kuiz', room.quiz], ['Hos', room.host], ['Keadaan', pill(label, kind)], ['Dibuka', `${duration(room.age)} lalu`]].flatMap(([k, v]) => [h('dt', null, k), h('dd', null, v)])
				);
				people.replaceChildren(...(room.people.length
					? room.people.map((p) => h('li', { class: p.online ? '' : 'off' }, h('i'), p.name, !p.approved && h('span', { class: 'sub' }, '(menunggu)')))
					: [h('li', null, 'Belum ada murid')]));
			};
			let first;
			try {
				first = await api(`/rooms/${encodeURIComponent(code)}`);
			} catch (error) {
				return toast(error.message, 'bad');
			}
			await openDialog((close) => {
				render(first);
				open = {
					code,
					refresh: async () => {
						try {
							render(await api(`/rooms/${encodeURIComponent(code)}`));
						} catch {
							close();
						}
					}
				};
				return h('div', { class: 'sheet' },
					sheetHead(`Bilik ${code}`, close, 'Dikemas kini sendiri'),
					facts,
					h('div', null, h('h3', { class: 'sub' }, 'Murid'), h('div', { class: 'gap' }), people),
					h('div', { class: 'sheet-foot' },
						h('button', { class: 'btn danger', type: 'button', onClick: async () => {
							if (!(await confirmBox({ title: `Tutup bilik ${code}?`, body: 'Semua murid dalam bilik ini akan diputuskan dan permainan berhenti.', ok: 'Tutup bilik', danger: true }))) return;
							try {
								await api(`/rooms/${encodeURIComponent(code)}/close`, { method: 'POST' });
								toast(`Bilik ${code} ditutup.`);
								close();
							} catch (error) {
								toast(error.message, 'bad');
							}
						} }, icon('x', 16), 'Tutup bilik'),
						h('button', { class: 'btn', type: 'button', onClick: () => close() }, 'Selesai')
					)
				);
			}, { drawer: true });
			open = null;
		}

		function paintFeed(fresh) {
			feed.replaceChildren(...(events.length ? events.map((e, i) => eventRow(e, { fresh: fresh && i === 0 })) : [h('li', null, empty('smile', 'Belum ada yang masuk.'))]));
		}

		this.onSearch = (value) => {
			text = value;
			if (ctx.state.live) paint(ctx.state.live);
		};

		try {
			const log = await api('/activity?per=60');
			events.push(...log.items.filter((e) => LIVE_KINDS.test(e.kind)).slice(0, 14));
		} catch {
			/* the feed fills as things happen */
		}
		paintFeed(false);
		if (ctx.state.live) paint(ctx.state.live);

		const stops = [
			ctx.on('live', paint),
			ctx.on('event', (event) => {
				if (!LIVE_KINDS.test(event.kind) || paused) return;
				events.unshift(event);
				events.length = Math.min(events.length, 14);
				paintFeed(true);
			}),
			ctx.on('tick', () => refreshTimes(feed))
		];
		return () => {
			stops.forEach((stop) => stop());
			delete this.onSearch;
			clear(grid);
		};
	}
};
