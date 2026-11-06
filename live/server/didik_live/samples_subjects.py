"""Sample quizzes for the subject games: Sains, Sejarah and Pendidikan Islam, each at three levels (Tahap 1 for
Tahun 1 to 3, Tahap 2 for Tahun 4 to 6, Menengah for Tingkatan 1 to 5). Every quiz plays all twelve of its
subject's games once, so a parent can see each game by playing one quiz in Kuiz Interaktif.

Facts follow the KSSR and KSSM syllabuses; check them again when changing anything, because children will
believe them. Arabic is written with its harakat, and no prophet or angel is ever pictured.
"""

from __future__ import annotations

from .sample_kit import _blank, _diagram, _match, _money, _multiple, _number, _order, _single, _sort, _text, _tf, play

SUBJECT_SAMPLES = [
    # ------------------------------------------------------------------ Sains
    {
        "title": "Sains Tahap 1: Saintis Cilik",
        "description": "12 permainan sains untuk Tahun 1 hingga 3: makmal ramuan, teropong, magnet, litar, organ badan dan banyak lagi.",
        "questions": [
            play("ramuan", _single(
                "Bahan manakah yang larut dalam air?", "Gula", "Batu", "Kayu", "Klip kertas", time=45,
                stickers={"Gula": "gula-gula", "Batu": "batu-kecil", "Kayu": "kayu", "Klip kertas": "klip-kertas"},
                why="Gula larut dalam air: ia bercampur sehingga tidak kelihatan lagi. Batu, kayu dan klip kertas tidak larut.",
            )),
            play("teropong", _single(
                "Bintang manakah yang paling dekat dengan Bumi?", "Matahari", "Bulan", "Marikh", "Bintang Utara", time=45, pic="matahari",
                why="Matahari ialah sebuah bintang, dan bintang yang paling dekat dengan Bumi. Bulan bukan bintang; ia satelit Bumi.",
            )),
            play("orbit", _order(
                "Susun planet ini mengikut jarak dari Matahari, yang terdekat dahulu.", "Merkurius", "Venus", "Bumi", "Marikh", time=60, pic="planet",
                why="Merkurius paling dekat dengan Matahari, diikuti Venus, Bumi dan Marikh.",
            )),
            play("tubuh", _diagram(
                "Labelkan organ dalam badan ini.", "rajah-organ", [(53, 29, "Jantung"), (27, 33, "Paru-paru"), (74, 45, "Perut")],
                why="Jantung mengepam darah, paru-paru membantu kita bernafas, dan perut mencerna makanan.",
            )),
            play("rantai", _order(
                "Susun rantai makanan ini. Mula dengan tumbuhan.", "Padi", "Tikus", "Ular", time=60,
                why="Padi ialah pengeluar. Padi dimakan oleh tikus, dan tikus dimakan oleh ular.",
            )),
            play("litar", _single(
                "Masukkan bahan yang membolehkan mentol menyala.", "Kunci besi", "Pemadam", "Kayu", "Bulu", time=45,
                stickers={"Kunci besi": "kunci", "Kayu": "kayu", "Bulu": "bulu"},
                why="Besi ialah logam. Logam membenarkan arus elektrik mengalir (konduktor), jadi mentol menyala. Pemadam, kayu dan bulu ialah penebat.",
            )),
            play("magnet", _sort(
                "Benda manakah yang ditarik oleh magnet?",
                [
                    ("Ditarik magnet", "magnet", [("Paku besi", "skru"), ("Klip kertas", "klip-kertas"), ("Gunting", "gunting")]),
                    ("Tidak ditarik", None, [("Kayu", "kayu"), ("Bulu", "bulu"), ("Span", "span")]),
                ],
                why="Magnet menarik benda yang diperbuat daripada besi atau keluli, seperti paku, klip kertas dan gunting. Kayu, bulu dan span tidak ditarik.",
            )),
            play("jirim", _sort(
                "Isihkan mengikut keadaan jirim.",
                [
                    ("Pepejal", None, [("Ais", "ais"), ("Batu", "batu-kecil")]),
                    ("Cecair", None, [("Air", "air"), ("Susu", "susu")]),
                    ("Gas", None, [("Wap air", "minuman-panas"), ("Udara dalam belon", "belon")]),
                ],
                why="Pepejal mempunyai bentuk tetap, cecair mengikut bentuk bekasnya, dan gas memenuhi seluruh ruang.",
            )),
            play("kitaran", _order(
                "Susun kitaran hidup katak, bermula dengan telur.", "Telur", "Berudu", "Katak muda", "Katak dewasa", time=60, pic="katak",
                why="Katak bertelur di dalam air. Telur menetas menjadi berudu, berudu tumbuh kaki menjadi katak muda, kemudian katak dewasa.",
            )),
            play("mikroskop", _diagram(
                "Lihat sel haiwan melalui mikroskop. Labelkan dua bahagiannya.", "rajah-sel-haiwan", [(37, 39, "Nukleus"), (92, 55, "Membran sel")],
                why="Nukleus ialah pusat kawalan sel. Membran sel ialah lapisan nipis yang membalut sel.",
            )),
            play("unsur", _match(
                "Padankan bahan dengan benda yang diperbuat daripadanya.",
                [("Kaca", "Tingkap"), ("Kayu", "Meja"), ("Logam", "Sudu"), ("Plastik", "Botol air")],
                time=60, pic="sudu",
                why="Tingkap daripada kaca supaya cahaya masuk, meja daripada kayu, sudu daripada logam dan botol air daripada plastik.",
            )),
            play("alat", _number(
                "Laraskan termometer kepada suhu badan manusia yang normal.", 37, "°C", time=45, pic="termometer",
                why="Suhu badan manusia yang sihat ialah kira-kira 37 °C. Jika lebih tinggi, mungkin kita demam.",
            ) | {"tolerance": 1}),
        ],
    },
    {
        "title": "Sains Tahap 2: Penyiasat Alam",
        "description": "12 permainan sains untuk Tahun 4 hingga 6: fotosintesis, sistem pencernaan, kitaran air, litar elektrik dan unsur.",
        "questions": [
            play("ramuan", _multiple(
                "Tuang DUA bahan mentah yang digunakan oleh tumbuhan untuk fotosintesis.", ["Karbon dioksida", "Air"], ["Oksigen", "Garam"], time=60,
                pic="daun", stickers={"Air": "air", "Garam": "garam"},
                why="Tumbuhan menggunakan karbon dioksida dan air, dengan bantuan cahaya matahari dan klorofil, untuk menghasilkan glukosa dan oksigen.",
            )),
            play("teropong", _single(
                "Planet manakah yang dikenali sebagai Planet Merah?", "Marikh", "Musytari", "Venus", "Zuhal", time=45,
                why="Marikh kelihatan merah kerana tanahnya mengandungi banyak besi oksida (karat).",
            )),
            play("orbit", _order(
                "Susun planet ini mengikut jarak dari Matahari.", "Merkurius", "Venus", "Bumi", "Marikh", "Musytari", "Zuhal", time=75, pic="rajah-suria",
                why="Urutan planet dari Matahari: Merkurius, Venus, Bumi, Marikh, Musytari, Zuhal, Uranus dan Neptun.",
            )),
            play("tubuh", _diagram(
                "Labelkan bahagian sistem pencernaan.", "rajah-cerna",
                [(52, 13, "Esofagus"), (58, 34, "Perut"), (50, 62, "Usus kecil"), (69, 56, "Usus besar"), (51, 88, "Rektum")],
                why="Makanan melalui esofagus ke perut, kemudian usus kecil (tempat makanan diserap) dan usus besar (air diserap), dan sisa dikeluarkan melalui rektum.",
            )),
            play("rantai", _order(
                "Susun rantai makanan ini dari pengeluar.", "Rumput", "Belalang", "Katak", "Ular", "Helang", time=75,
                why="Rumput (pengeluar) dimakan belalang, belalang dimakan katak, katak dimakan ular, dan ular dimakan helang.",
            )),
            play("litar", _single(
                "Komponen manakah yang membekalkan tenaga elektrik kepada litar?", "Bateri", "Mentol", "Klip kertas", "Span", time=45,
                stickers={"Bateri": "bateri", "Mentol": "mentol", "Klip kertas": "klip-kertas", "Span": "span"},
                why="Bateri ialah sumber tenaga elektrik dalam litar. Mentol menggunakan tenaga itu untuk menyala.",
            )),
            play("magnet", _sort(
                "Isihkan bahan magnet dan bahan bukan magnet.",
                [
                    ("Bahan magnet", "magnet", [("Paku besi", "skru"), ("Klip kertas keluli", "klip-kertas"), ("Gunting keluli", "gunting")]),
                    ("Bahan bukan magnet", None, [("Tin aluminium", None), ("Pembaris plastik", "pembaris"), ("Pensel kayu", "pensel")]),
                ],
                why="Besi dan keluli ialah bahan magnet. Aluminium, plastik dan kayu tidak ditarik oleh magnet.",
            )),
            play("jirim", _sort(
                "Isihkan bahan ini mengikut keadaan jirim pada suhu bilik.",
                [
                    ("Pepejal", None, [("Garam", "garam"), ("Kayu", "kayu")]),
                    ("Cecair", None, [("Minyak masak", None), ("Air", "air")]),
                    ("Gas", None, [("Oksigen", None), ("Wap air", "minuman-panas")]),
                ],
                why="Garam dan kayu pepejal, minyak dan air cecair, manakala oksigen dan wap air ialah gas.",
            )),
            play("kitaran", _order(
                "Susun kitaran air, bermula dengan sejatan.", "Sejatan", "Kondensasi", "Kerpasan", "Air larian ke laut", time=60, pic="rajah-kitaran-air",
                why="Air laut menyejat apabila dipanaskan Matahari, wap air terkondensasi menjadi awan, turun sebagai hujan (kerpasan), dan mengalir semula ke laut.",
            )),
            play("mikroskop", _diagram(
                "Labelkan bahagian sel tumbuhan ini.", "rajah-sel-pokok",
                [(9, 50, "Dinding sel"), (31, 23, "Kloroplas"), (33, 39, "Nukleus"), (65, 57, "Vakuol")],
                why="Sel tumbuhan mempunyai dinding sel, kloroplas dan vakuol yang besar. Kloroplas mengandungi klorofil untuk fotosintesis.",
            )),
            play("unsur", _match(
                "Padankan simbol unsur dengan namanya.",
                [("H", "Hidrogen"), ("O", "Oksigen"), ("C", "Karbon"), ("Fe", "Ferum (besi)")],
                time=60, pic="tabung-uji",
                why="H ialah hidrogen, O oksigen, C karbon, dan Fe ialah ferum (besi), daripada nama Latinnya.",
            )),
            play("alat", _number(
                "Silinder penyukat berisi 250 ml air. Kemudian 150 ml lagi dituang. Laraskan bacaan isi padu air sekarang.", 400, "ml", time=60,
                why="250 ml + 150 ml = 400 ml.",
            )),
        ],
    },
    {
        "title": "Sains Menengah: Makmal Sains",
        "description": "12 permainan sains untuk Tingkatan 1 hingga 5: asid dan alkali, galaksi, organ, rantai makanan laut, sel dan unsur.",
        "questions": [
            play("ramuan", _single(
                "Larutan manakah yang menukarkan kertas litmus biru kepada merah?", "Jus lemon", "Air sabun", "Air suling", "Ubat gigi", time=45,
                stickers={"Jus lemon": "lemon", "Air sabun": "sabun", "Air suling": "air"},
                why="Jus lemon berasid (mengandungi asid sitrik). Asid menukarkan litmus biru kepada merah. Air sabun dan ubat gigi beralkali, air suling neutral.",
            )),
            play("teropong", _single(
                "Sistem Suria kita berada dalam galaksi yang bernama?", "Bima Sakti", "Andromeda", "Awan Magellan Besar", "Sombrero", time=45, pic="bimasakti",
                why="Sistem Suria terletak dalam galaksi Bima Sakti. Andromeda ialah galaksi jiran terbesar kita.",
            )),
            play("orbit", _order(
                "Susun planet ini mengikut jarak dari Matahari.", "Marikh", "Musytari", "Zuhal", "Uranus", "Neptun", time=60, pic="rajah-suria",
                why="Selepas Marikh datang planet gergasi: Musytari, Zuhal, Uranus dan Neptun yang paling jauh.",
            )),
            play("tubuh", _diagram(
                "Labelkan organ-organ ini.", "rajah-organ",
                [(53, 29, "Jantung"), (27, 33, "Paru-paru"), (30, 49, "Hati"), (74, 45, "Perut"), (75, 61, "Ginjal"), (51, 93, "Pundi kencing")],
                time=90,
                why="Jantung mengepam darah, paru-paru untuk pertukaran gas, hati menghasilkan hempedu, perut mencerna, ginjal menapis darah dan pundi kencing menyimpan air kencing.",
            )),
            play("rantai", _order(
                "Susun rantai makanan di laut, dari pengeluar.", "Fitoplankton", "Zooplankton", "Udang", "Ikan", "Jerung", time=75,
                why="Fitoplankton (pengeluar) dimakan zooplankton, kemudian udang, ikan, dan jerung sebagai pemangsa teratas.",
            )),
            play("litar", _single(
                "Bahan bukan logam manakah yang boleh mengalirkan arus elektrik?", "Grafit pensel", "Kaca", "Getah", "Plastik", time=45,
                stickers={"Grafit pensel": "pensel"},
                why="Grafit (karbon dalam mata pensel) ialah bukan logam yang mengalirkan elektrik. Kaca, getah dan plastik ialah penebat.",
            )),
            play("magnet", _sort(
                "Isihkan logam ini: bahan magnet atau bukan?",
                [
                    ("Bahan magnet", "magnet", [("Besi", None), ("Nikel", None), ("Kobalt", None)]),
                    ("Bukan bahan magnet", None, [("Kuprum", None), ("Aluminium", None), ("Emas", "cincin")]),
                ],
                why="Hanya beberapa logam ialah bahan magnet: besi, nikel dan kobalt. Kuprum, aluminium dan emas tidak ditarik oleh magnet.",
            )),
            play("jirim", _sort(
                "Isihkan bahan ini mengikut keadaan jirim pada suhu bilik (25 °C).",
                [
                    ("Pepejal", None, [("Natrium klorida", "garam"), ("Besi", None)]),
                    ("Cecair", None, [("Merkuri", None), ("Air", "air")]),
                    ("Gas", None, [("Nitrogen", None), ("Karbon dioksida", None)]),
                ],
                why="Merkuri ialah satu-satunya logam yang cecair pada suhu bilik. Nitrogen dan karbon dioksida ialah gas, natrium klorida dan besi pepejal.",
            )),
            play("kitaran", _order(
                "Susun fasa bulan, bermula dengan bulan baru.", "Bulan baru", "Bulan sabit", "Bulan separa", "Bulan purnama", time=60, pic="bulan-purnama",
                why="Selepas bulan baru, bahagian yang bercahaya bertambah: bulan sabit, bulan separa (suku pertama), kemudian bulan purnama.",
            )),
            play("mikroskop", _diagram(
                "Labelkan bahagian sel haiwan.", "rajah-sel-haiwan",
                [(37, 39, "Nukleus"), (92, 55, "Membran sel"), (66, 72, "Sitoplasma"), (53, 35, "Mitokondria")],
                why="Nukleus mengawal sel, membran sel mengawal bahan keluar masuk, sitoplasma tempat tindak balas berlaku, dan mitokondria menghasilkan tenaga.",
            )),
            play("unsur", _match(
                "Padankan simbol unsur dengan nama Melayunya.",
                [("Na", "Natrium"), ("K", "Kalium"), ("Cu", "Kuprum"), ("Ag", "Argentum"), ("Fe", "Ferum")],
                time=75, pic="kelalang",
                why="Simbol-simbol ini datang daripada nama Latin: Na natrium, K kalium, Cu kuprum, Ag argentum dan Fe ferum.",
            )),
            play("alat", _number(
                "Laraskan termometer kepada suhu ais tulen yang sedang melebur.", 0, "°C", time=45, pic="ais",
                why="Ais tulen melebur pada 0 °C. Takat lebur ais sama dengan takat beku air.",
            )),
        ],
    },
    # ------------------------------------------------------------------ Sejarah
    {
        "title": "Sejarah Tahap 1: Kenali Negaraku",
        "description": "12 permainan sejarah untuk Tahun 1 hingga 3: Jalur Gemilang, peta Malaysia, artifak lama dan hari kemerdekaan.",
        "questions": [
            play("gali", _single(
                "Benda lama apakah yang digunakan untuk menyimpan air?", "Tempayan", "Keris", "Syiling", "Cincin", time=60,
                stickers={"Tempayan": "tempayan", "Keris": "keris", "Syiling": "syiling", "Cincin": "cincin"},
                why="Tempayan ialah bekas besar daripada tanah liat untuk menyimpan air, digunakan sejak zaman dahulu.",
            )),
            play("empayar", _order(
                "Susun kehidupan manusia dahulu kala, dari yang paling awal.", "Tinggal di gua", "Bercucuk tanam dan berkampung", "Membina kerajaan", time=60,
                why="Manusia awal tinggal di gua, kemudian bercucuk tanam dan membina kampung, dan akhirnya membina kerajaan seperti Melaka.",
            )),
            play("garismasa", _order(
                "Susun peristiwa ini, yang paling awal dahulu.", "Kesultanan Melayu Melaka (sekitar 1400)", "Tanah Melayu merdeka (1957)", "Malaysia ditubuhkan (1963)", time=60,
                why="Kesultanan Melaka bermula sekitar tahun 1400, Tanah Melayu merdeka pada 1957, dan Malaysia ditubuhkan pada 1963.",
            )),
            play("peta", _diagram(
                "Pacakkan nama pada peta Malaysia.", "rajah-malaysia", [(14, 50, "Semenanjung Malaysia"), (64, 79, "Sarawak"), (88, 32, "Sabah")],
                why="Malaysia terdiri daripada Semenanjung Malaysia, serta Sabah dan Sarawak di Pulau Borneo.",
            )),
            play("muzium", _sort(
                "Susun benda dalam almari muzium: dahulu atau sekarang?",
                [
                    ("Dahulu", "kunci-lama", [("Pelita", "lilin"), ("Kereta lembu", "lembu"), ("Surat", "surat")]),
                    ("Sekarang", None, [("Lampu elektrik", "mentol"), ("Kereta", "kereta"), ("Telefon pintar", None)]),
                ],
                why="Dahulu orang menggunakan pelita, kereta lembu dan surat. Sekarang kita menggunakan lampu elektrik, kereta dan telefon pintar.",
            )),
            play("skrol", _blank(
                "Lengkapkan tulisan pada skrol.", "Bendera Malaysia ialah [Jalur Gemilang] dan bunga kebangsaan ialah bunga [raya].", "Sang Saka", "mawar",
                pic="rajah-jalur",
                why="Bendera Malaysia dinamakan Jalur Gemilang, dan bunga kebangsaan kita ialah bunga raya.",
            )),
            play("pelabuhan", _match(
                "Kapal belayar ke ibu negeri. Padankan negeri dengan ibu negerinya.",
                [("Kedah", "Alor Setar"), ("Johor", "Johor Bahru"), ("Sarawak", "Kuching")],
                time=60,
                why="Ibu negeri Kedah ialah Alor Setar, Johor ialah Johor Bahru, dan Sarawak ialah Kuching.",
            )),
            play("siapa", _single(
                "Siapakah Perdana Menteri Malaysia yang pertama?", "Tunku Abdul Rahman", "Tun Abdul Razak", "Tun Hussein Onn", "Tun Dr. Mahathir Mohamad", time=45,
                why="Tunku Abdul Rahman Putra Al-Haj ialah Perdana Menteri pertama dan dikenali sebagai Bapa Kemerdekaan.",
            )),
            play("istana", _order(
                "Susun kawasan pentadbiran ini, dari yang paling besar.", "Negara", "Negeri", "Daerah", "Kampung", time=60,
                why="Sebuah negara dibahagikan kepada negeri, negeri kepada daerah, dan daerah mempunyai banyak kampung.",
            )),
            play("arkib", _tf(
                "Hari Kebangsaan Malaysia disambut pada 31 Ogos setiap tahun.", True, time=30, pic="kalendar",
                why="Betul. Tanah Melayu mencapai kemerdekaan pada 31 Ogos 1957, jadi Hari Kebangsaan disambut pada 31 Ogos.",
            )),
            play("mesinmasa", _number(
                "Pada tahun berapakah Tanah Melayu mencapai kemerdekaan?", 1957, "", time=45,
                why="Tanah Melayu merdeka pada 31 Ogos 1957.",
            )),
            play("mesintaip", _text(
                "Taip nama ibu negara Malaysia.", "Kuala Lumpur", time=45, pic="bangunan",
                why="Ibu negara Malaysia ialah Kuala Lumpur. Putrajaya pula ialah pusat pentadbiran kerajaan.",
            )),
        ],
    },
    {
        "title": "Sejarah Tahap 2: Kesultanan dan Kemerdekaan",
        "description": "12 permainan sejarah untuk Tahun 4 hingga 6: zaman prasejarah, Kesultanan Melayu Melaka, penjajahan dan Rukun Negara.",
        "questions": [
            play("gali", _single(
                "Tapak prasejarah manakah di Sarawak yang menemui tengkorak manusia berusia kira-kira 40 000 tahun?",
                "Gua Niah", "Gua Cha", "Lembah Lenggong", "Bukit Tengkorak", time=60, pic="rajah-gua-niah",
                why="Gua Niah di Sarawak. Lembah Lenggong di Perak, Gua Cha di Kelantan dan Bukit Tengkorak di Sabah juga tapak prasejarah yang penting.",
            )),
            play("empayar", _order(
                "Bina empayar Melaka: susun peristiwa dari yang terawal.",
                "Parameswara membuka Melaka", "Laksamana Cheng Ho singgah di Melaka", "Zaman pemerintahan Sultan Mansur Syah", "Portugis menawan Melaka",
                time=75,
                why="Parameswara membuka Melaka sekitar 1400. Cheng Ho singgah pada awal abad ke-15. Melaka gemilang semasa Sultan Mansur Syah, dan jatuh ke tangan Portugis pada 1511.",
            )),
            play("garismasa", _order(
                "Susun peristiwa ini mengikut tahun.",
                "Portugis menawan Melaka (1511)", "Belanda menawan Melaka (1641)", "Perjanjian Inggeris-Belanda (1824)", "Perjanjian Pangkor (1874)",
                time=75,
                why="1511 Portugis, 1641 Belanda, 1824 Perjanjian Inggeris-Belanda, dan 1874 Perjanjian Pangkor.",
            )),
            play("peta", _diagram(
                "Pacakkan nama negeri pada peta Semenanjung.", "rajah-semenanjung",
                [(22, 25, "Kedah"), (28, 44, "Perak"), (46, 32, "Kelantan"), (55, 57, "Pahang"), (73, 81, "Johor")],
                why="Kedah di utara barat, Kelantan di timur laut, Perak di barat, Pahang di tengah, dan Johor di hujung selatan.",
            )),
            play("muzium", _sort(
                "Pamerkan artifak dalam almari zaman yang betul.",
                [
                    ("Zaman Prasejarah", "beliung", [("Kapak batu", "batu-kecil"), ("Tembikar tanah", "tempayan"), ("Tulang manusia purba", "tulang")]),
                    ("Kesultanan Melaka", "mahkota", [("Keris", "keris"), ("Mata wang timah", "syiling"), ("Mahkota", "mahkota")]),
                ],
                why="Manusia prasejarah menggunakan alat batu dan tembikar. Kesultanan Melaka mempunyai keris, mata wang timah dan alat kebesaran diraja.",
            )),
            play("skrol", _blank(
                "Lengkapkan tulisan pada skrol.",
                "Rukun Negara diisytiharkan pada 31 Ogos [1970]. Prinsip pertamanya ialah [Kepercayaan kepada Tuhan].",
                "1957", "Keluhuran Perlembagaan",
                why="Rukun Negara diisytiharkan pada 31 Ogos 1970. Lima prinsipnya bermula dengan Kepercayaan kepada Tuhan.",
            )),
            play("pelabuhan", _match(
                "Padankan pedagang dengan barang yang dibawa ke Melaka.",
                [("Pedagang China", "Sutera dan tembikar"), ("Pedagang India", "Kain"), ("Pedagang Arab", "Minyak wangi")],
                time=60, pic="perahu-layar",
                why="Melaka menjadi pelabuhan entrepot: pedagang China membawa sutera dan tembikar, India membawa kain, Arab membawa minyak wangi.",
            )),
            play("siapa", _single(
                "Saya laksamana Melaka yang terkenal dengan kata-kata \"Takkan Melayu hilang di dunia\". Siapakah saya?",
                "Hang Tuah", "Hang Jebat", "Tun Perak", "Hang Kasturi", time=45,
                why="Kata-kata itu dikaitkan dengan Hang Tuah, laksamana Melaka yang terkenal dalam Hikayat Hang Tuah.",
            )),
            play("istana", _order(
                "Susun pembesar Kesultanan Melayu Melaka dari yang tertinggi.", "Bendahara", "Penghulu Bendahari", "Temenggung", "Laksamana", time=60,
                why="Selepas Sultan, Bendahara paling tinggi, diikuti Penghulu Bendahari, Temenggung dan Laksamana.",
            )),
            play("arkib", _tf(
                "Tunku Abdul Rahman mengisytiharkan kemerdekaan di Stadium Merdeka, Kuala Lumpur.", True, time=30, pic="akhbar",
                why="Betul. Pada 31 Ogos 1957, Tunku Abdul Rahman melaungkan \"Merdeka!\" di Stadium Merdeka.",
            )),
            play("mesinmasa", _number(
                "Pada tahun berapakah Perjanjian Pangkor ditandatangani?", 1874, "", time=45,
                why="Perjanjian Pangkor ditandatangani pada tahun 1874 dan memperkenalkan Sistem Residen di Perak.",
            )),
            play("mesintaip", _text(
                "Taip nama pengasas Kesultanan Melayu Melaka.", "Parameswara", time=45, pic="mahkota",
                why="Parameswara, seorang putera dari Palembang, membuka Melaka sekitar tahun 1400.",
            )),
        ],
    },
    {
        "title": "Sejarah Menengah: Ke Arah Malaysia",
        "description": "12 permainan sejarah untuk Tingkatan 1 hingga 5: Lembah Bujang, kerajaan Alam Melayu, Negeri-negeri Selat, nasionalisme dan Malaysia.",
        "questions": [
            play("gali", _single(
                "Tapak arkeologi di Kedah yang mempunyai candi dan dikaitkan dengan kerajaan Kedah Tua ialah?",
                "Lembah Bujang", "Gua Niah", "Kota Gelanggi", "Lembah Lenggong", time=60, pic="rajah-lembah-bujang",
                why="Lembah Bujang di Kedah ialah tapak arkeologi dengan banyak candi, bukti kerajaan Kedah Tua yang maju dalam perdagangan.",
            )),
            play("empayar", _order(
                "Susun kerajaan Alam Melayu ini mengikut zaman kegemilangannya, yang terawal dahulu.", "Funan", "Srivijaya", "Majapahit", "Melaka", time=75,
                why="Funan gemilang sekitar abad pertama hingga keenam, Srivijaya abad ketujuh hingga ketiga belas, Majapahit selepasnya, dan Melaka pada abad kelima belas.",
            )),
            play("garismasa", _order(
                "Susun peristiwa ke arah kemerdekaan.",
                "Malayan Union (1946)", "Persekutuan Tanah Melayu (1948)", "Pilihan raya umum pertama (1955)", "Kemerdekaan (1957)",
                time=75,
                why="Malayan Union 1946 ditentang, diganti Persekutuan Tanah Melayu 1948. Pilihan raya umum pertama 1955, dan merdeka pada 1957.",
            )),
            play("peta", _diagram(
                "Negeri-negeri Melayu Bersekutu (1895). Pacakkan nama negeri anggotanya.", "rajah-semenanjung",
                [(28, 44, "Perak"), (35, 61, "Selangor"), (51, 70, "Negeri Sembilan"), (55, 57, "Pahang")],
                why="Negeri-negeri Melayu Bersekutu dibentuk pada 1895 oleh Perak, Selangor, Negeri Sembilan dan Pahang.",
            )),
            play("muzium", _sort(
                "Isihkan peninggalan ini mengikut kuasa penjajah.",
                [
                    ("Portugis", None, [("Kota A Famosa", "kota"), ("Gereja St. Paul", None)]),
                    ("Belanda", None, [("Bangunan Stadthuys", "dewan-klasik")]),
                    ("British", None, [("Sistem Residen", "akhbar"), ("Perjanjian Pangkor", "surat")]),
                ],
                pic="rajah-afamosa",
                why="Portugis membina Kota A Famosa dan Gereja St. Paul, Belanda membina Stadthuys, dan British memperkenalkan Sistem Residen melalui Perjanjian Pangkor.",
            )),
            play("skrol", _blank(
                "Lengkapkan tulisan pada skrol Perlembagaan.",
                "Perlembagaan Persekutuan menetapkan [Islam] sebagai agama bagi Persekutuan dan bahasa [Melayu] sebagai bahasa kebangsaan.",
                "Inggeris", "Jawi",
                why="Perkara 3 Perlembagaan Persekutuan menetapkan Islam sebagai agama bagi Persekutuan, dan Perkara 152 menetapkan bahasa Melayu sebagai bahasa kebangsaan.",
            )),
            play("pelabuhan", _match(
                "Negeri-negeri Selat: padankan pelabuhan dengan bagaimana British memperolehnya.",
                [("Pulau Pinang", "Francis Light (1786)"), ("Singapura", "Stamford Raffles (1819)"), ("Melaka", "Perjanjian Inggeris-Belanda (1824)")],
                time=75,
                why="Francis Light menduduki Pulau Pinang pada 1786, Raffles membuka Singapura pada 1819, dan Melaka diserahkan kepada British melalui Perjanjian Inggeris-Belanda 1824.",
            )),
            play("siapa", _single(
                "Saya memimpin penentangan terhadap Malayan Union dan menjadi Presiden UMNO yang pertama. Siapakah saya?",
                "Dato' Onn Jaafar", "Tunku Abdul Rahman", "Tun Tan Cheng Lock", "Tun V. T. Sambanthan", time=45,
                why="Dato' Onn Jaafar mengetuai penentangan terhadap Malayan Union dan menjadi Presiden UMNO pertama pada 1946.",
            )),
            play("istana", _order(
                "Susun Perdana Menteri Malaysia dari yang pertama.", "Tunku Abdul Rahman", "Tun Abdul Razak", "Tun Hussein Onn", "Tun Dr. Mahathir Mohamad", time=60,
                why="Tunku Abdul Rahman yang pertama, diikuti Tun Abdul Razak, Tun Hussein Onn dan Tun Dr. Mahathir Mohamad.",
            )),
            play("arkib", _tf(
                "Malayan Union diperkenalkan oleh British pada tahun 1946.", True, time=30, pic="akhbar",
                why="Betul. Malayan Union diisytiharkan pada 1 April 1946 dan ditentang kuat oleh orang Melayu.",
            )),
            play("mesinmasa", _number(
                "Pada tahun berapakah Malaysia dibentuk?", 1963, "", time=45,
                why="Malaysia dibentuk pada 16 September 1963 oleh Persekutuan Tanah Melayu, Sabah, Sarawak dan Singapura.",
            )),
            play("mesintaip", _text(
                "Taip nama perjanjian tahun 1874 yang memperkenalkan Sistem Residen di Perak.", "Perjanjian Pangkor", "Pangkor", time=45,
                why="Perjanjian Pangkor 1874 membawa Residen British ke Perak.",
            )),
        ],
    },
    # ------------------------------------------------------------------ Pendidikan Islam
    {
        "title": "Pendidikan Islam Tahap 1: Anak Soleh",
        "description": "12 permainan Pendidikan Islam untuk Tahun 1 hingga 3: huruf hijaiyah, wuduk, solat, rukun iman dan sirah.",
        "questions": [
            play("tajwid", _sort(
                "Warnakan huruf: titiknya di atas atau di bawah?",
                [
                    ("Titik di atas", None, [("ت", None), ("ث", None), ("خ", None)]),
                    ("Titik di bawah", None, [("ب", None), ("ج", None), ("ي", None)]),
                ],
                why="Ta (ت), Tsa (ث) dan Kha (خ) bertitik di atas. Ba (ب), Jim (ج) dan Ya (ي) bertitik di bawah.",
            )),
            play("hijaiyah", _single(
                "Yang manakah huruf Ba?", "ب", "ت", "ث", "ن", time=30,
                why="Ba (ب) mempunyai satu titik di bawah. Ta dua titik di atas, Tsa tiga titik di atas, Nun satu titik di atas.",
            )),
            play("wuduk", _order(
                "Susun rukun wuduk mengikut tertib.",
                "Niat dan basuh muka", "Basuh kedua-dua tangan hingga siku", "Sapu sebahagian kepala", "Basuh kedua-dua kaki hingga buku lali",
                time=60,
                why="Rukun wuduk: niat, membasuh muka, membasuh tangan hingga siku, menyapu sebahagian kepala, membasuh kaki hingga buku lali, dan tertib.",
            )),
            play("solat", _order(
                "Susun gerakan solat ini.", "Takbiratul ihram", "Rukuk", "Sujud", "Salam", time=60,
                why="Solat bermula dengan takbiratul ihram, kemudian rukuk, sujud, dan diakhiri dengan salam.",
            )),
            play("kiblat", _single(
                "Dari Malaysia, ke arah manakah kita menghadap ketika solat?", "Barat laut", "Timur", "Selatan", "Timur laut", time=45, pic="rajah-kaabah",
                why="Kita menghadap kiblat, iaitu Kaabah di Makkah. Dari Malaysia, Kaabah terletak di sebelah barat laut.",
            )),
            play("waktu", _match(
                "Padankan solat dengan bilangan rakaatnya.", [("Subuh", "2 rakaat"), ("Zohor", "4 rakaat"), ("Maghrib", "3 rakaat")], time=60,
                why="Subuh 2 rakaat, Zohor 4 rakaat, Asar 4 rakaat, Maghrib 3 rakaat dan Isyak 4 rakaat.",
            )),
            play("rukun", _multiple(
                "Dirikan TIGA tiang rukun iman.", ["Beriman kepada Allah", "Beriman kepada malaikat", "Beriman kepada kitab"], ["Menunaikan solat", "Berpuasa"], time=60,
                why="Rukun iman ada enam: beriman kepada Allah, malaikat, kitab, rasul, hari akhirat, serta qada dan qadar. Solat dan puasa ialah rukun Islam.",
            )),
            play("timbangan", _sort(
                "Letakkan perbuatan di piring neraca yang betul.",
                [
                    ("Berpahala", None, [("Menolong kawan", "berjabat"), ("Bercakap benar", None), ("Memberi salam", None)]),
                    ("Berdosa", None, [("Menipu", None), ("Mengejek kawan", None), ("Membazir makanan", "nasi")]),
                ],
                why="Menolong kawan, bercakap benar dan memberi salam ialah amalan baik. Menipu, mengejek dan membazir ialah perbuatan yang dilarang.",
            )),
            play("hijrah", _order(
                "Susun perjalanan hijrah Nabi Muhammad SAW.", "Makkah", "Gua Thur", "Madinah", time=45,
                why="Nabi Muhammad SAW berhijrah dari Makkah, bersembunyi di Gua Thur, kemudian tiba di Madinah.",
            )),
            play("malaikat", _match(
                "Nyalakan lentera: padankan malaikat dengan tugasnya.",
                [("Jibril", "Menyampaikan wahyu"), ("Mikail", "Menurunkan hujan"), ("Israfil", "Meniup sangkakala")],
                time=60,
                why="Jibril menyampaikan wahyu, Mikail menurunkan hujan dan rezeki, Israfil meniup sangkakala.",
            )),
            play("zakat", _money(
                "Ayah membayar zakat fitrah untuk adik sebanyak RM7. Bayar dengan tepat.", 700, "beg-wang", time=60,
                why="Zakat fitrah dibayar pada bulan Ramadan. Kadarnya ditetapkan oleh setiap negeri, contohnya RM7 seorang.",
            )),
            play("kafilah", _tf(
                "Nabi Muhammad SAW dilahirkan di Makkah.", True, time=30, pic="khemah",
                why="Betul. Nabi Muhammad SAW dilahirkan di Makkah pada Tahun Gajah.",
            )),
        ],
    },
    {
        "title": "Pendidikan Islam Tahap 2: Ibadah dan Sirah",
        "description": "12 permainan Pendidikan Islam untuk Tahun 4 hingga 6: hukum nun sakinah, qalqalah, solat, hukum taklifi dan sirah.",
        "questions": [
            play("tajwid", _sort(
                "Warnakan setiap kalimah mengikut hukum nun sakinah dan tanwin.",
                [
                    ("Izhar Halqi", None, [("مِنْ عِلْمٍ", None), ("مِنْ حَكِيمٍ", None)]),
                    ("Idgham", None, [("مَنْ يَعْمَلْ", None), ("مِنْ رَبِّهِمْ", None)]),
                    ("Iqlab", None, [("مِنْ بَعْدِ", None), ("سَمِيعٌ بَصِيرٌ", None)]),
                ],
                time=90,
                why="Nun sakinah atau tanwin bertemu huruf halqi (ع, ح) ialah Izhar Halqi; bertemu ي atau ر ialah Idgham; bertemu ب ialah Iqlab.",
            )),
            play("hijaiyah", _single(
                "Huruf manakah ialah huruf qalqalah?", "ق", "ف", "ك", "م", time=30,
                why="Huruf qalqalah ada lima: ق ط ب ج د (qaf, tha, ba, jim, dal). Ia dibaca memantul apabila bertanda sukun.",
            )),
            play("wuduk", _order(
                "Susun perkara sunat sebelum membasuh muka ketika berwuduk.",
                "Membaca basmalah", "Membasuh kedua-dua tapak tangan", "Berkumur-kumur", "Memasukkan air ke hidung",
                time=60,
                why="Sunat dimulakan dengan basmalah, membasuh tapak tangan, berkumur-kumur dan memasukkan air ke hidung, sebelum membasuh muka.",
            )),
            play("solat", _order(
                "Susun gerakan dalam satu rakaat solat.", "Takbiratul ihram", "Rukuk", "Iktidal", "Sujud", "Duduk antara dua sujud", time=75,
                why="Selepas takbiratul ihram dan membaca al-Fatihah: rukuk, iktidal, sujud, duduk antara dua sujud, kemudian sujud kali kedua.",
            )),
            play("kiblat", _single(
                "Apakah yang dijadikan kiblat oleh umat Islam ketika solat?", "Kaabah", "Masjid Nabawi", "Masjidil Aqsa", "Gua Hira", time=45, pic="kaabah",
                why="Umat Islam menghadap Kaabah di Masjidil Haram, Makkah, ketika solat.",
            )),
            play("waktu", _match(
                "Padankan solat fardu dengan permulaan waktunya.",
                [
                    ("Subuh", "Terbit fajar sadiq"),
                    ("Zohor", "Matahari tergelincir"),
                    ("Asar", "Bayang-bayang sama panjang dengan objek"),
                    ("Maghrib", "Matahari terbenam"),
                    ("Isyak", "Hilang mega merah"),
                ],
                time=90,
                why="Subuh bermula fajar sadiq, Zohor apabila matahari tergelincir, Asar apabila bayang-bayang sama panjang, Maghrib apabila matahari terbenam, dan Isyak apabila hilang mega merah.",
            )),
            play("rukun", _multiple(
                "Dirikan SEMUA tiang rukun Islam.",
                ["Mengucap dua kalimah syahadah", "Menunaikan solat", "Mengeluarkan zakat", "Berpuasa pada bulan Ramadan", "Menunaikan haji"],
                ["Beriman kepada rasul"], time=75,
                why="Rukun Islam ada lima: syahadah, solat, zakat, puasa Ramadan dan haji bagi yang mampu. Beriman kepada rasul ialah rukun iman.",
            )),
            play("timbangan", _sort(
                "Letakkan setiap perbuatan di piring hukumnya.",
                [
                    ("Wajib", None, [("Solat lima waktu", None), ("Puasa Ramadan", None)]),
                    ("Sunat", None, [("Solat dhuha", None), ("Bersedekah", "beg-wang")]),
                    ("Haram", None, [("Mencuri", None), ("Minum arak", None)]),
                ],
                time=75,
                why="Solat lima waktu dan puasa Ramadan wajib, solat dhuha dan sedekah sunat, manakala mencuri dan minum arak haram.",
            )),
            play("hijrah", _order(
                "Susun perjalanan hijrah Nabi Muhammad SAW.", "Makkah", "Gua Thur", "Quba", "Madinah", time=60, pic="unta",
                why="Baginda bersembunyi di Gua Thur, singgah di Quba dan membina Masjid Quba, kemudian tiba di Madinah.",
            )),
            play("malaikat", _match(
                "Nyalakan lentera: padankan malaikat dengan tugasnya.",
                [("Raqib", "Mencatat amalan baik"), ("Atid", "Mencatat amalan buruk"), ("Munkar dan Nakir", "Menyoal di alam kubur"), ("Ridwan", "Menjaga syurga")],
                time=75,
                why="Raqib mencatat amalan baik, Atid mencatat amalan buruk, Munkar dan Nakir menyoal di alam kubur, dan Ridwan menjaga syurga.",
            )),
            play("zakat", _money(
                "Zakat fitrah ialah RM7 seorang. Bayar zakat untuk 3 orang ahli keluarga.", 2100, "beg-wang", time=75,
                why="RM7 × 3 orang = RM21.",
            )),
            play("kafilah", _single(
                "Pada usia berapakah Nabi Muhammad SAW menerima wahyu pertama?", "40 tahun", "25 tahun", "53 tahun", "63 tahun", time=45,
                why="Wahyu pertama diturunkan di Gua Hira ketika baginda berusia 40 tahun. Baginda berkahwin pada usia 25, berhijrah pada 53 dan wafat pada 63 tahun.",
            )),
        ],
    },
    {
        "title": "Pendidikan Islam Menengah: Fiqh, Tajwid dan Sirah",
        "description": "12 permainan Pendidikan Islam untuk Tingkatan 1 hingga 5: hukum mim sakinah, qalqalah kubra, fardu ain dan kifayah, puasa, zakat dan sirah.",
        "questions": [
            play("tajwid", _sort(
                "Warnakan setiap kalimah mengikut hukum mim sakinah.",
                [
                    ("Ikhfa' Syafawi", None, [("تَرْمِيهِمْ بِحِجَارَةٍ", None), ("وَهُمْ بِالْآخِرَةِ", None)]),
                    ("Idgham Mithlain", None, [("لَهُمْ مَا", None), ("كَمْ مِنْ", None)]),
                    ("Izhar Syafawi", None, [("أَمْ لَمْ", None), ("عَلَيْهِمْ وَلَا", None)]),
                ],
                time=90,
                why="Mim sakinah bertemu ب ialah Ikhfa' Syafawi, bertemu م ialah Idgham Mithlain, dan bertemu huruf lain ialah Izhar Syafawi.",
            )),
            play("hijaiyah", _single(
                "Kalimah manakah dibaca dengan qalqalah kubra apabila diwaqafkan?", "أَحَدْ", "الرَّحِيمْ", "النَّاسْ", "الْعَالَمِينْ", time=45,
                why="Qalqalah kubra berlaku apabila huruf qalqalah (ق ط ب ج د) berada di hujung kalimah yang diwaqafkan, seperti dal dalam أَحَدْ.",
            )),
            play("wuduk", _order(
                "Susun anggota wuduk ini mengikut tertib, termasuk perkara sunat.",
                "Membasuh muka", "Membasuh tangan hingga siku", "Menyapu sebahagian kepala", "Menyapu kedua-dua telinga", "Membasuh kaki hingga buku lali",
                time=75,
                why="Selepas menyapu kepala, disunatkan menyapu kedua-dua telinga, kemudian membasuh kaki hingga buku lali.",
            )),
            play("solat", _order(
                "Susun gerakan pada rakaat terakhir solat.",
                "Iktidal", "Sujud pertama", "Duduk antara dua sujud", "Sujud kedua", "Duduk tahiyat akhir", "Salam",
                time=90,
                why="Selepas iktidal: sujud, duduk antara dua sujud, sujud kali kedua, duduk tahiyat akhir, dan memberi salam.",
            )),
            play("kiblat", _single(
                "Arah kiblat bertukar dari Baitul Maqdis ke Kaabah pada tahun ke berapa Hijrah?", "Tahun ke-2 Hijrah", "Tahun ke-1 Hijrah", "Tahun ke-5 Hijrah", "Tahun ke-8 Hijrah",
                time=45, pic="kaabah",
                why="Pertukaran kiblat berlaku pada tahun ke-2 Hijrah, kira-kira 16 hingga 17 bulan selepas hijrah ke Madinah.",
            )),
            play("waktu", _match(
                "Padankan solat sunat dengan waktunya.",
                [("Dhuha", "Pagi, selepas matahari naik"), ("Tahajud", "Malam, selepas bangun tidur"), ("Witir", "Selepas Isyak hingga sebelum Subuh")],
                time=75,
                why="Solat dhuha pada waktu pagi, tahajud pada waktu malam selepas tidur, dan witir antara Isyak hingga sebelum Subuh.",
            )),
            play("rukun", _multiple(
                "Dirikan tiang perkara yang MEMBATALKAN puasa.",
                ["Makan dan minum dengan sengaja", "Muntah dengan sengaja", "Keluar darah haid"],
                ["Bersugi", "Mandi", "Tidur"], time=75,
                why="Puasa batal kerana makan dan minum dengan sengaja, muntah dengan sengaja dan haid. Bersugi, mandi dan tidur tidak membatalkan puasa.",
            )),
            play("timbangan", _sort(
                "Letakkan setiap amalan di piring yang betul: fardu ain atau fardu kifayah?",
                [
                    ("Fardu ain", None, [("Solat lima waktu", None), ("Puasa Ramadan", None), ("Menutup aurat", None)]),
                    ("Fardu kifayah", None, [("Solat jenazah", None), ("Memandikan jenazah", None), ("Belajar ilmu perubatan", "stetoskop")]),
                ],
                time=75,
                why="Fardu ain wajib atas setiap individu. Fardu kifayah wajib atas masyarakat: jika sebahagian telah melaksanakannya, gugur kewajipan yang lain.",
            )),
            play("hijrah", _order(
                "Susun peristiwa sirah Nabi Muhammad SAW mengikut masa.",
                "Kelahiran baginda", "Wahyu pertama di Gua Hira", "Hijrah ke Madinah", "Perang Badar", "Pembukaan Kota Makkah",
                time=75,
                why="Baginda lahir pada Tahun Gajah, menerima wahyu pertama pada usia 40 tahun, berhijrah pada 622 Masihi, Perang Badar tahun ke-2 Hijrah dan Fathu Makkah tahun ke-8 Hijrah.",
            )),
            play("malaikat", _match(
                "Nyalakan lentera: padankan kitab dengan rasul yang menerimanya.",
                [("Taurat", "Nabi Musa AS"), ("Zabur", "Nabi Daud AS"), ("Injil", "Nabi Isa AS"), ("Al-Quran", "Nabi Muhammad SAW")],
                time=75, pic="buku-terbuka",
                why="Taurat diturunkan kepada Nabi Musa, Zabur kepada Nabi Daud, Injil kepada Nabi Isa, dan al-Quran kepada Nabi Muhammad SAW.",
            )),
            play("zakat", _money(
                "Kadar zakat harta ialah 2.5%. Jika harta yang wajib dizakatkan bernilai RM4,000, bayar zakatnya.", 10000, "beg-wang", time=90,
                why="2.5% × RM4,000 = RM100. Zakat harta hanya wajib apabila harta mencukupi nisab dan haul.",
            )),
            play("kafilah", _tf(
                "Perang Badar berlaku pada tahun ke-2 Hijrah.", True, time=30, pic="khemah",
                why="Betul. Perang Badar berlaku pada 17 Ramadan tahun ke-2 Hijrah, dan tentera Islam menang walaupun bilangannya kecil.",
            )),
        ],
    },
]
