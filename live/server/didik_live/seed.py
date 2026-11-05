"""A demo parent and sample quizzes, so the app can be tried the moment it starts.

On a public server there is no demo parent (its password is public): the sample quizzes belong to the
library account instead, which has no password at all, so nobody can sign in as it.

The sample quizzes use every question type and suit every game; three are pitched at older students
(Tingkatan 1-5 content), and the last three, for the youngest, are made of the hands-on types. Every
question has a picture and an explanation for a child who gets it wrong.

Sample quizzes owned by the library account (or, locally, the demo parent) are refreshed when this file
changes them, so a server updated to a new version gets the new pictures and explanations too. Copies a
parent has made are theirs and are never touched. Facts were checked; keep them checked when you change them,
because children will believe them.
"""

from __future__ import annotations

import logging

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Quiz, User
from .questions import parse_questions
from .security import hash_password

log = logging.getLogger("didik.seed")

DEMO_EMAIL = "demo@didik.test"
DEMO_PASSWORD = "main-bersama"
# The owner of the sample quizzes on a public server. ".invalid" is never a real address, and "!" is never
# a password hash, so the account can neither sign in nor receive a reset link.
LIBRARY_EMAIL = "kuiz-contoh@didik.invalid"
LIBRARY_NAME = "Perpustakaan DIDIK"
NO_PASSWORD = "!"


def _extra(question: dict, pic: str | None, why: str) -> dict:
    """Every sample question has a picture (a 3D sticker) and an explanation for a child who got it wrong."""
    if pic:
        question["picture"] = pic
    if why:
        question["explain"] = why
    return question


def _single(prompt: str, right: str, *wrong: str, time: int = 20, pic: str | None = None, why: str = "", stickers: dict | None = None) -> dict:
    choices = [{"text": right, "correct": True}] + [{"text": w} for w in wrong]
    for choice in choices:
        if stickers and choice["text"] in stickers:
            choice["sticker"] = stickers[choice["text"]]
    return _extra({"type": "single", "prompt": prompt, "choices": choices, "time_limit": time}, pic, why)


def _multiple(prompt: str, right: list[str], wrong: list[str], time: int = 30, pic: str | None = None, why: str = "") -> dict:
    choices = [{"text": r, "correct": True} for r in right] + [{"text": w} for w in wrong]
    return _extra({"type": "multiple", "prompt": prompt, "choices": choices, "time_limit": time}, pic, why)


def _tf(prompt: str, answer: bool, time: int = 15, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "truefalse", "prompt": prompt, "answer": answer, "time_limit": time}, pic, why)


def _text(prompt: str, *answers: str, time: int = 30, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "text", "prompt": prompt, "answers": list(answers), "time_limit": time}, pic, why)


def _number(prompt: str, answer: float, unit: str = "", time: int = 25, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "number", "prompt": prompt, "answer": answer, "unit": unit, "time_limit": time}, pic, why)


def _order(prompt: str, *items: str, time: int = 40, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "order", "prompt": prompt, "items": [{"text": i} for i in items], "time_limit": time}, pic, why)


def _match(prompt: str, pairs: list[tuple], time: int = 45, pic: str | None = None, why: str = "") -> dict:
    """pairs: (left, right) or (left, right, sticker for the left)"""
    rows = [{"left": p[0], "right": p[1], **({"sticker": p[2]} if len(p) > 2 else {})} for p in pairs]
    return _extra({"type": "match", "prompt": prompt, "pairs": rows, "time_limit": time}, pic, why)


def _blank(prompt: str, sentence: str, *distractors: str, time: int = 30, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "blank", "prompt": prompt, "sentence": sentence, "distractors": list(distractors), "time_limit": time}, pic, why)


def _count(prompt: str, sticker: str, place: str, answer: int, time: int = 45, why: str = "") -> dict:
    return _extra({"type": "count", "prompt": prompt, "sticker": sticker, "place": place, "answer": answer, "time_limit": time}, None, why)


def _spell(prompt: str, word: str, sticker: str | None = None, decoys: int = 0, time: int = 45, why: str = "") -> dict:
    return _extra({"type": "spell", "prompt": prompt, "word": word, "sticker": sticker, "decoys": decoys, "time_limit": time}, None, why)


def _sort(prompt: str, groups: list[tuple[str, str | None, list[tuple[str, str | None]]]], time: int = 60, pic: str | None = None, why: str = "") -> dict:
    """groups: (name, sticker, [(thing, sticker), ...])"""
    return _extra(
        {
            "type": "sort",
            "prompt": prompt,
            "groups": [{"id": f"g{i}", "name": name, "sticker": sticker} for i, (name, sticker, _) in enumerate(groups)],
            "items": [
                {"text": text, "sticker": thing, "group": f"g{i}"} for i, (_, _, things) in enumerate(groups) for text, thing in things
            ],
            "time_limit": time,
        },
        pic,
        why,
    )


def _missing(prompt: str, word: str, hide: list[int], sticker: str | None = None, decoys: int = 2, time: int = 45, why: str = "") -> dict:
    return _extra({"type": "missing", "prompt": prompt, "word": word, "hide": hide, "sticker": sticker, "decoys": decoys, "time_limit": time}, None, why)


def _puzzle(prompt: str, sticker: str, grid: int = 2, time: int = 60, why: str = "") -> dict:
    return _extra({"type": "puzzle", "prompt": prompt, "sticker": sticker, "grid": grid, "time_limit": time}, None, why)


def _blocks(prompt: str, answer: int, time: int = 60, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "blocks", "prompt": prompt, "answer": answer, "time_limit": time}, pic, why)


