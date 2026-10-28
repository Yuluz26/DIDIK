// Art and words for Legenda Story Mode. The art lives in static/story/ (built by
// scripts/story_assets.py, listed with its source and status in static/story/manifest.json). The rules
// and every number that matters (hearts, boss bars, who hit) come from the server.

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
	/** Poses drawn for this boss; the rest are played in code from `idle`. */
	poses: ('idle' | 'attack' | 'special' | 'hurt' | 'defeat')[];
	/** The element the boss attacks with (its counterattack effect) and a filter for it. */
	strikes: Element;
	strikeFilter?: string;
	/** Light over the scene: a top and a bottom tint, and the colour of the boss's aura. */
	light: [string, string];
	aura: string;
	/** Ambient particles in the air. */
	motes: 'petals' | 'embers' | 'leaves' | 'wisps' | 'mist';
	/** The boss's height on the stage, as a share of the stage width. */
	bossSize: number;
	/** Boss reveal still: the boss's own pose (world 1) or a cinematic close-up (worlds 2 to 5). */
	reveal: string;
}

export const WORLD_ART: WorldArt[] = [
	{
		key: 'chini',
		poses: ['idle', 'attack', 'special', 'hurt', 'defeat'],
		strikes: 'air',
		light: ['rgb(255 244 214 / 0.18)', 'rgb(10 60 90 / 0.25)'],
		aura: '#3fe0d0',
		motes: 'petals',
		bossSize: 0.6,
		reveal: '/story/bosses/chini/reveal.webp'
	},
	{
		key: 'lupar',
		poses: ['idle'],
		strikes: 'air',
		strikeFilter: 'hue-rotate(-40deg) saturate(0.8)',
		light: ['rgb(255 170 90 / 0.22)', 'rgb(40 20 30 / 0.3)'],
		aura: '#ffb347',
		motes: 'embers',
		bossSize: 0.58,
		reveal: '/story/worlds/lupar/reveal.webp'
	},
	{
		key: 'larut',
		poses: ['idle'],
		strikes: 'tanah',
		light: ['rgb(200 255 170 / 0.16)', 'rgb(10 40 20 / 0.32)'],
		aura: '#7dff9a',
		motes: 'leaves',
		bossSize: 0.52,
		reveal: '/story/worlds/larut/reveal.webp'
	},
	{
		key: 'kancil',
		poses: ['idle'],
		strikes: 'angin',
		strikeFilter: 'hue-rotate(120deg) saturate(1.6) brightness(0.9)',
		light: ['rgb(170 120 255 / 0.2)', 'rgb(20 10 50 / 0.42)'],
		aura: '#b77dff',
		motes: 'wisps',
		bossSize: 0.56,
		reveal: '/story/worlds/kancil/reveal.webp'
	},
	{
		key: 'ledang',
		poses: ['idle'],
		strikes: 'angin',
		strikeFilter: 'saturate(0.2) brightness(1.3)',
		light: ['rgb(255 255 255 / 0.2)', 'rgb(40 70 100 / 0.26)'],
		aura: '#bfefff',
		motes: 'mist',
		bossSize: 0.62,
		reveal: '/story/worlds/ledang/reveal.webp'
	}
];

export const bossArt = (world: number, pose: string) => {
	const art = WORLD_ART[world];
	return `/story/bosses/${art.key}/${art.poses.includes(pose as never) ? pose : 'idle'}.webp`;
};
export const battleBg = (world: number) => `/story/worlds/${WORLD_ART[world].key}/battle.webp`;
export const symbol = (world: number) => `/story/ui/symbol_${WORLD_ART[world].key}.webp`;
export const elementIcon = (el: string) => `/story/ui/element_${el}.webp`;
export const fxStill = (el: string) => `/story/fx/${el}.webp`;
export const fxSheet = (el: string) => `/story/fx/${el}_sheet.webp`;

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

/** Everything a world's battles need: its backdrop, the boss, the hero's poses and the effects. */
export function worldUrls(world: number, hero: string | null): string[] {
	const art = WORLD_ART[world];
	const urls = [battleBg(world), art.reveal, symbol(world), ...art.poses.map((p) => bossArt(world, p))];
	if (hero) urls.push(...(['idle', 'ready', 'attack', 'cast', 'hurt', 'victory'] as Pose[]).map((p) => heroArt(hero, p)));
	urls.push(fxStill(art.strikes), fxSheet(art.strikes));
	return urls;
}

export function elementUrls(): string[] {
	return ELEMENTS.flatMap((el) => [fxStill(el), fxSheet(el), elementIcon(el)]);
}

export function reducedMotion(): boolean {
	return typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));
