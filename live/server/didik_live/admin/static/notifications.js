// Notifications: what the site tells the owner (a new parent, a sign-in from a new address) and the owner's own notes.
// Create, read, pin, edit, delete.

import { api } from './core.js';
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
		const list = h('ul', { class: 'list note-list' });
		const body = h('div', { class: 'card' }, skeletons(3));
		const readAll = h('button', { class: 'btn sm', type: 'button', onClick: async () => { await api('/notifications/read-all', { method: 'POST' }); toast('Semua ditandakan sudah dibaca.'); load(); } }, icon('check', 15), 'Tandakan semua dibaca');
		const clearRead = h('button', { class: 'btn sm', type: 'button', onClick: async () => {
			if (!(await confirmBox({ title: 'Kosongkan yang sudah dibaca?', body: 'Notifikasi yang sudah dibaca akan dibuang. Yang disematkan kekal.', ok: 'Kosongkan', danger: true }))) return;
			await api('/notifications', { method: 'DELETE' });
			toast('Dikosongkan.');
			load();
		} }, icon('trash', 15), 'Kosongkan yang dibaca');
		root.append(h('div', { class: 'toolbar' }, seg([['all', 'Semua'], ['unread', 'Belum dibaca'], ['pinned', 'Disematkan'], ['manual', 'Nota saya']], show, (value) => { show = value; load(); }), h('span', { class: 'grow' }), readAll, clearRead), body);

		const card = (note) => {
			const [label, iconName, tone] = LEVELS[note.level] || LEVELS.info;
			return h('li', { class: note.read ? '' : 'unread', data: { id: note.id } },
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
			const shown = query ? rows.filter((n) => `${n.title} ${n.body}`.toLowerCase().includes(query)) : rows;
			clear(list);
			shown.forEach((note) => list.append(card(note)));
			body.replaceChildren(shown.length ? list : empty('inbox', query ? 'Tiada notifikasi yang sepadan.' : show === 'unread' ? 'Semua sudah dibaca.' : 'Belum ada notifikasi.'));
		};

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
			text = value;
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