def _clock(prompt: str, hour: int, minute: int = 0, time: int = 45, pic: str | None = None, why: str = "") -> dict:
    return _extra({"type": "clock", "prompt": prompt, "hour": hour, "minute": minute, "time_limit": time}, pic, why)


def _money(prompt: str, amount: int, sticker: str | None = None, time: int = 60, why: str = "") -> dict:
    return _extra({"type": "money", "prompt": prompt, "amount": amount, "sticker": sticker, "time_limit": time}, None, why)


SAMPLES = [
    {
        "title": "Haiwan di Malaysia",
        "description": "Belalai, belang dan kitaran hidup rama-rama. Sesuai untuk 6 hingga 9 tahun.",
        "questions": [
            _single(
                "Haiwan manakah yang mempunyai belalai?", "Gajah", "Harimau", "Penyu", "Kancil", pic="gajah",
                why="Gajah menggunakan belalainya yang panjang untuk bernafas, menghidu, mengambil makanan dan minum air.",
            ),
            _tf(
                "Penyu bertelur di pantai.", True, pic="penyu",
                why="Penyu betina naik ke pantai, biasanya pada waktu malam, menggali lubang di pasir dan bertelur di situ.",
            ),
            _single(
                "Apakah haiwan kebangsaan Malaysia?", "Harimau Malaya", "Gajah", "Orang utan", "Enggang", pic="harimau",
                why="Harimau Malaya ialah haiwan kebangsaan Malaysia. Dua ekor harimau juga terdapat pada Jata Negara.",
            ),
            _tf(
                "Kelawar ialah sejenis burung.", False, pic="kelawar",
                why="Kelawar boleh terbang, tetapi ia mamalia, bukan burung. Ia melahirkan anak dan anaknya menyusu.",
            ),
            _number(
                "Berapakah bilangan kaki seekor labah-labah?", 8, "kaki", pic="labah-labah",
                why="Labah-labah bukan serangga. Ia mempunyai 8 kaki, manakala serangga seperti semut mempunyai 6 kaki.",
            ),
            _order(
                "Susun kitaran hidup rama-rama.", "Telur", "Ulat", "Kepompong", "Rama-rama", pic="rama-rama",
                why="Telur menetas menjadi ulat. Ulat membentuk kepompong, dan dari kepompong keluar rama-rama.",
            ),
            _match(
                "Padankan haiwan dengan tempat tinggalnya.",
                [("Ikan", "Air", "ikan"), ("Burung", "Sarang", "burung"), ("Arnab", "Lubang", "arnab"), ("Lembu", "Kandang", "lembu")],
                pic="sarang",
                why="Ikan hidup di dalam air, burung membuat sarang, arnab menggali lubang dan lembu dipelihara di kandang.",
            ),
            _text(
                "Haiwan apakah yang berwarna jingga dan berbelang hitam?", "harimau", "harimau malaya", pic="tanda-soal",
                why="Harimau berbulu jingga dengan belang hitam. Belangnya membantu ia bersembunyi di dalam hutan.",
            ),
            _blank(
                "Lengkapkan ayat.", "Sang [Kancil] terkenal dalam cerita rakyat kerana sangat [cerdik/bijak].", "Gajah", "malas", pic="buku",
                why="Sang Kancil ialah watak cerita rakyat Melayu. Badannya kecil tetapi akalnya cerdik.",
            ),
            _multiple(
                "Pilih semua haiwan yang boleh terbang.", ["Enggang", "Kelawar", "Rama-rama"], ["Penyu", "Kucing"], pic="burung",
                why="Enggang, kelawar dan rama-rama mempunyai sayap. Penyu berenang dan kucing berjalan.",
            ),
            _tf(
                "Ikan bernafas menggunakan insang.", True, pic="ikan",
                why="Insang mengambil oksigen yang ada di dalam air. Sebab itu ikan boleh bernafas di dalam air.",
            ),
            _single(
                "Di negeri manakah orang utan liar boleh ditemui?", "Sabah", "Perlis", "Melaka", "Johor", pic="orang-utan",
                why="Di Malaysia, orang utan liar hanya hidup di hutan Borneo, iaitu di Sabah dan Sarawak.",
            ),
        ],
    },
    {
        "title": "Matematik Ceria",
        "description": "Tambah, tolak dan nombor genap untuk Tahun 1 dan 2.",
        "questions": [
            _single("3 + 4 = ?", "7", "6", "8", "9", time=15, pic="abakus", why="Mula dari 3 dan kira 4 lagi: 4, 5, 6, 7. Jadi 3 + 4 = 7."),
            _number("10 − 6 = ?", 4, time=20, pic="nombor", why="Ambil 6 daripada 10, tinggal 4. Semak: 4 + 6 = 10."),
            _tf("5 + 5 = 10", True, time=10, pic="abakus", why="Lima tambah lima ialah sepuluh, sama seperti jari tangan kiri dan tangan kanan."),
            _tf("9 lebih kecil daripada 6.", False, time=12, pic="nombor", why="9 lebih besar daripada 6. Bila membilang, 6 datang dahulu, kemudian 7, 8 dan 9."),
            _order("Susun nombor dari kecil ke besar.", "2", "5", "8", "11", time=30, pic="pembaris", why="Yang paling kecil dahulu: 2, kemudian 5, 8 dan 11."),
            _match(
                "Padankan soalan dengan jawapannya.", [("2 + 2", "4"), ("3 + 3", "6"), ("5 + 3", "8"), ("7 + 2", "9")], pic="abakus",
                why="2 + 2 = 4, 3 + 3 = 6, 5 + 3 = 8 dan 7 + 2 = 9.",
            ),
            _number(
                "Ali ada 12 biji gula-gula. Dia beri 5 biji kepada adik. Berapa biji yang tinggal?", 7, "biji", time=40, pic="gula-gula",
                why="Memberi bermaksud tolak: 12 − 5 = 7. Ali masih ada 7 biji.",
            ),
            _single("Berapakah bilangan sisi sebuah segi tiga?", "3", "4", "5", "6", time=15, pic="sesiku", why="Segi tiga ada 3 sisi dan 3 bucu. Namanya pun ada perkataan 'tiga'."),
            _multiple(
                "Pilih semua nombor genap.", ["2", "4", "10"], ["7", "9"], time=25, pic="nombor",
                why="Nombor genap boleh dibahagi dua sama rata; digit akhirnya 0, 2, 4, 6 atau 8. 7 dan 9 ialah nombor ganjil.",
            ),
            _blank("Lengkapkan ayat.", "Dua puluh tambah tiga ialah [23].", "32", "203", time=25, pic="nombor", why="Dua puluh ialah 20. 20 + 3 = 23, dibaca dua puluh tiga."),
            _text(
                "Tulis nombor yang datang selepas 19.", "20", "dua puluh", time=20, pic="nombor",
                why="Selepas 19 ialah 20. Bila sa sudah 9, tambah satu lagi menjadi satu puluh baharu: 2 puluh, 0 sa.",
            ),
            _single("Seminggu ada berapa hari?", "7", "5", "6", "10", time=15, pic="kalendar", why="Seminggu ada 7 hari: Isnin, Selasa, Rabu, Khamis, Jumaat, Sabtu dan Ahad."),
        ],
    },
    {
        "title": "Bahasa Melayu: Kata dan Ayat",
        "description": "Kata nama, lawan kata dan membina ayat.",
        "questions": [
            _single(
                "Antara berikut, yang manakah kata nama?", "Meja", "Lari", "Cantik", "Makan", pic="huruf",
                why="Kata nama ialah nama benda, orang, haiwan atau tempat. Meja ialah benda. Lari dan makan ialah kata kerja; cantik ialah kata adjektif.",
            ),
            _multiple(
                "Pilih semua buah-buahan.", ["Durian", "Rambutan", "Manggis"], ["Kubis", "Bayam"], pic="mangga",
                why="Durian, rambutan dan manggis ialah buah-buahan. Kubis dan bayam ialah sayur-sayuran.",
            ),
            _match(
                "Padankan perkataan dengan lawannya.", [("Besar", "Kecil"), ("Tinggi", "Rendah"), ("Panas", "Sejuk", "api"), ("Siang", "Malam", "matahari")], pic="huruf",
                why="Lawan kata ialah perkataan yang maknanya bertentangan: besar dan kecil, tinggi dan rendah, panas dan sejuk, siang dan malam.",
            ),
            _blank("Pilih perkataan yang sesuai.", "Adik [minum] susu setiap pagi.", "makan", "tidur", pic="susu", why="Susu ialah minuman, jadi perkataan yang sesuai ialah 'minum'."),
            _blank("Pilih perkataan yang sesuai.", "Ibu memasak di [dapur].", "bilik air", "padang", pic="rumah", why="Memasak dilakukan di dapur, tempat menyediakan makanan di rumah."),
            _order(
                "Susun perkataan menjadi ayat.", "Saya", "suka", "membaca", "buku", pic="buku",
                why="Ayat yang betul: 'Saya suka membaca buku.' Mula dengan siapa, kemudian perbuatan, kemudian apa.",
            ),
            _tf(
                "Perkataan 'kucing' ialah kata kerja.", False, pic="kucing",
                why="'Kucing' ialah kata nama kerana ia nama haiwan. Kata kerja ialah perbuatan, seperti lari atau makan.",
            ),
            _text("Apakah warna daun yang segar?", "hijau", pic="daun", why="Daun yang segar berwarna hijau kerana mengandungi klorofil, yang membantu tumbuhan membuat makanan."),
            _single("Apakah huruf pertama dalam perkataan 'bola'?", "b", "o", "l", "a", time=15, pic="bola", why="Bola dieja B-O-L-A. Huruf pertamanya ialah 'b'."),
            _text("Eja nama buah berduri yang digelar Raja Buah.", "durian", pic="mahkota", why="Durian digelar Raja Buah. Kulitnya berduri tajam dan baunya kuat."),
        ],
    },
    {
        "title": "Sains: Betul atau Salah?",
        "description": "Kenyataan pendek tentang alam. Paling seronok dengan Lompat!.",
        "questions": [
            _tf("Matahari terbit di sebelah timur.", True, pic="matahari", why="Bumi berputar dari barat ke timur, jadi Matahari kelihatan terbit di timur dan terbenam di barat."),
            _tf("Air membeku menjadi ais apabila sangat sejuk.", True, pic="ais", why="Air membeku menjadi ais pada 0 °C. Bila dipanaskan, ais cair semula menjadi air."),
            _tf("Ikan boleh hidup lama di darat tanpa air.", False, pic="ikan", why="Ikan bernafas dengan insang yang memerlukan air. Di darat, ikan tidak dapat bernafas dengan baik."),
            _tf(
                "Tumbuhan memerlukan cahaya matahari untuk membuat makanan.", True, pic="anak-pokok",
                why="Tumbuhan hijau membuat makanan melalui fotosintesis, yang memerlukan cahaya matahari, air dan karbon dioksida.",
            ),
            _tf("Bulan menghasilkan cahayanya sendiri.", False, pic="bulan", why="Bulan tidak bercahaya sendiri. Ia memantulkan cahaya Matahari."),
            _tf("Magnet boleh menarik paku besi.", True, pic="magnet", why="Magnet menarik benda daripada besi dan keluli, seperti paku. Ia tidak menarik kertas, plastik atau kayu."),
            _tf("Kita bernafas menggunakan paru-paru.", True, pic="angin", why="Udara yang kita sedut masuk ke paru-paru. Di situ oksigen masuk ke dalam darah."),
            _tf("Gajah ialah haiwan yang bertelur.", False, pic="gajah", why="Gajah ialah mamalia. Ia melahirkan anak dan anaknya menyusu, bukan menetas daripada telur."),
            _tf("Hujan turun dari awan.", True, pic="hujan", why="Titisan air kecil di dalam awan bergabung menjadi besar dan berat, lalu jatuh sebagai hujan."),
            _tf("Ayam mempunyai empat kaki.", False, pic="ayam", why="Ayam ialah sejenis burung. Ia mempunyai dua kaki dan dua sayap."),
            _single(
                "Apakah yang kita gunakan untuk melihat?", "Mata", "Telinga", "Hidung", time=15, pic="kanta",
                why="Kita melihat dengan mata, mendengar dengan telinga dan menghidu bau dengan hidung.",
            ),
            _single(
                "Ais itu panas atau sejuk?", "Sejuk", "Panas", time=10, pic="ais", stickers={"Sejuk": "salji", "Panas": "api"},
                why="Ais ialah air yang membeku, jadi ia sangat sejuk.",
            ),
        ],
    },
    {
        "title": "Malaysiaku",
        "description": "Bendera, negeri, gunung dan sungai negara kita.",
        "questions": [
            _single(
                "Apakah bunga kebangsaan Malaysia?", "Bunga raya", "Bunga mawar", "Bunga orkid", "Bunga matahari", pic="tulip",
                why="Bunga raya ialah bunga kebangsaan Malaysia. Lima kelopaknya melambangkan lima prinsip Rukun Negara.",
            ),
            _single(
                "Apakah ibu negara Malaysia?", "Kuala Lumpur", "Ipoh", "Johor Bahru", "Kuching", pic="bangunan",
                why="Kuala Lumpur ialah ibu negara Malaysia. Putrajaya pula ialah pusat pentadbiran kerajaan persekutuan.",
            ),
            _number(
                "Berapakah bilangan jalur merah dan putih pada Jalur Gemilang?", 14, "jalur", pic="bulan",
                why="Jalur Gemilang ada 14 jalur merah dan putih. Ia melambangkan 13 negeri dan Kerajaan Persekutuan.",
            ),
            _tf("Gunung Kinabalu terletak di Sabah.", True, pic="gunung", why="Gunung Kinabalu terletak di Sabah. Tingginya kira-kira 4,095 meter."),
            _text(
                "Apakah nama gunung tertinggi di Malaysia?", "Gunung Kinabalu", "Kinabalu", pic="gunung",
                why="Gunung Kinabalu di Sabah ialah gunung tertinggi di Malaysia, kira-kira 4,095 meter tingginya.",
            ),
            _number(
                "Berapakah bilangan negeri di Malaysia?", 13, "negeri", pic="peta",
                why="Malaysia ada 13 negeri dan 3 Wilayah Persekutuan: Kuala Lumpur, Putrajaya dan Labuan.",
            ),
            _match(
                "Padankan negeri dengan ibu negerinya.",
                [("Selangor", "Shah Alam"), ("Kedah", "Alor Setar"), ("Sabah", "Kota Kinabalu"), ("Sarawak", "Kuching")],
                pic="peta",
                why="Ibu negeri Selangor ialah Shah Alam, Kedah ialah Alor Setar, Sabah ialah Kota Kinabalu dan Sarawak ialah Kuching.",
            ),
            _order(
                "Susun hari mengikut urutan.", "Isnin", "Selasa", "Rabu", "Khamis", pic="kalendar",
                why="Hari dalam seminggu: Isnin, Selasa, Rabu, Khamis, Jumaat, Sabtu dan Ahad.",
            ),
            _multiple(
                "Pilih semua warna yang ada pada Jalur Gemilang.", ["Merah", "Putih", "Biru", "Kuning"], ["Hijau", "Ungu"], pic="bintang",
                why="Jalur Gemilang berwarna merah, putih, biru dan kuning. Kuning ialah warna anak bulan dan bintang.",
            ),
            _tf("Sungai Rajang terletak di Sarawak.", True, pic="bot", why="Sungai Rajang di Sarawak ialah sungai terpanjang di Malaysia."),
        ],
    },
    # For older students (Tingkatan 1-5 content); like every sample, they can be played with any game.
    {
        "title": "Sains Tingkatan 1: Sel dan Jirim",
        "description": "Sel, organel, keadaan jirim dan gas adi.",
        "questions": [
            _single(
                "Apakah unit asas bagi semua benda hidup?", "Sel", "Tisu", "Organ", "Atom", pic="mikroskop",
                why="Sel ialah unit asas semua benda hidup. Sel yang sama membentuk tisu, dan tisu membentuk organ.",
            ),
            _single(
                "Organel manakah yang menjalankan respirasi sel?", "Mitokondrion", "Ribosom", "Nukleus", "Vakuol", pic="bateri",
                why="Mitokondrion menjalankan respirasi sel untuk membebaskan tenaga daripada glukosa. Ribosom mensintesis protein dan nukleus mengawal aktiviti sel.",
            ),
            _tf(
                "Sel tumbuhan mempunyai dinding sel, tetapi sel haiwan tidak.", True, pic="anak-pokok",
                why="Sel tumbuhan mempunyai dinding sel yang memberi bentuk tetap. Sel haiwan hanya mempunyai membran sel.",
            ),
            _number(
                "Pada suhu berapakah air tulen mendidih pada tekanan atmosfera biasa?", 100, "°C", pic="termometer",
                why="Pada tekanan atmosfera biasa, air tulen mendidih pada 100 °C dan membeku pada 0 °C.",
            ),
            _text(
                "Apakah nama planet yang paling hampir dengan Matahari?", "Utarid", "Merkuri", pic="matahari",
                why="Utarid (Merkuri) ialah planet paling hampir dengan Matahari, diikuti Zuhrah, Bumi dan Marikh.",
            ),
            _match(
                "Padankan keadaan jirim dengan cirinya.",
                [("Pepejal", "Bentuk tetap", "batu"), ("Cecair", "Ikut bentuk bekas", "air"), ("Gas", "Memenuhi seluruh ruang", "belon")],
                pic="tabung-uji",
                why="Pepejal mempunyai bentuk tetap. Cecair mengikut bentuk bekasnya. Gas memenuhi seluruh ruang bekasnya.",
            ),
            _order(
                "Susun aras organisasi hidupan, dari yang paling ringkas.", "Sel", "Tisu", "Organ", "Sistem", pic="dna",
                why="Sel membentuk tisu, tisu membentuk organ, dan beberapa organ bekerjasama sebagai satu sistem.",
            ),
            _multiple(
                "Pilih semua gas adi.", ["Helium", "Neon", "Argon"], ["Oksigen", "Nitrogen"], pic="belon",
                why="Helium, neon dan argon ialah gas adi (Kumpulan 18) yang sangat tidak reaktif. Oksigen dan nitrogen bukan gas adi.",
            ),
            _tf(
                "Bunyi boleh merambat melalui vakum.", False, pic="loceng",
                why="Bunyi memerlukan medium (pepejal, cecair atau gas) untuk merambat. Vakum tidak mempunyai zarah, jadi bunyi tidak dapat merambat.",
            ),
            _blank(
                "Lengkapkan ayat.", "Tumbuhan hijau membuat makanan melalui proses [fotosintesis].", "respirasi", "transpirasi", pic="daun",
                why="Dalam fotosintesis, tumbuhan menggunakan cahaya, air dan karbon dioksida untuk menghasilkan glukosa dan oksigen.",
            ),
        ],
    },
    {
        "title": "Matematik Tingkatan 1-2: Nombor dan Algebra",
        "description": "Kuasa dua, peratus, persamaan linear, nombor perdana dan pecahan.",
        "questions": [
            _single("Berapakah nilai 3² + 4²?", "25", "49", "14", "7", pic="sesiku", why="3² = 3 × 3 = 9 dan 4² = 4 × 4 = 16. Jadi 9 + 16 = 25."),
            _number("Selesaikan 2x + 5 = 17. Berapakah nilai x?", 6, pic="huruf", why="Tolak 5 daripada kedua-dua belah: 2x = 12. Bahagi dengan 2: x = 6."),
            _single("Berapakah 15% daripada 200?", "30", "15", "20", "45", pic="beg-duit", why="15% daripada 200 = 15/100 × 200 = 30."),
            _tf(
                "Semua nombor perdana ialah nombor ganjil.", False, pic="nombor",
                why="2 ialah nombor perdana yang genap kerana faktornya hanya 1 dan 2. Semua nombor perdana yang lain ialah ganjil.",
            ),
            _number(
                "Berapakah hasil tambah sudut pedalaman sebuah segi tiga?", 180, "darjah", pic="sesiku",
                why="Tiga sudut pedalaman mana-mana segi tiga sentiasa berjumlah 180°.",
            ),
            _order(
                "Susun nombor ini dari yang terkecil.", "-5", "-2", "0", "3", pic="pembaris",
                why="Pada garis nombor, nombor negatif berada di kiri sifar: −5, kemudian −2, 0 dan 3.",
            ),
            _match(
                "Padankan pecahan dengan nombor perpuluhannya.", [("1/2", "0.5"), ("1/4", "0.25"), ("3/4", "0.75"), ("1/5", "0.2")], pic="kek",
                why="Bahagikan pengangka dengan penyebut: 1 ÷ 2 = 0.5, 1 ÷ 4 = 0.25, 3 ÷ 4 = 0.75 dan 1 ÷ 5 = 0.2.",
            ),
            _multiple(
                "Pilih semua nombor perdana.", ["2", "3", "7", "11"], ["9", "15"], pic="nombor",
                why="Nombor perdana hanya ada dua faktor: 1 dan dirinya sendiri. 9 = 3 × 3 dan 15 = 3 × 5, jadi kedua-duanya bukan perdana.",
            ),
            _text(
                "Apakah nama poligon yang mempunyai lapan sisi?", "Oktagon", "Segi lapan", pic="tanda-soal",
                why="Poligon lapan sisi dipanggil oktagon atau segi lapan. Papan tanda BERHENTI berbentuk oktagon.",
            ),
            _blank(
                "Lengkapkan ayat.", "Luas segi empat tepat berukuran 8 cm × 5 cm ialah [40] cm².", "13", "26", pic="pembaris",
                why="Luas segi empat tepat = panjang × lebar = 8 cm × 5 cm = 40 cm².",
            ),
        ],
    },
    {
        "title": "Sejarah Tingkatan 4-5: Merdeka dan Malaysia",
        "description": "Dari Malayan Union hingga pembentukan Malaysia.",
        "questions": [
            _single(
                "Bilakah Persekutuan Tanah Melayu mencapai kemerdekaan?", "31 Ogos 1957", "16 September 1963", "31 Ogos 1963", "16 September 1957",
                pic="kalendar",
                why="Persekutuan Tanah Melayu merdeka pada 31 Ogos 1957. Malaysia pula dibentuk pada 16 September 1963.",
            ),
            _single(
                "Siapakah Perdana Menteri Malaysia yang pertama?", "Tunku Abdul Rahman Putra Al-Haj", "Tun Abdul Razak Hussein", "Tun Hussein Onn",
                "Tun Dr. Mahathir Mohamad", pic="bangunan",
                why="Tunku Abdul Rahman Putra Al-Haj ialah Perdana Menteri pertama (1957 hingga 1970) dan dikenali sebagai Bapa Kemerdekaan.",
            ),
            _tf(
                "Malaysia dibentuk pada 16 September 1963.", True, pic="peta",
                why="Pada 16 September 1963, Persekutuan Tanah Melayu, Sabah, Sarawak dan Singapura bergabung membentuk Malaysia.",
            ),
            _number(
                "Berapakah bilangan negeri dalam Persekutuan Tanah Melayu semasa merdeka pada tahun 1957?", 11, "negeri", pic="peta",
                why="Persekutuan Tanah Melayu terdiri daripada 11 negeri: sembilan negeri Melayu, serta Pulau Pinang dan Melaka.",
            ),
            _order(
                "Susun peristiwa ini mengikut urutan masa.", "Malayan Union diperkenalkan", "Persekutuan Tanah Melayu ditubuhkan",
                "Kemerdekaan Persekutuan Tanah Melayu", "Pembentukan Malaysia", pic="skrol",
                why="Malayan Union (1946), Persekutuan Tanah Melayu (1948), kemerdekaan (1957) dan pembentukan Malaysia (1963).",
            ),
            _text(
                "Apakah nama dokumen yang dibacakan oleh Tunku Abdul Rahman di Stadium Merdeka pada 31 Ogos 1957?",
                "Pemasyhuran Kemerdekaan", "Pengisytiharan Kemerdekaan", pic="skrol",
                why="Tunku Abdul Rahman membacakan Pemasyhuran Kemerdekaan di Stadium Merdeka, lalu melaungkan 'Merdeka!' sebanyak tujuh kali.",
            ),
            _match(
                "Padankan tokoh dengan gelarannya.",
                [("Tunku Abdul Rahman", "Bapa Kemerdekaan"), ("Tun Abdul Razak", "Bapa Pembangunan"), ("Tun Hussein Onn", "Bapa Perpaduan"), ("Tun Dr. Mahathir Mohamad", "Bapa Pemodenan")],
                pic="pingat",
                why="Tunku Abdul Rahman ialah Bapa Kemerdekaan, Tun Abdul Razak Bapa Pembangunan, Tun Hussein Onn Bapa Perpaduan dan Tun Dr. Mahathir Bapa Pemodenan.",
            ),
            _multiple(
                "Pilih wilayah yang bersama Persekutuan Tanah Melayu membentuk Malaysia pada tahun 1963.", ["Sabah", "Sarawak", "Singapura"], ["Brunei"],
                pic="peta",
                why="Sabah, Sarawak dan Singapura menyertai Malaysia pada tahun 1963. Brunei menarik diri dan tidak menyertainya.",
            ),
            _tf(
                "Singapura berpisah daripada Malaysia pada tahun 1965.", True, pic="kalendar",
                why="Singapura berpisah daripada Malaysia pada 9 Ogos 1965 dan menjadi sebuah negara merdeka.",
            ),
            _blank(
                "Lengkapkan ayat.", "Perlembagaan Persekutuan ialah undang-undang [tertinggi] negara.", "terendah", "sementara", pic="skrol",
                why="Perlembagaan Persekutuan ialah undang-undang tertinggi. Undang-undang lain yang bercanggah dengannya terbatal.",
            ),
        ],
    },
    {
        "title": "Jom Kira, Eja dan Isih",
        "description": "Kuiz sentuh dan seret untuk 4 hingga 7 tahun: kira objek, susun huruf dan isih ke bakul. "
        "Paling seronok dengan Kuiz Interaktif.",
        "questions": [
            _count("Masukkan 5 biji epal ke dalam bakul.", "epal", "bakul", 5, why="Kira satu demi satu sambil memasukkan: 1, 2, 3, 4, 5. Berhenti bila sampai 5."),
            _spell("Susun huruf untuk mengeja nama haiwan ini.", "kucing", "kucing", why="Kucing dieja K-U-C-I-N-G. Sebut perlahan-lahan: ku-cing."),
            _sort(
                "Haiwan ini tinggal di darat atau di laut?",
                [
                    ("Darat", "pokok", [("Kucing", "kucing"), ("Lembu", "lembu"), ("Arnab", "arnab")]),
                    ("Laut", "bot", [("Ikan", "ikan"), ("Sotong", "sotong"), ("Paus", "paus")]),
                ],
                pic="bumi",
                why="Kucing, lembu dan arnab hidup di darat. Ikan, sotong dan ikan paus hidup di laut.",
            ),
            _single(
                "Yang manakah sejenis buah?", "Pisang", "Kereta", "Kasut", "Bola", pic="bakul",
                stickers={"Pisang": "pisang", "Kereta": "kereta", "Kasut": "kasut", "Bola": "bola"},
                why="Pisang ialah buah yang boleh dimakan. Kereta, kasut dan bola ialah benda.",
            ),
            _count("Masukkan 8 biji telur ke dalam kotak.", "telur", "kotak", 8, why="Kira perlahan-lahan hingga 8: 1, 2, 3, 4, 5, 6, 7, 8."),
            _spell("Eja nama buah ini.", "pisang", "pisang", decoys=1, why="Pisang dieja P-I-S-A-N-G. Ada dua suku kata: pi-sang."),
            _sort(
                "Kenderaan ini bergerak di udara, di darat atau di air?",
                [
                    ("Udara", "awan", [("Kapal terbang", "kapal-terbang"), ("Helikopter", "helikopter")]),
                    ("Darat", "pokok", [("Kereta", "kereta"), ("Bas", "bas"), ("Basikal", "basikal")]),
                    ("Air", "air", [("Bot", "bot"), ("Kapal", "kapal")]),
                ],
                pic="peta",
                why="Kapal terbang dan helikopter terbang di udara. Kereta, bas dan basikal bergerak di jalan. Bot dan kapal belayar di air.",
            ),
            _count("3 + 2 = ? Letakkan donat sebanyak jawapannya di atas pinggan.", "donat", "pinggan", 5, why="3 + 2 = 5. Letakkan 3 biji, kemudian 2 biji lagi: semuanya 5 biji."),
            _tf("Lebah membuat madu.", True, pic="lebah", why="Lebah mengumpul cecair manis (nektar) daripada bunga dan menukarnya menjadi madu di sarangnya."),
            _spell("Eja perkataan ini.", "BOLA", "bola", decoys=2, why="Bola dieja B-O-L-A."),
            _order(
                "Susun haiwan dari yang paling kecil hingga paling besar.", "Tikus", "Kucing", "Lembu", "Gajah", pic="gajah",
                why="Tikus paling kecil, kemudian kucing, lembu, dan gajah yang paling besar.",
            ),
            _count("Naikkan 6 ekor ayam ke dalam bas.", "ayam", "bas", 6, why="Kira ayam satu demi satu sehingga 6 ekor berada di dalam bas."),
        ],
    },
    {
        "title": "Jom Main Matematik",
        "description": "Nilai tempat, jam, wang dan bentuk untuk Tahun 1 hingga 3, dengan blok, jarum jam dan syiling. "
        "Paling seronok dengan Kuiz Interaktif.",
        "questions": [
            _blocks("Bina nombor 24 dengan blok puluh dan sa.", 24, why="24 = 2 puluh dan 4 sa. Ambil 2 blok puluh dan 4 blok sa."),
            _clock("Laraskan jam kepada pukul 3.00.", 3, 0, pic="jam", why="Pukul 3.00: jarum panjang di angka 12 dan jarum pendek di angka 3."),
            _money("Aiskrim ini berharga RM2.50. Bayar dengan tepat.", 250, "aiskrim", why="RM2.50 = RM1 + RM1 + 50 sen. Dua keping RM1 dan satu syiling 50 sen."),
            _count("3 + 4 = ? Masukkan epal sebanyak jawapannya ke dalam bakul.", "epal", "bakul", 7, why="3 + 4 = 7. Masukkan 3 biji, kemudian 4 biji lagi."),
            _single(
                "Pilih bentuk segi empat sama.", "Segi empat sama", "Bulatan", "Segi tiga", pic="pembaris",
                stickers={"Segi empat sama": "segi-empat", "Bulatan": "bulatan", "Segi tiga": "sesiku"},
                why="Segi empat sama ada 4 sisi yang sama panjang dan 4 bucu. Bulatan tiada bucu, segi tiga ada 3 bucu.",
            ),
            _blocks("Bina nombor 139 dengan blok ratus, puluh dan sa.", 139, why="139 = 1 ratus, 3 puluh dan 9 sa."),
            _clock(
                "Laraskan jam kepada pukul 7.30.", 7, 30, pic="jam",
                why="Pukul 7.30: jarum panjang di angka 6 (30 minit) dan jarum pendek di antara angka 7 dan 8.",
            ),
            _money("Pisang ini berharga 80 sen. Bayar dengan tepat.", 80, "pisang", why="80 sen = 50 sen + 20 sen + 10 sen."),
            _tf(
                "Pada pukul 12.00, jarum panjang dan jarum pendek sama-sama menunjuk angka 12.", True, pic="jam",
                why="Pada pukul 12.00 kedua-dua jarum menunjuk ke atas, ke angka 12.",
            ),
            _money("Buku ini berharga RM6.20. Bayar dengan tepat.", 620, "buku", why="RM6.20 = RM5 + RM1 + 20 sen."),
            _clock(
                "Laraskan jam kepada pukul 10.15.", 10, 15, pic="jam",
                why="Pukul 10.15: jarum panjang di angka 3 (15 minit) dan jarum pendek baru melepasi angka 10.",
            ),
        ],
    },
    {
        "title": "Jom Main Bahasa",
        "description": "Cantum gambar, huruf hilang, susun huruf dan padan gambar untuk 4 hingga 7 tahun. "
        "Paling seronok dengan Kuiz Interaktif.",
        "questions": [
            _puzzle("Cantumkan gambar kucing ini.", "kucing", 2, why="Lihat bahagian gambar: telinga di atas, kaki di bawah. Letakkan setiap kepingan di tempatnya."),
            _missing("Lengkapkan huruf yang hilang.", "ikan", [1], "ikan", why="Ikan dieja I-K-A-N. Huruf yang hilang ialah 'k'."),
            _single(
                "Yang manakah gajah?", "Gajah", "Zirafah", "Singa", "Panda", pic="tanda-soal",
                stickers={"Gajah": "gajah", "Zirafah": "zirafah", "Singa": "singa", "Panda": "panda"},
                why="Gajah besar, berwarna kelabu dan mempunyai belalai yang panjang.",
            ),
            _match(
                "Padankan haiwan dengan bunyinya.",
                [("Kucing", "Mengiau", "kucing"), ("Lembu", "Menguak", "lembu"), ("Ayam", "Berkokok", "ayam"), ("Anjing", "Menyalak", "anjing")],
                pic="loceng",
                why="Kucing mengiau, lembu menguak, ayam berkokok dan anjing menyalak.",
            ),
            _missing("Lengkapkan huruf yang hilang.", "buku", [0, 2], "buku", why="Buku dieja B-U-K-U. Huruf yang hilang ialah 'b' dan 'k'."),
            _spell("Susun huruf untuk mengeja perkataan ini.", "rumah", "rumah", decoys=1, why="Rumah dieja R-U-M-A-H. Sebut perlahan-lahan: ru-mah."),
            _puzzle("Cantumkan gambar roket ini (9 keping).", "roket", 3, why="Mula dengan kepingan di bucu, kemudian bahagian tepi, dan akhir sekali bahagian tengah."),
            _missing("Lengkapkan huruf yang hilang.", "bunga", [1, 3], "bunga", why="Bunga dieja B-U-N-G-A. Huruf yang hilang ialah 'u' dan 'g'."),
            _sort(
                "Huruf vokal atau konsonan?",
                [
                    ("Vokal", None, [("a", None), ("i", None), ("u", None)]),
                    ("Konsonan", None, [("b", None), ("k", None), ("m", None)]),
                ],
                pic="huruf",
                why="Huruf vokal dalam bahasa Melayu ialah a, e, i, o dan u. Huruf-huruf lain ialah konsonan.",
            ),
            _tf("Perkataan 'bola' bermula dengan huruf b.", True, pic="bola", why="Bola dieja B-O-L-A, jadi huruf pertamanya ialah b."),
        ],
    },
]


