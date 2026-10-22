"""A demo parent and sample quizzes, so the app can be tried the moment it starts.

The sample quizzes use every question type and suit every game; the last three are pitched at older
students (Tingkatan 1-5 content). Facts were checked; keep them checked when you change them,
because children will believe them.
"""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Quiz, User
from .questions import parse_questions
from .security import hash_password

log = logging.getLogger("didik.seed")

DEMO_EMAIL = "demo@didik.test"
DEMO_PASSWORD = "main-bersama"


def _single(prompt: str, right: str, *wrong: str, time: int = 20) -> dict:
    choices = [{"text": right, "correct": True}] + [{"text": w} for w in wrong]
    return {"type": "single", "prompt": prompt, "choices": choices, "time_limit": time}


def _multiple(prompt: str, right: list[str], wrong: list[str], time: int = 30) -> dict:
    choices = [{"text": r, "correct": True} for r in right] + [{"text": w} for w in wrong]
    return {"type": "multiple", "prompt": prompt, "choices": choices, "time_limit": time}


def _tf(prompt: str, answer: bool, time: int = 15) -> dict:
    return {"type": "truefalse", "prompt": prompt, "answer": answer, "time_limit": time}


def _text(prompt: str, *answers: str, time: int = 30) -> dict:
    return {"type": "text", "prompt": prompt, "answers": list(answers), "time_limit": time}


def _number(prompt: str, answer: float, unit: str = "", time: int = 25) -> dict:
    return {"type": "number", "prompt": prompt, "answer": answer, "unit": unit, "time_limit": time}


def _order(prompt: str, *items: str, time: int = 40) -> dict:
    return {"type": "order", "prompt": prompt, "items": [{"text": i} for i in items], "time_limit": time}


def _match(prompt: str, pairs: list[tuple[str, str]], time: int = 45) -> dict:
    return {"type": "match", "prompt": prompt, "pairs": [{"left": a, "right": b} for a, b in pairs], "time_limit": time}


def _blank(prompt: str, sentence: str, *distractors: str, time: int = 30) -> dict:
    return {"type": "blank", "prompt": prompt, "sentence": sentence, "distractors": list(distractors), "time_limit": time}


