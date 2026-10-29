// Notifications: what the site tells the owner (a new parent, a sign-in from a new address) and the owner's own notes.
// Create, read, pin, edit, delete.

import { api } from './core.js';
import { askBulk, bulk, bulkBar, Selection } from './bulk.js';
import { ago, clear, confirmBox, empty, h, icon, openDialog, seg, sheetHead, skeletons, tile, toast } from './ui.js';

const LEVELS = {
	info: ['Maklumat', 'info', ''],
	success: ['Berjaya', 'check', 'mint'],
	warning: ['Amaran', 'alert', 'amber'],
	danger: ['Penting', 'alert', 'red']
};

/** The dialog for a new note or an edit. Resolves with the saved notification, or undefined when cancelled. */
export function editNote(note) {
	return openDialog((close) => {
		let level = note?.level || 'info';
		const title = h('input', { class: 'input', id: 'note-title', maxlength: 120, required: true, value: note?.title || '', autofocus: true, autocomplete: 'off' });
		const body = h('textarea', { class: 'input', id: 'note-body', maxlength: 600, rows: 4 }, note?.body || '');
		const pinned = h('input', { type: 'checkbox', id: 'note-pin' });
		pinned.checked = !!note?.pinned;
		const error = h('p', { class: 'error-line', role: 'alert', hidden: true });
		title.addEventListener('input', () => (error.hidden = true));
		const levels = h('div', { class: 'levels', role: 'group', 'aria-label': 'Tahap' });
		const drawLevels = () => {
			clear(levels);
			for (const [key, [label]] of Object.entries(LEVELS)) {
				levels.append(h('button', { type: 'button', class: 'btn sm', 'aria-pressed': String(key === level), onClick: () => { level = key; drawLevels(); } }, label));
			}
		};
		drawLevels();

		const form = h('form', { class: 'sheet', novalidate: true },
			sheetHead(note ? 'Sunting notifikasi' : 'Nota baharu', close),
			h('label', { class: 'field' }, h('span', null, 'Tajuk'), title),
			h('label', { class: 'field' }, h('span', null, 'Butiran (pilihan)'), body),
			h('div', { class: 'field' }, h('span', null, 'Tahap'), levels),
			h('label', { class: 'check' }, pinned, 'Sematkan di atas'),
			error,
			h('div', { class: 'sheet-foot' }, h('button', { class: 'btn', type: 'button', onClick: () => close() }, 'Batal'), h('button', { class: 'btn primary', type: 'submit' }, 'Simpan'))
		);
		form.addEventListener('submit', async (event) => {
			event.preventDefault();
			if (!title.value.trim()) {
				error.hidden = false;
				error.textContent = 'Tajuk wajib diisi.';
				return title.focus();
			}
			const payload = { title: title.value.trim(), body: body.value.trim(), level, pinned: pinned.checked };
			try {
				close(note ? await api(`/notifications/${note.id}`, { method: 'PATCH', body: payload }) : await api('/notifications', { method: 'POST', body: payload }));
				toast(note ? 'Notifikasi dikemas kini.' : 'Nota disimpan.');
			} catch (problem) {
				error.hidden = false;
				error.textContent = problem.message;
			}
		});
		return form;
	});
}

