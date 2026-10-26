// The eight games as the front page shows them: islands on one sea, each with what a child does there.

export interface GameIslandInfo {
	key: string;
	title: string;
	/** How the game is paced, in a few plain words. */
	pace: string;
	line: string;
	/** The island's colour on the map's card. */
	tint: string;
}

export const GAMES: GameIslandInfo[] = [
	{
		key: 'lumba',
		title: 'Lumba Sampan',
		pace: 'Semua menjawab serentak',
		line: 'Jawapan betul dan pantas mendayung sampan lebih jauh. Jawapan salah pun masih bergerak sedikit, jadi tiada yang tertinggal di jeti.',
		tint: '#ba512b'
	},
	{
		key: 'lompat',
		title: 'Lompat!',
		pace: 'Semua menjawab serentak',
		line: 'Lompat ke pulau jawapan sebelum masa tamat. Pulau yang salah tenggelam; yang jatuh ke air naik semula selepas dua jawapan betul.',
		tint: '#227a8e'
	},
	{
		key: 'harta',
		title: 'Pulau Harta Karun',
		pace: 'Ikut kadar sendiri',
		line: 'Setiap jawapan betul memberi satu penyodok. Ketik tanda X untuk menggali syiling dan permata sebelum masa tamat.',
		tint: '#94681a'
	},
	{
		key: 'hutan',
		title: 'Hutan Misteri',
		pace: 'Jelajah bersama kawan',
		line: 'Berjalan di dalam hutan, buka peti soalan dan kumpul lima kunci. Pintu keluar terbuka untuk yang cukup kunci.',
		tint: '#2e6e43'
	},
	{
		key: 'pasukan',
		title: 'Pasukan Warna',
		pace: 'Dua pasukan',
		line: 'Pasukan Harimau lawan pasukan Penyu. Jawapan betul memberi bendera untuk menawan petak pulau.',
		tint: '#ae5b0a'
	},
	{
		key: 'kampung',
		title: 'Kampung Kita',
		pace: 'Semua sepasukan',
		line: 'Semua membina satu kampung. Setiap jawapan betul membawa bahan binaan, dan rumah naik sedikit demi sedikit.',
		tint: '#467e22'
	},
	{
		key: 'teka',
		title: 'Teka Gambar',
		pace: 'Semua menjawab serentak',
		line: 'Jawapan betul membuka petak gambar rahsia. Teka gambar itu seawal mungkin untuk mata lebih banyak.',
		tint: '#1d5a99'
	},
	{
		key: 'kebun',
		title: 'Kebun Ajaib',
		pace: 'Ikut kadar sendiri',
		line: 'Jawapan betul memberi air. Tanam benih, siram sampai masak, tuai untuk syiling dan beli tanah baharu.',
		tint: '#956641'
	}
];
