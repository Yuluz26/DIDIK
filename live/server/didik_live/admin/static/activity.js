// Aktiviti: everything that happened, newest first, by day. New events arrive at the top while you look.

import { api, query } from './core.js';
import { eventRow, refreshTimes } from './feed.js';
import { dayLabel, empty, h, seg, skeletons } from './ui.js';

const GROUPS = [['', 'Semua'], ['user', 'Ibu bapa'], ['quiz', 'Kuiz'], ['room', 'Bilik'], ['player', 'Murid'], ['game', 'Permainan']];

export default {
	title: 'Aktiviti',
	subtitle: 'Semua yang berlaku di laman, yang terbaharu dahulu. Disimpan 90 hari.',
	search: 'Cari dalam aktiviti…',

	async mount(root, ctx) {
		const state = { group: '', q: '', before: null, more: false };
		const list = h('div');
		const more = h('button', { class: 'btn', type: 'button', onClick: () => load(true) }, 'Muat lagi');
		const card = h('section', { class: 'card' }, skeletons(6));
		root.append(h('div', { class: 'toolbar' }, seg(GROUPS, '', (value) => {
			state.group = value;
			load();
		})), card);

		let lastDay = '';
		const section = (day) => {
			const ul = h('ul', { class: 'list feed tall' });
			list.append(h('h2', { class: 'day' }, day), ul);
			return ul;
		};
		let currentList = null;

		function add(event, { fresh = false, top = false } = {}) {
			const day = dayLabel(event.at);
			if (top) {
				if (day !== list.firstChild?.textContent) {
					const ul = h('ul', { class: 'list feed tall' });
					list.prepend(ul);
					list.prepend(h('h2', { class: 'day' }, day));
					ul.append(eventRow(event, { fresh, detail: true }));
					return;
				}
				list.firstChild.nextSibling.prepend(eventRow(event, { fresh, detail: true }));
				return;
			}
			if (day !== lastDay) {
				lastDay = day;
				currentList = section(day);
			}
			currentList.append(eventRow(event, { detail: true }));
		}

		async function load(append = false) {
			if (!append) {
				card.replaceChildren(skeletons(6));
				list.replaceChildren();
				lastDay = '';
			}
			try {
				const page = await api(`/activity${query({ group: state.group, q: state.q, before: append ? state.before : '', per: 40 })}`);
				page.items.forEach((event) => add(event));
				state.before = page.items.at(-1)?.id ?? state.before;
				state.more = page.more;
				if (!list.firstChild) card.replaceChildren(empty('list', state.q || state.group ? 'Tiada aktiviti yang sepadan.' : 'Belum ada aktiviti.'));
				else card.replaceChildren(list, state.more ? h('div', { class: 'toolbar more' }, more) : '');
			} catch (error) {
				card.replaceChildren(h('p', { class: 'error-line' }, error.message));
			}
		}

		this.onSearch = (value) => {
			state.q = value;
			load();
		};
		const stops = [
			ctx.on('event', (event) => {
				if (event.kind.startsWith('admin.') || state.q || (state.group && !event.kind.startsWith(`${state.group}.`)) || !list.firstChild) return;
				add(event, { fresh: true, top: true });
			}),
			ctx.on('tick', () => refreshTimes(list))
		];
		await load();
		return () => {
			stops.forEach((stop) => stop());
			delete this.onSearch;
		};
	}
};
