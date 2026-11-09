<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import Logo from '$ui/Logo.svelte';

	type Prices = { free: { monthly: number; yearly: number }; premium: { monthly: number; yearly: number }; family: { monthly: number; yearly: number } };
	let prices = $state<Prices | null>(null);
	let interval = $state<'monthly' | 'yearly'>('monthly');
	let error = $state('');
	onMount(async () => {
		try {
			const result = await api.get<{ plans: { key: keyof Prices; pricesSen: Prices[keyof Prices] }[] }>('/api/membership/plans');
			prices = Object.fromEntries(result.plans.map((p) => [p.key, p.pricesSen])) as Prices;
		} catch (problem) { error = problem instanceof Error ? problem.message : 'Harga tidak dapat dimuat.'; }
	});
	const money = (sen: number) => `RM${(sen / 100).toFixed(2)}`;
</script>

<svelte:head><title>Pelan keahlian · DIDIK</title><meta name="description" content="Pelan keahlian DIDIK Free, Premium dan Family untuk ibu bapa dan anak." /></svelte:head>
<div class="pricing">
	<header><a href="/" aria-label="DIDIK, laman utama"><Logo /></a><a href="/ibu-bapa">Ruang ibu bapa</a></header>
	<main>
		<div class="lead"><h1>Satu tempat belajar.<br />Ruang untuk setiap keluarga.</h1><p>Mula percuma. Pilih Premium untuk semua permainan, atau Family untuk sehingga tiga anak. Harga rasmi dalam Ringgit Malaysia.</p></div>
		<div class="toggle" role="group" aria-label="Tempoh bayaran"><button class:active={interval === 'monthly'} onclick={() => interval = 'monthly'}>Bulanan</button><button class:active={interval === 'yearly'} onclick={() => interval = 'yearly'}>Tahunan</button></div>
		{#if error}<p role="alert">{error}</p>{:else if !prices}<p aria-busy="true">Memuatkan harga…</p>{:else}
		<div class="grid">
			<section><h2>Free</h2><p class="cost">RM0.00 <small>selamanya</small></p><p>Mula bermain dan cipta kuiz tanpa bayaran.</p><ul><li>Satu profil anak</li><li>Kuiz Interaktif asas</li><li>Hasil kuiz asas</li></ul><a href="/ibu-bapa">Daftar percuma</a></section>
			<section class="accent"><h2>Premium</h2><p class="cost">{money(prices.premium[interval])} <small>/{interval === 'monthly' ? 'bulan' : 'tahun'}</small></p><p>Lebih banyak cara untuk belajar dan bermain.</p><ul><li>Satu profil anak</li><li>14 permainan 2D</li><li>Hikayat Lima Alam</li><li>Hos bilik Party</li></ul><a href="/ibu-bapa/keahlian">Pilih Premium</a></section>
			<section><h2>Family</h2><p class="cost">{money(prices.family[interval])} <small>/{interval === 'monthly' ? 'bulan' : 'tahun'}</small></p><p>Satu keahlian untuk anak-anak di rumah.</p><ul><li>Sehingga tiga profil anak</li><li>Semua ciri Premium</li><li>Profil belajar setiap anak</li><li>Solo dan Party</li></ul><a href="/ibu-bapa/keahlian">Pilih Family</a></section>
		</div>{/if}
		<p class="terms">Premium dan Family dibayar melalui QR bagi setiap tempoh. Tiada caj pembaharuan automatik. Selepas membayar, hantar bukti ke WhatsApp DIDIK; keahlian aktif selepas semakan admin. Harga yang dipaparkan ialah jumlah pelan; sebarang caj bank atau aplikasi pembayaran, jika ada, ditunjukkan oleh penyedia anda sebelum pembayaran.</p>
	</main>
</div>
<style>
	.pricing{min-height:100dvh;background:#edeef5;color:#292d47;font-family:var(--font-body);padding:0 max(1rem,calc((100vw - 76rem)/2)) 5rem}.pricing header{display:flex;justify-content:space-between;align-items:center;padding:1.5rem 0}.pricing header>a:last-child{font-weight:800;color:#5c44ba}.lead{margin:clamp(2rem,6vw,5rem) 0 2rem}.lead h1{font:700 clamp(2.4rem,5vw,4.4rem)/1.04 var(--font-display);letter-spacing:-.025em;max-width:16ch;margin:0 0 1.2rem}.lead p{font-size:1.15rem;line-height:1.6;max-width:60ch;color:#565c76}.toggle{display:flex;gap:.4rem;margin:2rem 0}.toggle button{border:0;border-radius:99px;background:#e0daef;color:#513ab3;font:800 1rem var(--font-body);padding:.75rem 1.2rem;cursor:pointer}.toggle button.active{background:#7054d8;color:white}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}.grid section{display:flex;flex-direction:column;align-items:start;min-height:26rem;background:#fafbfe;border-radius:16px;padding:clamp(1.4rem,2.5vw,2.2rem);box-shadow:8px 8px 24px #a3acc650,-8px -8px 24px #fff}.grid section.accent{background:#e5dcff}.grid h2{font:700 1.7rem var(--font-display);margin:0}.cost{font:700 clamp(1.7rem,3vw,2.3rem) var(--font-display);margin:1.2rem 0 .4rem}.cost small{font:600 1rem var(--font-body);color:#565c76}.grid section>p:not(.cost){line-height:1.5;color:#565c76}.grid ul{padding-left:1.2rem;line-height:1.9;flex:1}.grid a{display:inline-flex;align-items:center;justify-content:center;min-height:2.8rem;padding:.2rem 1.1rem;border-radius:11px;background:#7054d8;color:#fff;text-decoration:none;font-weight:800}.terms{max-width:78ch;line-height:1.65;margin:2rem 0;color:#565c76}.pricing :is(a,button):focus-visible{outline:3px solid #dd4f88;outline-offset:3px}@media(max-width:790px){.grid{grid-template-columns:1fr}.grid section{min-height:0}.lead h1{max-width:20ch}}
</style>
