// Langsung: every room open right now and the children in it, as it changes. A pause button freezes the
// screen while you read; the connection keeps listening and the page catches up when you resume.

import { api } from './core.js';
import { askBulk, bulk, bulkBar, Selection } from './bulk.js';
import { eventRow, refreshTimes } from './feed.js';
import { roomPopup } from './popups.js';
import { clear, duration, empty, h, icon, num, pill, tile, toast } from './ui.js';

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

		const [kidsCard, kidsOut] = summary('Murid dalam talian', '0', 'smile', 'mint');
		const [roomsCard, roomsOut] = summary('Bilik terbuka', '0', 'door', '');
		const [playCard, playOut] = summary('Sedang bermain', '0', 'play', 'blue');
		const grid = h('div', { class: 'rooms' });
		const cards = new Map();
		const selection = new Selection();
		const all = h('input', { type: 'checkbox', class: 'pick', 'aria-label': 'Pilih semua bilik yang dipaparkan', onChange: () => selection.many([...cards.keys()].map((code) => [code, code]), all.checked) });
		const bar = bulkBar(selection, {
			actions: [
				{ label: 'Tutup bilik', icon: 'x', tone: 'danger', run: async (codes) => {
					if (!(await askBulk({ ids: codes, names: codes.map((code) => `Bilik ${code}`), typed: false, title: `Tutup ${codes.length} bilik?`, body: 'Semua murid dalam bilik ini diputuskan dan permainan berhenti.', ok: 'Tutup bilik' }))) return false;
					await bulk('/rooms/bulk', { codes, action: 'close' }, { noun: 'bilik', did: 'ditutup' });
				} }
			]
		});
		const pause = h('button', { class: 'btn sm', type: 'button', 'aria-pressed': 'false', onClick: () => setPaused(!paused) });
		const feed = h('ul', { class: 'list feed' });
		const events = [];

		root.append(
			h('div', { class: 'grid kpis' }, kidsCard, roomsCard, playCard),
			h('div', { class: 'gap' }),
			h('div', { class: 'grid' },
				h('section', { class: 's8' }, h('div', { class: 'toolbar' }, h('h2', { class: 'visually-hidden' }, 'Bilik'), h('label', { class: 'check pick-all-inline' }, all, 'Pilih semua'), h('span', { class: 'grow' }), pause), grid, bar.el),
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
			const button = h('button', { class: 'room', type: 'button', onClick: () => details(refs.code.textContent) },
				h('span', { class: 'room-top' }, refs.code, refs.phase),
				refs.title,
				refs.sub,
				h('span', { class: 'sub' }, refs.kids, refs.age)
			);
			const box = h('input', { type: 'checkbox', class: 'pick', onChange: () => selection.toggle(refs.code.textContent, box.checked, `Bilik ${refs.code.textContent}`) });
			const el = h('div', { class: 'room-wrap' }, button, h('label', { class: 'room-pick' }, box));
			return { el, refs, box };
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
				card.box.setAttribute('aria-label', `Pilih bilik ${room.code}`);
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
			selection.keep([...keep]); // a room that closed is no longer picked
			sync();
		}

		function sync() {
			for (const [code, card] of cards) {
				card.box.checked = selection.has(code);
				card.el.classList.toggle('selected', card.box.checked);
			}
			const chosen = [...cards.keys()].filter((code) => selection.has(code)).length;
			all.checked = cards.size > 0 && chosen === cards.size;
			all.indeterminate = chosen > 0 && chosen < cards.size;
			all.disabled = cards.size === 0;
		}
		selection.onChange(sync);

		const details = (code) => roomPopup(code, { on: ctx.on }).catch((error) => toast(error.message, 'bad'));

		function paintFeed(fresh) {
			feed.replaceChildren(...(events.length ? events.map((e, i) => eventRow(e, { fresh: fresh && i === 0 })) : [h('li', null, empty('smile', 'Belum ada yang masuk.'))]));
		}

		this.onSearch = (value) => {
			if (value === text) return;
			text = value;
			selection.clear();
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
