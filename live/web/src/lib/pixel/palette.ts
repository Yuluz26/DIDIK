/*
 * The one palette every pixel picture is painted from. Materials are ramps of five tones, dark to
 * light, with shadows leaning cool and highlights warm, so a tree, a roof and a river all sit in the
 * same soft, sunny light. Pictures that need a colour a child chose (their hoodie, their skin) build
 * a ramp from it with `rampFrom`.
 */
import { COLOURS, SKINS } from '$lib/names';
import { type Ramp, mix, ramp, rampFrom, rgba } from './pix';

export const M = {
	leaf: ramp(['#2b5a34', '#3d7a3c', '#589a46', '#82ba54', '#b4d86c']),
	pine: ramp(['#1d4a3c', '#2a6a4a', '#3d8858', '#5aa668', '#88c986']),
	autumn: ramp(['#7c2a1c', '#b04426', '#d9672f', '#f0923f', '#ffc566']),
	grass: ramp(['#3c7c3a', '#54a043', '#72bc4c', '#92d25c', '#b6e47a']),
	bark: ramp(['#4a2c22', '#6a4331', '#8c5e41', '#b0825a', '#d2a77a']),
	plank: ramp(['#6e4a30', '#946541', '#b98657', '#d8a877', '#efc99a']),
	stone: ramp(['#55525a', '#7b7880', '#a19ea0', '#c6c1b8', '#e8e2d2']),
	water: ramp(['#1d6585', '#2a8aa3', '#47b0bd', '#7fd2d2', '#c1efe8']),
	deep: ramp(['#164a6e', '#1e6a8c', '#2a88a6', '#46a8bc', '#78cbd2']),
	sand: ramp(['#b2855a', '#d1a974', '#e9c78d', '#f5dfaa', '#fff0cc']),
	dirt: ramp(['#9c6e3d', '#bb8d52', '#d4a96a', '#e6c68b', '#f4dcab']),
	roof: ramp(['#6e2220', '#9a3328', '#c24a35', '#e0674a', '#f58a68']),
	thatch: ramp(['#7a5a2a', '#9c7a3a', '#bf9a4e', '#dcb868', '#f0d488']),
	metal: ramp(['#23222b', '#3a3a46', '#555766', '#7d8094', '#aeb2c4']),
	cloth: ramp(['#a8a4bc', '#cfcbdc', '#ebe8f2', '#f8f6fb', '#ffffff']),
	gold: ramp(['#a8741a', '#d49a22', '#f5c43a', '#ffe070', '#fff6b0']),
	red: rampFrom('#e2483d'),
	pink: rampFrom('#ec6ca5'),
	sun: rampFrom('#f5c518'),
	sky: rampFrom('#2f7fcf'),
	violet: rampFrom('#8a5cd1'),
	cream: ramp(['#c9b79c', '#e6d6bb', '#f6ead3', '#fff6e6', '#ffffff']),
	night: ramp(['#14121f', '#221f33', '#2f2c48', '#434062', '#5f5b84'])
} satisfies Record<string, Ramp>;

/** What a child wears: their colour, as a ramp. */
const coats = new Map<string, Ramp>();
export function coat(colour: string): Ramp {
	let r = coats.get(colour);
	if (!r) coats.set(colour, (r = rampFrom(COLOURS[colour] ?? COLOURS.hijau)));
	return r;
}

const skins = new Map<string, Ramp>();
/** Four tones of skin with a warm rosy shade, and a pink for cheeks. */
export function skin(tone: string): Ramp {
	let r = skins.get(tone);
	if (!r) {
		const base = rgba(SKINS[tone] ?? SKINS.s2);
		const shade = rgba('#a64a4a');
		const lit = rgba('#fff4e0');
		r = { c: [mix(base, shade, 0.5), mix(base, shade, 0.22), base, mix(base, lit, 0.35)], ink: mix(base, shade, 0.72) };
		skins.set(tone, r);
	}
	return r;
}

/** Hair: mostly dark browns and black, with a few warmer ones for variety. */
export const HAIRS = [
	ramp(['#1a1420', '#2c2130', '#41303e', '#5a4352']),
	ramp(['#2a1a14', '#40291d', '#5a3a28', '#7a5238']),
	ramp(['#3a2418', '#58361f', '#7a4d2c', '#a26b3c']),
	ramp(['#171a2a', '#232a42', '#33405e', '#4b5c82']),
	ramp(['#4a2018', '#6c3220', '#8f4a2c', '#b8683c']),
	ramp(['#5a4020', '#7e5e30', '#a88442', '#d0aa5c'])
];

export const BLUSH = rgba('#f08a96');
export const EYE = rgba('#241b2c');
export const WHITE = rgba('#ffffff');
export const OUTLINE = rgba('#2a1f2d');
