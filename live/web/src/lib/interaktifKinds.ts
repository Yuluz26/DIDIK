// The four kinds of Kuiz Interaktif a parent can open a room in: the general one (each question its own
// hands-on game) and one for each subject, where every question is played as one of that subject's
// twelve games (server: game/modes/interaktif.py, games.py). The chooser and the front page show them
// with these stickers, colours and photographs.

import { GAMES, type GameInfo, type Subject } from './subjects/games';

export interface InteraktifKind {
	/** the server's mode key */
	key: string;
	subject: Subject | null;
	name: string;
	/** the small line above the name */
	kicker: string;
	line: string;
	stickers: [string, string, string];
	/** a photograph or drawing from static/rajah for the front page */
	photo?: string;
	/** card colours: background, and the ink of the kicker */
	tint: string;
	ink: string;
}

export const INTERAKTIF_KINDS: InteraktifKind[] = [
	{
		key: 'interaktif',
		subject: null,
		name: 'Kuiz Interaktif',
		kicker: 'Umum · semua subjek',
		line: 'Kira dan masukkan, susun huruf, isih ke bakul, cantum gambar dan bayar dengan wang.',
		stickers: ['epal', 'bakul', 'buku'],
		tint: 'linear-gradient(135deg, #ffe8f3, #eee6ff 50%, #e3f6ff)',
		ink: '#6c3fb8'
	},
	{
		key: 'interaktif-sains',
		subject: 'sains',
		name: 'Makmal Sains',
		kicker: 'Interaktif Sains',
		line: 'Ramuan berbuih, teropong angkasa, litar, magnet dan organ badan seperti imbasan X-ray.',
		stickers: ['kelalang', 'teropong', 'planet'],
		photo: 'rajah-suria',
		tint: 'linear-gradient(135deg, #dcf6ef, #dfeaff)',
		ink: '#0d7a6a'
	},
	{
		key: 'interaktif-sejarah',
		subject: 'sejarah',
		name: 'Ekspedisi Sejarah',
		kicker: 'Interaktif Sejarah',
		line: 'Gali artifak, bina empayar, putar mesin masa dan pacak pin pada peta purba.',
		stickers: ['beliung', 'tempayan', 'mahkota'],
		photo: 'rajah-afamosa',
		tint: 'linear-gradient(135deg, #fff1d6, #f5e1c5)',
		ink: '#9a5a12'
	},
	{
		key: 'interaktif-islam',
		subject: 'islam',
		name: 'Cahaya Ilmu',
		kicker: 'Interaktif Pendidikan Islam',
		line: 'Warna tajwid, kompas kiblat, langkah wuduk, peta hijrah dan tabung zakat.',
		stickers: ['masjid', 'buku-terbuka', 'bulan-bintang'],
		photo: 'rajah-kaabah',
		tint: 'linear-gradient(135deg, #e0f5e8, #fbf1d3)',
		ink: '#17794a'
	}
];

export const interaktifKind = (key: string): InteraktifKind | undefined => INTERAKTIF_KINDS.find((k) => k.key === key);

/** The subject's games, for a line of their names. */
export const kindGames = (kind: InteraktifKind): GameInfo[] => (kind.subject ? GAMES.filter((g) => g.subject === kind.subject) : []);
