// The quiz editor's data: the same shape the server stores (see didik_live/questions.py), with ids
// made here so every list can be keyed while it is edited. Ids match the server's pattern.

import { countPrompt } from '$lib/stickers';

export type QuestionType =
	| 'single'
	| 'multiple'
	| 'truefalse'
	| 'text'
	| 'number'
	| 'order'
	| 'match'
	| 'blank'
	| 'count'
	| 'spell'
	| 'sort'
	| 'missing'
	| 'puzzle'
	| 'blocks'
	| 'clock'
	| 'money';

export interface Choice {
	id: string;
	text: string;
	correct: boolean;
	sticker?: string | null;
}

export interface Item {
	id: string;
	text: string;
}

export interface Pair {
	id: string;
	left: string;
	right: string;
	sticker?: string | null;
}

export interface SortGroup {
	id: string;
	name: string;
	sticker: string | null;
}

export interface SortItem {
	id: string;
	text: string;
	sticker: string | null;
	group: string;
}

interface Base {
	id: string;
	prompt: string;
	image: string | null;
	/** A 3D sticker that illustrates the question (the "gambar rajah"). */
	picture: string | null;
	/** Why the answer is right, shown to a child who got it wrong. */
	explain: string;
	time_limit: number;
}

export type Question = Base &
	(
		| { type: 'single'; choices: Choice[] }
		| { type: 'multiple'; choices: Choice[]; partial: boolean }
		| { type: 'truefalse'; answer: boolean }
		| { type: 'text'; answers: string[]; forgive_typo: boolean }
		| { type: 'number'; answer: number | null; tolerance: number; unit: string }
		| { type: 'order'; items: Item[] }
		| { type: 'match'; pairs: Pair[] }
		| { type: 'blank'; sentence: string; distractors: string[]; word_bank: boolean }
		| { type: 'count'; sticker: string; place: string; answer: number }
		| { type: 'spell'; word: string; sticker: string | null; decoys: number }
		| { type: 'sort'; groups: SortGroup[]; items: SortItem[] }
		| { type: 'missing'; word: string; hide: number[]; sticker: string | null; decoys: number }
		| { type: 'puzzle'; sticker: string | null; grid: 2 | 3 }
		| { type: 'blocks'; answer: number }
		| { type: 'clock'; hour: number; minute: number }
		| { type: 'money'; amount: number; sticker: string | null }
	);

export interface QuizDraft {
	title: string;
	description: string;
	questions: Question[];
}

/** "biasa": every game shows it as a card of options or a box. "interaktif": the child touches, drags and
 * sorts things; made for Kuiz Interaktif, and playable in the other games too. */
export type TypeKind = 'biasa' | 'interaktif';

export const TYPES: { type: QuestionType; name: string; hint: string; kind: TypeKind }[] = [
	{ type: 'single', name: 'Pilihan tunggal', hint: 'Satu jawapan betul daripada 2 hingga 6 pilihan.', kind: 'biasa' },
	{ type: 'multiple', name: 'Pilih semua', hint: 'Lebih daripada satu jawapan boleh betul.', kind: 'biasa' },
	{ type: 'truefalse', name: 'Betul atau salah', hint: 'Satu kenyataan, kanak-kanak pilih betul atau salah.', kind: 'biasa' },
	{ type: 'text', name: 'Taip jawapan', hint: 'Kanak-kanak menaip perkataan. Ejaan hampir sama boleh diterima.', kind: 'biasa' },
	{ type: 'number', name: 'Nombor', hint: 'Jawapan berupa nombor, dengan julat jika perlu.', kind: 'biasa' },
	{ type: 'order', name: 'Susun turutan', hint: 'Tulis dalam turutan betul; kanak-kanak melihatnya bercampur.', kind: 'biasa' },
	{ type: 'match', name: 'Padankan', hint: 'Pasangan kiri dan kanan untuk dipadankan.', kind: 'biasa' },
	{ type: 'blank', name: 'Isi tempat kosong', hint: 'Ayat dengan perkataan dalam [kurungan] sebagai tempat kosong.', kind: 'biasa' },
	{ type: 'count', name: 'Kira dan masukkan', hint: 'Kanak-kanak seret objek ke dalam bakul, kotak atau bas sehingga cukup bilangannya.', kind: 'interaktif' },
	{ type: 'spell', name: 'Susun huruf', hint: 'Huruf bercampur, dengan gambar petunjuk, disusun menjadi perkataan.', kind: 'interaktif' },
	{ type: 'sort', name: 'Isih kumpulan', hint: 'Seret setiap benda ke bakul kumpulannya: darat atau laut, buah atau sayur.', kind: 'interaktif' },
	{ type: 'missing', name: 'Huruf hilang', hint: 'Satu hingga tiga huruf disembunyikan; kanak-kanak isi dengan jubin huruf.', kind: 'interaktif' },
	{ type: 'puzzle', name: 'Cantum gambar', hint: 'Gambar dipotong 4 atau 9 keping untuk dicantum semula.', kind: 'interaktif' },
	{ type: 'blocks', name: 'Bina nombor', hint: 'Bina nombor dengan blok ratus, puluh dan sa (nilai tempat).', kind: 'interaktif' },
	{ type: 'clock', name: 'Laraskan jam', hint: 'Pusing jarum jam sehingga menunjukkan masa yang diminta.', kind: 'interaktif' },
	{ type: 'money', name: 'Bayar dengan wang', hint: 'Bayar harga dengan syiling dan wang kertas Malaysia.', kind: 'interaktif' }
];

