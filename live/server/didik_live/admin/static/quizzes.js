// Kuiz: every quiz parents wrote. Look at the questions, fix a title, or remove one.

import { api, query } from './core.js';
import { dataTable } from './table.js';
import { ago, confirmBox, h, icon, num, openDialog, pill, seg, sheetHead, stamp, toast } from './ui.js';

const TYPES = { single: 'Pilihan tunggal', multiple: 'Pilih semua betul', truefalse: 'Betul/Salah', text: 'Taip jawapan', number: 'Nombor', order: 'Susun turutan', match: 'Padankan', blank: 'Isi tempat kosong' };

function drawer(id, onChange) {
	return api(`/quizzes/${id}`).then((quiz) =>
		openDialog((close) => {
			const title = h('input', { class: 'input', id: 'quiz-title', maxlength: 120, value: quiz.title });
			const about = h('textarea', { class: 'input', id: 'quiz-about', maxlength: 500, rows: 3 }, quiz.description);
			const error = h('p', { class: 'error-line', role: 'alert', hidden: true });
			const done = (message) => {
				toast(message);
				onChange();
				close(true);
			};
			const save = async (event) => {
				event.preventDefault();
				try {
					await api(`/quizzes/${id}`, { method: 'PATCH', body: { title: title.value.trim(), description: about.value.trim() } });
					done('Kuiz dikemas kini.');
				} catch (problem) {
					error.hidden = false;
					error.textContent = problem.message;
				}
			};
			return h('div', { class: 'sheet' },
				sheetHead(quiz.title, close, `oleh ${quiz.owner} · ${num(quiz.questions)} soalan`),
				h('dl', { class: 'kv' }, ...[['Dicipta', stamp(quiz.createdAt)], ['Dikemas kini', stamp(quiz.updatedAt)], ['Jenis', quiz.sample ? pill('Kuiz contoh', 'info') : pill('Kuiz ibu bapa', '')]].flatMap(([k, v]) => [h('dt', null, k), h('dd', null, v)])),
				h('div', { class: 'levels' }, Object.entries(quiz.types).map(([type, count]) => h('span', { class: 'tag' }, `${TYPES[type] || type} · ${count}`))),
				h('form', { class: 'stack', onSubmit: save },
					h('label', { class: 'field' }, h('span', null, 'Tajuk'), title),
					h('label', { class: 'field' }, h('span', null, 'Penerangan'), about),
					error,
					h('div', { class: 'sheet-foot' },
						h('button', { class: 'btn danger', type: 'button', onClick: async () => {
							if (await confirmBox({ title: `Padam “${quiz.title}”?`, body: `Kuiz milik ${quiz.owner} ini dipadam untuk selama-lamanya.`, ok: 'Padam kuiz', danger: true })) {
								try {
									await api(`/quizzes/${id}`, { method: 'DELETE' });
									done('Kuiz dipadam.');
								} catch (problem) {
									toast(problem.message, 'bad');
								}
							}
						} }, icon('trash', 16), 'Padam'),
						h('button', { class: 'btn primary', type: 'submit' }, 'Simpan')
					)
				),
				h('div', null, h('h3', { class: 'sub' }, `Soalan (${quiz.prompts.length}${quiz.questions > quiz.prompts.length ? ` daripada ${quiz.questions}` : ''})`), h('div', { class: 'gap' }),
					h('ol', { class: 'prompts' }, quiz.prompts.map((p) => h('li', null, p || '(tanpa teks)'))))
			);
		}, { drawer: true })
	);
}

export default {
	title: 'Kuiz',
	subtitle: 'Semua kuiz yang ditulis ibu bapa.',
	search: 'Cari tajuk kuiz atau nama ibu bapa…',

	async mount(root, ctx) {
		const state = { samples: false, q: ctx.params.get('q') || '', page: 1 };
		const table = dataTable({
			columns: ['Kuiz', 'Ibu bapa', 'Soalan', 'Dikemas kini', ''],
			emptyText: 'Tiada kuiz yang sepadan.',
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
		root.append(h('div', { class: 'toolbar' }, seg([['mine', 'Ibu bapa'], ['samples', 'Kuiz contoh']], 'mine', (value) => {
			state.samples = value === 'samples';
			state.page = 1;
			load();
		}), count), table.el);

		async function load() {
			table.busy(true);
			try {
				const result = await api(`/quizzes${query({ q: state.q, samples: state.samples, page: state.page })}`);
				table.set(result);
				count.textContent = `${num(result.total)} kuiz`;
			} catch (error) {
				toast(error.message, 'bad');
			} finally {
				table.busy(false);
			}
		}
		const open = (id) => drawer(id, load).catch((error) => toast(error.message, 'bad'));

		this.onSearch = (value) => {
			state.q = value;
			state.page = 1;
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
