// A table with a pager. On a phone each row becomes a card (see admin.css): `data-label` names each cell there.

import { h, icon, num } from './ui.js';

export function dataTable({ columns, render, emptyText, onPage }) {
	const body = h('tbody');
	const info = h('span');
	const prev = h('button', { class: 'btn sm', type: 'button', onClick: () => onPage(-1) }, icon('up', 14), 'Sebelum');
	const next = h('button', { class: 'btn sm', type: 'button', onClick: () => onPage(1) }, 'Seterusnya', icon('down', 14));
	prev.firstChild.style.transform = 'rotate(-90deg)';
	next.lastChild.style.transform = 'rotate(-90deg)';
	const message = h('p', { class: 'empty' });
	const el = h('section', { class: 'card table-card' },
		h('table', { class: 'tbl' }, h('thead', null, h('tr', null, columns.map((c) => h('th', { scope: 'col' }, c)))), body),
		message,
		h('div', { class: 'pager' }, info, h('div', null, prev, next))
	);
	message.hidden = true;

	return {
		el,
		busy(on) {
			el.setAttribute('aria-busy', String(on));
			el.style.opacity = on ? '0.6' : '';
		},
		set({ items, total, page, per }) {
			body.replaceChildren(...items.map(render));
			message.hidden = items.length > 0;
			message.textContent = emptyText;
			const first = total ? (page - 1) * per + 1 : 0;
			info.textContent = total ? `${num(first)}–${num(first + items.length - 1)} daripada ${num(total)}` : '0 keputusan';
			prev.disabled = page <= 1;
			next.disabled = page * per >= total;
			el.querySelector('.pager').hidden = total <= per;
		}
	};
}