export const KINDS: { kind: TypeKind; name: string; note: string }[] = [
	{ kind: 'interaktif', name: 'Interaktif', note: 'Sentuh dan seret. Paling seronok dengan Kuiz Interaktif.' },
	{ kind: 'biasa', name: 'Biasa', note: 'Pilih, taip atau padankan.' }
];

export const TYPE_NAME = Object.fromEntries(TYPES.map((t) => [t.type, t.name])) as Record<QuestionType, string>;

export const TIME_LIMITS = [10, 15, 20, 30, 45, 60, 90, 120];

export const LIMITS = { questions: 60, choices: 6, answers: 8, items: 6, pairs: 5, distractors: 6, groups: 3, things: 8, count: 20, decoys: 4 };

export function newId(): string {
	const bytes = crypto.getRandomValues(new Uint8Array(6));
	return Array.from(bytes, (b) => 'abcdefghijklmnopqrstuvwxyz0123456789'[b % 36]).join('');
}

const choice = (correct = false): Choice => ({ id: newId(), text: '', correct });
const item = (): Item => ({ id: newId(), text: '' });
const pair = (): Pair => ({ id: newId(), left: '', right: '' });
const group = (): SortGroup => ({ id: newId(), name: '', sticker: null });
const thing = (groupId: string): SortItem => ({ id: newId(), text: '', sticker: null, group: groupId });