def _without_ids(value: Any) -> Any:
    """A quiz's questions with the ids left out: ids are made afresh on every parse, the rest is the content."""
    if isinstance(value, dict):
        return {k: _without_ids(v) for k, v in value.items() if k != "id"}
    if isinstance(value, list):
        return [_without_ids(v) for v in value]
    return value


def refresh_samples(db: Session, owner: User) -> int:
    """Brings this owner's sample quizzes up to date with SAMPLES (new pictures, explanations, fixes).
    Returns how many changed."""
    changed = 0
    by_title = {sample["title"]: sample for sample in SAMPLES}
    for quiz in db.scalars(select(Quiz).where(Quiz.owner_id == owner.id, Quiz.is_sample.is_(True))):
        sample = by_title.get(quiz.title)
        if sample is None:
            continue
        fresh = [q.model_dump() for q in parse_questions(sample["questions"])]
        if _without_ids(fresh) != _without_ids(quiz.questions) or quiz.description != sample["description"]:
            quiz.questions = fresh
            quiz.description = sample["description"]
            changed += 1
    if changed:
        db.commit()
        log.info("Kuiz contoh dikemas kini: %d", changed)
    return changed


def _add_sample(db: Session, parent: User, sample: dict) -> None:
    questions = parse_questions(sample["questions"])
    db.add(
        Quiz(
            owner_id=parent.id,
            title=sample["title"],
            description=sample["description"],
            questions=[q.model_dump() for q in questions],
            is_sample=True,
        )
    )


