/*
 * Small pictures drawn by hand, a character to a pixel: the eight stickers, a flame for a streak,
 * hearts, keys, a crown, a coin, and the thumb stick. Each map says which colour a letter is.
 */
import { memo, sheetOf } from './cache';
import { Pix, pack, rgba } from './pix';


const make = Pix.sketch;

const HEART = [
	'..kkk...kkk..',
	'.krrrk.krrrk.',
	'krwwrrkrrrrrk',
	'krwrrrrrrrrrk',
	'krrrrrrrrrrdk',
	'krrrrrrrrrrdk',
	'.krrrrrrrrdk.',
	'..krrrrrrdk..',
	'...krrrrdk...',
	'....krrdk....',
	'.....kdk.....',
	'......k......'
];

const STAR = [
	'.......k.......',
	'......kyk......',
	'......kyk......',
	'.....kyyyk.....',
	'kkkkkkyywyykkkk',
	'kyyyyyyyyyyyyyk',
	'.kyyyyyyyyyyyk.',
	'..kyyyyyyyyyk..',
	'...kyyyyyyyk...',
	'...kyyyyyyyk...',
	'..kyyyykyyyyk..',
	'..kyyyk.kyyyk..',
	'.kyyyk...kyyyk.',
	'.kkkk.....kkkk.'
];

const LAUGH = [
	'....kkkkkkk....',
	'..kkyyyyyyykk..',
	'.kyyyyyyyyyyyk.',
	'.kyykkyyykkyyk.',
	'kyykyyyyyyykyyk',
	'kyyyyyyyyyyyyyk',
	'kybyyyyyyyyybyk',
	'kybykkkkkkkybyk',
	'kyyykwwwwwkyyyk',
	'.kyykrrrrrkyyk.',
	'.kyyykrrrkyyyk.',
	'..kkyykkkyykk..',
	'....kkkkkkk....'
];

const CLAP = [
	'...s......s...',
	'..s...kk...s..',
	'.....kppk.....',
	'....kppppk....',
	'..kkkppppkkk..',
	'.kpppppppppk..',
	'.kpppppppppk..',
	'.kpppppppppk..',
	'..kpppppppk...',
	'..kpppppppk...',
	'...kpppppk....',
	'....kkkkk.....'
];

const WOW = [
	'....kkkkkkk....',
	'..kkyyyyyyykk..',
	'.kyyyyyyyyyyyk.',
	'.kbbyyyyyyybbk.',
	'kyyyyyyyyyyyyyk',
	'kyywkyyyyywkyyk',
	'kyykkyyyyykkyyk',
	'kyyyyyykyyyyyyk',
	'kyyyyykrrkyyyyk',
	'.kyyyykrrkyyyk.',
	'.kyyyyykkyyyyk.',
	'..kkyyyyyyykk..',
	'....kkkkkkk....'
];

const THUMB = [
	'.......kk......',
	'......kppk.....',
	'......kppk.....',
	'.....kpppk.....',
	'.kkkkkpppkkkk..',
	'kttkpppppppppk.',
	'kttkpppppppppk.',
	'kttkpppppppppk.',
	'kttkkpppppppdk.',
	'kttkpkpppppdk..',
	'kttkkpppppdk...',
	'.kkk.kkkkkk....'
];

const FIRE = [
	'.......k.......',
	'......krk......',
	'.....krrk..k...',
	'....krrrk.krk..',
	'...krrorrkrrrk.',
	'..krrooorrrrrk.',
	'..krroyoorrrrk.',
	'.krrooyyoorrrk.',
	'.krroyyyyoorrk.',
	'.krroyywyyorrk.',
	'..krooyyyyorrk.',
	'..kkroooooorkk.',
	'....kkrrrrkk...',
	'......kkkk.....'
];

const RAINBOW = [
	'...kkkkkkkkk...',
	'.kkrrrrrrrrrkk.',
	'kkrooooooooorkk',
	'krooyyyyyyyoork',
	'kroyyggggggyoRk',
	'kroygbbbbbbgyok',
	'kroygbwwwwbgyok',
	'kwwwkgbwwbgkwwk',
	'kwwwwk....kwwwk',
	'.kkkk......kkkk'
];

const LEGEND_STICKER: Record<string, string> = {
	k: '#3a1820', r: '#e8553f', w: '#ffffff', d: '#b02a30', y: '#ffd34d', b: '#4fc3f7', p: '#f2c08a', s: '#ffb627', t: '#14958a', o: '#ff9a3c', g: '#6cb33f', R: '#e8553f'
};

const STICKERS: Record<string, readonly string[]> = {
	hati: HEART,
	bintang: STAR,
	ketawa: LAUGH,
	tepuk: CLAP,
	wah: WOW,
	ok: THUMB,
	api: FIRE,
	pelangi: RAINBOW
};

/** One of the eight stickers. */
export function sticker(name: string) {
	return memo(`sticker:${name}`, () => {
		const rows = STICKERS[name] ?? STICKERS.hati;
		const legend = name === 'bintang' ? { ...LEGEND_STICKER, y: '#ffc02e', w: '#fff3a8' } : name === 'tepuk' ? { ...LEGEND_STICKER, p: '#f2c08a' } : LEGEND_STICKER;
		const art = make(rows, legend);
		const out = new Pix(16, 16);
		out.stamp(art, Math.floor((16 - art.w) / 2), Math.floor((16 - art.h) / 2));
		return sheetOf(out);
	});
}

