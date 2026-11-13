// The subject games' pictures and what an answer's words mean.
//
// Pictures: real photographs and scientific images kept in static/game-assets (made by
// tools/game-assets/build.py, with every source and licence in manifest.json beside them). A game names a
// picture by its key ("space/mars"); `asset` gives its address and size, so the page keeps room for it
// while it loads. A key that is not in the library gives nothing, and the game shows its fallback.
//
// Words: the lexicon (written by the server from didik_live/lexicon.py, so both sides agree) says that
// "Marikh" is Mars, the fourth planet, pictured by space/mars. `find` looks an answer up.

import { ASSET_SIZES } from './assets.gen';
import LEXICON from './lexicon.gen.json';

export interface Asset {
	key: string;
	src: string;
	w: number;
	h: number;
}

export function asset(key: string | null | undefined): Asset | undefined {
	if (!key) return undefined;
	const size = ASSET_SIZES[key];
	return size ? { key, src: `/game-assets/${key}.webp`, w: size[0], h: size[1] } : undefined;
}

export interface Entry {
	/** the picture, a key of the asset library (or none) */
	key: string | null;
	words: string;
	name: string;
	[more: string]: unknown;
}

type Group = keyof typeof LEXICON;

/** Lower case, without accents: the same folding as the server's. */
export const fold = (text: string): string =>
	text
		.toLowerCase()
		.normalize('NFD')
		.replace(/[̀-ͯ]/g, '');

const patterns = new Map<string, RegExp>();
const pattern = (words: string): RegExp => {
	let made = patterns.get(words);
	if (!made) patterns.set(words, (made = new RegExp(`(?<![a-z0-9])(?:${words})(?![a-z0-9])`)));
	return made;
};

/** The entry of a group that some words mean ("Planet Marikh" → Mars), or nothing. */
export function find<T extends Entry = Entry>(group: Group, text: string | null | undefined): T | undefined {
	if (!text) return undefined;
	const folded = fold(text);
	return (LEXICON[group] as unknown as T[]).find((entry) => pattern(entry.words).test(folded));
}

export interface Element extends Entry {
	sym: string;
	z: number;
	group: number;
	period: number;
	family: string;
}

/** The element some words name: its symbol exactly ("Fe", "Fe (ferum)") or its name. The server's rule. */
export function element(text: string): Element | undefined {
	const words = text.trim();
	const symbol = /^[A-Z][a-z]?(?![A-Za-z])/.exec(words);
	if (symbol) return (LEXICON.elements as unknown as Element[]).find((e) => e.sym === symbol[0]);
	return find<Element>('elements', words);
}

/** Which state of matter a group's name means, or nothing. */
export function stateOfGroup(name: string): 'pepejal' | 'cecair' | 'gas' | undefined {
	const folded = fold(name);
	return (['pepejal', 'cecair', 'gas'] as const).find((state) => pattern(state).test(folded));
}

/** Whether a group's name means "pulled by a magnet" (true), "not pulled" (false), or neither. */
export function pulls(name: string): boolean | undefined {
	const folded = fold(name);
	if (!/magnet|ditarik|tertarik|melekat/.test(folded)) return undefined;
	return !/(?<![a-z])(tidak|bukan|tak|tiada)(?![a-z])/.test(folded);
}

/** Every entry of a group that some words could mean. */
export function findAll<T extends Entry = Entry>(group: Group, text: string | null | undefined): T[] {
	if (!text) return [];
	const folded = fold(text);
	return (LEXICON[group] as unknown as T[]).filter((entry) => pattern(entry.words).test(folded));
}

export interface Stage extends Entry {
	cycle: string;
}

/** The one cycle every one of these stages belongs to (a frog's life, the water cycle), as the server finds it. */
export function cycleOf(texts: string[]): string | undefined {
	let shared: Set<string> | null = null;
	for (const text of texts) {
		const cycles = new Set(findAll<Stage>('stages', text).map((e) => e.cycle));
		shared = shared === null ? cycles : new Set([...shared].filter((c) => cycles.has(c)));
	}
	return shared && shared.size ? [...shared].sort()[0] : undefined;
}

/** A stage's entry within a known cycle. */
export const stageOf = (cycle: string | undefined, text: string): Stage | undefined => findAll<Stage>('stages', text).find((e) => e.cycle === cycle);
