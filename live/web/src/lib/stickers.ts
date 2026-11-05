// The 3D stickers a question can show (Microsoft Fluent Emoji 3D, MIT licence; see static/pelekat/LICENSE.txt).
// The server accepts the same keys (didik_live/stickers.py); a test keeps the two lists the same.
//
// Each sticker has its Malay name and the counting word that goes with it (penjodoh bilangan), so the
// editor can write "Masukkan 5 biji epal ke dalam bakul." for a parent.

export type StickerGroup = 'haiwan' | 'makanan' | 'benda' | 'alam' | 'kenderaan' | 'sekolah' | 'lain';

export interface Sticker {
	key: string;
	name: string;
	group: StickerGroup;
	/** The counting word: ekor, biji, buah... */
	unit: string;
}

const S = (group: StickerGroup, unit: string, list: string) =>
	list.split(',').map((pair) => {
		const [key, name] = pair.trim().split('=');
		return { key, name, group, unit } satisfies Sticker;
	});

export const STICKERS: Sticker[] = [
	...S(
		'haiwan',
		'ekor',
		'kucing=Kucing, anjing=Anjing, ayam=Ayam, anak-ayam=Anak ayam, itik=Itik, ikan=Ikan, arnab=Arnab, lembu=Lembu, kambing=Kambing, gajah=Gajah, harimau=Harimau, monyet=Monyet, penyu=Penyu, burung=Burung, burung-hantu=Burung hantu, rama-rama=Rama-rama, lebah=Lebah, kumbang=Kumbang, katak=Katak, siput=Siput, ketam=Ketam, sotong=Sotong, paus=Ikan paus, zirafah=Zirafah, singa=Singa, panda=Panda, penguin=Penguin, unta=Unta, kuda=Kuda, tikus=Tikus, ular=Ular, buaya=Buaya, dinosaur=Dinosaur, orang-utan=Orang utan, merak=Burung merak, ikan-buntal=Ikan buntal, jerung=Jerung, dolfin=Ikan lumba-lumba, kelawar=Kelawar, labah-labah=Labah-labah, ulat=Ulat, semut=Semut, kuda-belang=Kuda belang'
	),
	...S(
		'makanan',
		'biji',
		'epal=Epal, pisang=Pisang, oren=Oren, tembikai=Tembikai, anggur=Anggur, strawberi=Strawberi, nanas=Nanas, mangga=Mangga, kelapa=Kelapa, telur=Telur, donat=Donat, gula-gula=Gula-gula, cendawan=Cendawan, kek=Kek'
	),
	...S('makanan', 'batang', 'lobak-merah=Lobak merah, jagung=Jagung, cili=Cili'),
	...S('makanan', 'keping', 'roti=Roti, biskut=Biskut'),
	...S('makanan', 'mangkuk', 'nasi=Nasi'),
	...S('makanan', 'gelas', 'susu=Susu'),
	...S('makanan', 'kon', 'aiskrim=Aiskrim'),
	...S('makanan', 'biji', 'epal-hijau=Epal hijau'),
	...S('makanan', 'balang', 'madu=Madu'),
	...S('benda', 'biji', 'bola=Bola, belon=Belon, hati=Hati'),
	...S('benda', 'buah', 'wau=Wau, teddy=Anak patung, buku=Buku, beg=Beg, jam=Jam, topi=Topi, loceng=Loceng'),
	...S('benda', 'batang', 'pensel=Pensel, krayon=Krayon'),
	...S('benda', 'kaki', 'payung=Payung'),
	...S('benda', 'pasang', 'kasut=Kasut'),
	...S('benda', 'helai', 'baju=Baju'),
	...S('benda', 'bungkus', 'hadiah=Hadiah'),
	...S('benda', 'buah', 'rumah=Rumah, sekolah=Sekolah, masjid=Masjid, bangunan=Bangunan, beg-duit=Beg duit, plag=Plag, magnet=Magnet'),
	...S('benda', 'keping', 'syiling=Syiling'),
	...S('benda', 'biji', 'bateri=Bateri'),
	...S('alam', 'kuntum', 'bunga=Bunga raya, bunga-matahari=Bunga matahari'),
	...S('alam', 'batang', 'pokok=Pokok, pokok-kelapa=Pokok kelapa'),
	...S('alam', 'biji', 'matahari=Matahari, bulan=Bulan, bintang=Bintang, batu=Batu'),
	...S('alam', 'gumpal', 'awan=Awan, hujan=Awan hujan'),
	...S('alam', 'titis', 'air=Air'),
	...S('alam', 'butir', 'salji=Salji'),
	...S('alam', 'buah', 'pelangi=Pelangi, api=Api, gunung=Gunung, gunung-berapi=Gunung berapi, ombak=Ombak, kilat=Kilat, angin=Angin'),
	...S('alam', 'batang', 'anak-pokok=Anak pokok, kaktus=Kaktus'),
	...S('alam', 'helai', 'daun=Daun'),
	...S('alam', 'kuntum', 'tulip=Bunga tulip'),
	...S('alam', 'ketul', 'ais=Ais'),
	...S(
		'kenderaan',
		'buah',
		'kereta=Kereta, bas=Bas, basikal=Basikal, motosikal=Motosikal, lori=Lori, kereta-api=Kereta api, kapal-terbang=Kapal terbang, helikopter=Helikopter, bot=Bot, kapal=Kapal, roket=Roket, bomba=Kereta bomba, ambulans=Ambulans'
	),
	...S(
		'sekolah',
		'buah',
		'buku-buku=Buku-buku, mikroskop=Mikroskop, tabung-uji=Tabung uji, dna=DNA, kanta=Kanta pembesar, termometer=Termometer, bumi=Bumi, peta=Peta dunia, kalendar=Kalendar, skrol=Skrol, abakus=Abakus, pembaris=Pembaris, sesiku=Sesiku, mentol=Mentol, otak=Otak, jam-pasir=Jam pasir, kompas=Kompas, tanda-soal=Tanda soal, nombor=Nombor, huruf=Huruf, bulatan=Bulatan, segi-empat=Segi empat'
	),
	...S('sekolah', 'batang', 'tulang=Tulang, gigi=Gigi'),
	...S('lain', 'buah', 'bakul=Bakul, kotak=Kotak, troli=Troli, sarang=Sarang, pinggan=Pinggan, piala=Piala, mahkota=Mahkota, pingat=Pingat'),
	...S('lain', 'biji', 'kilauan=Kilauan, bintang-bersinar=Bintang bersinar, mercun=Mercun')
];

