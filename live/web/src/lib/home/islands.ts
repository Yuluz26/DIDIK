// The fourteen games as the front page shows them: islands on one sea, each with what a child does there.

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
	},
	{
		key: 'pancing',
		title: 'Pancing Ikan',
		pace: 'Ikut kadar sendiri',
		line: 'Jawapan betul memberi umpan. Lempar joran dan lihat apa yang menyambar, dari ikan bilis sampai Arowana Emas.',
		tint: '#1b7185'
	},
	{
		key: 'wau',
		title: 'Lumba Wau',
		pace: 'Semua menjawab serentak',
		line: 'Jawapan betul dan pantas menaikkan wau kamu lebih tinggi, melepasi awan sampai ke garisan penamat.',
		tint: '#b0412e'
	},
	{
		key: 'kubu',
		title: 'Kubu Pasir',
		pace: 'Ikut kadar sendiri',
		line: 'Jawapan betul memberi baldi pasir. Bina istana setingkat demi setingkat, dan bina tembok sebelum ombak datang.',
		tint: '#8f6210'
	},
	{
		key: 'keretapi',
		title: 'Kereta Api Kampung',
		pace: 'Ikut kadar sendiri',
		line: 'Arang dari jawapan betul menambah gerabak dan membawa penumpang dari stesen ke stesen.',
		tint: '#5c4a8a'
	},
	{
		key: 'pasar',
		title: 'Pasar Malam',
		pace: 'Ikut kadar sendiri',
		line: 'Jawapan betul memberi barang untuk dijual. Hias gerai dengan lampu, kanopi dan muzik untuk lebih ramai pelanggan.',
		tint: '#a4366a'
	},
	{
		key: 'bintang',
		title: 'Kejar Bintang',
		pace: 'Dua pasukan',
		line: 'Pasukan Harimau lawan Pasukan Penyu. Tangkap bintang jatuh dan nyalakan buruj di langit malam.',
		tint: '#34407e'
	}
];