def seed(db: Session) -> bool:
    """Creates the demo parent and the sample quizzes once. Returns True when it did.

    When the demo parent already exists, sample quizzes added in a later version (or deleted from the
    demo account) are added to it, so an existing local database gets them too.
    """
    if db.scalar(select(func.count()).select_from(User)):
        parent = db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if parent is not None:
            have = set(db.scalars(select(Quiz.title).where(Quiz.owner_id == parent.id, Quiz.is_sample.is_(True))))
            missing = [sample for sample in SAMPLES if sample["title"] not in have]
            for sample in missing:
                _add_sample(db, parent, sample)
            if missing:
                db.commit()
                log.info("Kuiz contoh baharu ditambah ke akaun demo: %s", ", ".join(s["title"] for s in missing))
            refresh_samples(db, parent)
        return False
    parent = User(name="Ibu Demo", email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD))
    db.add(parent)
    db.flush()
    for sample in SAMPLES:
        _add_sample(db, parent, sample)
    db.commit()
    log.warning("Akaun demo dicipta: %s / %s (untuk localhost sahaja)", DEMO_EMAIL, DEMO_PASSWORD)
    return True


def seed_library(db: Session) -> int:
    """On a public server: the sample quizzes, owned by the library account, added once each (a title
    that is already a sample, whoever owns it, is not added again). Returns how many were added."""
    have = set(db.scalars(select(Quiz.title).where(Quiz.is_sample.is_(True))))
    missing = [sample for sample in SAMPLES if sample["title"] not in have]
    library = db.scalar(select(User).where(User.email == LIBRARY_EMAIL))
    if library is not None:
        refresh_samples(db, library)
    if not missing:
        return 0
    if library is None:
        library = User(name=LIBRARY_NAME, email=LIBRARY_EMAIL, password_hash=NO_PASSWORD)
        db.add(library)
        db.flush()
    for sample in missing:
        _add_sample(db, library, sample)
    db.commit()
    log.info("Kuiz contoh ditambah: %s", ", ".join(s["title"] for s in missing))
    return len(missing)