SAMPLES = [
    {
        "title": "Haiwan di Malaysia",
        "description": "Belalai, belang dan kitaran hidup rama-rama. Sesuai untuk 6 hingga 9 tahun.",
        "questions": [
            _single("Haiwan manakah yang mempunyai belalai?", "Gajah", "Harimau", "Penyu", "Kancil"),
            _tf("Penyu bertelur di pantai.", True),
            _single("Apakah haiwan kebangsaan Malaysia?", "Harimau Malaya", "Gajah", "Orang utan", "Enggang"),
            _tf("Kelawar ialah sejenis burung.", False),
            _number("Berapakah bilangan kaki seekor labah-labah?", 8, "kaki"),
            _order("Susun kitaran hidup rama-rama.", "Telur", "Ulat", "Kepompong", "Rama-rama"),
            _match("Padankan haiwan dengan tempat tinggalnya.", [("Ikan", "Air"), ("Burung", "Sarang"), ("Arnab", "Lubang"), ("Lembu", "Kandang")]),
            _text("Haiwan apakah yang berwarna jingga dan berbelang hitam?", "harimau", "harimau malaya"),
            _blank("Lengkapkan ayat.", "Sang [Kancil] terkenal dalam cerita rakyat kerana sangat [cerdik/bijak].", "Gajah", "malas"),
            _multiple("Pilih semua haiwan yang boleh terbang.", ["Enggang", "Kelawar", "Rama-rama"], ["Penyu", "Kucing"]),
            _tf("Ikan bernafas menggunakan insang.", True),
            _single("Di negeri manakah orang utan liar boleh ditemui?", "Sabah", "Perlis", "Melaka", "Johor"),
        ],
    },
    {
        "title": "Matematik Ceria",
        "description": "Tambah, tolak dan nombor genap untuk Tahun 1 dan 2.",
        "questions": [
            _single("3 + 4 = ?", "7", "6", "8", "9", time=15),
            _number("10 − 6 = ?", 4, time=20),
            _tf("5 + 5 = 10", True, time=10),
            _tf("9 lebih kecil daripada 6.", False, time=12),
            _order("Susun nombor dari kecil ke besar.", "2", "5", "8", "11", time=30),
            _match("Padankan soalan dengan jawapannya.", [("2 + 2", "4"), ("3 + 3", "6"), ("5 + 3", "8"), ("7 + 2", "9")]),
            _number("Ali ada 12 biji gula-gula. Dia beri 5 biji kepada adik. Berapa biji yang tinggal?", 7, "biji", time=40),
            _single("Berapakah bilangan sisi sebuah segi tiga?", "3", "4", "5", "6", time=15),
            _multiple("Pilih semua nombor genap.", ["2", "4", "10"], ["7", "9"], time=25),
            _blank("Lengkapkan ayat.", "Dua puluh tambah tiga ialah [23].", "32", "203", time=25),
            _text("Tulis nombor yang datang selepas 19.", "20", "dua puluh", time=20),
            _single("Seminggu ada berapa hari?", "7", "5", "6", "10", time=15),
        ],
    },
    {
        "title": "Bahasa Melayu: Kata dan Ayat",
        "description": "Kata nama, lawan kata dan membina ayat.",
        "questions": [
            _single("Antara berikut, yang manakah kata nama?", "Meja", "Lari", "Cantik", "Makan"),
            _multiple("Pilih semua buah-buahan.", ["Durian", "Rambutan", "Manggis"], ["Kubis", "Bayam"]),
            _match("Padankan perkataan dengan lawannya.", [("Besar", "Kecil"), ("Tinggi", "Rendah"), ("Panas", "Sejuk"), ("Siang", "Malam")]),
            _blank("Pilih perkataan yang sesuai.", "Adik [minum] susu setiap pagi.", "makan", "tidur"),
            _blank("Pilih perkataan yang sesuai.", "Ibu memasak di [dapur].", "bilik air", "padang"),
            _order("Susun perkataan menjadi ayat.", "Saya", "suka", "membaca", "buku"),
            _tf("Perkataan 'kucing' ialah kata kerja.", False),
            _text("Apakah warna daun yang segar?", "hijau"),
            _single("Apakah huruf pertama dalam perkataan 'bola'?", "b", "o", "l", "a", time=15),
            _text("Eja nama buah berduri yang digelar Raja Buah.", "durian"),
        ],
    },
    {
        "title": "Sains: Betul atau Salah?",
        "description": "Kenyataan pendek tentang alam. Paling seronok dengan Lompat!.",
        "questions": [
            _tf("Matahari terbit di sebelah timur.", True),
            _tf("Air membeku menjadi ais apabila sangat sejuk.", True),
            _tf("Ikan boleh hidup lama di darat tanpa air.", False),
            _tf("Tumbuhan memerlukan cahaya matahari untuk membuat makanan.", True),
            _tf("Bulan menghasilkan cahayanya sendiri.", False),
            _tf("Magnet boleh menarik paku besi.", True),
            _tf("Kita bernafas menggunakan paru-paru.", True),
            _tf("Gajah ialah haiwan yang bertelur.", False),
            _tf("Hujan turun dari awan.", True),
            _tf("Ayam mempunyai empat kaki.", False),
            _single("Apakah yang kita gunakan untuk melihat?", "Mata", "Telinga", "Hidung", time=15),
            _single("Ais itu panas atau sejuk?", "Sejuk", "Panas", time=10),
        ],
    },
    {
        "title": "Malaysiaku",
        "description": "Bendera, negeri, gunung dan sungai negara kita.",
        "questions": [
            _single("Apakah bunga kebangsaan Malaysia?", "Bunga raya", "Bunga mawar", "Bunga orkid", "Bunga matahari"),
            _single("Apakah ibu negara Malaysia?", "Kuala Lumpur", "Ipoh", "Johor Bahru", "Kuching"),
            _number("Berapakah bilangan jalur merah dan putih pada Jalur Gemilang?", 14, "jalur"),
            _tf("Gunung Kinabalu terletak di Sabah.", True),
            _text("Apakah nama gunung tertinggi di Malaysia?", "Gunung Kinabalu", "Kinabalu"),
            _number("Berapakah bilangan negeri di Malaysia?", 13, "negeri"),
            _match("Padankan negeri dengan ibu negerinya.", [("Selangor", "Shah Alam"), ("Kedah", "Alor Setar"), ("Sabah", "Kota Kinabalu"), ("Sarawak", "Kuching")]),
            _order("Susun hari mengikut urutan.", "Isnin", "Selasa", "Rabu", "Khamis"),
            _multiple("Pilih semua warna yang ada pada Jalur Gemilang.", ["Merah", "Putih", "Biru", "Kuning"], ["Hijau", "Ungu"]),
            _tf("Sungai Rajang terletak di Sarawak.", True),
        ],
    },
    # For older students (Tingkatan 1-5 content); like every sample, they can be played with any game.
    {
        "title": "Sains Tingkatan 1: Sel dan Jirim",
        "description": "Sel, organel, keadaan jirim dan gas adi.",
        "questions": [
            _single("Apakah unit asas bagi semua benda hidup?", "Sel", "Tisu", "Organ", "Atom"),
            _single("Organel manakah yang menjalankan respirasi sel?", "Mitokondrion", "Ribosom", "Nukleus", "Vakuol"),
            _tf("Sel tumbuhan mempunyai dinding sel, tetapi sel haiwan tidak.", True),
            _number("Pada suhu berapakah air tulen mendidih pada tekanan atmosfera biasa?", 100, "°C"),
            _text("Apakah nama planet yang paling hampir dengan Matahari?", "Utarid", "Merkuri"),
            _match("Padankan keadaan jirim dengan cirinya.", [("Pepejal", "Bentuk tetap"), ("Cecair", "Ikut bentuk bekas"), ("Gas", "Memenuhi seluruh ruang")]),
            _order("Susun aras organisasi hidupan, dari yang paling ringkas.", "Sel", "Tisu", "Organ", "Sistem"),
            _multiple("Pilih semua gas adi.", ["Helium", "Neon", "Argon"], ["Oksigen", "Nitrogen"]),
            _tf("Bunyi boleh merambat melalui vakum.", False),
            _blank("Lengkapkan ayat.", "Tumbuhan hijau membuat makanan melalui proses [fotosintesis].", "respirasi", "transpirasi"),
        ],
    },
    {
        "title": "Matematik Tingkatan 1-2: Nombor dan Algebra",
        "description": "Kuasa dua, peratus, persamaan linear, nombor perdana dan pecahan.",
        "questions": [
            _single("Berapakah nilai 3² + 4²?", "25", "49", "14", "7"),
            _number("Selesaikan 2x + 5 = 17. Berapakah nilai x?", 6),
            _single("Berapakah 15% daripada 200?", "30", "15", "20", "45"),
            _tf("Semua nombor perdana ialah nombor ganjil.", False),
            _number("Berapakah hasil tambah sudut pedalaman sebuah segi tiga?", 180, "darjah"),
            _order("Susun nombor ini dari yang terkecil.", "-5", "-2", "0", "3"),
            _match("Padankan pecahan dengan nombor perpuluhannya.", [("1/2", "0.5"), ("1/4", "0.25"), ("3/4", "0.75"), ("1/5", "0.2")]),
            _multiple("Pilih semua nombor perdana.", ["2", "3", "7", "11"], ["9", "15"]),
            _text("Apakah nama poligon yang mempunyai lapan sisi?", "Oktagon", "Segi lapan"),
            _blank("Lengkapkan ayat.", "Luas segi empat tepat berukuran 8 cm × 5 cm ialah [40] cm².", "13", "26"),
        ],
    },
    {
        "title": "Sejarah Tingkatan 4-5: Merdeka dan Malaysia",
        "description": "Dari Malayan Union hingga pembentukan Malaysia.",
        "questions": [
            _single("Bilakah Persekutuan Tanah Melayu mencapai kemerdekaan?", "31 Ogos 1957", "16 September 1963", "31 Ogos 1963", "16 September 1957"),
            _single("Siapakah Perdana Menteri Malaysia yang pertama?", "Tunku Abdul Rahman Putra Al-Haj", "Tun Abdul Razak Hussein", "Tun Hussein Onn", "Tun Dr. Mahathir Mohamad"),
            _tf("Malaysia dibentuk pada 16 September 1963.", True),
            _number("Berapakah bilangan negeri dalam Persekutuan Tanah Melayu semasa merdeka pada tahun 1957?", 11, "negeri"),
            _order("Susun peristiwa ini mengikut urutan masa.", "Malayan Union diperkenalkan", "Persekutuan Tanah Melayu ditubuhkan", "Kemerdekaan Persekutuan Tanah Melayu", "Pembentukan Malaysia"),
            _text("Apakah nama dokumen yang dibacakan oleh Tunku Abdul Rahman di Stadium Merdeka pada 31 Ogos 1957?", "Pemasyhuran Kemerdekaan", "Pengisytiharan Kemerdekaan"),
            _match("Padankan tokoh dengan gelarannya.", [("Tunku Abdul Rahman", "Bapa Kemerdekaan"), ("Tun Abdul Razak", "Bapa Pembangunan"), ("Tun Hussein Onn", "Bapa Perpaduan"), ("Tun Dr. Mahathir Mohamad", "Bapa Pemodenan")]),
            _multiple("Pilih wilayah yang bersama Persekutuan Tanah Melayu membentuk Malaysia pada tahun 1963.", ["Sabah", "Sarawak", "Singapura"], ["Brunei"]),
            _tf("Singapura berpisah daripada Malaysia pada tahun 1965.", True),
            _blank("Lengkapkan ayat.", "Perlembagaan Persekutuan ialah undang-undang [tertinggi] negara.", "terendah", "sementara"),
        ],
    },
]


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
        return False
    parent = User(name="Ibu Demo", email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD))
    db.add(parent)
    db.flush()
    for sample in SAMPLES:
        _add_sample(db, parent, sample)
    db.commit()
    log.warning("Akaun demo dicipta: %s / %s (untuk localhost sahaja)", DEMO_EMAIL, DEMO_PASSWORD)
    return True
