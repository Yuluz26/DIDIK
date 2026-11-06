// One made-up question for each subject game, written the way the pretend server (mock.ts) reads it.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const EXAMPLES: Record<string, any> = {
	ramuan: {
		type: 'multiple',
		game: 'ramuan',
		prompt: 'Pilih DUA bahan yang diperlukan oleh tumbuhan untuk fotosintesis.',
		choices: [
			{ text: 'Karbon dioksida', correct: true },
			{ text: 'Air', correct: true, sticker: 'air' },
			{ text: 'Garam', sticker: 'garam' },
			{ text: 'Gula-gula', sticker: 'gula-gula' }
		],
		explain: 'Tumbuhan menggunakan karbon dioksida dan air, dengan bantuan cahaya matahari dan klorofil, untuk menghasilkan glukosa dan oksigen.'
	},
	teropong: {
		type: 'single',
		game: 'teropong',
		prompt: 'Planet manakah yang paling besar dalam Sistem Suria?',
		choices: [{ text: 'Musytari', correct: true }, { text: 'Bumi' }, { text: 'Marikh' }, { text: 'Zuhal' }],
		explain: 'Musytari ialah planet terbesar. Ia boleh memuatkan lebih 1000 Bumi.'
	},
	orbit: {
		type: 'order',
		game: 'orbit',
		prompt: 'Susun planet ini mengikut jarak dari Matahari, yang terdekat dahulu.',
		items: ['Merkurius', 'Venus', 'Bumi', 'Marikh', 'Musytari'],
		explain: 'Urutan dari Matahari: Merkurius, Venus, Bumi, Marikh, Musytari, Zuhal, Uranus dan Neptun.'
	},
	tubuh: {
		type: 'diagram',
		game: 'tubuh',
		prompt: 'Labelkan organ-organ dalam badan ini.',
		diagram: 'rajah-organ',
		spots: [
			[53, 29, 'Jantung'],
			[27, 33, 'Paru-paru'],
			[74, 45, 'Perut'],
			[75, 61, 'Ginjal']
		],
		explain: 'Jantung mengepam darah, paru-paru untuk bernafas, perut mencerna makanan dan ginjal menapis darah.'
	},
	rantai: {
		type: 'order',
		game: 'rantai',
		prompt: 'Susun rantai makanan ini, bermula dengan pengeluar.',
		items: ['Padi', 'Tikus', 'Ular', 'Helang'],
		explain: 'Padi (pengeluar) dimakan oleh tikus, tikus dimakan oleh ular, dan ular dimakan oleh helang.'
	},
	litar: {
		type: 'single',
		game: 'litar',
		prompt: 'Bahan manakah yang akan menyalakan mentol jika dimasukkan ke dalam litar?',
		choices: [{ text: 'Klip kertas', correct: true, sticker: 'klip-kertas' }, { text: 'Kayu', sticker: 'kayu' }, { text: 'Span', sticker: 'span' }, { text: 'Bulu', sticker: 'bulu' }],
		explain: 'Klip kertas diperbuat daripada logam, iaitu konduktor elektrik. Kayu, span dan bulu ialah penebat.'
	},
	magnet: {
		type: 'sort',
		game: 'magnet',
		prompt: 'Isihkan benda yang ditarik oleh magnet.',
		groups: [['Ditarik magnet', 'magnet'], ['Tidak ditarik']],
		items: [
			['Paku', 0, 'skru'],
			['Klip kertas', 0, 'klip-kertas'],
			['Kunci besi', 0, 'kunci'],
			['Pemadam', 1],
			['Kayu', 1, 'kayu'],
			['Syiling plastik', 1]
		],
		explain: 'Magnet menarik benda yang diperbuat daripada besi, keluli, nikel dan kobalt.'
	},
	jirim: {
		type: 'sort',
		game: 'jirim',
		prompt: 'Isihkan mengikut keadaan jirim.',
		groups: [['Pepejal'], ['Cecair'], ['Gas']],
		items: [
			['Ais', 0, 'ais'],
			['Batu', 0, 'batu-kecil'],
			['Air', 1, 'air'],
			['Susu', 1, 'susu'],
			['Wap air', 2, 'minuman-panas'],
			['Udara dalam belon', 2, 'belon']
		],
		explain: 'Pepejal ada bentuk tetap, cecair mengikut bentuk bekas, dan gas memenuhi seluruh ruang.'
	},
	kitaran: {
		type: 'order',
		game: 'kitaran',
		prompt: 'Susun kitaran hidup rama-rama, bermula dengan telur.',
		items: ['Telur', 'Ulat (larva)', 'Kepompong (pupa)', 'Rama-rama dewasa'],
		explain: 'Rama-rama melalui metamorfosis lengkap: telur, larva, pupa dan dewasa.'
	},
	mikroskop: {
		type: 'diagram',
		game: 'mikroskop',
		prompt: 'Labelkan bahagian sel tumbuhan ini.',
		diagram: 'rajah-sel-pokok',
		spots: [
			[9, 50, 'Dinding sel'],
			[31, 23, 'Kloroplas'],
			[33, 39, 'Nukleus'],
			[65, 57, 'Vakuol']
		],
		explain: 'Sel tumbuhan ada dinding sel, kloroplas dan vakuol yang besar, yang tiada pada sel haiwan.'
	},
	unsur: {
		type: 'match',
		game: 'unsur',
		prompt: 'Padankan simbol unsur dengan namanya.',
		pairs: [
			['H', 'Hidrogen'],
			['O', 'Oksigen'],
			['Na', 'Natrium'],
			['Fe', 'Ferum (besi)']
		],
		explain: 'H hidrogen, O oksigen, Na natrium dan Fe ferum (besi). Na dan Fe datang daripada nama Latin.'
	},
	alat: {
		type: 'number',
		game: 'alat',
		prompt: 'Air tulen mendidih pada suhu berapa?',
		answer: 100,
		unit: '°C',
		explain: 'Pada tekanan udara biasa, air tulen mendidih pada 100 °C dan membeku pada 0 °C.'
	},
	gali: {
		type: 'single',
		game: 'gali',
		prompt: 'Di manakah tengkorak manusia berusia kira-kira 40 000 tahun ditemui di Malaysia?',
		choices: [{ text: 'Gua Niah', correct: true }, { text: 'Lembah Bujang' }, { text: 'Bukit Bunuh' }, { text: 'Gua Cha' }],
		picture: 'rajah-gua-niah',
		explain: 'Tengkorak manusia moden yang sangat tua ditemui di Gua Niah, Sarawak.'
	},
	empayar: {
		type: 'order',
		game: 'empayar',
		prompt: 'Susun pembesar Kesultanan Melayu Melaka mengikut kedudukan, dari yang tertinggi.',
		items: ['Bendahara', 'Penghulu Bendahari', 'Temenggung', 'Laksamana'],
		explain: 'Selepas Sultan, Bendahara paling tinggi, diikuti Penghulu Bendahari, Temenggung dan Laksamana.'
	},
	garismasa: {
		type: 'order',
		game: 'garismasa',
		prompt: 'Susun peristiwa ini mengikut tahun, yang terawal dahulu.',
		items: ['Portugis menawan Melaka (1511)', 'Perjanjian Pangkor (1874)', 'Merdeka (1957)', 'Pembentukan Malaysia (1963)'],
		explain: '1511, 1874, 1957 dan 1963.'
	},
	peta: {
		type: 'diagram',
		game: 'peta',
		prompt: 'Pacakkan nama negeri pada peta.',
		diagram: 'rajah-semenanjung',
		spots: [
			[46, 32, 'Kelantan'],
			[28, 44, 'Perak'],
			[52, 77, 'Melaka'],
			[73, 81, 'Johor']
		],
		explain: 'Kelantan di timur laut, Perak di barat, Melaka di selatan dan Johor di hujung selatan.'
	},
	muzium: {
		type: 'sort',
		game: 'muzium',
		prompt: 'Letakkan artifak di almari zaman yang betul.',
		groups: [['Zaman Prasejarah', 'beliung'], ['Kesultanan Melaka', 'mahkota']],
		items: [
			['Kapak batu', 0, 'batu-kecil'],
			['Tembikar tanah', 0, 'tempayan'],
			['Keris', 1, 'keris'],
			['Syiling timah', 1, 'syiling']
		],
		explain: 'Zaman prasejarah menggunakan alat batu dan tembikar. Kesultanan Melaka mempunyai keris dan mata wang timah.'
	},
	skrol: {
		type: 'blank',
		game: 'skrol',
		prompt: 'Lengkapkan ayat pada skrol.',
		sentence: 'Melaka diasaskan oleh [Parameswara] pada sekitar tahun [1400].',
		distractors: ['Hang Tuah', '1511'],
		explain: 'Parameswara membuka Melaka sekitar tahun 1400.'
	},
	pelabuhan: {
		type: 'match',
		game: 'pelabuhan',
		prompt: 'Padankan pedagang dengan barang yang dibawa ke Melaka.',
		pairs: [
			['Pedagang China', 'Sutera dan tembikar'],
			['Pedagang India', 'Kain'],
			['Pedagang Arab', 'Minyak wangi']
		],
		explain: 'Melaka menjadi pelabuhan entrepot yang menerima barang dari China, India dan Arab.'
	},
	siapa: {
		type: 'single',
		game: 'siapa',
		prompt: 'Saya Perdana Menteri Malaysia yang pertama dan melaungkan "Merdeka!" pada 31 Ogos 1957. Siapakah saya?',
		choices: [{ text: 'Tunku Abdul Rahman', correct: true }, { text: 'Tun Abdul Razak' }, { text: 'Tun Hussein Onn' }, { text: 'Tun Dr. Ismail' }],
		explain: 'Tunku Abdul Rahman ialah Bapa Kemerdekaan dan Perdana Menteri pertama.'
	},
	istana: {
		type: 'order',
		game: 'istana',
		prompt: 'Susun dari atas: siapa paling tinggi dalam pentadbiran Kesultanan Melaka?',
		items: ['Sultan', 'Bendahara', 'Temenggung', 'Rakyat'],
		explain: 'Sultan di puncak, diikuti para pembesar seperti Bendahara dan Temenggung, kemudian rakyat.'
	},
	arkib: {
		type: 'truefalse',
		game: 'arkib',
		prompt: 'Malaysia dibentuk pada 16 September 1963.',
		answer: true,
		explain: 'Malaysia ditubuhkan pada 16 September 1963 oleh Persekutuan Tanah Melayu, Sabah, Sarawak dan Singapura.'
	},
	mesinmasa: {
		type: 'number',
		game: 'mesinmasa',
		prompt: 'Pada tahun berapakah Melaka jatuh ke tangan Portugis?',
		answer: 1511,
		explain: 'Portugis yang diketuai Alfonso de Albuquerque menawan Melaka pada tahun 1511.'
	},
	mesintaip: {
		type: 'text',
		game: 'mesintaip',
		prompt: 'Taip nama bendera Malaysia.',
		answers: ['Jalur Gemilang'],
		picture: 'rajah-jalur',
		explain: 'Bendera Malaysia dinamakan Jalur Gemilang. Ia mempunyai 14 jalur merah dan putih.'
	},
	tajwid: {
		type: 'sort',
		game: 'tajwid',
		prompt: 'Warnakan setiap kalimah mengikut hukum nun sakinah.',
		groups: [['Izhar Halqi'], ['Iqlab'], ['Idgham']],
		items: [
			['مِنْ عِلْمٍ', 0],
			['مِنْ بَعْدِ', 1],
			['مِنْ رَبِّهِمْ', 2],
			['مَنْ يَعْمَلْ', 2]
		],
		explain: 'Nun sakinah bertemu huruf halqi (seperti ع) ialah Izhar, bertemu ب ialah Iqlab, bertemu ر atau ي ialah Idgham.'
	},
	hijaiyah: {
		type: 'single',
		game: 'hijaiyah',
		prompt: 'Yang manakah huruf "Kha"?',
		choices: [{ text: 'خ', correct: true }, { text: 'ح' }, { text: 'ج' }, { text: 'ع' }],
		explain: 'Kha (خ) bertitik satu di atas. Ha (ح) tiada titik, Jim (ج) bertitik di bawah.'
	},
	wuduk: {
		type: 'order',
		game: 'wuduk',
		prompt: 'Susun rukun wuduk mengikut tertib.',
		items: ['Niat dan basuh muka', 'Basuh kedua-dua tangan hingga siku', 'Sapu sebahagian kepala', 'Basuh kedua-dua kaki hingga buku lali'],
		explain: 'Rukun wuduk: niat, membasuh muka, tangan hingga siku, menyapu sebahagian kepala, kaki hingga buku lali, dan tertib.'
	},
	solat: {
		type: 'order',
		game: 'solat',
		prompt: 'Susun gerakan solat dalam satu rakaat.',
		items: ['Takbiratul ihram', 'Rukuk', 'Iktidal', 'Sujud', 'Duduk antara dua sujud'],
		explain: 'Selepas takbiratul ihram dan bacaan al-Fatihah: rukuk, iktidal, sujud, duduk antara dua sujud, kemudian sujud kali kedua.'
	},
	kiblat: {
		type: 'single',
		game: 'kiblat',
		prompt: 'Dari Malaysia, ke arah manakah kiblat?',
		choices: [{ text: 'Barat laut', correct: true }, { text: 'Timur' }, { text: 'Selatan' }, { text: 'Timur laut' }],
		explain: 'Kaabah di Makkah terletak di sebelah barat laut Malaysia.'
	},
	waktu: {
		type: 'match',
		game: 'waktu',
		prompt: 'Padankan solat dengan bilangan rakaatnya.',
		pairs: [
			['Subuh', '2 rakaat'],
			['Zohor', '4 rakaat'],
			['Maghrib', '3 rakaat']
		],
		explain: 'Subuh 2 rakaat, Zohor 4, Asar 4, Maghrib 3 dan Isyak 4.'
	},
	rukun: {
		type: 'multiple',
		game: 'rukun',
		prompt: 'Pilih TIGA rukun Islam.',
		choices: [{ text: 'Mengucap dua kalimah syahadah', correct: true }, { text: 'Menunaikan solat', correct: true }, { text: 'Berpuasa pada bulan Ramadan', correct: true }, { text: 'Beriman kepada malaikat' }, { text: 'Bersedekah setiap hari' }],
		explain: 'Rukun Islam ada lima: syahadah, solat, zakat, puasa Ramadan dan haji. Beriman kepada malaikat ialah rukun iman.'
	},
	timbangan: {
		type: 'sort',
		game: 'timbangan',
		prompt: 'Letakkan perbuatan di piring neraca yang betul.',
		groups: [['Diberi pahala'], ['Berdosa']],
		items: [
			['Menolong ibu', 0],
			['Bersedekah', 0],
			['Mengumpat', 1],
			['Menipu', 1]
		],
		explain: 'Menolong ibu dan bersedekah ialah amalan baik. Mengumpat dan menipu ialah perbuatan berdosa.'
	},
	hijrah: {
		type: 'order',
		game: 'hijrah',
		prompt: 'Susun perjalanan hijrah Nabi Muhammad SAW.',
		items: ['Makkah', 'Gua Thur', 'Quba', 'Madinah'],
		explain: 'Baginda bersembunyi di Gua Thur, kemudian singgah di Quba dan membina masjid pertama sebelum tiba di Madinah.'
	},
	malaikat: {
		type: 'match',
		game: 'malaikat',
		prompt: 'Padankan malaikat dengan tugasnya.',
		pairs: [
			['Jibril', 'Menyampaikan wahyu'],
			['Mikail', 'Menurunkan hujan dan rezeki'],
			['Israfil', 'Meniup sangkakala']
		],
		explain: 'Jibril menyampaikan wahyu, Mikail menurunkan hujan dan rezeki, Israfil meniup sangkakala.'
	},
	zakat: {
		type: 'money',
		game: 'zakat',
		prompt: 'Zakat fitrah untuk seorang ialah RM7. Bayar dengan tepat.',
		amount: 700,
		sticker: 'beg-wang',
		explain: 'Kadar zakat fitrah ditetapkan oleh pihak berkuasa agama negeri, contohnya RM7 seorang.'
	},
	kafilah: {
		type: 'single',
		game: 'kafilah',
		prompt: 'Di gua manakah Nabi Muhammad SAW menerima wahyu pertama?',
		choices: [{ text: 'Gua Hira', correct: true }, { text: 'Gua Thur' }, { text: 'Gua Kahfi' }],
		explain: 'Wahyu pertama, Surah al-Alaq ayat 1 hingga 5, diturunkan di Gua Hira.'
	}
};
