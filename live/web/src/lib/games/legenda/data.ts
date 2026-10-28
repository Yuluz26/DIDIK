// Art and words for Legenda Story Mode. The art lives in static/story/ (built by
// scripts/story_assets.py, listed with its source and status in static/story/manifest.json). The rules
// and every number that matters (hearts, boss bars, who hit) come from the server.

import { FIELDS, type Field } from './layout';

export const ELEMENTS = ['api', 'angin', 'petir', 'tanah', 'air'] as const;
export type Element = (typeof ELEMENTS)[number];

export const ELEMENT_NAME: Record<Element, string> = {
	api: 'Api',
	angin: 'Angin',
	petir: 'Petir',
	tanah: 'Tanah',
	air: 'Air'
};

/** Particle and glow colours for each element: core, edge. */
export const ELEMENT_TINT: Record<Element, [string, string]> = {
	api: ['#ffd27a', '#ff5a1f'],
	angin: ['#e9fff4', '#3fd69a'],
	petir: ['#fff6b0', '#ffc21a'],
	tanah: ['#ffe2b0', '#a8692a'],
	air: ['#e4fbff', '#2aa8ff']
};

export type Pose = 'idle' | 'ready' | 'attack' | 'cast' | 'hurt' | 'victory';

export interface Hero {
	key: 'tuah' | 'mahsuri';
	name: string;
	title: string;
	blurb: string;
}

export const HEROES: Hero[] = [
	{ key: 'tuah', name: 'Hang Tuah', title: 'Laksamana muda', blurb: 'Berani, setia, pantas dengan keris.' },
	{ key: 'mahsuri', name: 'Mahsuri', title: 'Puteri Langkawi', blurb: 'Tenang, jujur, kuat dengan pedang cahaya.' }
];

export const heroArt = (hero: string, pose: Pose | 'portrait') => `/story/heroes/${hero}/${pose}.webp`;

export interface WorldArt {
	key: string;
	/** The element the boss attacks with (its counterattack effect) and a filter for it. */
	strikes: Element;
	strikeFilter?: string;
	/** The colour of the boss's glow when it is nearly beaten. */
	aura: string;
	/** Ambient particles in the air. */
	motes: 'petals' | 'embers' | 'leaves' | 'wisps' | 'mist';
}

export const WORLD_ART: WorldArt[] = [
	{ key: 'chini', strikes: 'air', aura: '#3fe0d0', motes: 'petals' },
	{ key: 'lupar', strikes: 'air', strikeFilter: 'hue-rotate(-40deg) saturate(0.8)', aura: '#ffb347', motes: 'embers' },
	{ key: 'larut', strikes: 'tanah', aura: '#7dff9a', motes: 'leaves' },
	{ key: 'kancil', strikes: 'angin', strikeFilter: 'hue-rotate(120deg) saturate(1.6) brightness(0.9)', aura: '#b77dff', motes: 'wisps' },
	{ key: 'ledang', strikes: 'angin', strikeFilter: 'saturate(0.2) brightness(1.3)', aura: '#bfefff', motes: 'mist' }
];

/** Where things stand on this world's battlefield painting. */
export const field = (world: number): Field => FIELDS[world];

/** The battlefield painting with the boss, the small characters and the live HUD parts taken out. */
export const battleBg = (world: number) => `/story/worlds/${WORLD_ART[world].key}/field.webp`;
export const bossArt = (world: number) => `/story/worlds/${WORLD_ART[world].key}/boss.webp`;
export const minionArt = (world: number, which: 'a' | 'b') => `/story/worlds/${WORLD_ART[world].key}/minion_${which}.webp`;
export const symbol = (world: number) => `/story/ui/symbol_${WORLD_ART[world].key}.webp`;
export const elementIcon = (el: string) => `/story/ui/element_${el}.webp`;
export const fxStill = (el: string) => `/story/fx/${el}.webp`;
/** The 12-frame attack effect (4 by 3 frames of 314 by 418). */
export const fxSlash = (el: string) => `/story/fx/${el}_slash.webp`;
/** Where an effect is centred on its target: slashes in the middle, the earth burst on the ground. */
export const FX_ANCHOR: Record<string, number> = { api: 0.5, angin: 0.5, petir: 0.55, tanah: 0.9, air: 0.5 };

/** Six hearts from twelve halves: 'full', 'half' or 'empty' for each. */
export function heartIcons(halves: number, max = 12): ('full' | 'half' | 'empty')[] {
	return Array.from({ length: max / 2 }, (_, i) => (halves >= i * 2 + 2 ? 'full' : halves === i * 2 + 1 ? 'half' : 'empty'));
}

/** 9 halves read as "4½". */
export function heartsText(halves: number): string {
	const whole = Math.floor(halves / 2);
	return halves % 2 ? `${whole || ''}½` : String(whole);
}

// ------------------------------------------------------------ loading

const cache = new Map<string, Promise<void>>();

/** Fetches and decodes images once, so a pose change never flickers mid-attack. */
export function preload(urls: string[]): Promise<void> {
	if (typeof Image === 'undefined') return Promise.resolve();
	return Promise.all(
		urls.map((url) => {
			let job = cache.get(url);
			if (!job) {
				const img = new Image();
				img.decoding = 'async';
				img.src = url;
				job = img.decode().catch(() => undefined);
				cache.set(url, job);
			}
			return job;
		})
	).then(() => undefined);
}

/** Everything a world's battles need: the battlefield, its boss and minions, the hero's poses and the effects. */
export function worldUrls(world: number, hero: string | null): string[] {
	const art = WORLD_ART[world];
	const urls = [battleBg(world), bossArt(world), minionArt(world, 'a'), minionArt(world, 'b'), symbol(world)];
	if (hero) urls.push(...(['idle', 'ready', 'attack', 'cast', 'hurt', 'victory'] as Pose[]).map((p) => heroArt(hero, p)));
	urls.push(fxStill(art.strikes), fxSlash(art.strikes));
	return urls;
}

export function elementUrls(): string[] {
	return ELEMENTS.flatMap((el) => [fxStill(el), fxSlash(el), elementIcon(el)]);
}

export function reducedMotion(): boolean {
	return typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));
