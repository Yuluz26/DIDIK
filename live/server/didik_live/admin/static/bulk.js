// Acting on many rows at once: which rows are picked (`Selection`), the bar of actions that appears
// while any are (`bulkBar`), and the plain-words report of what happened (`report`).
//
// The server does the work in one transaction and says how many it did and how many it skipped (the demo
// account, rows already gone, rows already in the asked state); `report` turns that into one toast.

import { api } from './core.js';
import { confirmBox, h, icon, num, toast } from './ui.js';

export class Selection {
	constructor() {
		this.items = new Map(); // id -> a name to show in a confirmation
		this.listeners = new Set();
	}

	get size() {
		return this.items.size;
	}

	has(id) {
		return this.items.has(id);
	}

	ids() {
		return [...this.items.keys()];
	}

	names() {
		return [...this.items.values()].filter(Boolean);
	}

	toggle(id, on, name = '') {
		if (on) this.items.set(id, name);
		else this.items.delete(id);
		this.emit();
	}

	many(entries, on) {
		for (const [id, name] of entries) {
			if (on) this.items.set(id, name || this.items.get(id) || '');
			else this.items.delete(id);
		}
		this.emit();
	}

	/** Keeps only the ids still on screen (a row that vanished is no longer picked). */
	keep(ids) {
		const alive = new Set(ids);
		let changed = false;
		for (const id of this.items.keys()) {
			if (!alive.has(id)) {
				this.items.delete(id);
				changed = true;
			}
		}
		if (changed) this.emit();
	}

	clear() {
		if (!this.items.size) return;
		this.items.clear();
		this.emit();
	}

	onChange(fn) {
		this.listeners.add(fn);
		return () => this.listeners.delete(fn);
	}

	emit() {
		for (const fn of this.listeners) fn(this);
	}
}

/**
 * The bar that rises while rows are picked. `actions` is [{ label, icon, tone?, run(ids, names) }]; `run` returns
 * false to keep the selection (a cancelled confirmation). `matching(...)` offers "pick all N that match".
 */
export function bulkBar(selection, { actions }) {
	const count = h('b', null, '0');
	const hint = h('span', { class: 'bulk-hint' });
	const spoken = h('span', { class: 'visually-hidden', 'aria-live': 'polite' });
	let busy = false;
	let match = null;

	const buttons = actions.map((action) =>
		h('button', { class: `btn sm ${action.tone || ''}`, type: 'button', onClick: () => run(action) }, icon(action.icon, 15), action.label)
	);
	const clear = h('button', { class: 'link', type: 'button', onClick: () => selection.clear() }, 'Batal pilih');
	const el = h('div', { class: 'bulkbar', role: 'region', 'aria-label': 'Tindakan untuk baris yang dipilih', hidden: true }, h('span', { class: 'bulk-count' }, count, ' dipilih'), hint, h('span', { class: 'grow' }), buttons, clear, spoken);

	async function run(action) {
		if (busy) return;
		busy = true;
		buttons.forEach((button) => (button.disabled = true));
		try {
			if ((await action.run(selection.ids(), selection.names())) !== false) selection.clear();
		} catch (error) {
			toast(error.message, 'bad');
		} finally {
			busy = false;
			buttons.forEach((button) => (button.disabled = false));
		}
	}

	function paint() {
		el.hidden = selection.size === 0;
		actions.forEach((action, index) => (buttons[index].hidden = action.show ? !action.show() : false));
		count.textContent = num(selection.size);
		spoken.textContent = selection.size ? `${selection.size} dipilih` : '';
		hint.replaceChildren();
		if (!match || !selection.size) return;
		if (selection.size >= match.total) {
			hint.append(`Semua ${num(match.total)} yang sepadan dipilih`);
		} else if (match.pageIds.length && match.pageIds.every((id) => selection.has(id))) {
			hint.append(
				h('button', { class: 'link', type: 'button', onClick: async () => {
					try {
						const found = await match.fetchAll();
						selection.many(found.ids.map((id) => [id, '']), true);
						if (found.capped) toast(`Hanya ${num(found.ids.length)} yang pertama dipilih (had sekali jalan).`);
					} catch (error) {
						toast(error.message, 'bad');
					}
				} }, `Pilih semua ${num(match.total)} yang sepadan`)
			);
		}
	}
	selection.onChange(paint);

	return {
		el,
		/** Tells the bar what the list holds: `total` rows match, `pageIds` are on screen, `fetchAll()` returns { ids, capped }. */
		matching(info) {
			match = info;
			paint();
		}
	};
}

/** POSTs a bulk action and reports it: "3 ibu bapa dipadam. 2 dilangkau." */
export async function bulk(path, body, { noun, did }) {
	const result = await api(path, { method: 'POST', body });
	const skipped = result.skipped ? ` ${num(result.skipped)} dilangkau (akaun sistem, sudah dipadam, atau sudah dalam keadaan itu).` : '';
	if (result.done) toast(`${num(result.done)} ${noun} ${did}.${skipped}`);
	else toast(`Tiada ${noun} yang berubah.${skipped}`, 'bad');
	return result;
}

/** The usual question before a bulk action: a typed word when more than one row could be lost. */
export function askBulk({ ids, names, title, body, ok, word = 'PADAM', danger = true, typed = true }) {
	return confirmBox({ title, body, detail: names.slice(0, 5), more: Math.max(0, ids.length - Math.min(names.length, 5)), type: typed && ids.length > 1 && danger ? word : '', ok, danger });
}
