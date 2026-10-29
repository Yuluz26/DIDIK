# Senarai Semak Visual / QA Aset DIDIK Legenda

- [ ] **Tuah**: 5 elemen berbeza, rupa watak konsisten antara variasi dan sama standard dengan hero asal dalam repo.
- [ ] **Mahsuri**: 5 elemen berbeza, rupa watak konsisten antara variasi dan sama standard dengan hero asal dalam repo.
- [ ] Arah menghadap hero/arah senjata sepadan dengan pertempuran semasa.
- [ ] Setiap imej 768 × 960 dan berformat PNG RGBA lutsinar (tiada latar magenta).
- [ ] Tiada bahagian watak/senjata yang terpotong oleh sempadan sprite.
- [ ] Kedudukan kaki dan tubuh hampir konsisten bagi semua elemen.
- [ ] Warna pastel terang/ornamen masih boleh dibaca pada skrin telefon.
- [ ] Kenal pasti semua warping/tepi berwarna magenta hasil AI/chroma key dan baiki jika perlu.
- [ ] Fail tidak overwrite sprites `idle/ready/attack/cast/hurt/victory` sedia ada.
- [ ] Visual elemen hanya muncul selepas pengesahan unlock daripada server.
- [ ] Idle/attack/cast/hurt/victory transition berfungsi tanpa gangguan; jika tiada pose unik, fallback jelas.
- [ ] Uji 5 elemen × 2 hero + Solo + Party + portrait/landscape.

**Had pakej:** hanya satu pose `equipped_ready` bagi setiap hero/elemen. Ia bukan sprite sheet animasi lengkap dan bukan dijamin sama reka bentuk tepat seperti hero repo. Review manusia disarankan sebelum integrasi produksi.