/** A heart for a life: full red, or an empty outline once lost. */
export function heart(full: boolean) {
	return memo(`heart:${full}`, () => {
		if (full) return sheetOf(make(HEART, LEGEND_STICKER));
		const ghost = make(HEART, { k: '#8c8a96', r: '#d8d4e0', w: '#eeeaf4', d: '#c0bccc' });
		return sheetOf(ghost);
	});
}

const KEY = [
	'..kkkk.......',
	'.kyyyyk......',
	'kyywwyyk.....',
	'kyw..wyykkkkk',
	'kyyyyyyyyyyyk',
	'.kyyyyyk.kyyk',
	'..kkkkk..kkkk'
];

/** A key for a chest opened; grey while it is still to be won. */
export function key(have: boolean) {
	return memo(`key:${have}`, () =>
		sheetOf(have ? make(KEY, { k: '#5a3b00', y: '#ffc02e', w: '#fff3a8' }) : make(KEY, { k: '#8c8a96', y: '#d8d4e0', w: '#eeeaf4' }))
	);
}

const CROWN = [
	'k...k...k...k',
	'kk.kyk.kyk.kk',
	'kykkyykkyykyk',
	'kyyyyyyyyyyyk',
	'kyywyyryyywyk',
	'kyyyyyyyyyyyk',
	'.kkkkkkkkkkk.'
];

export function crown() {
	return memo('crown', () => sheetOf(make(CROWN, { k: '#7a5410', y: '#ffc02e', w: '#fff3a8', r: '#e8553f' })));
}

const COIN = [
	'..kkkk..',
	'.kyyyyk.',
	'kyywyyyk',
	'kywyyyyk',
	'kyyyyyok',
	'kyyyyook',
	'.koooook',
	'..kkkk..'
];

export function coin() {
	return memo('coin', () => sheetOf(make(COIN, { k: '#7a5410', y: '#ffd34d', w: '#fff3a8', o: '#d49a22' })));
}

/** The base of the thumb stick: an octagon ring with a dithered inside. */
export function stickBase() {
	return memo('stick:base', () => {
		const N = 40;
		const p = new Pix(N, N);
		const white = pack(255, 255, 255, 120);
		const ring = rgba('#ffffff');
		const inside = (x: number, y: number, r: number) => {
			const dx = Math.abs(x + 0.5 - N / 2);
			const dy = Math.abs(y + 0.5 - N / 2);
			return dx <= r && dy <= r && dx + dy <= r * 1.42;
		};
		for (let y = 0; y < N; y++) {
			for (let x = 0; x < N; x++) {
				if (inside(x, y, 19.5)) p.set(x, y, inside(x, y, 17.5) ? ((x + y) % 2 ? white : 0) : ring);
			}
		}
		return sheetOf(p);
	});
}

/** The knob: a small sun-coloured octagon with a light corner and a dark underside. */
export function stickKnob() {
	return memo('stick:knob', () => {
		const N = 18;
		const p = new Pix(N, N);
		const inside = (x: number, y: number, r: number) => {
			const dx = Math.abs(x + 0.5 - N / 2);
			const dy = Math.abs(y + 0.5 - N / 2);
			return dx <= r && dy <= r && dx + dy <= r * 1.42;
		};
		for (let y = 0; y < N; y++) {
			for (let x = 0; x < N; x++) {
				if (!inside(x, y, 8.8)) continue;
				const c = !inside(x, y, 7.8) ? '#7a5410' : y > 12 ? '#d49a22' : x + y < 13 ? '#ffe070' : '#ffc02e';
				p.set(x, y, rgba(c));
			}
		}
		return sheetOf(p);
	});
}

/** One course of a tower: a gold coin seen from the side, or a leafy crate, to repeat upwards. */
export function stackTile(kind: 'coins' | 'harvest') {
	return memo(`stack:${kind}`, () => {
		const rows =
			kind === 'coins'
				? ['kkkkkkkkkkkkkk', 'kwwyyyyyyyyyyk', 'kyyyyyyyyyyyok', 'koooooooooooook']
				: ['kkkkkkkkkkkkkk', 'kwggggggggggok', 'kgggglgggggggk', 'kooooooooooook'];
		return sheetOf(make(rows, kind === 'coins' ? { k: '#7a5410', w: '#fff3a8', y: '#ffd34d', o: '#d49a22' } : { k: '#2b5a34', w: '#b4d86c', g: '#6cb33f', l: '#82ba54', o: '#3d7a3c' })).pix;
	});
}

const TICK = [
	'........kk',
	'.......kwk',
	'......kwk.',
	'kk...kwk..',
	'kwk.kwk...',
	'.kwkwk....',
	'..kwk.....',
	'...k......'
];

/** The mark on a chosen swatch: a white tick with a dark edge, so it reads on any colour. */
export function tick() {
	return memo('tick', () => sheetOf(make(TICK, { k: '#2a1f2d', w: '#ffffff' })));
}
