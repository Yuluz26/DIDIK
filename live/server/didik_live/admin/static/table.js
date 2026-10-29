// A table with a pager and, when given a `selection`, a checkbox column: pick rows one by one, a whole page, or a range
// with shift-click. On a phone each row becomes a card (see admin.css): `data-label` names each cell there, and the
// page's "pick all" moves out of the (hidden) header into a row of its own.

import { h, icon, num } from './ui.js';

export function dataTable({ columns, render, emptyText, onPage, selection, rowId, rowName, selectable = () => true }) {
	const body = h('tbody');
	const info = h('span');
	const prev = h('button', { class: 'btn sm', type: 'button', onClick: () => onPage(-1) }, icon('up', 14), 'Sebelum');
	const next = h('button', { class: 'btn sm', type: 'button', onClick: () => onPage(1) }, 'Seterusnya', icon('down', 14));
	prev.firstChild.style.transform = 'rotate(-90deg)';
	next.lastChild.style.transform = 'rotate(-90deg)';
	const message = h('p', { class: 'empty' });
	message.hidden = true;

	let items = [];
	let last = -1;
	const pickable = () => items.filter(selectable);
	const entries = () => pickable().map((item) => [rowId(item), rowName?.(item) || '']);
	const everyPick = () => h('input', { type: 'checkbox', class: 'pick', 'aria-label': 'Pilih semua pada halaman ini', onChange: (event) => selection.many(entries(), event.target.checked) });
	const master = selection && everyPick();
	const phoneAll = selection && everyPick();

	const head = h('tr', null, selection && h('th', { class: 'pick-col', scope: 'col' }, master), columns.map((c) => h('th', { scope: 'col' }, c)));
	const el = h('section', { class: 'card table-card' },
		selection && h('label', { class: 'pick-all check' }, phoneAll, 'Pilih semua pada halaman ini'),
		h('table', { class: 'tbl' }, h('thead', null, head), body),
		message,
		h('div', { class: 'pager' }, info, h('div', null, prev, next))
	);

	function row(item, index) {
		const tr = render(item);
		if (!selection) return tr;
		const id = rowId(item);
		const box = h('input', { type: 'checkbox', class: 'pick', 'aria-label': `Pilih ${rowName?.(item) || id}`, disabled: !selectable(item) });
		box.addEventListener('click', (event) => {
			const from = event.shiftKey && last >= 0 ? Math.min(last, index) : index;
			const to = event.shiftKey && last >= 0 ? Math.max(last, index) : index;
			selection.many(items.slice(from, to + 1).filter(selectable).map((i) => [rowId(i), rowName?.(i) || '']), box.checked);
			last = index;
		});
		tr.prepend(h('td', { class: 'pick', 'data-label': 'Pilih' }, box));
		tr.dataset.id = id;
		return tr;
	}

	/** Brings the checkboxes in line with the selection. */
	function sync() {
		if (!selection) return;
		const ids = pickable().map(rowId);
		const chosen = ids.filter((id) => selection.has(id));
		for (const tr of body.rows) {
			const on = selection.has(Number.isNaN(Number(tr.dataset.id)) ? tr.dataset.id : Number(tr.dataset.id));
			const box = tr.querySelector('input.pick');
			if (box) box.checked = on;
			tr.classList.toggle('selected', on);
		}
		for (const box of [master, phoneAll]) {
			box.checked = ids.length > 0 && chosen.length === ids.length;
			box.indeterminate = chosen.length > 0 && chosen.length < ids.length;
			box.disabled = ids.length === 0;
		}
	}
	selection?.onChange(sync);

	return {
		el,
		busy(on) {
			el.setAttribute('aria-busy', String(on));
			el.style.opacity = on ? '0.6' : '';
		},
		sync,
		set({ items: next_, total, page, per }) {
			items = next_;
			last = -1;
			body.replaceChildren(...items.map(row));
			message.hidden = items.length > 0;
			message.textContent = emptyText;
			const first = total ? (page - 1) * per + 1 : 0;
			info.textContent = total ? `${num(first)}–${num(first + items.length - 1)} daripada ${num(total)}` : '0 keputusan';
			prev.disabled = page <= 1;
			next.disabled = page * per >= total;
			el.querySelector('.pager').hidden = total <= per;
			sync();
		}
	};
}
