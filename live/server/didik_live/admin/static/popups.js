// The details popups: a parent, a quiz, a room. One popup is a header (who or what, its state), a row of figures, sections,
// and the actions. A parent leads to their quizzes and a quiz to its parent, with a way back; both swap inside the one open
// dialog (see openDialog). On a phone the popup is a sheet from the bottom of the screen (admin.css).

import { api } from './core.js';
import { ago, avatar, clock, confirmBox, date, duration, empty, h, icon, num, openDialog, pill, seg, stamp, tile, toast } from './ui.js';

const TYPES = { single: 'Pilihan tunggal', multiple: 'Pilih semua betul', truefalse: 'Betul/Salah', text: 'Taip jawapan', number: 'Nombor', order: 'Susun turutan', match: 'Padankan', blank: 'Isi tempat kosong' };
const PHASES = { lobby: ['Menunggu', 'info'], playing: ['Bermain', 'ok'], ended: ['Tamat', 'warn'] };

/** A time under a figure that does not repeat the date above it: "3 hari lalu" while it is recent, else the hour. */
const since = (iso) => (Date.now() - new Date(iso).getTime() < 7 * 86400_000 ? ago(iso) : `jam ${clock(iso)}`);

const figure = ([label, value, hint]) => h('div', { class: 'pop-stat' }, h('span', { class: 'k' }, label), h('b', null, value), hint && h('small', null, hint));
const section = (title, ...content) => h('section', { class: 'pop-section' }, h('h3', { class: 'pop-h' }, title), content);

/** The frame every popup shares. */
function frame({ close, back, lead, title, sub, pills = [], figures = [], body = [], foot = [] }) {
	return h('div', { class: 'pop', role: 'group', 'aria-labelledby': 'pop-title' },
		h('header', { class: 'pop-hero' },
			back && h('button', { class: 'pop-back', type: 'button', onClick: back.run }, icon('back', 14), back.label),
			h('div', { class: 'pop-id' }, lead, h('div', { class: 'pop-title' }, h('h2', { id: 'pop-title' }, title), sub && h('p', null, sub), pills.length > 0 && h('div', { class: 'pop-pills' }, pills))),
			h('button', { class: 'pop-x', type: 'button', 'aria-label': 'Tutup', onClick: () => close() }, icon('x', 18))
		),
		figures.length > 0 && h('div', { class: 'pop-stats' }, figures.map((item) => (item.nodeType ? item : figure(item)))),
		h('div', { class: 'pop-body' }, body),
		foot.length > 0 && h('footer', { class: 'pop-foot' }, foot)
	);
}

/** Opens another record inside the open popup, with a way back to where we came from. */
async function show(ctx, kind, id, back) {
	try {
		const data = await api(kind === 'user' ? `/users/${id}` : `/quizzes/${id}`);
		ctx.swap((close, swap) => (kind === 'user' ? viewUser : viewQuiz)(data, { ...ctx, close, swap, back }));
	} catch (error) {
		toast(error.message, 'bad');
	}
}

// ---------------------------------------------------------------- a parent

