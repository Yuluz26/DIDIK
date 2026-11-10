<script lang="ts">
	import Logo from '$ui/Logo.svelte';
	import PlanSection from '$lib/home/PlanSection.svelte';
	import { beachTile } from '$lib/pixel/sea';

	const beach = 'url(' + beachTile().toURL(1) + ')';
</script>

<svelte:head>
	<title>Pelan keahlian · DIDIK</title>
	<meta name="description" content="Pelan keahlian DIDIK Free, Premium dan Family untuk ibu bapa dan anak." />
</svelte:head>

<div class="membership">
	<header class="site-header">
		<div class="header-inner">
			<a class="home-link" href="/" aria-label="DIDIK, laman utama"><Logo /></a>
			<nav aria-label="Pautan utama">
				<a href="/">Laman utama</a>
				<a class="parent-link" href="/ibu-bapa">Ruang ibu bapa <span aria-hidden="true">↗</span></a>
			</nav>
		</div>
	</header>

	<main>
		<PlanSection {beach} showPaymentNote={false} />
		<section class="payment" aria-labelledby="payment-title">
			<div class="payment-inner">
				<div class="payment-heading">
					<h2 id="payment-title">Mudah untuk mula bermain.</h2>
					<p>Pembayaran Premium dan Family dibuat melalui kod QR. Setiap tempoh dibayar sekali; tiada caj pembaharuan automatik.</p>
				</div>
				<ol class="steps">
					<li><span class="step-number">1</span><h3>Pilih pelan</h3><p>Masuk ke ruang ibu bapa dan pilih Premium atau Family.</p></li>
					<li><span class="step-number">2</span><h3>Imbas kod QR</h3><p>Bayar jumlah untuk tempoh Bulanan atau Tahunan yang dipilih.</p></li>
					<li><span class="step-number">3</span><h3>Hantar bukti</h3><p>Kirim bukti pembayaran melalui WhatsApp. Akses aktif selepas semakan admin.</p></li>
				</ol>
				<div class="payment-actions">
					<a class="start" href="/ibu-bapa/keahlian">Lihat keahlian saya <span aria-hidden="true">↗</span></a>
					<a class="whatsapp" href="https://wa.me/60139558132" target="_blank" rel="noopener noreferrer">Hantar bukti di WhatsApp <span aria-hidden="true">↗</span></a>
				</div>
				<p class="fine-print">Harga yang dipaparkan ialah jumlah pelan. Sebarang caj bank atau aplikasi pembayaran, jika ada, ditunjukkan oleh penyedia anda sebelum pembayaran.</p>
			</div>
		</section>
	</main>
</div>

<style>
	.membership { min-height: 100dvh; color: var(--ink); font-family: var(--font-body); }
	.site-header { position: relative; z-index: 2; background: #fff9ec; border-bottom: 1px solid #e6d5b5; }
	.header-inner { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; width: min(calc(100% - 2rem),76rem); margin: 0 auto; padding: .9rem 0; }
	.home-link { display: inline-flex; align-items: center; min-width: 0; text-decoration: none; }
	.site-header nav { display: flex; align-items: center; gap: clamp(.75rem,2vw,1.8rem); }
	.site-header nav a { color: var(--ink); font-size: .88rem; font-weight: 800; text-decoration: none; white-space: nowrap; }
	.site-header nav .parent-link { display: inline-flex; align-items: center; gap: .45rem; min-height: 42px; padding: .5rem .8rem; border-radius: 10px; background: #224938; color: #fff; }
	.payment { padding: clamp(4rem,7vw,6rem) 1rem clamp(4.5rem,8vw,7rem); background: #fff9ee; }
	.payment-inner { width: min(100%,76rem); margin: 0 auto; }
	.payment-heading { display: grid; grid-template-columns: minmax(0,1.1fr) minmax(0,.9fr); align-items: end; gap: 2rem; margin-bottom: 2.2rem; }
	.payment-heading h2 { max-width: 14ch; margin: 0; font: 700 clamp(2rem,4vw,3.4rem)/1.04 var(--font-display); letter-spacing: -.02em; text-wrap: balance; }
	.payment-heading p { max-width: 42ch; margin: 0; color: var(--ink-2); font-size: 1.03rem; line-height: 1.55; }
	.steps { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 1rem; margin: 0; padding: 0; list-style: none; }
	.steps li { min-width: 0; padding: 1.4rem; border-top: 2px solid #315544; background: #f3eddf; }
	.step-number { display: grid; place-items: center; width: 2rem; height: 2rem; border-radius: 50%; background: #315544; color: #fff; font-weight: 900; }
	.steps h3 { margin: 1rem 0 .4rem; font: 700 1.35rem/1.15 var(--font-display); }
	.steps p { max-width: 30ch; margin: 0; color: var(--ink-2); line-height: 1.5; }
	.payment-actions { display: flex; flex-wrap: wrap; gap: .75rem; margin-top: 2rem; }
	.payment-actions a { display: inline-flex; align-items: center; justify-content: space-between; gap: 2rem; min-height: 48px; padding: .7rem 1rem; border-radius: 10px; font-weight: 800; text-decoration: none; transition: transform 160ms cubic-bezier(.23,1,.32,1); }
	.payment-actions .start { background: #214537; color: #fff; }
	.payment-actions .whatsapp { border: 1px solid #214537; color: #214537; }
	.fine-print { max-width: 78ch; margin: 1.7rem 0 0; color: var(--ink-2); font-size: .85rem; line-height: 1.5; }
	.membership a:focus-visible { outline: 3px solid #6543b9; outline-offset: 3px; }
	@media (hover:hover) and (pointer:fine) { .payment-actions a:hover { transform: translateY(-2px); } .site-header nav a:not(.parent-link):hover { text-decoration: underline; text-underline-offset: 4px; } }
	@media (max-width: 720px) {
		.payment-heading { grid-template-columns: 1fr; gap: .7rem; }
		.steps { grid-template-columns: 1fr; gap: .65rem; }
		.steps li { display: grid; grid-template-columns: 2rem minmax(0,1fr); column-gap: .8rem; padding: 1rem; }
		.steps h3 { margin: 0; align-self: center; }
		.steps p { grid-column: 2; margin-top: .25rem; }
	}
	@media (max-width: 450px) {
		.header-inner { width: min(calc(100% - 1.5rem),76rem); }
		.site-header nav { gap: .5rem; }
		.site-header nav a { font-size: .76rem; }
		.site-header nav .parent-link { padding: .45rem .6rem; }
		.payment-actions a { width: 100%; }
	}
	@media (prefers-reduced-motion: reduce) { .payment-actions a { transition: none; } }
</style>
