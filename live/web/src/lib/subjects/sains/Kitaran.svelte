<!--
	Roda Kitaran: a wheel of stages round a turning arrow (a life cycle, the water cycle, the Moon's
	phases). Place 1 is at the top; the cycle runs clockwise and back to the start. Each stage is a real
	photograph (frog spawn, a tadpole; steam, a cloud, rain), and the Moon's phases are drawn on the real
	Moon. What is at the hub belongs to the cycle: the Earth the Moon goes round, the Sun that drives the
	water cycle. The server gives this game only to stages that all belong to one cycle it knows.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import GameImage from '../GameImage.svelte';
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import { cycleOf, stageOf } from '../assets';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	const cycle = $derived(cycleOf((p.question.items ?? []).map((i) => i.text)));
	const stage = (text: string) => stageOf(cycle, text);
	const HUB: Record<string, [string, string]> = { bulan: ['space/earth', 'Bumi'], air: ['space/sun', 'Matahari'] };
	const NAMES: Record<string, string> = { katak: 'Kitaran hidup katak', 'rama-rama': 'Kitaran hidup rama-rama', ayam: 'Kitaran hidup ayam', tumbuhan: 'Kitaran hidup tumbuhan', air: 'Kitaran air', bulan: 'Fasa Bulan' };

	const at = (i: number, n: number) => {
		const a = (-90 + (i * 360) / n) * (Math.PI / 180);
		return { x: 50 + Math.cos(a) * 36, y: 50 + Math.sin(a) * 36 };
	};
</script>

