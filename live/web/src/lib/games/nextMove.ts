/** The action a child should take after answering in each 2D game. */
export function nextMove(mode: string, game: any): { title: string; detail: string; button: string; target: string } {
	const world = game.world ?? {};
	switch (mode) {
		case 'harta': return { title: 'Masa menggali harta!', detail: world.canDig ? 'Ketik tanda X di pulau untuk gunakan penyodok kamu.' : 'Lihat pulau, kemudian jawab soalan lagi untuk dapat penyodok.', button: 'Pergi ke pulau', target: '.treasure .map' };
		case 'pasukan': return { title: 'Masa tawan petak!', detail: game.seat?.step === 'capture' ? 'Ketik petak yang bercahaya untuk tawan dengan bendera kamu, atau simpan bendera dahulu.' : 'Lihat petak pasukan kamu. Jawab soalan lagi untuk dapat bendera.', button: 'Lihat peta pasukan', target: '.teams' };
		case 'kampung': return { title: world.tokens > 0 ? 'Hias kampung kamu!' : 'Kampung sedang membesar!', detail: world.tokens > 0 ? 'Pilih hiasan di bawah peta, kemudian ketik padang untuk meletakkannya.' : 'Lihat bangunan yang sedang dibina. Jawab lagi untuk dapat bahan dan hiasan.', button: world.tokens > 0 ? 'Pilih hiasan' : 'Lihat kampung', target: world.tokens > 0 ? '.village .tray' : '.village .map' };
		case 'kebun': return { title: 'Jom berkebun!', detail: 'Ketik batas kosong untuk tanam bunga atau buah. Ketik tanaman untuk siram, dan ketik lagi bila sudah masak untuk tuai.', button: 'Pergi ke batas', target: '.kebun' };
		case 'pancing': return { title: 'Jom memancing!', detail: 'Ketik “Lempar joran” di bawah tasik untuk gunakan umpan yang kamu dapat.', button: 'Lempar joran', target: '.pancing .acts' };
		case 'kubu': return { title: 'Bina kubu pasir!', detail: 'Gunakan pasir kamu untuk tambah tingkat, bina tembok atau pacak bendera.', button: 'Pilih binaan', target: '.kubu .acts' };
		case 'keretapi': return { title: 'Jalankan kereta api!', detail: 'Gunakan arang untuk bergerak ke stesen seterusnya atau tambah gerabak.', button: 'Lihat pilihan kereta api', target: '.keretapi .acts' };
		case 'pasar': return { title: 'Buka gerai pasar!', detail: 'Jual barang yang kamu dapat. Kamu juga boleh beli naik taraf untuk gerai.', button: 'Pergi ke gerai', target: '.pasar .acts' };
		case 'bintang': return { title: 'Lihat bintang kamu!', detail: 'Bintang daripada jawapan kamu sudah naik ke langit pasukan. Jawab lagi untuk kumpul lebih banyak.', button: 'Lihat langit', target: '.sky' };
		case 'teka': return { title: 'Cuba teka gambar!', detail: 'Lihat petak gambar yang terbuka, kemudian taip tekaannya di bawah gambar. Soalan seterusnya akan muncul sendiri.', button: 'Pergi teka gambar', target: '.teka .guess' };
		case 'lumba': return { title: 'Lihat sampan berlumba!', detail: 'Jawapan kamu membantu sampan bergerak. Saksikan perlumbaan sementara menunggu soalan seterusnya.', button: 'Lihat perlumbaan', target: '.play' };
		case 'wau': return { title: 'Lihat wau terbang!', detail: 'Jawapan kamu membantu wau terbang lebih jauh. Saksikan wau sementara menunggu soalan seterusnya.', button: 'Lihat wau', target: '.play' };
		case 'lompat': return { title: 'Lihat lompatan kamu!', detail: 'Saksikan watak melompat ke pulau pilihan kamu. Soalan seterusnya akan muncul sendiri.', button: 'Lihat kolam', target: '.scene' };
		case 'hutan': return { title: 'Teruskan jelajah hutan!', detail: 'Gerakkan watak dengan kayu kawalan atau kekunci anak panah. Dekati peti untuk buka soalan lain; apabila kunci cukup, cari pintu keluar.', button: 'Teruskan jelajah', target: '.forest .stage' };
		default: return { title: 'Jom terus bermain!', detail: 'Lihat permainan kamu dan pilih langkah seterusnya.', button: 'Lihat permainan', target: '.world' };
	}
}

export function showNextMove(target: string) {
	requestAnimationFrame(() => {
		const element = document.querySelector(target);
		if (element instanceof HTMLElement) element.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'center' });
	});
}