export default {
	title: 'Notifikasi',
	subtitle: 'Apa yang laman beritahu anda, dan nota anda sendiri.',
	search: 'Cari notifikasi…',
	action: { label: 'Nota baharu', icon: 'plus', run: () => editNote() },

	async mount(root, ctx) {
		let show = 'all';
		let text = '';
		let rows = [];
		let shown = [];
		let last = -1;
		const selection = new Selection();
		const list = h('ul', { class: 'list note-list' });
		const all = h('input', { type: 'checkbox', class: 'pick', 'aria-label': 'Pilih semua notifikasi yang dipaparkan', onChange: () => selection.many(shown.map((n) => [n.id, n.title]), all.checked) });
		const bar = bulkBar(selection, {
			actions: [
				{ label: 'Dibaca', icon: 'check', run: async (ids) => { await bulk('/notifications/bulk', { ids, action: 'read' }, { noun: 'notifikasi', did: 'ditandakan sudah dibaca' }); load(); } },
				{ label: 'Belum dibaca', icon: 'bell', run: async (ids) => { await bulk('/notifications/bulk', { ids, action: 'unread' }, { noun: 'notifikasi', did: 'ditandakan belum dibaca' }); load(); } },
				{ label: 'Sematkan', icon: 'pin', run: async (ids) => { await bulk('/notifications/bulk', { ids, action: 'pin' }, { noun: 'notifikasi', did: 'disematkan' }); load(); } },
				{ label: 'Nyahsemat', icon: 'x', run: async (ids) => { await bulk('/notifications/bulk', { ids, action: 'unpin' }, { noun: 'notifikasi', did: 'dinyahsematkan' }); load(); } },
				{ label: 'Padam', icon: 'trash', tone: 'danger', run: async (ids, names) => {
					if (!(await askBulk({ ids, names, typed: false, title: `Padam ${ids.length} notifikasi?`, body: 'Notifikasi yang dipilih dibuang. Ini tidak boleh dibatalkan.', ok: 'Padam' }))) return false;
					await bulk('/notifications/bulk', { ids, action: 'delete' }, { noun: 'notifikasi', did: 'dipadam' });
					load();
				} }
			]
		});
		const body = h('div', { class: 'card' }, skeletons(3));
		const readAll = h('button', { class: 'btn sm', type: 'button', onClick: async () => { await api('/notifications/read-all', { method: 'POST' }); toast('Semua ditandakan sudah dibaca.'); load(); } }, icon('check', 15), 'Tandakan semua dibaca');
		const clearRead = h('button', { class: 'btn sm', type: 'button', onClick: async () => {
			if (!(await confirmBox({ title: 'Kosongkan yang sudah dibaca?', body: 'Notifikasi yang sudah dibaca akan dibuang. Yang disematkan kekal.', ok: 'Kosongkan', danger: true }))) return;
			await api('/notifications', { method: 'DELETE' });
			toast('Dikosongkan.');
			load();
		} }, icon('trash', 15), 'Kosongkan yang dibaca');
		root.append(h('div', { class: 'toolbar' }, h('label', { class: 'check pick-all-inline' }, all, 'Pilih semua'), seg([['all', 'Semua'], ['unread', 'Belum dibaca'], ['pinned', 'Disematkan'], ['manual', 'Nota saya']], show, (value) => { show = value; selection.clear(); load(); }), h('span', { class: 'grow' }), readAll, clearRead), body, bar.el);

		const card = (note) => {
			const [label, iconName, tone] = LEVELS[note.level] || LEVELS.info;
			const index = shown.indexOf(note);
			const box = h('input', { type: 'checkbox', class: 'pick', 'aria-label': `Pilih “${note.title}”` });
			box.addEventListener('click', (event) => {
				const from = event.shiftKey && last >= 0 ? Math.min(last, index) : index;
				const to = event.shiftKey && last >= 0 ? Math.max(last, index) : index;
				selection.many(shown.slice(from, to + 1).map((n) => [n.id, n.title]), box.checked);
				last = index;
			});
			return h('li', { class: note.read ? '' : 'unread', data: { id: note.id } },
				box,
				tile(iconName, tone),
				h('span', { class: 'grow' },
					h('b', null, note.title),
					note.body && h('span', { class: 'body' }, note.body),
					h('small', null, `${label} · ${note.source === 'manual' ? 'nota saya' : 'laman'} · ${ago(note.createdAt)}`)
				),
				h('span', { class: 'actions' },
					h('button', { class: 'icon-btn', type: 'button', 'aria-label': note.pinned ? 'Nyahsemat' : 'Sematkan', 'aria-pressed': String(note.pinned), title: note.pinned ? 'Nyahsemat' : 'Sematkan', onClick: () => patch(note, { pinned: !note.pinned }) }, icon('pin', 17)),
					h('button', { class: 'icon-btn', type: 'button', 'aria-label': note.read ? 'Tandakan belum dibaca' : 'Tandakan sudah dibaca', title: note.read ? 'Tandakan belum dibaca' : 'Tandakan sudah dibaca', onClick: () => patch(note, { read: !note.read }) }, icon('check', 17)),
					h('button', { class: 'icon-btn', type: 'button', 'aria-label': 'Sunting', title: 'Sunting', onClick: async () => { if (await editNote(note)) load(); } }, icon('edit', 17)),
					h('button', { class: 'icon-btn', type: 'button', 'aria-label': 'Padam', title: 'Padam', onClick: () => remove(note) }, icon('trash', 17))
				)
			);
		};

		const paint = () => {
			const query = text.toLowerCase();
			shown = query ? rows.filter((n) => `${n.title} ${n.body}`.toLowerCase().includes(query)) : rows;
			last = -1;
			selection.keep(shown.map((n) => n.id)); // a note that was deleted or filtered out is no longer picked
			clear(list);
			shown.forEach((note) => list.append(card(note)));
			body.replaceChildren(shown.length ? list : empty('inbox', query ? 'Tiada notifikasi yang sepadan.' : show === 'unread' ? 'Semua sudah dibaca.' : 'Belum ada notifikasi.'));
			sync();
		};

		function sync() {
			for (const li of list.children) {
				const on = selection.has(Number(li.dataset.id));
				li.querySelector('input.pick').checked = on;
				li.classList.toggle('selected', on);
			}
			const chosen = shown.filter((n) => selection.has(n.id)).length;
			all.checked = shown.length > 0 && chosen === shown.length;
			all.indeterminate = chosen > 0 && chosen < shown.length;
			all.disabled = shown.length === 0;
		}
		selection.onChange(sync);

		async function load() {
			try {
				rows = (await api(`/notifications?show=${show}`)).items;
				paint();
			} catch (error) {
				body.replaceChildren(h('p', { class: 'error-line' }, error.message));
			}
		}
		async function patch(note, changes) {
			try {
				await api(`/notifications/${note.id}`, { method: 'PATCH', body: changes });
				load();
			} catch (error) {
				toast(error.message, 'bad');
			}
		}
		async function remove(note) {
			if (!(await confirmBox({ title: 'Padam notifikasi ini?', body: `“${note.title}” akan dibuang.`, ok: 'Padam', danger: true }))) return;
			try {
				await api(`/notifications/${note.id}`, { method: 'DELETE' });
				toast('Dipadam.');
				load();
			} catch (error) {
				toast(error.message, 'bad');
			}
		}

		this.onSearch = (value) => {
			if (value === text) return;
			text = value;
			selection.clear();
			paint();
		};
		const stops = ['notification', 'notification-removed', 'notifications-changed'].map((type) => ctx.on(type, load));
		await load();
		return () => {
			stops.forEach((stop) => stop());
			delete this.onSearch;
		};
	}
};
