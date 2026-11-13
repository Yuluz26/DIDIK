<!--
	Bina Empayar: a Malay palace raised floor by floor, the first answer as its stone foundation and the last
	under its tiered roof. Each floor is laid with an answer; when all are right, the flags fly.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();
	import { asset } from '../assets';
	// the reconstructed Malacca Sultanate Palace, the kind of building the floors raise
	const PALACE = asset('hist/palace');
</script>

<OrderPlay {p} pool="Bahan binaan" tip="Tingkat 1 ialah asas di bawah. Bina ke atas.">
	{#snippet board(v: OrderView)}
		{@const n = v.slots.length}
		<div class="site" class:won={v.allRight} style:--palace={PALACE ? `url(${PALACE.src})` : 'none'}>
			<div class="palace">
				<div class="roof" aria-hidden="true">
					<span class="tier t1"></span><span class="tier t2"></span><span class="tier t3"></span>
					<span class="flag f1"></span><span class="flag f2"></span>
				</div>
				{#each [...v.slots.keys()].reverse() as i (i)}
					{@const id = v.slots[i]}
					{@const ok = v.ok(i)}
					<div class="floor" class:filled={!!id} class:base={i === 0} style:--w="{70 + ((i === 0 ? n : n - i) / n) * 30}%" data-zone={v.zone(i)}>
						<span class="n">{i + 1}</span>
						{#if id}
							<button type="button" class="stone" disabled={v.locked} {@attach v.grab(i)} aria-label="{v.text(id)}, tingkat {i + 1}">
								{v.text(id)}
								{#if ok !== null}<Mark {ok} />{/if}
							</button>
							{#if v.should(i)}<span class="should">→ {v.should(i)}</span>{/if}
						{:else}
							<span class="empty">{i === 0 ? 'Asas' : `Tingkat ${i + 1}`}</span>
						{/if}
					</div>
				{/each}
			</div>
			<span class="tree" aria-hidden="true"><Sticker key="pokok-kelapa" size={58} alt="" /></span>
			<p class="real">Istana Kesultanan Melaka seperti dibina semula di Bandar Hilir, Melaka</p>
		</div>
	{/snippet}
</OrderPlay>

<style>
	.site {
		background-image: linear-gradient(180deg, rgb(255 248 230 / 0.7), rgb(255 248 230 / 0.35) 60%, rgb(80 60 20 / 0.25)), var(--palace) !important;
		background-size: cover !important;
		background-position: center 30% !important;
	}
	.real {
		position: relative;
		margin: 0.3rem auto 0;
		width: fit-content;
		padding: 0.1rem 0.6rem;
		border-radius: 999px;
		background: rgb(255 248 230 / 0.92);
		color: #5a4318;
		font: 700 0.7rem/1.3 var(--font-body);
		text-align: center;
	}
	.site {
		position: relative;
		padding: 1rem 0.6rem 0;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #ffe7c4 0%, #fff6e6 60%, #c9a46a 60.5%, #b98d52 100%);
		box-shadow: inset 0 0 0 3px #a57b43;
		overflow: hidden;
	}
	.palace {
		position: relative;
		z-index: 1;
		display: grid;
		justify-items: center;
		padding-bottom: 0.6rem;
	}
	.roof {
		position: relative;
		width: 82%;
		height: 4.6rem;
	}
	.tier {
		position: absolute;
		left: 50%;
		translate: -50% 0;
		clip-path: polygon(50% 0, 100% 100%, 0 100%);
		background: linear-gradient(180deg, #8f3a1f, #5e2412);
	}
	.t1 {
		bottom: 0;
		width: 100%;
		height: 2.4rem;
	}
	.t2 {
		bottom: 1.4rem;
		width: 72%;
		height: 2.2rem;
		background: linear-gradient(180deg, #a8472a, #6f2b16);
	}
	.t3 {
		bottom: 2.7rem;
		width: 44%;
		height: 1.9rem;
		background: linear-gradient(180deg, #c45a35, #81321a);
	}
	.flag {
		position: absolute;
		bottom: 4.2rem;
		width: 2px;
		height: 1.6rem;
		background: #5a3a1a;
		opacity: 0;
		transition: opacity 0.4s;
	}
	.flag::after {
		content: '';
		position: absolute;
		left: 2px;
		top: 0;
		width: 1.1rem;
		height: 0.7rem;
		background: #f5c518;
		clip-path: polygon(0 0, 100% 50%, 0 100%);
		animation: wave 0.8s ease-in-out infinite alternate;
	}
	.f1 {
		left: 44%;
	}
	.f2 {
		left: 56%;
	}
	.won .flag {
		opacity: 1;
	}
	.floor {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: center;
		gap: 0.3rem;
		width: var(--w);
		min-height: 3.2rem;
		padding: 0.35rem 0.5rem 0.35rem 2rem;
		border: 2px dashed #a57b43;
		border-bottom: 0;
		background: rgb(255 248 230 / 0.5);
	}
	.floor.filled {
		border: 0;
		border-top: 3px solid #6b4423;
		background:
			repeating-linear-gradient(90deg, transparent 0 22px, rgb(90 55 20 / 0.25) 22px 24px),
			linear-gradient(180deg, #f1d39c, #d9ae6a);
		box-shadow: inset 0 -4px 0 rgb(90 55 20 / 0.25);
		animation: lay 0.35s var(--spring, ease-out);
	}
	.floor.base.filled {
		background:
			repeating-linear-gradient(90deg, transparent 0 30px, rgb(60 60 60 / 0.3) 30px 32px),
			linear-gradient(180deg, #c8c3b8, #9d978a);
	}
	.floor:global(.zone-hover) {
		outline: 3px solid #f0a400;
		outline-offset: -3px;
	}
	.n {
		position: absolute;
		left: 0.4rem;
		top: 50%;
		translate: 0 -50%;
		display: grid;
		place-items: center;
		width: 1.4rem;
		height: 1.4rem;
		border-radius: 50%;
		background: #6b4423;
		color: #fff;
		font: 700 0.75rem var(--font-display);
	}
	.stone {
		position: relative;
		padding: 0.25rem 0.6rem;
		border: 0;
		border-radius: 6px;
		background: rgb(255 255 255 / 0.8);
		color: #3d2410;
		font: 700 0.95rem/1.15 var(--font-body);
		cursor: grab;
		touch-action: none;
	}
	.stone:disabled {
		cursor: default;
	}
	.empty {
		color: #8a6538;
		font-weight: 700;
		font-size: 0.85rem;
	}
	.should {
		color: #8a2a00;
		font-weight: 800;
		font-size: 0.82rem;
	}
	.tree {
		position: absolute;
		left: 0.2rem;
		bottom: 0.3rem;
		opacity: 0.9;
	}
	@keyframes lay {
		from {
			transform: translateY(-14px);
			opacity: 0;
		}
	}
	@keyframes wave {
		to {
			transform: skewY(8deg) scaleX(0.85);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.floor.filled,
		.flag::after {
			animation: none;
		}
	}
</style>