function viewUser(user, ctx) {
	const { close, onChange } = ctx;
	const here = () => ({ label: user.name, run: () => show(ctx, 'user', user.id, ctx.back) });
	const error = h('p', { class: 'error-line', role: 'alert', hidden: true });
	const fail = (problem) => {
		error.hidden = false;
		error.textContent = problem.message;
	};
	const done = async (work, message) => {
		try {
			await work();
			toast(message);
			onChange();
			close(true);
		} catch (problem) {
			fail(problem);
		}
	};

	const name = h('input', { class: 'input', id: 'user-name', maxlength: 80, value: user.name, disabled: user.system, 'aria-label': 'Nama paparan' });
	const save = h('button', { class: 'btn', type: 'submit', disabled: true }, 'Simpan');
	name.addEventListener('input', () => {
		error.hidden = true;
		save.disabled = !name.value.trim() || name.value.trim() === user.name;
	});
	const rename = h('form', { class: 'pop-inline', onSubmit: async (event) => {
		event.preventDefault();
		try {
			await api(`/users/${user.id}`, { method: 'PATCH', body: { name: name.value.trim() } });
			toast('Nama dikemas kini.');
			onChange();
			show(ctx, 'user', user.id, ctx.back); // stays open, now showing the new name
		} catch (problem) {
			fail(problem);
		}
	} }, name, save);

	const quizzes = user.quizList.length
		? h('ul', { class: 'pop-list' }, user.quizList.slice(0, 12).map((quiz) =>
			h('li', null, h('button', { type: 'button', class: 'pop-row', onClick: () => show(ctx, 'quiz', quiz.id, here()) },
				tile('book', 'blue'),
				h('span', { class: 'grow' }, h('b', null, quiz.title), h('small', null, `${num(quiz.questions)} soalan · dikemas kini ${ago(quiz.updatedAt)}`)),
				icon('chevron', 16)
			))
		))
		: empty('book', 'Belum menulis kuiz.');

	const status = user.disabled ? pill('Digantung', 'bad') : user.system ? pill('Akaun sistem', 'info') : pill('Aktif', 'ok');
	return frame({
		close,
		back: ctx.back,
		lead: avatar(user.name, 56),
		title: user.name,
		sub: user.email,
		pills: [status],
		figures: [
			['Kuiz', num(user.quizList.length)],
			['Gambar', num(user.pictures)],
			['Mendaftar', date(user.createdAt), since(user.createdAt)],
			['Log masuk', user.lastLoginAt ? ago(user.lastLoginAt) : 'Belum pernah', user.lastLoginAt ? stamp(user.lastLoginAt) : 'akaun ini belum masuk']
		],
		body: [
			section(user.quizList.length > 12 ? `Kuiz (12 daripada ${num(user.quizList.length)})` : 'Kuiz', quizzes),
			!user.system && section('Nama paparan', rename),
			error
		],
		foot: user.system
			? [h('span', { class: 'sub push' }, 'Akaun sistem tidak boleh diubah.'), h('button', { class: 'btn', type: 'button', onClick: () => close() }, 'Selesai')]
			: [
				h('button', { class: 'btn danger push', type: 'button', onClick: async () => {
					if (await confirmBox({ title: `Padam ${user.name}?`, body: 'Akaun, semua kuiz dan gambarnya dipadam, dan bilik terbukanya ditutup. Ini tidak boleh dibatalkan.', ok: 'Padam akaun', danger: true })) {
						done(() => api(`/users/${user.id}`, { method: 'DELETE' }), 'Akaun dipadam.');
					}
				} }, icon('trash', 16), 'Padam'),
				h('button', { class: 'btn', type: 'button', onClick: async () => {
					if (!user.disabled && !(await confirmBox({ title: `Gantung ${user.name}?`, body: 'Ibu bapa ini tidak boleh log masuk dan bilik yang dibukanya ditutup. Anda boleh memulihkannya bila-bila masa.', ok: 'Gantung', danger: true }))) return;
					done(() => api(`/users/${user.id}`, { method: 'PATCH', body: { disabled: !user.disabled } }), user.disabled ? 'Akaun dipulihkan.' : 'Akaun digantung.');
				} }, icon(user.disabled ? 'check' : 'ban', 16), user.disabled ? 'Pulihkan' : 'Gantung'),
				h('button', { class: 'btn primary', type: 'button', onClick: () => close() }, 'Selesai')
			]
	});
}

// ---------------------------------------------------------------- a quiz

function viewQuiz(quiz, ctx) {
	const { close, onChange } = ctx;
	const here = () => ({ label: quiz.title, run: () => show(ctx, 'quiz', quiz.id, ctx.back) });
	const panel = h('div');

	const title = h('input', { class: 'input', id: 'quiz-title', maxlength: 120, value: quiz.title });
	const about = h('textarea', { class: 'input', id: 'quiz-about', maxlength: 500, rows: 3 }, quiz.description);
	const error = h('p', { class: 'error-line', role: 'alert', hidden: true });
	const edit = h('form', { class: 'stack', onSubmit: async (event) => {
		event.preventDefault();
		try {
			await api(`/quizzes/${quiz.id}`, { method: 'PATCH', body: { title: title.value.trim(), description: about.value.trim() } });
			toast('Kuiz dikemas kini.');
			onChange();
			show(ctx, 'quiz', quiz.id, ctx.back);
		} catch (problem) {
			error.hidden = false;
			error.textContent = problem.message;
		}
	} },
		h('label', { class: 'field' }, h('span', null, 'Tajuk'), title),
		h('label', { class: 'field' }, h('span', null, 'Penerangan'), about),
		error,
		h('div', null, h('button', { class: 'btn primary', type: 'submit' }, 'Simpan perubahan'))
	);

	const questions = h('div', { class: 'stack' },
		h('div', { class: 'pop-tags' }, Object.entries(quiz.types).map(([type, count]) => h('span', { class: 'tag' }, `${TYPES[type] || type} · ${count}`))),
		quiz.description && h('p', { class: 'pop-about' }, quiz.description),
		quiz.prompts.length
			? h('ol', { class: 'prompts' }, quiz.prompts.map((p) => h('li', null, p || '(tanpa teks)')))
			: empty('book', 'Kuiz ini belum ada soalan.'),
		quiz.questions > quiz.prompts.length && h('p', { class: 'sub' }, `Menunjukkan ${quiz.prompts.length} daripada ${num(quiz.questions)} soalan.`)
	);
	const tabs = seg([['soalan', 'Soalan'], ['sunting', 'Sunting']], 'soalan', (value) => panel.replaceChildren(value === 'soalan' ? questions : edit));
	panel.append(questions);

	const owner = h('button', { class: 'link-inline', type: 'button', onClick: () => show(ctx, 'user', quiz.ownerId, here()) }, quiz.owner);
	return frame({
		close,
		back: ctx.back,
		lead: h('span', { class: 'pop-badge' }, icon('book', 26)),
		title: quiz.title,
		sub: h('span', null, 'oleh ', owner),
		pills: [quiz.sample ? pill('Kuiz contoh', 'info') : pill('Kuiz ibu bapa')],
		figures: [
			['Soalan', num(quiz.questions)],
			['Jenis soalan', num(Object.keys(quiz.types).length)],
			['Dicipta', date(quiz.createdAt), since(quiz.createdAt)],
			['Dikemas kini', ago(quiz.updatedAt), stamp(quiz.updatedAt)]
		],
		body: [tabs, panel],
		foot: [
			h('button', { class: 'btn danger push', type: 'button', onClick: async () => {
				if (!(await confirmBox({ title: `Padam “${quiz.title}”?`, body: `Kuiz milik ${quiz.owner} ini dipadam untuk selama-lamanya.`, ok: 'Padam kuiz', danger: true }))) return;
				try {
					await api(`/quizzes/${quiz.id}`, { method: 'DELETE' });
					toast('Kuiz dipadam.');
					onChange();
					close(true);
				} catch (problem) {
					toast(problem.message, 'bad');
				}
			} }, icon('trash', 16), 'Padam'),
			h('button', { class: 'btn primary', type: 'button', onClick: () => close() }, 'Selesai')
		]
	});
}

