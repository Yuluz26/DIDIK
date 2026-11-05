// The three kinds of game DIDIK offers, in the order a host meets them: Kuiz Interaktif, the 2D island
// games, and the story mode. The server says which kind each game is (ModeInfo.family).

import type { ModeInfo } from './types';

export interface Family {
	key: ModeInfo['family'];
	name: string;
	note: string;
	/** A 3D sticker that stands for the kind (lib/stickers.ts). */
	sticker: string;
}

export const FAMILIES: Family[] = [
	{
		key: 'interaktif',
		name: 'Kuiz Interaktif',
		note: 'Sentuh, seret dan susun bersama Didi. Setiap soalan satu permainan kecil, ikut kadar sendiri.',
		sticker: 'bintang-bersinar'
	},
	{
		key: '2d',
		name: 'Permainan 2D',
		note: 'Empat belas pulau pixel: berlumba, melompat, menggali, menanam dan berpasukan.',
		sticker: 'bot'
	},
	{
		key: 'story',
		name: 'Story Mode',
		note: 'Hikayat Lima Alam: wira, boss dan lima dunia legenda Melayu, Solo atau Party.',
		sticker: 'mahkota'
	}
];

/** The games of each kind, in the server's order. */
export function byFamily(modes: ModeInfo[]): { family: Family; modes: ModeInfo[] }[] {
	return FAMILIES.map((family) => ({ family, modes: modes.filter((m) => (m.family ?? '2d') === family.key) })).filter((g) => g.modes.length);
}
