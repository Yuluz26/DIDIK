// The battle sounds supplied with the art (static/story/audio, synthesised demos for now). They follow
// the same mute switch as the chiptune sounds in lib/sound.ts.

import { isMuted } from '$lib/sound';
import { storyArt } from './data';

const FILES = {
	correct: 'correct',
	wrong: 'wrong',
	hit: 'boss_hit',
	heal: 'heal',
	click: 'menu_click',
	unlock: 'world_unlock'
} as const;

export type Sfx = keyof typeof FILES;

const pool = new Map<Sfx, HTMLAudioElement>();

export function sfx(name: Sfx, volume = 0.7): void {
	if (typeof Audio === 'undefined' || isMuted()) return;
	let base = pool.get(name);
	if (!base) {
		base = new Audio(storyArt(`audio/${FILES[name]}.wav`));
		base.preload = 'auto';
		pool.set(name, base);
	}
	const voice = base.cloneNode() as HTMLAudioElement;
	voice.volume = volume;
	void voice.play().catch(() => undefined);
}
