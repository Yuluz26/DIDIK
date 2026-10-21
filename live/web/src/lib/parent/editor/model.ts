// The quiz editor's data: the same shape the server stores (see didik_live/questions.py), with ids
// made here so every list can be keyed while it is edited. Ids match the server's pattern.

export type QuestionType = 'single' | 'multiple' | 'truefalse' | 'text' | 'number' | 'order' | 'match' | 'blank';

export interface Choice {
	id: string;
	text: string;
	correct: boolean;
}

export interface Item {
	id: string;
	text: string;
}

export interface Pair {
	id: string;
	left: string;
	right: string;
}

interface Base {
	id: string;
	prompt: string;
	image: string | null;
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
	);

export interface QuizDraft {
	title: string;
	description: string;
	questions: Question[];
}

export const TYPES: { type: QuestionType; name: string; hint: string }[] = [
	{ type: 'single', name: 'Pilihan tunggal', hint: 'Satu jawapan betul daripada 2 hingga 6 pilihan.' },
	{ type: 'multiple', name: 'Pilih semua', hint: 'Lebih daripada satu jawapan boleh betul.' },
	{ type: 'truefalse', name: 'Betul atau salah', hint: 'Satu kenyataan, kanak-kanak pilih betul atau salah.' },
	{ type: 'text', name: 'Taip jawapan', hint: 'Kanak-kanak menaip perkataan. Ejaan hampir sama boleh diterima.' },
	{ type: 'number', name: 'Nombor', hint: 'Jawapan berupa nombor, dengan julat jika perlu.' },
	{ type: 'order', name: 'Susun turutan', hint: 'Tulis dalam turutan betul; kanak-kanak melihatnya bercampur.' },
	{ type: 'match', name: 'Padankan', hint: 'Pasangan kiri dan kanan untuk dipadankan.' },
	{ type: 'blank', name: 'Isi tempat kosong', hint: 'Ayat dengan perkataan dalam [kurungan] sebagai tempat kosong.' }
];

export const TYPE_NAME = Object.fromEntries(TYPES.map((t) => [t.type, t.name])) as Record<QuestionType, string>;

export const TIME_LIMITS = [10, 15, 20, 30, 45, 60, 90, 120];

export const LIMITS = { questions: 60, choices: 6, answers: 8, items: 6, pairs: 5, distractors: 6 };

export function newId(): string {
	const bytes = crypto.getRandomValues(new Uint8Array(6));
	return Array.from(bytes, (b) => 'abcdefghijklmnopqrstuvwxyz0123456789'[b % 36]).join('');
}

const choice = (correct = false): Choice => ({ id: newId(), text: '', correct });
const item = (): Item => ({ id: newId(), text: '' });
const pair = (): Pair => ({ id: newId(), left: '', right: '' });

/** A fresh question of a type; `from` keeps the prompt, picture and time of the question it replaces. */
export function blank(type: QuestionType, from?: Question): Question {
	const base: Base = { id: from?.id ?? newId(), prompt: from?.prompt ?? '', image: from?.image ?? null, time_limit: from?.time_limit ?? 20 };
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
	}
}

export const make = { choice, item, pair };

/** A deep copy with new ids, for "Salin soalan". */
export function duplicate(question: Question): Question {
	const copy = JSON.parse(JSON.stringify(question)) as Question;
	copy.id = newId();
	if ('choices' in copy) copy.choices.forEach((c) => (c.id = newId()));
	if ('items' in copy) copy.items.forEach((i) => (i.id = newId()));
	if ('pairs' in copy) copy.pairs.forEach((p) => (p.id = newId()));
	return copy;
}

/** Fills in what older or hand-written questions may lack, so every field has an editor. */
export function normalise(raw: Record<string, unknown>): Question {
	const type = raw.type as QuestionType;
	const fresh = blank(type);
	const question = { ...fresh, ...raw } as Question;
	if ('choices' in question) question.choices = question.choices.map((c) => ({ ...c, id: c.id || newId() }));
	if ('items' in question) question.items = question.items.map((i) => ({ ...i, id: i.id || newId() }));
	if ('pairs' in question) question.pairs = question.pairs.map((p) => ({ ...p, id: p.id || newId() }));
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
