// Kuiz: every quiz parents wrote. Look at the questions, fix a title, or remove one.

import { api, query } from './core.js';
import { askBulk, bulk, bulkBar, Selection } from './bulk.js';
import { dataTable } from './table.js';
import { quizPopup } from './popups.js';
import { ago, h, icon, num, seg, toast } from './ui.js';

export default {
	title: 'Kuiz',
	subtitle: 'Semua kuiz yang ditulis ibu bapa.',
	search: 'Cari tajuk kuiz atau nama ibu bapa…',

	async mount(root, ctx) {
		const state = { samples: false, q: ctx.params.get('q') || '', page: 1 };
		const selection = new Selection();
		const table = dataTable({
			columns: ['Kuiz', 'Ibu bapa', 'Soalan', 'Dikemas kini', ''],
			emptyText: 'Tiada kuiz yang sepadan.',
			selection,
			rowId: (q) => q.id,
			rowName: (q) => q.title,
			onPage: (step) => {
				state.page += step;
				load();
			},
			render: (q) => h('tr', null,
				h('td', { class: 'lead' }, h('button', { class: 'row-open', type: 'button', onClick: () => open(q.id), 'aria-label': `Buka ${q.title}` }, h('span', { class: 'person' }, h('span', { class: 'tile-ic blue' }, icon('book', 17)), h('span', null, h('b', null, q.title), h('small', null, q.description || '—'))))),
				h('td', { 'data-label': 'Ibu bapa' }, q.owner),
				h('td', { class: 'num', 'data-label': 'Soalan' }, num(q.questions)),
				h('td', { 'data-label': 'Dikemas kini' }, ago(q.updatedAt)),
				h('td', null, h('span', { class: 'actions' }, h('button', { class: 'btn sm', type: 'button', onClick: () => open(q.id) }, 'Butiran')))
			)
		});
		const count = h('span', { class: 'sub' });
		const bar = bulkBar(selection, {
			actions: [
				{ label: 'Padam', icon: 'trash', tone: 'danger', run: async (ids, names) => {
					const many = `${num(ids.length)} kuiz`;
					if (!(await askBulk({ ids, names, title: `Padam ${many}?`, body: state.samples ? 'Kuiz contoh akan dibuang. Ini tidak boleh dibatalkan.' : 'Kuiz ini dipadam untuk selama-lamanya daripada akaun pemiliknya.', ok: `Padam ${many}` }))) return false;
					await bulk('/quizzes/bulk', { ids, action: 'delete' }, { noun: 'kuiz', did: 'dipadam' });
					load();
				} }
			]
		});
		root.append(h('div', { class: 'toolbar' }, seg([['mine', 'Ibu bapa'], ['samples', 'Kuiz contoh']], 'mine', (value) => {
			state.samples = value === 'samples';
			state.page = 1;
			selection.clear();
			load();
		}), count), table.el, bar.el);

		async function load() {
			table.busy(true);
			try {
				const result = await api(`/quizzes${query({ q: state.q, samples: state.samples, page: state.page })}`);
				table.set(result);
				count.textContent = `${num(result.total)} kuiz`;
				bar.matching({ total: result.total, pageIds: result.items.map((q) => q.id), fetchAll: () => api(`/quizzes/ids${query({ q: state.q, samples: state.samples })}`) });
			} catch (error) {
				toast(error.message, 'bad');
			} finally {
				table.busy(false);
			}
		}
		const open = (id) => quizPopup(id, { onChange: load }).catch((error) => toast(error.message, 'bad'));

		this.onSearch = (value) => {
			if (value === state.q) return;
			state.q = value;
			state.page = 1;
			selection.clear();
			load();
		};
		const stop = ctx.on('event', (event) => event.kind.startsWith('quiz.') && load());
		await load();
		return () => {
			stop();
			delete this.onSearch;
		};
	}
};
