// Ibu bapa: everyone who signed up. Find, look at, rename, suspend or delete.

import { api, query } from './core.js';
import { askBulk, bulk, bulkBar, Selection } from './bulk.js';
import { dataTable } from './table.js';
import { userPopup } from './popups.js';
import { ago, avatar, date, h, num, pill, seg, toast } from './ui.js';

export default {
	title: 'Ibu bapa',
	subtitle: 'Akaun yang mendaftar, dan apa yang mereka buat.',
	search: 'Cari nama atau emel…',

	async mount(root, ctx) {
		const state = { status: 'active', q: ctx.params.get('q') || '', page: 1 };
		const selection = new Selection();
		const table = dataTable({
			columns: ['Ibu bapa', 'Mendaftar', 'Log masuk terakhir', 'Kuiz', 'Status', ''],
			emptyText: 'Tiada ibu bapa yang sepadan.',
			selection,
			rowId: (u) => u.id,
			rowName: (u) => u.name,
			selectable: (u) => !u.system, // the demo and sample-library accounts are never touched
			onPage: (step) => {
				state.page += step;
				load();
			},
			render: (u) => h('tr', null,
				h('td', { class: 'lead' }, h('button', { class: 'row-open', type: 'button', onClick: () => open(u.id), 'aria-label': `Buka ${u.name}` }, h('span', { class: 'person' }, avatar(u.name), h('span', null, h('b', null, u.name), h('small', null, u.email))))),
				h('td', { 'data-label': 'Mendaftar' }, date(u.createdAt)),
				h('td', { 'data-label': 'Log masuk terakhir' }, u.lastLoginAt ? ago(u.lastLoginAt) : 'Belum pernah'),
				h('td', { class: 'num', 'data-label': 'Kuiz' }, num(u.quizzes)),
				h('td', { 'data-label': 'Status' }, u.disabled ? pill('Digantung', 'bad') : u.system ? pill('Sistem', 'info') : pill('Aktif', 'ok')),
				h('td', null, h('span', { class: 'actions' }, h('button', { class: 'btn sm', type: 'button', onClick: () => open(u.id) }, 'Butiran')))
			)
		});
		const count = h('span', { class: 'sub' });
		const people = (ids) => `${num(ids.length)} ibu bapa`;
		const bar = bulkBar(selection, {
			actions: [
				{ label: 'Gantung', icon: 'ban', show: () => state.status === 'active', run: async (ids, names) => {
					if (!(await askBulk({ ids, names, danger: false, title: `Gantung ${people(ids)}?`, body: 'Mereka tidak boleh log masuk lagi dan bilik yang mereka buka ditutup. Anda boleh memulihkan mereka bila-bila masa.', ok: 'Gantung' }))) return false;
					await bulk('/users/bulk', { ids, action: 'suspend' }, { noun: 'ibu bapa', did: 'digantung' });
					load();
				} },
				{ label: 'Pulihkan', icon: 'check', show: () => state.status === 'suspended', run: async (ids) => {
					await bulk('/users/bulk', { ids, action: 'restore' }, { noun: 'ibu bapa', did: 'dipulihkan' });
					load();
				} },
				{ label: 'Padam', icon: 'trash', tone: 'danger', show: () => state.status !== 'system', run: async (ids, names) => {
					if (!(await askBulk({ ids, names, title: `Padam ${people(ids)}?`, body: 'Akaun, semua kuiz dan gambar mereka dipadam, dan bilik yang mereka buka ditutup. Ini tidak boleh dibatalkan.', ok: `Padam ${people(ids)}` }))) return false;
					await bulk('/users/bulk', { ids, action: 'delete' }, { noun: 'ibu bapa', did: 'dipadam' });
					load();
				} }
			]
		});
		root.append(h('div', { class: 'toolbar' }, seg([['active', 'Aktif'], ['suspended', 'Digantung'], ['system', 'Sistem']], state.status, (value) => {
			state.status = value;
			state.page = 1;
			selection.clear(); // rows of another list are not "picked" any more
			load();
		}), count), table.el, bar.el);

		async function load() {
			table.busy(true);
			try {
				const result = await api(`/users${query({ q: state.q, status: state.status, page: state.page })}`);
				table.set(result);
				count.textContent = `${num(result.total)} akaun`;
				bar.matching({ total: result.total, pageIds: result.items.filter((u) => !u.system).map((u) => u.id), fetchAll: () => api(`/users/ids${query({ q: state.q, status: state.status })}`) });
			} catch (error) {
				toast(error.message, 'bad');
			} finally {
				table.busy(false);
			}
		}
		const open = (id) => userPopup(id, { onChange: load }).catch((error) => toast(error.message, 'bad'));

		this.onSearch = (value) => {
			if (value === state.q) return; // the same words again (a re-fired input event) change nothing, picks included
			state.q = value;
			state.page = 1;
			selection.clear();
			load();
		};
		const stop = ctx.on('event', (event) => /^user\.(signup|suspended|restored|deleted)$/.test(event.kind) && load());
		await load();
		return () => {
			stop();
			delete this.onSearch;
		};
	}
};
