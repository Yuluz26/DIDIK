<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import Icon from '$ui/Icon.svelte';
	import Didi from '$ui/Didi.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import { GAMES } from './islands';
	import { reveal } from './reveal';

	let { beach, showPaymentNote = true }: { beach: string; showPaymentNote?: boolean } = $props();
	type Interval = 'monthly' | 'yearly';
	type Plan = { key: string; pricesSen: { monthly: number; yearly: number } };
	let plans = $state<Record<string, Plan>>({});
	let interval = $state<Interval>('monthly');
	let failed = $state(false);
	const money = (sen: number) => 'RM' + (sen / 100).toFixed(2);

	onMount(async () => {
		try {
			const result = await api.get<{ plans: Plan[] }>('/api/membership/plans');
			plans = Object.fromEntries(result.plans.map((plan) => [plan.key, plan]));
		} catch { failed = true; }
	});
</script>

<section id="pelan" class="plan-land" style:--beach={beach} aria-labelledby="pelan-title">
	<div class="wrap inner">
		<div class="heading" {@attach reveal()}>
			<div class="copy">
				<h2 id="pelan-title">Setiap anak ada cara bermain.</h2>
				<p>Mulakan dengan kuiz percuma. Bila bersedia menjelajah lebih jauh, ada pelan untuk satu anak atau seisi rumah.</p>
			</div>
			<div class="mascot" aria-hidden="true"><Didi mood="happy" size={104} /></div>
		</div>
		<div class="controls" {@attach reveal(70)}>
			<p>Harga rasmi dalam Ringgit Malaysia</p>
			<div class="period" role="group" aria-label="Tempoh keahlian">
				<button type="button" class:active={interval === 'monthly'} aria-pressed={interval === 'monthly'} onclick={() => interval = 'monthly'}>Bulanan</button>
				<button type="button" class:active={interval === 'yearly'} aria-pressed={interval === 'yearly'} onclick={() => interval = 'yearly'}>Tahunan</button>
			</div>
		</div>
		{#if failed}
			<p role="alert" class="loading">Harga tidak dapat dimuat. <a href="/keahlian">Buka halaman keahlian</a> untuk cuba lagi.</p>
		{:else if !plans.free || !plans.premium || !plans.family}
			<p class="loading" aria-busy="true">Memuatkan pelan…</p>
		{:else}
			<div class="cards">
				<article class="card free" {@attach reveal(90)}>
					<div class="card-art"><span class="art-orbit" aria-hidden="true"></span><Sticker key="awan" size={96} alt="" /><span class="card-tag">Mula di sini</span></div>
					<div class="card-body">
						<h3>Free</h3>
						<p class="summary">Ruang pertama untuk cuba, tulis dan main bersama.</p>
						<p class="price"><strong>{money(plans.free.pricesSen.monthly)}</strong><span>selamanya</span></p>
						<ul><li>Satu profil anak</li><li>Kuiz contoh dan Interaktif asas</li><li>Keputusan kuiz asas</li></ul>
						<a class="choose" href="/ibu-bapa">Daftar percuma <Icon name="next" size={19} /></a>
					</div>
				</article>
				<article class="card premium" {@attach reveal(150)}>
					<div class="card-art"><span class="art-orbit" aria-hidden="true"></span><Sticker key="bintang-bersinar" size={104} alt="" /><span class="card-tag">Pengembaraan penuh</span></div>
					<div class="card-body">
						<h3>Premium</h3>
						<p class="summary">Satu anak, semua dunia permainan DIDIK.</p>
						<p class="price"><strong>{money(plans.premium.pricesSen[interval])}</strong><span>/{interval === 'monthly' ? 'bulan' : 'tahun'}</span></p>
						<ul><li>Satu profil anak</li><li>Semua 14 permainan 2D</li><li>Hikayat Lima Alam dan hos bilik</li></ul>
						<a class="choose" href="/ibu-bapa/keahlian">Pilih Premium <Icon name="next" size={19} /></a>
					</div>
				</article>
				<article class="card family" {@attach reveal(210)}>
					<div class="card-art"><span class="art-orbit" aria-hidden="true"></span><Sticker key="rumah" size={104} alt="" /><span class="card-tag">Untuk seisi rumah</span></div>
					<div class="card-body">
						<h3>Family</h3>
						<p class="summary">Lebih ramai anak, satu keahlian keluarga.</p>
						<p class="price"><strong>{money(plans.family.pricesSen[interval])}</strong><span>/{interval === 'monthly' ? 'bulan' : 'tahun'}</span></p>
						<ul><li>Sehingga tiga profil anak</li><li>Semua ciri Premium</li><li>Story Mode Solo dan Party</li></ul>
						<a class="choose" href="/ibu-bapa/keahlian">Pilih Family <Icon name="next" size={19} /></a>
					</div>
				</article>
			</div>
		{/if}
		<div class="game-catalog" {@attach reveal(160)}>
			<div class="catalog-heading">
				<div><h3>Semua permainan dalam Premium &amp; Family</h3><p>Nama penuh, supaya anda tahu dunia mana yang boleh dipilih.</p></div>
				<span>{GAMES.length} permainan 2D</span>
			</div>
			<ul class="game-list" aria-label="Senarai permainan 2D Premium dan Family">
				{#each GAMES as game (game.key)}<li style:--game-color={game.tint}>{game.title}</li>{/each}
			</ul>
			<p class="more-games"><strong>Juga termasuk</strong> Kuiz Interaktif (Umum, Sains, Sejarah, Pendidikan Islam) dan Story Mode: Hikayat Lima Alam.</p>
		</div>
		{#if showPaymentNote}<p class="payment-note" {@attach reveal(230)}>Premium dan Family dibayar melalui QR bagi setiap tempoh. Hantar bukti ke WhatsApp DIDIK; akses aktif selepas semakan admin. Tiada pembaharuan atau caj automatik. <a href="/keahlian">Lihat semua butiran pelan</a>.</p>{/if}
	</div>
</section>

<style>
	.plan-land { position: relative; overflow: hidden; padding: clamp(4rem,8vw,7rem) 0 clamp(5rem,9vw,8rem); background: var(--beach) 0 0 / calc(var(--px) * 64) calc(var(--px) * 64); color: var(--ink); }
	.inner { position: relative; }
	.heading { display: flex; align-items: end; justify-content: space-between; gap: 2rem; }
	.copy { max-width: 43rem; }
	.copy h2 { max-width: 17ch; margin: 0; font: 700 clamp(2rem,4vw,3.6rem)/1.04 var(--font-display); letter-spacing: -.02em; text-wrap: balance; }
	.copy p { max-width: 55ch; margin: 1rem 0 0; color: var(--ink-2); font-size: clamp(1rem,1.3vw,1.2rem); line-height: 1.55; }
	.mascot { flex: none; transform-origin: 50% 100%; animation: peek 5s cubic-bezier(.77,0,.175,1) infinite; }
	.controls { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin: 2.3rem 0 1.4rem; }
	.controls p { margin: 0; color: var(--ink-2); font-size: .94rem; font-weight: 800; }
	.period { display: flex; gap: .2rem; padding: .2rem; border: 1.5px solid var(--edge); border-radius: 999px; background: #fff8ec; box-shadow: 0 4px 12px #4430231e; }
	.period button { min-height: 40px; padding: .5rem 1.15rem; border: 0; border-radius: 999px; background: transparent; color: var(--ink); font: 800 .9rem var(--font-body); cursor: pointer; transition: background-color 180ms ease,color 180ms ease; }
	.period button.active { background: var(--ink); color: #fff; }
	.cards { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); align-items: stretch; gap: clamp(.8rem,1.5vw,1.3rem); padding: .65rem 0 1rem; }
	.card { --card-bg: #fffaf1; --art-bg: #e4ecdf; --art-shape: #d0e3d2; --button-bg: #203b31; display: flex; flex-direction: column; min-width: 0; overflow: hidden; border: 1px solid #3e372e; border-radius: 18px; background: var(--card-bg); box-shadow: 0 14px 27px #4e342329,0 3px 5px #4e34231a; transition: transform 240ms cubic-bezier(.23,1,.32,1),box-shadow 240ms cubic-bezier(.23,1,.32,1); }
	.card.premium { --card-bg: #f4edff; --art-bg: #dcd0fa; --art-shape: #bba4f2; --button-bg: #5c3baa; position: relative; transform: translateY(-8px); box-shadow: 0 20px 34px #4024593a,0 4px 7px #40245924; }
	.card.family { --card-bg: #fff4e9; --art-bg: #f9d6bc; --art-shape: #f2baa1; --button-bg: #8b4038; }
	.card-art { position: relative; display: grid; place-items: center; height: 132px; isolation: isolate; overflow: hidden; background: var(--art-bg); }
	.art-orbit { position: absolute; z-index: -1; width: 210px; height: 210px; top: 31px; left: calc(50% - 105px); border-radius: 50%; background: var(--art-shape); }
	.card-art :global(img), .card-art :global(svg) { filter: drop-shadow(0 8px 6px #392b2930); transition: transform 260ms cubic-bezier(.23,1,.32,1); }
	.card-tag { position: absolute; top: 15px; right: 16px; padding: .35rem .65rem; border: 1px solid #473d3b; border-radius: 999px; background: #fffdf5e8; color: #31302d; font-size: .7rem; font-weight: 900; line-height: 1.1; }
	.card-body { display: flex; flex: 1; flex-direction: column; padding: clamp(1.25rem,2vw,1.8rem); }
	.card h3 { margin: 0; font: 700 clamp(1.7rem,2.5vw,2.2rem)/1.05 var(--font-display); letter-spacing: -.02em; }
	.summary { min-height: 3rem; max-width: 29ch; margin: .65rem 0 1.15rem; color: var(--ink-2); font-size: .98rem; line-height: 1.45; }
	.price { display: flex; align-items: baseline; flex-wrap: wrap; gap: .3rem .5rem; margin: 0; padding-bottom: 1rem; border-bottom: 1px solid #93867375; }
	.price strong { font: 700 clamp(2rem,3.2vw,2.7rem)/1 var(--font-display); letter-spacing: -.03em; font-variant-numeric: tabular-nums; }
	.price span { color: var(--ink-2); font-size: .85rem; font-weight: 800; }
	.card ul { display: grid; align-content: start; gap: .8rem; flex: 1; margin: 1.25rem 0 1.8rem; padding: 0; list-style: none; }
	.card li { position: relative; padding-left: 1.65rem; font-size: .9rem; font-weight: 700; line-height: 1.35; }
	.card li::before { content: '✓'; position: absolute; left: 0; top: -.08rem; display: grid; place-items: center; width: 1.1rem; height: 1.1rem; border-radius: 50%; background: #dbeadf; color: #145439; font: 900 .73rem var(--font-body); }
	.premium li::before { background: #e2d6ff; color: #53329e; }
	.family li::before { background: #fce1cf; color: #8b4038; }
	.choose { display: flex; align-items: center; justify-content: space-between; gap: .7rem; min-height: 3.25rem; padding: .68rem 1rem; border-radius: 11px; background: var(--button-bg); color: #fff; font: 700 .96rem var(--font-display); text-decoration: none; transition: filter 160ms ease; }
	.game-catalog { margin-top: 1.6rem; padding: clamp(1.2rem,2.5vw,2rem); border: 1px solid #63513b; border-radius: 17px; background: #fffaf0; box-shadow: 0 11px 24px #4e34231d; }
	.catalog-heading { display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin-bottom: 1.15rem; }
	.catalog-heading h3 { max-width: 25ch; margin: 0; font: 700 clamp(1.3rem,2.4vw,1.9rem)/1.1 var(--font-display); text-wrap: balance; }
	.catalog-heading p { margin: .4rem 0 0; color: var(--ink-2); font-size: .88rem; line-height: 1.4; }
	.catalog-heading > span { flex: none; padding: .4rem .7rem; border-radius: 999px; background: #e7dcfa; color: #50348b; font-size: .76rem; font-weight: 900; }
	.game-list { display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap: 0 1rem; margin: 0; padding: 0; list-style: none; }
	.game-list li { position: relative; min-width: 0; padding: .63rem .2rem .63rem 1.15rem; border-top: 1px solid #e5d9c6; font-size: .87rem; font-weight: 800; line-height: 1.25; }
	.game-list li::before { content: ''; position: absolute; left: .15rem; top: 1.02rem; width: .5rem; height: .5rem; border-radius: 50%; background: var(--game-color); }
	.more-games { margin: .85rem 0 0; padding-top: .9rem; border-top: 1px solid #c9baa6; color: var(--ink-2); font-size: .87rem; line-height: 1.5; }
	.more-games strong { margin-right: .4rem; color: var(--ink); }
	.payment-note { max-width: 75ch; margin: 1.4rem 0 0; color: var(--ink-2); font-weight: 700; line-height: 1.55; }
	.payment-note a { color: var(--brand-deep); text-underline-offset: 3px; }
	.plan-land :is(a,button):focus-visible { outline: 3px solid #6543b9; outline-offset: 3px; }
	.loading { padding: 2rem 0; font-weight: 800; }
	@keyframes peek { 0%,82%,100% { transform: rotate(0); } 87% { transform: rotate(-5deg); } 94% { transform: rotate(4deg); } }
	@media (hover:hover) and (pointer:fine) {
		.card:not(.premium):hover { transform: translateY(-5px); box-shadow: 0 18px 32px #4e342334,0 4px 7px #4e342320; }
		.card.premium:hover { transform: translateY(-13px); box-shadow: 0 26px 40px #40245945,0 5px 9px #40245928; }
		.card:hover .card-art :global(img), .card:hover .card-art :global(svg) { transform: translateY(-5px) rotate(-5deg); }
		.choose:hover { filter: brightness(1.12); }
	}
	@media (max-width: 880px) {
		.cards { grid-template-columns: 1fr; max-width: 36rem; margin-inline: auto; gap: 1.15rem; }
		.card.premium { transform: none; }
		.card.premium:hover { transform: translateY(-5px); }
		.card-art { height: 120px; }
		.summary { min-height: 0; }
		.heading { align-items: center; }
		.mascot { width: 80px; overflow: hidden; }
		.controls { align-items: start; flex-direction: column; }
		.game-list { grid-template-columns: repeat(2,minmax(0,1fr)); }
	}
	@media (max-width: 500px) {
		.plan-land { padding-top: 3.5rem; }
		.mascot { display: none; }
		.controls { margin-top: 1.5rem; }
		.card-body { padding: 1.2rem; }
		.period { width: 100%; }
		.period button { flex: 1; }
		.copy h2 { max-width: 15ch; }
		.catalog-heading { align-items: start; flex-direction: column; }
		.game-list { gap: 0 .6rem; }
		.game-list li { font-size: .78rem; }
	}
	@media (prefers-reduced-motion: reduce) {
		.mascot { animation: none; }
		.card, .card-art :global(img), .card-art :global(svg), .choose { transition: none; }
	}
</style>
