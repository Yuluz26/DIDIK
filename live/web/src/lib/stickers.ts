// The 3D stickers a question can show (Microsoft Fluent Emoji 3D, MIT licence; see static/pelekat/LICENSE.txt).
// The server accepts the same keys (didik_live/stickers.py); a test keeps the two lists the same.
//
// Each sticker has its Malay name and the counting word that goes with it (penjodoh bilangan), so the
// editor can write "Masukkan 5 biji epal ke dalam bakul." for a parent.

export type StickerGroup = 'haiwan' | 'makanan' | 'benda' | 'alam' | 'kenderaan' | 'sekolah' | 'badan' | 'sejarah' | 'islam' | 'lain';

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
	...S('lain', 'biji', 'kilauan=Kilauan, bintang-bersinar=Bintang bersinar, mercun=Mercun'),
	...S(
		'sekolah',
		'buah',
		'teropong=Teropong, planet=Planet Zuhal, kelalang=Kelalang kimia, piring-petri=Piring petri, satelit=Satelit, komet=Komet, mikrob=Mikrob, pil=Pil, stetoskop=Stetoskop, gear=Gear, spana=Spana, neraca=Neraca'
	),
	...S('badan', 'buah', 'jantung=Jantung, paru-paru=Paru-paru, mata=Mata, hidung=Hidung, mulut=Mulut'),
	...S('badan', 'titis', 'darah=Darah'),
	...S('badan', 'belah', 'telinga=Telinga, kaki=Kaki, lengan=Lengan, tangan=Tangan'),
	...S(
		'alam',
		'biji',
		'batu-kecil=Batu kecil, bulan-baru=Bulan baru, bulan-sabit=Bulan sabit, bulan-separuh=Bulan separa, bulan-purnama=Bulan purnama, sabit=Anak bulan'
	),
	...S(
		'alam',
		'buah',
		'puting-beliung=Puting beliung, bimasakti=Bima Sakti, gunung-salji=Gunung bersalji, pulau=Pulau, padang-pasir=Padang pasir, fajar=Matahari terbit, senja=Matahari terbenam, malam=Malam berbintang'
	),
	...S('alam', 'batang', 'kayu=Kayu, herba=Herba, pokok-renek=Pokok malar hijau'),
	...S('alam', 'helai', 'daun-gugur=Daun gugur'),
	...S('haiwan', 'ekor', 'kumbang-kura=Kumbang kura-kura, cacing=Cacing, belalang=Belalang, helang=Helang, rusa=Rusa, udang=Udang'),
	...S('makanan', 'biji', 'lemon=Lemon, tomato=Tomato'),
	...S('makanan', 'ikat', 'sayur=Sayur, padi=Padi'),
	...S('makanan', 'cawan', 'minuman-panas=Minuman panas, teh=Teh'),
	...S('makanan', 'balang', 'garam=Garam'),
	...S(
		'benda',
		'buah',
		'span=Span, klip-kertas=Klip kertas, kunci=Kunci, gunting=Gunting, sudu=Sudu, skru=Skru dan nat, tukul=Tukul, cermin=Cermin, baldi=Baldi, kuali=Kuali, tanglung=Tanglung, beg-wang=Beg wang'
	),
	...S('benda', 'batang', 'lilin=Lilin'),
	...S('benda', 'helai', 'bulu=Bulu pelepah'),
	...S('benda', 'ketul', 'sabun=Sabun'),
	...S(
		'sejarah',
		'buah',
		'tempayan=Tempayan, dewan-klasik=Dewan purba, istana=Istana, kota=Kota, perahu-layar=Perahu layar, perisai=Perisai, kunci-lama=Kunci lama, beliung=Beliung, patung-batu=Patung batu, akhbar=Akhbar, surat=Surat, pin-peta=Pin peta, khemah=Khemah'
	),
	...S('sejarah', 'bilah', 'keris=Keris, pedang=Pedang'),
	...S('sejarah', 'set', 'busur=Busur dan anak panah'),
	...S('sejarah', 'ketul', 'bata=Batu bata'),
	...S('sejarah', 'batang', 'pen=Pen dakwat'),
	...S('sejarah', 'biji', 'permata=Permata, cincin=Cincin'),
	...S('sejarah', 'gulung', 'benang=Benang'),
	...S('islam', 'buah', 'kaabah=Kaabah, buku-terbuka=Kitab terbuka, bulan-bintang=Bulan dan bintang'),
	...S('islam', 'utas', 'tasbih=Tasbih'),
	...S('islam', 'pasang', 'tangan-doa=Tangan berdoa, berjabat=Berjabat tangan')
];

export const STICKER_GROUPS: { key: StickerGroup; name: string }[] = [
	{ key: 'haiwan', name: 'Haiwan' },
	{ key: 'makanan', name: 'Makanan' },
	{ key: 'benda', name: 'Benda' },
	{ key: 'alam', name: 'Alam' },
	{ key: 'kenderaan', name: 'Kenderaan' },
	{ key: 'sekolah', name: 'Sekolah & sains' },
	{ key: 'badan', name: 'Tubuh badan' },
	{ key: 'sejarah', name: 'Sejarah' },
	{ key: 'islam', name: 'Islam' },
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
