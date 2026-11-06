// The subject games: twelve each for Sains, Sejarah and Pendidikan Islam, for Tahun 1 to Tingkatan 5. A game
// is a look and a way of playing laid over a question type (the server's list, with the types each game
// can play, is didik_live/games.py; a test keeps the two the same). Each game's component is loaded only
// when a question asks for it.

import type { Component } from 'svelte';
import type { GameProps } from './kit.svelte';

export type Subject = 'sains' | 'sejarah' | 'islam';

export interface GameInfo {
	key: string;
	title: string;
	subject: Subject;
	/** The question types it plays. */
	types: string[];
	/** Its 3D sticker. */
	icon: string;
	/** One line for a parent choosing it. */
	blurb: string;
}

export const SUBJECTS: { key: Subject; name: string; icon: string }[] = [
	{ key: 'sains', name: 'Sains', icon: 'kelalang' },
	{ key: 'sejarah', name: 'Sejarah', icon: 'tempayan' },
	{ key: 'islam', name: 'Pendidikan Islam', icon: 'masjid' }
];

const G = (key: string, title: string, subject: Subject, types: string[], icon: string, blurb: string): GameInfo => ({ key, title, subject, types, icon, blurb });

export const GAMES: GameInfo[] = [
	G('ramuan', 'Makmal Ramuan', 'sains', ['single', 'multiple'], 'kelalang', 'Tuang botol bahan yang betul ke dalam bikar dan lihat ramuan berbuih.'),
	G('teropong', 'Teropong Angkasa', 'sains', ['single'], 'teropong', 'Gerakkan kanta teropong di langit malam untuk mencari jawapan.'),
	G('orbit', 'Orbit Planet', 'sains', ['order'], 'planet', 'Susun jawapan pada orbit, dari yang terdekat dengan Matahari.'),
	G('tubuh', 'Tubuh Manusia', 'sains', ['diagram'], 'jantung', 'Letak label organ pada tempatnya dalam badan, seperti imbasan X-ray.'),
	G('rantai', 'Rantai Makanan', 'sains', ['order'], 'helang', 'Sambung rantai: siapa dimakan oleh siapa, dari pengeluar hingga pemangsa.'),
	G('litar', 'Litar Elektrik', 'sains', ['single'], 'mentol', 'Masukkan bahan ke dalam litar. Jawapan betul menyalakan mentol.'),
	G('magnet', 'Magnet Ajaib', 'sains', ['sort'], 'magnet', 'Tarik benda ke magnet: yang melekat, dan yang tidak.'),
	G('jirim', 'Balang Jirim', 'sains', ['sort'], 'ais', 'Isih ke dalam balang pepejal, cecair dan gas.'),
	G('kitaran', 'Roda Kitaran', 'sains', ['order'], 'rama-rama', 'Lengkapkan roda kitaran: kitaran hidup, kitaran air, fasa bulan.'),
	G('mikroskop', 'Mikroskop', 'sains', ['diagram'], 'mikroskop', 'Intai melalui kanta mikroskop dan label bahagian sel.'),
	G('unsur', 'Jadual Berkala', 'sains', ['match'], 'tabung-uji', 'Padankan petak unsur dengan nama atau kegunaannya.'),
	G('alat', 'Alat Pengukur', 'sains', ['number'], 'termometer', 'Laraskan termometer, silinder penyukat atau pembaris kepada bacaan yang betul.'),
	G('gali', 'Gali Artifak', 'sejarah', ['single'], 'beliung', 'Gali tanah tapak arkeologi, temui artifak dan pilih yang betul.'),
	G('empayar', 'Bina Empayar', 'sejarah', ['order'], 'istana', 'Susun peristiwa dari asas hingga puncak. Istana naik setingkat demi setingkat.'),
	G('garismasa', 'Garis Masa', 'sejarah', ['order'], 'jam-pasir', 'Gantung peristiwa pada tali garis masa mengikut urutan tahun.'),
	G('peta', 'Peta Nusantara', 'sejarah', ['diagram'], 'pin-peta', 'Pacak pin nama pada peta purba.'),
	G('muzium', 'Kurator Muzium', 'sejarah', ['sort'], 'tempayan', 'Susun artifak ke dalam almari pameran zaman yang betul.'),
	G('skrol', 'Skrol Purba', 'sejarah', ['blank'], 'skrol', 'Lengkapkan tulisan pada skrol lama dengan cop mohor perkataan.'),
	G('pelabuhan', 'Pelabuhan Melaka', 'sejarah', ['match'], 'perahu-layar', 'Labuhkan kapal pedagang di gudang yang betul.'),
	G('siapa', 'Siapakah Aku?', 'sejarah', ['single'], 'tanda-soal', 'Buka petunjuk satu demi satu, kemudian teka tokoh atau tempatnya.'),
	G('istana', 'Hierarki Istana', 'sejarah', ['order'], 'mahkota', 'Susun dari atas ke bawah dalam piramid susun lapis.'),
	G('arkib', 'Arkib Negara', 'sejarah', ['truefalse'], 'akhbar', 'Baca dokumen lama dan cop BENAR atau PALSU.'),
	G('mesinmasa', 'Mesin Masa', 'sejarah', ['number'], 'gear', 'Putar roda tahun mesin masa ke tahun yang betul.'),
	G('mesintaip', 'Mesin Taip Merdeka', 'sejarah', ['text'], 'pen', 'Taip jawapan pada mesin taip lama.'),
	G('tajwid', 'Warna Tajwid', 'islam', ['sort'], 'buku-terbuka', 'Warnakan setiap kalimah mengikut hukum tajwidnya.'),
	G('hijaiyah', 'Huruf Hijaiyah', 'islam', ['single'], 'huruf', 'Pilih huruf yang betul pada papan luh kayu.'),
	G('wuduk', 'Langkah Wuduk', 'islam', ['order'], 'air', 'Susun langkah wuduk mengikut tertib. Air mengalir bila betul.'),
	G('solat', 'Gerakan Solat', 'islam', ['order'], 'tangan-doa', 'Susun gerakan solat di atas sejadah.'),
	G('kiblat', 'Kompas Kiblat', 'islam', ['single'], 'kaabah', 'Pusingkan jarum kompas ke jawapan yang betul.'),
	G('waktu', 'Langit Waktu Solat', 'islam', ['match'], 'senja', 'Padankan solat dengan langit dan bilangan rakaatnya.'),
	G('rukun', 'Tiang Rukun', 'islam', ['multiple'], 'masjid', 'Pilih tiang yang betul untuk menyokong bumbung masjid.'),
	G('timbangan', 'Neraca Amal', 'islam', ['sort'], 'neraca', 'Letak setiap perbuatan di piring neraca yang betul.'),
	G('hijrah', 'Peta Hijrah', 'islam', ['order'], 'unta', 'Ikut perjalanan hijrah dari Makkah ke Madinah.'),
	G('malaikat', 'Lentera Tugas', 'islam', ['match'], 'tanglung', 'Nyalakan lentera dengan memadankan nama dan tugasnya.'),
	G('zakat', 'Tabung Zakat', 'islam', ['money'], 'beg-wang', 'Bayar zakat dengan tepat ke dalam tabung.'),
	G('kafilah', 'Kafilah Sirah', 'islam', ['single', 'truefalse'], 'khemah', 'Bawa kafilah unta ke khemah jawapan yang betul.')
];

