// Diagrams and photographs from Wikimedia Commons under free licences (public domain, CC0, CC BY, CC BY-SA),
// in static/rajah/ (who made each one: static/rajah/CREDITS.txt, and under each picture). A question shows
// one as its picture ("gambar rajah"), or has a child label it (the "Label rajah" type).
// The server accepts the same keys (didik_live/diagrams.py); a test keeps the two lists the same.
//
// Each has its size (for the frame to keep its shape while it loads), its credit, and, for the ones made to
// be labelled, the places a parent is likely to want, in percent from the top left.

export interface Spot {
	x: number;
	y: number;
	label: string;
}

export interface Diagram {
	key: string;
	name: string;
	w: number;
	h: number;
	credit: string;
	/** A photograph rather than a drawing: shown filling its frame. */
	photo?: boolean;
	/** Places a parent can put labels on with one tap. */
	spots?: Spot[];
}

export const DIAGRAMS: Diagram[] = [
	{
		key: 'rajah-organ',
		name: 'Organ dalam badan',
		w: 625,
		h: 1000,
		credit: 'Mikael Häggström, domain awam',
		spots: [
			{ x: 53, y: 29, label: 'Jantung' },
			{ x: 27, y: 33, label: 'Paru-paru' },
			{ x: 30, y: 49, label: 'Hati' },
			{ x: 74, y: 45, label: 'Perut' },
			{ x: 75, y: 61, label: 'Ginjal' },
			{ x: 48, y: 77, label: 'Usus' },
			{ x: 51, y: 93, label: 'Pundi kencing' }
		]
	},
	{
		key: 'rajah-cerna',
		name: 'Sistem pencernaan',
		w: 1000,
		h: 898,
		credit: 'Arnavaz dan Medium69, domain awam',
		spots: [
			{ x: 52, y: 13, label: 'Esofagus' },
			{ x: 36, y: 29, label: 'Hati' },
			{ x: 58, y: 34, label: 'Perut' },
			{ x: 50, y: 62, label: 'Usus kecil' },
			{ x: 69, y: 56, label: 'Usus besar' },
			{ x: 51, y: 88, label: 'Rektum' }
		]
	},
	{
		key: 'rajah-sel-haiwan',
		name: 'Sel haiwan',
		w: 886,
		h: 1000,
		credit: 'domdomegg, CC BY 4.0',
		spots: [
			{ x: 37, y: 39, label: 'Nukleus' },
			{ x: 92, y: 55, label: 'Membran sel' },
			{ x: 66, y: 72, label: 'Sitoplasma' },
			{ x: 53, y: 35, label: 'Mitokondria' }
		]
	},
	{
		key: 'rajah-sel-pokok',
		name: 'Sel tumbuhan',
		w: 756,
		h: 1000,
		credit: 'domdomegg, CC BY 4.0',
		spots: [
			{ x: 9, y: 50, label: 'Dinding sel' },
			{ x: 31, y: 23, label: 'Kloroplas' },
			{ x: 33, y: 39, label: 'Nukleus' },
			{ x: 65, y: 57, label: 'Vakuol' },
			{ x: 25, y: 70, label: 'Sitoplasma' }
		]
	},
	{
		key: 'rajah-kitaran-air',
		name: 'Kitaran air',
		w: 1000,
		h: 474,
		credit: 'Joooo dan moyogo, CC BY-SA 3.0',
		spots: [
			{ x: 20, y: 52, label: 'Sejatan' },
			{ x: 26, y: 27, label: 'Kondensasi' },
			{ x: 71, y: 38, label: 'Kerpasan' },
			{ x: 46, y: 68, label: 'Air larian' },
			{ x: 9, y: 7, label: 'Matahari' }
		]
	},
	{
		key: 'rajah-rangka',
		name: 'Rangka manusia',
		w: 698,
		h: 1000,
		credit: 'LadyofHats dan Quico, domain awam',
		spots: [
			{ x: 47, y: 11, label: 'Tengkorak' },
			{ x: 33, y: 28, label: 'Tulang selangka' },
			{ x: 35, y: 43, label: 'Tulang rusuk' },
			{ x: 47, y: 57, label: 'Tulang belakang' },
			{ x: 33, y: 65, label: 'Tulang pinggul' },
			{ x: 16, y: 81, label: 'Tulang tangan' }
		]
	},
	{
		key: 'rajah-malaysia',
		name: 'Peta Malaysia',
		w: 1000,
		h: 341,
		credit: 'Golbez, CC BY 2.5 (diwarnakan)',
		spots: [
			{ x: 14, y: 50, label: 'Semenanjung Malaysia' },
			{ x: 64, y: 79, label: 'Sarawak' },
			{ x: 88, y: 32, label: 'Sabah' },
			{ x: 50, y: 30, label: 'Laut China Selatan' }
		]
	},
	{
		key: 'rajah-semenanjung',
		name: 'Peta Semenanjung Malaysia',
		w: 690,
		h: 874,
		credit: 'Golbez, CC BY 2.5 (diwarnakan)',
		spots: [
			{ x: 14, y: 14, label: 'Perlis' },
			{ x: 22, y: 25, label: 'Kedah' },
			{ x: 28, y: 44, label: 'Perak' },
			{ x: 46, y: 32, label: 'Kelantan' },
			{ x: 65, y: 38, label: 'Terengganu' },
			{ x: 55, y: 57, label: 'Pahang' },
			{ x: 35, y: 61, label: 'Selangor' },
			{ x: 51, y: 70, label: 'Negeri Sembilan' },
			{ x: 52, y: 77, label: 'Melaka' },
			{ x: 73, y: 81, label: 'Johor' }
		]
	},
	{
		key: 'rajah-arab',
		name: 'Peta Semenanjung Tanah Arab',
		w: 915,
		h: 1000,
		credit: 'Peter Fitzgerald, domain awam (diwarnakan)',
		spots: [
			{ x: 29, y: 55, label: 'Makkah' },
			{ x: 25, y: 44, label: 'Madinah' },
			{ x: 14, y: 50, label: 'Laut Merah' },
			{ x: 55, y: 50, label: 'Gurun' }
		]
	},
	{ key: 'rajah-jalur', name: 'Jalur Gemilang', w: 1000, h: 500, credit: 'MapGrid, domain awam' },
	{
		key: 'rajah-suria',
		name: 'Sistem Suria',
		w: 1000,
		h: 379,
		credit: 'Beinahegut dan Torr3, CC BY-SA 4.0',
		spots: [
			{ x: 2, y: 50, label: 'Matahari' },
			{ x: 17, y: 46, label: 'Bumi' },
			{ x: 37, y: 50, label: 'Musytari' },
			{ x: 58, y: 50, label: 'Zuhal' },
			{ x: 74, y: 49, label: 'Uranus' },
			{ x: 86, y: 49, label: 'Neptun' }
		]
	},
	{
		key: 'rajah-gunung-berapi',
		name: 'Gunung berapi (keratan)',
		w: 1000,
		h: 1000,
		credit: 'Sémhur, CC BY-SA 4.0',
		spots: [
			{ x: 50, y: 77, label: 'Magma' },
			{ x: 50, y: 53, label: 'Kawah' },
			{ x: 82, y: 63, label: 'Lava' },
			{ x: 55, y: 22, label: 'Abu dan gas' }
		]
	},
	{ key: 'rajah-afamosa', name: 'A Famosa, Melaka', w: 900, h: 675, credit: 'Wikimedia Commons, CC BY 2.5', photo: true },
	{ key: 'rajah-kaabah', name: 'Kaabah, Masjidil Haram', w: 900, h: 600, credit: 'مريم محمد الغلبان, CC0', photo: true },
	{ key: 'rajah-lembah-bujang', name: 'Candi di Lembah Bujang', w: 900, h: 599, credit: 'Imhadi, domain awam', photo: true },
	{ key: 'rajah-gua-niah', name: 'Gua Niah, Sarawak', w: 900, h: 625, credit: 'Nur Nafis Naim, CC BY-SA 4.0', photo: true },
	{ key: 'rajah-number-line', name: 'Garis nombor', w: 960, h: 56, credit: 'Wikimedia Commons, domain awam' },
	{ key: 'rajah-letters', name: 'Huruf abjad Rumi', w: 960, h: 535, credit: 'Cangjie6, CC BY-SA 4.0 / domain awam' },
	{ key: 'rajah-gajah-asia', name: 'Gajah Asia', w: 333, h: 500, credit: 'Kseajayne, CC BY 3.0', photo: true }
];

const BY_KEY = new Map(DIAGRAMS.map((d) => [d.key, d]));

export const diagramOf = (key: string | null | undefined): Diagram | undefined => (key ? BY_KEY.get(key) : undefined);

export const diagramUrl = (key: string): string => `/rajah/${key}.webp`;

export const isDiagram = (key: string | null | undefined): boolean => !!key && BY_KEY.has(key);