// ---------------------------------------------------------------- a room

function viewRoom(first, ctx) {
	const { close, on } = ctx;
	const code = first.code;
	const refs = { phase: h('span'), online: h('b'), kids: h('small'), age: h('b'), people: h('ul', { class: 'who-list' }) };
	const stop = h('button', { class: 'btn danger push', type: 'button', onClick: async () => {
		if (!(await confirmBox({ title: `Tutup bilik ${code}?`, body: 'Semua murid dalam bilik ini diputuskan dan permainan berhenti.', ok: 'Tutup bilik', danger: true }))) return;
		try {
			await api(`/rooms/${encodeURIComponent(code)}/close`, { method: 'POST' });
			toast(`Bilik ${code} ditutup.`);
			close(true);
		} catch (problem) {
			toast(problem.message, 'bad');
		}
	} }, icon('x', 16), 'Tutup bilik');

	const paint = (room) => {
		const [label, kind] = PHASES[room.phase] || PHASES.lobby;
		refs.phase.replaceChildren(pill(room.locked ? `${label} · dikunci` : label, kind));
		refs.online.textContent = `${room.online}/${room.players}`;
		refs.kids.textContent = room.online === room.players ? 'semua dalam talian' : `${room.players - room.online} di luar talian`;
		refs.age.textContent = duration(room.age);
		refs.people.replaceChildren(...(room.people.length
			? room.people.map((p) => h('li', { class: p.online ? '' : 'off' }, h('i'), p.name, room.phase !== 'lobby' && h('span', { class: 'sub' }, num(p.score)), !p.approved && h('span', { class: 'sub' }, '(menunggu)')))
			: [h('li', null, 'Belum ada murid')]));
	};
	paint(first);

	const ended = () => {
		unsubscribe();
		refs.phase.replaceChildren(pill('Sudah tamat', 'warn'));
		refs.people.replaceChildren(h('li', null, 'Bilik ini sudah ditutup.'));
		stop.disabled = true;
	};
	const unsubscribe = on('live', async () => {
		try {
			paint(await api(`/rooms/${encodeURIComponent(code)}`));
		} catch {
			ended();
		}
	});

	const el = frame({
		close,
		lead: h('span', { class: 'pop-badge mint' }, icon('door', 26)),
		title: h('span', { class: 'code' }, `Bilik ${code}`),
		sub: `${first.modeTitle} · ${first.host}`,
		pills: [refs.phase],
		// these two hold live values, so they are built here and updated in place
		figures: [
			h('div', { class: 'pop-stat' }, h('span', { class: 'k' }, 'Murid dalam talian'), refs.online, refs.kids),
			h('div', { class: 'pop-stat' }, h('span', { class: 'k' }, 'Dibuka sejak'), refs.age, h('small', null, 'dikemas kini sendiri'))
		],
		body: [section('Kuiz', h('p', { class: 'pop-about' }, first.quiz)), section('Murid', refs.people)],
		foot: [stop, h('button', { class: 'btn primary', type: 'button', onClick: () => close() }, 'Selesai')]
	});
	el.cleanup = unsubscribe;
	return el;
}

// ---------------------------------------------------------------- entry points

/** Each opens the popup and resolves when it is closed. A failed load throws, for the caller to say so. */
export async function userPopup(id, { onChange = () => {} } = {}) {
	const user = await api(`/users/${id}`);
	return openDialog((close, swap) => viewUser(user, { close, swap, onChange }), { variant: 'popup' });
}

export async function quizPopup(id, { onChange = () => {} } = {}) {
	const quiz = await api(`/quizzes/${id}`);
	return openDialog((close, swap) => viewQuiz(quiz, { close, swap, onChange }), { variant: 'popup' });
}

/** `on(type, fn)` is the page's listener (see core.js): the room's figures follow the live connection while it is open. */
export async function roomPopup(code, { on }) {
	const room = await api(`/rooms/${encodeURIComponent(code)}`);
	return openDialog((close, swap) => viewRoom(room, { close, swap, on }), { variant: 'popup' });
}