<OrderPlay {p} pool="Peringkat" tip="Peringkat 1 di atas, kemudian ikut arah jam.">
	{#snippet thing(item)}
		<span class="mini" class:night={cycle === 'bulan'}>
			<GameImage name={stage(item.text)?.key} fit="cover">
				{#snippet fallback()}<span class="dot">{item.text.slice(0, 1)}</span>{/snippet}
			</GameImage>
		</span>
		<span>{item.text}</span>
	{/snippet}
	{#snippet board(v: OrderView)}
		{@const n = v.slots.length}
		<div class="wheel" class:spin={v.allRight}>
			<svg class="track" viewBox="0 0 100 100" aria-hidden="true">
				<defs>
					<marker id="kitaran-head" viewBox="0 0 6 6" refX="3" refY="3" markerWidth="4" markerHeight="4" orient="auto">
						<path d="M0 0 L6 3 L0 6 z" fill="#2f9e8f" />
					</marker>
				</defs>
				{#each v.slots as _, i (i)}
					{@const a0 = (-90 + (i * 360) / n + 360 / n / 3.2) * (Math.PI / 180)}
					{@const a1 = (-90 + ((i + 1) * 360) / n - 360 / n / 3.2) * (Math.PI / 180)}
					<path
						d="M {50 + Math.cos(a0) * 36} {50 + Math.sin(a0) * 36} A 36 36 0 0 1 {50 + Math.cos(a1) * 36} {50 + Math.sin(a1) * 36}"
						fill="none"
						stroke="#2f9e8f"
						stroke-width="2.4"
						stroke-linecap="round"
						marker-end="url(#kitaran-head)"
					/>
				{/each}
			</svg>
			<span class="hub" aria-hidden="true">
				{#if cycle && HUB[cycle]}
					<span class="hub-pic"><GameImage name={HUB[cycle][0]} eager /></span>
					<b>{HUB[cycle][1]}</b>
				{:else}
					<b class="hub-name">{(cycle && NAMES[cycle]) || 'Kitaran'}</b>
				{/if}
			</span>
			{#each v.slots as id, i (i)}
				{@const pos = at(i, n)}
				{@const ok = v.ok(i)}
				<div class="stage" class:filled={!!id} style:left="{pos.x}%" style:top="{pos.y}%" data-zone={v.zone(i)}>
					<span class="n">{i + 1}</span>
					{#if id}
						<button type="button" class="thing" disabled={v.locked} {@attach v.grab(i)} aria-label="{v.text(id)}, peringkat {i + 1}">
							<span class="shot" class:night={cycle === 'bulan'}>
								<GameImage name={stage(v.text(id))?.key} eager fit="cover">
									{#snippet fallback()}{#if v.sticker(id)}<Sticker key={v.sticker(id) ?? ''} size={34} alt="" />{/if}{/snippet}
								</GameImage>
							</span>
							<span>{v.text(id)}</span>
							{#if ok !== null}<Mark {ok} />{/if}
						</button>
					{/if}
				</div>
			{/each}
		</div>
		{#if v.slots.some((_, i) => v.should(i))}
			<ol class="fix">
				{#each v.slots as _, i (i)}{#if v.should(i)}<li><b>{i + 1}</b> sepatutnya {v.should(i)}</li>{/if}{/each}
			</ol>
		{/if}
	{/snippet}
</OrderPlay>

<style>
	/* the stages are sized from the wheel, so the ones at the sides stay on it on a small phone */
	.wheel {
		container-type: inline-size;
		position: relative;
		width: min(100%, 24rem);
		aspect-ratio: 1;
		margin-inline: auto;
		border-radius: 50%;
		background: radial-gradient(circle, #f4fffb 0 30%, #dff6ef 31% 58%, #c8eee2 59%);
		box-shadow:
			inset 0 0 0 3px #9edccb,
			0 8px 22px rgb(30 110 95 / 0.15);
	}
	.track {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
	}
	.spin .track {
		animation: turn 6s linear infinite;
	}
	.hub {
		position: absolute;
		left: 50%;
		top: 50%;
		translate: -50% -50%;
		filter: drop-shadow(0 4px 6px rgb(0 0 0 / 0.15));
	}
	.hub {
		display: grid;
		justify-items: center;
		gap: 0.1rem;
		color: #1d5c52;
		font: 700 0.72rem var(--font-display);
		text-align: center;
	}
	.hub-pic {
		width: 3.6rem;
	}
	.hub-pic :global(img) {
		width: 100%;
	}
	.hub-name {
		max-width: 5.5rem;
		font-size: 0.82rem;
		line-height: 1.15;
	}
	/* a real photograph of the stage */
	.shot,
	.mini {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.7rem;
		height: 2.7rem;
		overflow: hidden;
		border-radius: 0.7rem;
		background: #eef6f3;
	}
	.shot.night,
	.mini.night {
		border-radius: 50%;
		background: #070b18;
	}
	.shot :global(img.g-img),
	.mini :global(img.g-img) {
		width: 100%;
		height: 100%;
	}
	.mini {
		width: 2.4rem;
		height: 2.4rem;
	}
	.dot {
		color: #2f9e8f;
		font: 700 1.1rem var(--font-display);
	}
	.stage {
		position: absolute;
		display: grid;
		place-items: center;
		width: min(5.6rem, 26cqi);
		min-height: 3.6rem;
		translate: -50% -50%;
		border: 3px dashed #63bfae;
		border-radius: 1.2rem;
		background: rgb(255 255 255 / 0.85);
	}
	.stage.filled {
		border-style: solid;
		border-color: #2f9e8f;
		background: #fff;
		box-shadow: 0 4px 10px rgb(30 110 95 / 0.2);
	}
	.stage:global(.zone-hover) {
		border-color: #f0a400;
		transform: scale(1.06);
	}
	.n {
		position: absolute;
		top: -0.7rem;
		left: -0.15rem;
		display: grid;
		place-items: center;
		width: 1.5rem;
		height: 1.5rem;
		border-radius: 50%;
		background: #2f9e8f;
		color: #fff;
		font: 700 0.8rem var(--font-display);
	}
	.thing {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.1rem;
		width: 100%;
		padding: 0.25rem 0.2rem;
		border: 0;
		background: transparent;
		color: var(--ink);
		font: 700 0.78rem/1.1 var(--font-body);
		text-align: center;
		cursor: grab;
		touch-action: none;
		overflow-wrap: anywhere;
	}
	.thing:disabled {
		cursor: default;
	}
	.fix {
		display: grid;
		gap: 0.2rem;
		margin: 0;
		padding: 0.5rem 0.8rem;
		border-radius: var(--r-md);
		background: var(--almost-soft, #fff1e6);
		color: var(--on-almost-soft, #8a3b12);
		font-weight: 700;
		list-style: none;
	}
	@keyframes turn {
		to {
			rotate: 360deg;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.spin .track {
			animation: none;
		}
	}
</style>
