<!--
	Langkah Wuduk: a tap pours a stream down past a droplet for each step. Put the steps in their tertib;
	when they are all right, the water runs. Each step shows the part of the body it washes.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	const PARTS: [RegExp, string][] = [
		[/niat|basmalah|bismillah/i, 'tangan-doa'],
		[/kumur|mulut/i, 'mulut'],
		[/hidung|istinsyaq/i, 'hidung'],
		[/telinga/i, 'telinga'],
		[/kaki|lali/i, 'kaki'],
		[/tangan|siku|lengan/i, 'tangan'],
		[/muka|wajah/i, 'mata']
	];
	const part = (text: string) => PARTS.find(([re]) => re.test(text))?.[1] ?? 'air';
</script>

<OrderPlay {p} pic={part} pool="Langkah" tip="Ikut tertib dari atas. Ketik atau seret ke titisan air.">
	{#snippet board(v: OrderView)}
		<div class="basin" class:flow={v.allRight}>
			<div class="tap" aria-hidden="true"><span class="spout"></span></div>
			<div class="stream" aria-hidden="true"></div>
			<ol class="drops">
				{#each v.slots as id, i (i)}
					{@const ok = v.ok(i)}
					<li class="row" data-zone={v.zone(i)}>
						<span class="drop" class:filled={!!id}>{i + 1}</span>
						{#if id}
							<button type="button" class="step" disabled={v.locked} {@attach v.grab(i)} aria-label="{v.text(id)}, langkah {i + 1}">
								<Sticker key={part(v.text(id))} size={34} alt="" />
								<span>{v.text(id)}</span>
								{#if ok !== null}<Mark {ok} />{/if}
							</button>
							{#if v.should(i)}<span class="should">→ {v.should(i)}</span>{/if}
						{:else}
							<span class="empty">Langkah {i + 1}</span>
						{/if}
					</li>
				{/each}
			</ol>
			<div class="pool" aria-hidden="true"></div>
		</div>
	{/snippet}
</OrderPlay>

<style>
	.basin {
		position: relative;
		padding: 3.4rem 0.8rem 2rem 3.4rem;
		border-radius: var(--r-lg);
		background:
			linear-gradient(90deg, rgb(255 255 255 / 0.5) 0 2px, transparent 2px) 0 0 / 28px 28px,
			linear-gradient(180deg, rgb(255 255 255 / 0.5) 0 2px, transparent 2px) 0 0 / 28px 28px,
			#dff3f7;
		box-shadow: inset 0 0 0 3px #a9d8e3;
		overflow: hidden;
	}
	.tap {
		position: absolute;
		left: 0.6rem;
		top: 0.5rem;
		width: 2.6rem;
		height: 1.6rem;
		border-radius: 0.5rem 0.5rem 0.3rem 0.3rem;
		background: linear-gradient(180deg, #e9edf2, #9aa3ad);
		box-shadow: inset 0 -3px 0 rgb(0 0 0 / 0.15);
	}
	.spout {
		position: absolute;
		left: 0.85rem;
		top: 1.4rem;
		width: 0.9rem;
		height: 1rem;
		border-radius: 0 0 0.3rem 0.3rem;
		background: linear-gradient(90deg, #b8c0ca, #e9edf2, #b8c0ca);
	}
	.stream {
		position: absolute;
		left: 1.55rem;
		top: 2.9rem;
		bottom: 1rem;
		width: 0.7rem;
		border-radius: 0.4rem;
		background: linear-gradient(180deg, rgb(120 200 240 / 0.25), rgb(120 200 240 / 0.15));
	}
	.flow .stream {
		background: repeating-linear-gradient(180deg, #7fd0f2 0 10px, #b9e8fb 10px 20px);
		background-size: 100% 40px;
		animation: run 0.6s linear infinite;
	}
	.pool {
		position: absolute;
		left: 0.4rem;
		right: 0.4rem;
		bottom: 0;
		height: 0.9rem;
		border-radius: 50% 50% 0 0;
		background: linear-gradient(180deg, #8fd6f5, #55b6e3);
		opacity: 0.4;
		transition: opacity 0.5s;
	}
	.flow .pool {
		opacity: 1;
	}
	.drops {
		display: grid;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.row {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.4rem;
		min-height: 3.2rem;
		padding: 0.3rem 0.5rem;
		border: 2px dashed #8ccbe0;
		border-radius: 12px;
		background: rgb(255 255 255 / 0.6);
	}
	.row:global(.zone-hover) {
		border-color: #1f8fc0;
		background: #fff;
	}
	.drop {
		position: absolute;
		left: -2.65rem;
		top: 50%;
		translate: 0 -50%;
		display: grid;
		place-items: center;
		width: 1.9rem;
		height: 1.9rem;
		border-radius: 50% 0 50% 50%;
		rotate: -45deg;
		background: #cfeefa;
		color: #1f6f95;
		font: 700 0.85rem var(--font-display);
		box-shadow: inset 0 0 0 2px #8ccbe0;
	}
	.drop.filled {
		background: radial-gradient(circle at 35% 30%, #e9f8ff, #4fb3e3);
		color: #fff;
	}
	.step {
		position: relative;
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		padding: 0;
		border: 0;
		background: transparent;
		color: #10394d;
		font: 700 0.95rem/1.15 var(--font-body);
		text-align: left;
		cursor: grab;
		touch-action: none;
	}
	.step:disabled {
		cursor: default;
	}
	.empty {
		color: #5b97ad;
		font-weight: 700;
		font-size: 0.88rem;
	}
	.should {
		color: #8a2a00;
		font-weight: 800;
		font-size: 0.82rem;
	}
	@keyframes run {
		to {
			background-position: 0 40px;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.flow .stream {
			animation: none;
		}
	}
</style>