export const STICKER_GROUPS: { key: StickerGroup; name: string }[] = [
	{ key: 'haiwan', name: 'Haiwan' },
	{ key: 'makanan', name: 'Makanan' },
	{ key: 'benda', name: 'Benda' },
	{ key: 'alam', name: 'Alam' },
	{ key: 'kenderaan', name: 'Kenderaan' },
	{ key: 'sekolah', name: 'Sekolah & sains' },
	{ key: 'lain', name: 'Lain-lain' }
];

const BY_KEY = new Map(STICKERS.map((s) => [s.key, s]));

export const stickerOf = (key: string | null | undefined): Sticker | undefined => (key ? BY_KEY.get(key) : undefined);

export const stickerUrl = (key: string): string => `/pelekat/${key}.webp`;

/** Stickers whose names appear in some words (a question being written), best first: longer names first,
 * so "burung hantu" comes before "burung". */
export function suggestStickers(text: string, limit = 4): Sticker[] {
	const words = ` ${text.toLowerCase().replace(/[^a-z\s-]/g, ' ').replace(/\s+/g, ' ')} `;
	return STICKERS.filter((s) => s.group !== 'lain' && words.includes(` ${s.name.toLowerCase()} `))
		.sort((a, b) => b.name.length - a.name.length)
		.slice(0, limit);
}

/** Where a "Kira dan masukkan" question's objects go, and how a sentence says it. */
export const PLACES: { key: string; name: string; phrase: string }[] = [
	{ key: 'bakul', name: 'Bakul', phrase: 'ke dalam bakul' },
	{ key: 'kotak', name: 'Kotak', phrase: 'ke dalam kotak' },
	{ key: 'troli', name: 'Troli', phrase: 'ke dalam troli' },
	{ key: 'bas', name: 'Bas', phrase: 'ke dalam bas' },
	{ key: 'kereta-api', name: 'Kereta api', phrase: 'ke dalam kereta api' },
	{ key: 'sarang', name: 'Sarang', phrase: 'ke dalam sarang' },
	{ key: 'pinggan', name: 'Pinggan', phrase: 'di atas pinggan' },
	{ key: 'beg', name: 'Beg', phrase: 'ke dalam beg' }
];

export const placeOf = (key: string) => PLACES.find((p) => p.key === key) ?? PLACES[0];

/** "Masukkan 5 biji epal ke dalam bakul." */
export function countPrompt(sticker: string, place: string, answer: number): string {
	const s = stickerOf(sticker);
	const what = s ? `${s.unit} ${s.name.toLowerCase()}` : 'objek';
	const verb = place === 'bas' || place === 'kereta-api' ? 'Naikkan' : place === 'pinggan' ? 'Letakkan' : 'Masukkan';
	return `${verb} ${answer} ${what} ${placeOf(place).phrase}.`;
}
