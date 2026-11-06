// A pretend server for the subject-game art sheet: turns a question written the way a parent writes it
// into what a child's browser gets (shuffled, tokens for ids), and an answer into the reveal. Mirrors
// didik_live/questions.py closely enough to play every game without a room.

import type { PublicQuestion, Reveal } from '$lib/types';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Raw = any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Answer = any;

let n = 0;
const tok = () => `t${(++n).toString(36)}`;
const shuffle = <T>(list: T[]): T[] => {
	const out = [...list];
	for (let i = out.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1));
		[out[i], out[j]] = [out[j], out[i]];
	}
	return out;
};

export interface Mock {
	question: PublicQuestion;
	reveal: Reveal;
}

export function mock(raw: Raw): Mock {
	const q: PublicQuestion = {
		id: tok(),
		type: raw.type,
		label: raw.type,
		prompt: raw.prompt,
		image: null,
		picture: raw.picture ?? null,
		timeLimit: 60,
		game: raw.game
	};
	let correct: Answer;
	switch (raw.type) {
		case 'single':
		case 'multiple': {
			const choices = raw.choices.map((c: Raw) => ({ ...c, id: tok() }));
			q.choices = shuffle(choices).map((c: Raw) => ({ id: c.id, text: c.text, sticker: c.sticker }));
			correct = choices.filter((c: Raw) => c.correct).map((c: Raw) => c.id);
			if (raw.type === 'multiple') q.pick = correct.length;
			break;
		}
		case 'truefalse':
			correct = raw.answer;
			break;
		case 'text':
			correct = raw.answers[0];
			break;
		case 'number':
			q.unit = raw.unit ?? '';
			correct = raw.answer;
			break;
		case 'order': {
			const items = raw.items.map((text: string) => ({ id: tok(), text }));
			q.items = shuffle(items);
			correct = items.map((i: Raw) => i.id);
			break;
		}
		case 'match': {
			const pairs = raw.pairs.map(([l, r, s]: [string, string, string?]) => ({ l: tok(), r: tok(), left: l, right: r, sticker: s }));
			q.left = pairs.map((x: Raw) => ({ id: x.l, text: x.left, sticker: x.sticker }));
			q.right = shuffle(pairs).map((x: Raw) => ({ id: x.r, text: x.right }));
			correct = Object.fromEntries(pairs.map((x: Raw) => [x.l, x.r]));
			break;
		}
		case 'sort': {
			const groups = raw.groups.map(([name, sticker]: [string, string?]) => ({ id: tok(), name, sticker: sticker ?? null }));
			const items = raw.items.map(([text, g, sticker]: [string, number, string?]) => ({ id: tok(), text, sticker: sticker ?? null, g: groups[g].id }));
			q.groups = groups;
			q.items = shuffle(items).map((i: Raw) => ({ id: i.id, text: i.text, sticker: i.sticker }));
			correct = Object.fromEntries(items.map((i: Raw) => [i.id, i.g]));
			break;
		}
		case 'blank': {
			const parts: (string | { blank: number })[] = [];
			const answers: string[] = [];
			let last = 0;
			for (const m of raw.sentence.matchAll(/\[([^\]]+)\]/g)) {
				if (m.index! > last) parts.push(raw.sentence.slice(last, m.index));
				parts.push({ blank: answers.length });
				answers.push(m[1].split('/')[0]);
				last = m.index! + m[0].length;
			}
			if (last < raw.sentence.length) parts.push(raw.sentence.slice(last));
			q.parts = parts;
			q.blanks = answers.length;
			q.bank = shuffle([...answers, ...(raw.distractors ?? [])]);
			correct = answers;
			break;
		}
		case 'money':
			q.amount = raw.amount;
			q.money = [5, 10, 20, 50, 100, 500, 1000, 5000].filter((m) => m <= Math.max(raw.amount, 50));
			q.sticker = raw.sticker ?? null;
			correct = raw.amount;
			break;
		case 'diagram': {
			const spots = raw.spots.map(([x, y, label]: [number, number, string]) => ({ s: tok(), b: tok(), x, y, label }));
			q.diagram = raw.diagram;
			q.spots = spots.map((s: Raw) => ({ id: s.s, x: s.x, y: s.y }));
			q.labels = shuffle(spots).map((s: Raw) => ({ id: s.b, text: s.label }));
			correct = Object.fromEntries(spots.map((s: Raw) => [s.s, s.b]));
			break;
		}
	}
	return { question: q, reveal: { correct, explain: raw.explain ?? '' } };
}