const BY_KEY = new Map(GAMES.map((g) => [g.key, g]));

export const gameOf = (key: string | null | undefined): GameInfo | undefined => (key ? BY_KEY.get(key) : undefined);

/** The games that can play a question type, by subject. */
export const gamesFor = (type: string): GameInfo[] => GAMES.filter((g) => g.types.includes(type));

type Loader = () => Promise<{ default: Component<GameProps> }>;

// One file per game, loaded only when a question needs it.
const LOADERS: Record<string, Loader> = {
	ramuan: () => import('./sains/Ramuan.svelte'),
	teropong: () => import('./sains/Teropong.svelte'),
	orbit: () => import('./sains/Orbit.svelte'),
	tubuh: () => import('./sains/Tubuh.svelte'),
	rantai: () => import('./sains/Rantai.svelte'),
	litar: () => import('./sains/Litar.svelte'),
	magnet: () => import('./sains/Magnet.svelte'),
	jirim: () => import('./sains/Jirim.svelte'),
	kitaran: () => import('./sains/Kitaran.svelte'),
	mikroskop: () => import('./sains/Mikroskop.svelte'),
	unsur: () => import('./sains/Unsur.svelte'),
	alat: () => import('./sains/Alat.svelte'),
	gali: () => import('./sejarah/Gali.svelte'),
	empayar: () => import('./sejarah/Empayar.svelte'),
	garismasa: () => import('./sejarah/GarisMasa.svelte'),
	peta: () => import('./sejarah/Peta.svelte'),
	muzium: () => import('./sejarah/Muzium.svelte'),
	skrol: () => import('./sejarah/Skrol.svelte'),
	pelabuhan: () => import('./sejarah/Pelabuhan.svelte'),
	siapa: () => import('./sejarah/Siapa.svelte'),
	istana: () => import('./sejarah/Istana.svelte'),
	arkib: () => import('./sejarah/Arkib.svelte'),
	mesinmasa: () => import('./sejarah/MesinMasa.svelte'),
	mesintaip: () => import('./sejarah/MesinTaip.svelte'),
	tajwid: () => import('./islam/Tajwid.svelte'),
	hijaiyah: () => import('./islam/Hijaiyah.svelte'),
	wuduk: () => import('./islam/Wuduk.svelte'),
	solat: () => import('./islam/Solat.svelte'),
	kiblat: () => import('./islam/Kiblat.svelte'),
	waktu: () => import('./islam/Waktu.svelte'),
	rukun: () => import('./islam/Rukun.svelte'),
	timbangan: () => import('./islam/Timbangan.svelte'),
	hijrah: () => import('./islam/Hijrah.svelte'),
	malaikat: () => import('./islam/Malaikat.svelte'),
	zakat: () => import('./islam/Zakat.svelte'),
	kafilah: () => import('./islam/Kafilah.svelte')
};

export const loaderOf = (key: string): Loader | undefined => LOADERS[key];