/** A fresh question of a type; `from` keeps the prompt, picture and time of the question it replaces. */
export function blank(type: QuestionType, from?: Question): Question {
	const base: Base = {
		id: from?.id ?? newId(),
		prompt: from?.prompt ?? '',
		image: from?.image ?? null,
		picture: from?.picture ?? null,
		explain: from?.explain ?? '',
		time_limit: from?.time_limit ?? 20
	};
	const keptChoices = from && (from.type === 'single' || from.type === 'multiple') ? from.choices : null;
	switch (type) {
		case 'single': {
			const choices = keptChoices ? keptChoices.map((c) => ({ ...c })) : [choice(true), choice(), choice()];
			const first = Math.max(0, choices.findIndex((c) => c.correct));
			choices.forEach((c, i) => (c.correct = i === first));
			return { ...base, type, choices };
		}
		case 'multiple': {
			const choices = keptChoices ? keptChoices.map((c) => ({ ...c })) : [choice(true), choice(true), choice(), choice()];
			while (choices.length < 3) choices.push(choice());
			return { ...base, type, choices, partial: true };
		}
		case 'truefalse':
			return { ...base, type, answer: true };
		case 'text':
			return { ...base, type, answers: [''], forgive_typo: true };
		case 'number':
			return { ...base, type, answer: null, tolerance: 0, unit: '' };
		case 'order':
			return { ...base, type, items: [item(), item(), item()] };
		case 'match':
			return { ...base, type, pairs: [pair(), pair(), pair()] };
		case 'blank':
			return { ...base, type, sentence: '', distractors: [], word_bank: true };
		case 'count':
			return { ...base, prompt: base.prompt || countPrompt('epal', 'bakul', 5), time_limit: Math.max(base.time_limit, 45), type, sticker: 'epal', place: 'bakul', answer: 5 };
		case 'spell':
			return { ...base, prompt: base.prompt || 'Susun huruf untuk mengeja perkataan ini.', time_limit: Math.max(base.time_limit, 45), type, word: '', sticker: null, decoys: 0 };
		case 'sort': {
			const groups = [group(), group()];
			const items = [thing(groups[0].id), thing(groups[1].id), thing(groups[0].id), thing(groups[1].id)];
			return { ...base, time_limit: Math.max(base.time_limit, 60), type, groups, items };
		}
		case 'missing':
			return { ...base, prompt: base.prompt || 'Lengkapkan huruf yang hilang.', time_limit: Math.max(base.time_limit, 45), type, word: '', hide: [], sticker: null, decoys: 2 };
		case 'puzzle':
			return { ...base, prompt: base.prompt || 'Cantumkan kepingan gambar ini.', time_limit: Math.max(base.time_limit, 60), type, sticker: 'kucing', grid: 2 };
		case 'blocks':
			return { ...base, prompt: base.prompt || 'Bina nombor 24 dengan blok puluh dan sa.', time_limit: Math.max(base.time_limit, 60), type, answer: 24 };
		case 'clock':
			return { ...base, prompt: base.prompt || 'Laraskan jam kepada pukul 3.00.', time_limit: Math.max(base.time_limit, 45), type, hour: 3, minute: 0 };
		case 'money':
			return { ...base, prompt: base.prompt || 'Aiskrim ini berharga RM2.50. Bayar dengan tepat.', time_limit: Math.max(base.time_limit, 60), type, amount: 250, sticker: 'aiskrim' };
	}
}

export const make = { choice, item, pair, group, thing };

/** A deep copy with new ids, for "Salin soalan". */
export function duplicate(question: Question): Question {
	const copy = JSON.parse(JSON.stringify(question)) as Question;
	copy.id = newId();
	if ('choices' in copy) copy.choices.forEach((c) => (c.id = newId()));
	if ('items' in copy) copy.items.forEach((i) => (i.id = newId()));
	if ('pairs' in copy) copy.pairs.forEach((p) => (p.id = newId()));
	if (copy.type === 'sort') {
		const renamed = new Map(copy.groups.map((g) => [g.id, newId()]));
		copy.groups.forEach((g) => (g.id = renamed.get(g.id)!));
		copy.items.forEach((i) => (i.group = renamed.get(i.group) ?? copy.groups[0].id));
	}
	return copy;
}

/** Fills in what older or hand-written questions may lack, so every field has an editor. */
export function normalise(raw: Record<string, unknown>): Question {
	const type = raw.type as QuestionType;
	const fresh = blank(type);
	const question = { ...fresh, ...raw } as Question;
	question.picture = question.picture ?? null;
	question.explain = question.explain ?? '';
	if ('choices' in question) question.choices = question.choices.map((c) => ({ ...c, id: c.id || newId() }));
	if ('items' in question) question.items = question.items.map((i) => ({ ...i, id: i.id || newId() }));
	if ('pairs' in question) question.pairs = question.pairs.map((p) => ({ ...p, id: p.id || newId() }));
	if (question.type === 'sort') {
		question.groups = question.groups.map((g) => ({ ...g, sticker: g.sticker ?? null, id: g.id || newId() }));
		question.items = question.items.map((i) => ({ ...i, sticker: i.sticker ?? null }));
	}
	if (question.type === 'spell') question.sticker = question.sticker ?? null;
	return question;
}

/** The parts of a blank sentence: text, and the answers of each [blank]. */
export function sentenceParts(sentence: string): ({ text: string } | { answers: string[] })[] {
	const parts: ({ text: string } | { answers: string[] })[] = [];
	let last = 0;
	for (const match of sentence.matchAll(/\[([^[\]]{1,40})\]/g)) {
		if (match.index > last) parts.push({ text: sentence.slice(last, match.index) });
		parts.push({ answers: match[1].split('/').map((a) => a.trim()).filter(Boolean) });
		last = match.index + match[0].length;
	}
	if (last < sentence.length) parts.push({ text: sentence.slice(last) });
	return parts;
}
