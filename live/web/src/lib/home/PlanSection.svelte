<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import Icon from '$ui/Icon.svelte';
	import Didi from '$ui/Didi.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import { reveal } from './reveal';

	let { beach }: { beach: string } = $props();
	type Interval = 'monthly' | 'yearly';
	type Plan = { key: string; pricesSen: { monthly: number; yearly: number } };
	let plans = $state<Record<string, Plan>>({});
	let interval = $state<Interval>('monthly');
	let failed = $state(false);
	const money = (sen: number) => `RM${(sen / 100).toFixed(2)}`;
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
			<div class="copy"><h2 id="pelan-title">Pilih cara keluarga bermain</h2><p>Mulakan dengan kuiz percuma. Bila bersedia menjelajah lebih jauh, ada pelan untuk satu anak atau seisi rumah.</p></div>
			<div class="mascot" aria-hidden="true"><Didi mood="happy" size={104} /></div>
		</div>
		<div class="controls" {@attach reveal(70)}><span>Harga rasmi dalam Ringgit Malaysia</span><div class="period" role="group" aria-label="Tempoh keahlian"><button type="button" class:active={interval === 'monthly'} aria-pressed={interval === 'monthly'} onclick={() => interval = 'monthly'}>Bulanan</button><button type="button" class:active={interval === 'yearly'} aria-pressed={interval === 'yearly'} onclick={() => interval = 'yearly'}>Tahunan</button></div></div>
		{#if failed}<p role="alert">Harga tidak dapat dimuat. <a href="/keahlian">Buka halaman keahlian</a> untuk cuba lagi.</p>{:else if !plans.free}<p class="loading" aria-busy="true">Memuatkan pelan…</p>{:else}
			<div class="cards">
				<article class="card free" {@attach reveal(90)}><div class="card-top"><div class="art"><Sticker key="awan" size={64} alt="" /></div><span class="label">Mula di sini</span></div><h3>Free</h3><p class="amount">{money(plans.free.pricesSen.monthly)} <small>selamanya</small></p><p class="summary">Ruang pertama untuk cuba, tulis dan main bersama.</p><ul><li>Satu profil anak</li><li>Kuiz contoh dan Interaktif asas</li><li>Keputusan kuiz asas</li></ul><a class="choose" href="/ibu-bapa">Daftar percuma <Icon name="next" size={18} /></a></article>
				<article class="card premium" {@attach reveal(150)}><div class="card-top"><div class="art"><Sticker key="bintang-bersinar" size={68} alt="" /></div><span class="label">Pengembaraan penuh</span></div><h3>Premium</h3><p class="amount">{money(plans.premium.pricesSen[interval])} <small>/{interval === 'monthly' ? 'bulan' : 'tahun'}</small></p><p class="summary">Satu anak, semua dunia permainan DIDIK.</p><ul><li>Satu profil anak</li><li>Semua 14 permainan 2D</li><li>Hikayat Lima Alam dan hos bilik</li></ul><a class="choose" href="/ibu-bapa/keahlian">Pilih Premium <Icon name="next" size={18} /></a></article>
				<article class="card family" {@attach reveal(210)}><div class="card-top"><div class="art"><Sticker key="rumah" size={68} alt="" /></div><span class="label">Untuk seisi rumah</span></div><h3>Family</h3><p class="amount">{money(plans.family.pricesSen[interval])} <small>/{interval === 'monthly' ? 'bulan' : 'tahun'}</small></p><p class="summary">Lebih ramai anak, satu keahlian keluarga.</p><ul><li>Sehingga tiga profil anak</li><li>Semua ciri Premium</li><li>Story Mode Solo dan Party</li></ul><a class="choose" href="/ibu-bapa/keahlian">Pilih Family <Icon name="next" size={18} /></a></article>
			</div>
		{/if}
		<p class="payment-note" {@attach reveal(230)}>Premium dan Family dibayar melalui QR bagi setiap tempoh. Hantar bukti ke WhatsApp DIDIK; akses aktif selepas semakan admin. Tiada pembaharuan atau caj automatik. <a href="/keahlian">Lihat semua butiran pelan</a>.</p>
	</div>
</section>

<style>
	.plan-land{position:relative;background:var(--beach) 0 0 / calc(var(--px) * 64) calc(var(--px) * 64);color:var(--ink);padding:clamp(4rem,8vw,7rem) 0 clamp(5rem,9vw,8rem);overflow:hidden}
	.inner{position:relative}.heading{display:flex;align-items:end;justify-content:space-between;gap:2rem}.copy{max-width:43rem}.copy h2{font:700 clamp(2rem,4vw,3.6rem)/1.04 var(--font-display);letter-spacing:-.02em;max-width:17ch}.copy p{font-size:clamp(1rem,1.3vw,1.2rem);line-height:1.55;max-width:55ch;margin-top:1rem;color:var(--ink-2)}.mascot{flex:none;transform-origin:50% 100%;animation:peek 5s cubic-bezier(.77,0,.175,1) infinite}.controls{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin:2.2rem 0 1.3rem}.controls>span{font-weight:800;color:var(--ink-2)}.period{display:flex;gap:.2rem;border:2px solid var(--edge);border-radius:999px;padding:.2rem;background:var(--paper);box-shadow:0 3px 0 #c9ae74}.period button{border:0;border-radius:999px;background:transparent;color:var(--ink);padding:.6rem 1.1rem;font:800 .95rem var(--font-body);cursor:pointer;transition:background-color 180ms ease,color 180ms ease,transform 160ms cubic-bezier(.23,1,.32,1)}.period button.active{background:var(--ink);color:var(--paper)}.period button:active{transform:scale(.97)}
	.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));align-items:stretch;gap:1rem}.card{--panel:#fff8ec;--button:#1f2d27;--button-ink:#fff8ec;display:flex;flex-direction:column;min-width:0;padding:clamp(1.3rem,2.2vw,2rem);border:2px solid var(--edge);border-radius:20px;background:var(--panel);box-shadow:0 5px 0 var(--edge);transition:transform 220ms cubic-bezier(.23,1,.32,1),box-shadow 220ms cubic-bezier(.23,1,.32,1)}.card.premium{--panel:#e8ddff;--button:#6442b9;--button-ink:#fff;position:relative;z-index:1}.card.family{--panel:#ffe1cf;--button:#963d36;--button-ink:#fff}.card-top{display:flex;align-items:start;justify-content:space-between;gap:.5rem;min-height:5rem}.art{transform-origin:50% 80%;transition:transform 220ms cubic-bezier(.23,1,.32,1)}.label{border:1px solid var(--edge);border-radius:999px;padding:.35rem .7rem;font:800 .75rem var(--font-body);background:rgb(255 255 255 / .55);white-space:nowrap}.card h3{font:700 clamp(1.65rem,2.6vw,2.25rem)/1.1 var(--font-display);margin:.8rem 0 0}.amount{font:700 clamp(1.8rem,3vw,2.5rem)/1.15 var(--font-display);margin:.55rem 0 0;font-variant-numeric:tabular-nums;white-space:nowrap}.amount small{font:700 .94rem var(--font-body);color:var(--ink-2)}.summary{min-height:3.1rem;line-height:1.5;color:var(--ink-2);margin:.75rem 0 0}.card ul{display:grid;gap:.65rem;list-style:none;margin:1.2rem 0 1.6rem;padding:0;flex:1}.card li{position:relative;padding-left:1.55rem;line-height:1.35;font-weight:700}.card li::before{content:'';position:absolute;left:.25rem;top:.32rem;width:.55rem;height:.55rem;border-radius:50%;background:var(--brand-deep)}.choose{display:flex;align-items:center;justify-content:space-between;gap:.7rem;min-height:3.2rem;padding:.65rem 1rem;border-radius:12px;background:var(--button);color:var(--button-ink);font:700 1rem var(--font-display);text-decoration:none;transition:transform 160ms cubic-bezier(.23,1,.32,1),background-color 160ms ease}.choose:active{transform:scale(.97)}.payment-note{max-width:75ch;margin:1.8rem 0 0;line-height:1.55;color:var(--ink-2);font-weight:700}.payment-note a{color:var(--brand-deep);text-underline-offset:3px}.plan-land :is(a,button):focus-visible{outline:3px solid #6543b9;outline-offset:3px}.loading{padding:2rem 0;font-weight:800}
	@keyframes peek{0%,82%,100%{transform:rotate(0)}87%{transform:rotate(-5deg)}94%{transform:rotate(4deg)}}
	@media(hover:hover) and (pointer:fine){.card:hover{transform:translateY(-5px);box-shadow:0 10px 0 var(--edge)}.card:hover .art{transform:rotate(-8deg) scale(1.06)}.choose:hover{transform:translateY(-2px)}}
	@media(max-width:880px){.cards{grid-template-columns:1fr;max-width:36rem;margin-inline:auto}.card{min-height:0}.card-top{min-height:0}.summary{min-height:0}.heading{align-items:center}.mascot{width:80px;overflow:hidden}.controls{align-items:start;flex-direction:column}}
	@media(max-width:500px){.plan-land{padding-top:3.5rem}.mascot{display:none}.controls{margin-top:1.5rem}.card{padding:1.25rem}.period{width:100%}.period button{flex:1}.label{font-size:.7rem}.copy h2{max-width:15ch}}
	@media(prefers-reduced-motion:reduce){.mascot{animation:none}.card,.art,.choose,.period button{transition:background-color 180ms ease,color 180ms ease}.card:hover,.card:hover .art,.choose:hover,.card:active,.choose:active{transform:none}}
</style>
