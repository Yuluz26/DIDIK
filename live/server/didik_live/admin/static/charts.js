// The few charts the dashboard draws, as plain SVG and CSS. Each shows its numbers in text beside it too
// (the chart never carries a value alone), so none of them needs a colour to be read.

import { h, icon, num, empty } from './ui.js';

const SVG = 'http://www.w3.org/2000/svg';
const svg = (tag, attrs) => {
	const el = document.createElementNS(SVG, tag);
	for (const [key, value] of Object.entries(attrs || {})) el.setAttribute(key, value);
	return el;
};

export const COLOURS = ['#6a5cf5', '#4f8cff', '#34d3a0', '#fb923c', '#a78bfa', '#7f89b3'];

/** Bars for a series (a day each), the last one brightest. Long series are folded to 30 bars. */
export function spark(values, tone = '') {
	let data = values;
	if (data.length > 30) {
		const step = Math.ceil(data.length / 30);
		data = Array.from({ length: Math.ceil(data.length / step) }, (_, i) => data.slice(i * step, (i + 1) * step).reduce((a, b) => a + b, 0));
	}
	const w = 92;
	const hgt = 36;
	const gap = 2;
	const bar = (w - gap * (data.length - 1)) / data.length;
	const top = Math.max(...data, 1);
	const root = svg('svg', { viewBox: `0 0 ${w} ${hgt}`, width: w, height: hgt, class: `spark ${tone}`, 'aria-hidden': 'true' });
	data.forEach((value, i) => {
		const height = Math.max(2.5, (value / top) * hgt);
		root.append(svg('rect', { x: i * (bar + gap), y: hgt - height, width: bar, height, rx: Math.min(1.6, bar / 2), fill: 'currentColor', opacity: i === data.length - 1 ? 1 : 0.3 + (0.45 * i) / data.length }));
	});
	return root;
}

/** Rings for shares of a whole. `parts` is [{label, count}] ; the middle names the total. */
export function donut(parts, total, label) {
	const sum = parts.reduce((a, p) => a + p.count, 0);
	const ring = svg('svg', { viewBox: '0 0 36 36', 'aria-hidden': 'true' });
	ring.append(svg('circle', { cx: 18, cy: 18, r: 15.9155, fill: 'none', stroke: 'rgb(255 255 255 / 0.07)', 'stroke-width': 4 }));
	let offset = 0;
	parts.forEach((part, i) => {
		const share = (part.count / sum) * 100;
		const draw = parts.length > 1 ? Math.max(share - 1, 0.5) : share;
		ring.append(svg('circle', { cx: 18, cy: 18, r: 15.9155, fill: 'none', stroke: COLOURS[i % COLOURS.length], 'stroke-width': 4, 'stroke-dasharray': `${draw} ${100 - draw}`, 'stroke-dashoffset': -offset }));
		offset += share;
	});
	const middle = h('div', { class: 'donut-mid' }, h('b', null, num(total)), h('small', null, label));
	const key = h('ul', { class: 'key' }, parts.map((part, i) => {
		const item = h('li', null, h('i'), h('span', null, part.label), h('b', null, `${Math.round((part.count / sum) * 100)}%`));
		item.querySelector('i').style.setProperty('--c', COLOURS[i % COLOURS.length]);
		return item;
	}));
	return h('div', { class: 'donut-wrap' }, h('div', { class: 'donut' }, ring, middle), key);
}

/** Tiles sized by share, like the reference's distribution card. Up to four; the rest are folded into one. */
export function tiles(items, unit) {
	if (!items.length) return empty('flag', 'Belum ada bilik dibuka dalam tempoh ini.');
	let shown = items.slice(0, 4);
	if (items.length > 4) shown = [...items.slice(0, 3), { title: 'Lain-lain', count: items.slice(3).reduce((a, i) => a + i.count, 0) }];
	const sum = items.reduce((a, i) => a + i.count, 0);
	return h('div', { class: 'tree', data: { n: shown.length }, role: 'list' }, shown.map((item) =>
		h('div', { class: 'tile', role: 'listitem', title: `${item.title}: ${num(item.count)} ${unit}` },
			h('b', null, `${Math.round((item.count / sum) * 100)}%`),
			h('span', null, item.title),
			h('small', null, `${num(item.count)} ${unit}`)
		)
	));
}

const DAYS = ['Isnin', 'Selasa', 'Rabu', 'Khamis', 'Jumaat', 'Sabtu', 'Ahad'];

/** Weekday by hour, brighter for busier. The summary names the busiest slot for a screen reader. */
export function heatmap({ grid, max }) {
	const wrap = h('div');
	if (!max) return empty('pulse', 'Belum ada murid masuk dalam empat minggu ini.');
	let best = { v: 0, d: 0, hr: 0 };
	grid.forEach((row, d) => row.forEach((v, hr) => v > best.v && (best = { v, d, hr })));
	const root = h('div', { class: 'heat', role: 'img', 'aria-label': `Murid masuk mengikut hari dan jam, empat minggu terakhir. Paling sibuk: ${DAYS[best.d]} jam ${String(best.hr).padStart(2, '0')}:00, ${best.v} murid.` });
	root.append(h('span'));
	for (let hr = 0; hr < 24; hr += 4) root.append(h('span', { class: 'h', 'aria-hidden': 'true' }, String(hr).padStart(2, '0')));
	grid.forEach((row, d) => {
		root.append(h('span', { class: 'd', 'aria-hidden': 'true' }, DAYS[d].slice(0, 3)));
		row.forEach((v, hr) => {
			const cell = h('span', { class: 'cell', 'aria-hidden': 'true', title: `${DAYS[d]} ${String(hr).padStart(2, '0')}:00 · ${v} murid` });
			cell.style.setProperty('--a', v ? (0.2 + (0.8 * v) / max).toFixed(2) : '0.06');
			root.append(cell);
		});
	});
	const legend = h('div', { class: 'legend', 'aria-hidden': 'true' }, 'Kurang', [0.06, 0.28, 0.5, 0.75, 1].map((a) => {
		const box = h('i');
		box.style.setProperty('--a', a);
		return box;
	}), 'Lebih');
	wrap.append(root, legend);
	return wrap;
}

export { icon };
