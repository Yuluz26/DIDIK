// What every subject game shares: the props an answer component gets, and the state of the two kinds
// of play most of them are made of. A game is only a look and a way of playing laid over a question type
// (didik_live/games.py), so what it sends is exactly what that type's plain answer component sends.
//
// While a child plays, the state is theirs. Once they have answered (`mine`) or the answer is shown
// (`reveal`), the game shows that instead and nothing moves: what they gave, with marks, and what was right.

import type { Answer, PublicQuestion, Reveal } from '$lib/types';
import { play } from '$lib/sound';
import { suggestStickers } from '$lib/stickers';

export interface GameProps {
	question: PublicQuestion;
	disabled?: boolean;
	mine?: Answer;
	reveal?: Reveal | null;
	onanswer?: (answer: Answer) => void;
}

export const isLocked = (p: GameProps): boolean => !!p.disabled || !!p.reveal || p.mine !== undefined;

/** Things put in order into numbered places (Susun turutan): `slots[i]` is the item in place i. */
export class Slots {
	slots = $state<(string | null)[]>([]);

	constructor(n: number) {
		this.slots = Array.from({ length: n }, () => null);
	}

	/** Puts an item in a place; one already there swaps to where the item came from (or goes back). */
	put(item: string, at: number): void {
		const next = [...this.slots];
		const from = next.indexOf(item);
		if (from === at) return;
		if (from >= 0) next[from] = next[at];
		next[at] = item;
		this.slots = next;
		play('pop');
	}

	/** Into the first empty place. */
	add(item: string): void {
		const at = this.slots.indexOf(null);
		if (at >= 0 && !this.slots.includes(item)) this.put(item, at);
	}

	take(at: number): void {
		const next = [...this.slots];
		next[at] = null;
		this.slots = next;
		play('tap');
	}

	clear(): void {
		this.slots = this.slots.map(() => null);
	}

	get full(): boolean {
		return this.slots.every(Boolean);
	}

	has(item: string): boolean {
		return this.slots.includes(item);
	}
}

/**
 * Things given a place: each thing to one bin (Isih: item → group), or each place one thing (Padankan:
 * left → right, Label rajah: spot → label, with `unique` so one thing is never in two places).
 */
export class Pairs {
	map = $state<Record<string, string>>({});
	picked = $state<string | null>(null);

	constructor(readonly unique = false) {}

	set(key: string, value: string): void {
		const next = { ...this.map };
		if (this.unique) for (const k of Object.keys(next)) if (next[k] === value) delete next[k];
		next[key] = value;
		this.map = next;
		this.picked = null;
		play('pop');
	}

	unset(key: string): void {
		const { [key]: _, ...rest } = this.map;
		this.map = rest;
		play('tap');
	}

	/** The key a value is set for (unique pairs). */
	keyOf(value: string): string | undefined {
		return Object.keys(this.map).find((k) => this.map[k] === value);
	}

	pick(thing: string): void {
		this.picked = this.picked === thing ? null : thing;
		play('tap');
	}

	clear(): void {
		this.map = {};
		this.picked = null;
	}

	count(): number {
		return Object.keys(this.map).length;
	}
}

/** What to show: the child's own answer once given, else (for the host) the right one, else the play. */
export function shown<T>(p: GameProps, live: T): T {
	if (p.mine !== undefined) return p.mine as T;
	if (p.reveal) return p.reveal.correct as T;
	return live;
}

/** The right answer, once it is known. */
export const rightOf = <T>(p: GameProps): T | undefined => (p.reveal ? (p.reveal.correct as T) : undefined);

/** Colours a list of things the same way every time, by their place in the list. */
export const TINTS = ['#ffd9e4', '#d7efff', '#dff5cf', '#fff0c2', '#eadcff', '#ffe2cc'];
export const EDGES = ['#f08aaa', '#6fb6e8', '#7fca5c', '#f1c447', '#a98ae6', '#f3a161'];

/** A 3D sticker whose name is in some words ("Ulat beluncas" → ulat), for things that have none. */
export const stickerFor = (text: string): string | undefined => suggestStickers(text, 1)[0]?.key;
