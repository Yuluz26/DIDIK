"""The 3D stickers a question can show: animals, food, things, vehicles. Each key is a picture in
web/static/pelekat/<key>.webp (Microsoft Fluent Emoji 3D, MIT licence; see LICENSE.txt beside them).

The web keeps the same keys with their Malay names in web/src/lib/stickers.ts; a test keeps the two lists
the same. Only these keys are accepted, so a question can never point at some other file.
"""

from __future__ import annotations

STICKERS: frozenset[str] = frozenset(
    """
    kucing anjing ayam anak-ayam itik ikan arnab lembu kambing gajah harimau monyet penyu burung burung-hantu
    rama-rama lebah kumbang katak siput ketam sotong paus zirafah singa panda penguin unta kuda tikus ular
    buaya dinosaur orang-utan merak ikan-buntal jerung dolfin kelawar labah-labah ulat semut kuda-belang
    epal pisang oren tembikai anggur strawberi nanas mangga kelapa lobak-merah jagung cili telur roti nasi susu
    aiskrim kek donat gula-gula biskut cendawan epal-hijau madu
    bola belon wau teddy buku pensel krayon beg jam payung kasut baju topi hadiah loceng hati
    rumah sekolah masjid bangunan beg-duit plag magnet syiling bateri
    bunga bunga-matahari pokok pokok-kelapa matahari bulan bintang awan pelangi hujan salji api air batu gunung
    gunung-berapi ombak kilat angin anak-pokok kaktus daun tulip ais
    buku-buku mikroskop tabung-uji dna kanta termometer bumi peta kalendar skrol abakus pembaris sesiku mentol
    otak jam-pasir kompas tanda-soal nombor huruf bulatan segi-empat tulang gigi
    kereta bas basikal motosikal lori kereta-api kapal-terbang helikopter bot kapal roket bomba ambulans
    bakul kotak troli sarang pinggan
    kilauan bintang-bersinar mercun piala mahkota pingat
    """.split()
)

# What a "Kira & masukkan" question's objects go into.
PLACES: frozenset[str] = frozenset({"bakul", "kotak", "troli", "bas", "sarang", "pinggan", "beg", "kereta-api"})


def check_sticker(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    if value not in STICKERS:
        raise ValueError("Gambar pelekat tidak dikenali.")
    return value
