<!--
	Orbit Planet: the Sun (a real image from the Solar Dynamics Observatory) at the top of a dark sky, and
	round it one true circle after another, each further out. Every orbit has one place on it; put each
	planet on its orbit, the nearest to the Sun first. The planets are their real pictures, from the
	spacecraft that visited them.

	The server gives this game only to questions that put bodies of the Solar System in their order from
	the Sun (lexicon "space"), so the picture never says something the question does not. Sizes and
	distances are not to scale, and the board says so.
-->
<script lang="ts">
	import GameImage from '../GameImage.svelte';
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import { asset, find, type Entry } from '../assets';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	interface Body extends Entry {
		wide?: boolean;
	}
	const body = (text: string) => find<Body>('space', text);

	// The Sun's centre sits just above the board; orbit i is a circle of radius R0 + i·GAP round it (rem).
	// Each orbit's place is a little to one side then the other, so the names never stack up.
	const CY = -1.5;
	const R0 = 5.6;
	const GAP = 3.9;
	const SIDE = [-23, 19, -13, 13, -9, 10];
	const radius = (i: number) => R0 + i * GAP;
	const place = (i: number) => {
		const a = (SIDE[i % SIDE.length] * Math.PI) / 180;
		return { x: Math.sin(a) * radius(i), y: CY + Math.cos(a) * radius(i) };
	};
	const SKY = asset('space/milkyway');
</script>

<OrderPlay {p} pool="Planet" tip="Ketik planet untuk letak pada orbit kosong yang terdekat dengan Matahari, atau seret ke orbitnya.">
	{#snippet thing(item)}
		<span class="mini" class:wide={body(item.text)?.wide}>
			<GameImage name={body(item.text)?.key} eager>
				{#snippet fallback()}<i class="rock"></i>{/snippet}
			</GameImage>
		</span>
		<span>{item.text}</span>
	{/snippet}
	{#snippet board(v: OrderView)}
		{@const n = v.slots.length}
		<div class="space" class:done={v.allRight} style:--sky={SKY ? `url(${SKY.src})` : 'none'} style:height="{CY + radius(n - 1) + 4.7}rem">
			{#each v.slots as _, i (i)}
				<span class="ring" style:--r="{radius(i)}rem" style:top="{CY}rem" style:--i={i} aria-hidden="true"></span>
			{/each}
			<span class="sun" style:top="{CY}rem" aria-hidden="true"><GameImage name="space/sun" eager /></span>
			<span class="sun-name">Matahari</span>

			<ol class="places">
				{#each v.slots as id, i (i)}
					{@const at = place(i)}
					{@const b = id ? body(v.text(id)) : undefined}
					{@const ok = v.ok(i)}
					<li class="place" class:left={at.x < 0} data-zone={v.zone(i)} style:left="calc(50% + {at.x}rem)" style:top="{at.y}rem">
						{#if id}
							<button
								type="button"
								class="planet"
								class:wide={b?.wide}
								class:ok={ok === true}
								class:off={ok === false}
								disabled={v.locked}
								{@attach v.grab(i)}
								aria-label="{v.text(id)} pada orbit {i + 1}. Ketik untuk keluarkan"
							>
								<span class="globe">
									<GameImage name={b?.key} eager>
										{#snippet fallback()}<i class="rock"></i>{/snippet}
									</GameImage>
									{#if ok !== null}<Mark {ok} />{/if}
								</span>
								<span class="name">{v.text(id)}</span>
							</button>
							{#if v.should(i)}<span class="should">→ {v.should(i)}</span>{/if}
						{:else}
							<span class="empty"><b>{i + 1}</b></span>
							<span class="hint">{i === 0 ? 'Terdekat' : i === n - 1 ? 'Terjauh' : `Orbit ${i + 1}`}</span>
						{/if}
					</li>
				{/each}
			</ol>
			<p class="scale">Saiz dan jarak bukan mengikut skala</p>
		</div>
	{/snippet}
</OrderPlay>

<style>
	.space {
		position: relative;
		overflow: hidden;
		border-radius: var(--r-lg);
		background:
			radial-gradient(60% 34% at 50% 0%, rgb(255 150 40 / 0.28), transparent 70%),
			linear-gradient(180deg, rgb(3 5 16 / 0.72), rgb(3 5 16 / 0.86)),
			var(--sky) 50% 50% / cover no-repeat,
			#05070f;
		box-shadow: inset 0 0 0 3px #171d3a;
	}
	.ring {
		position: absolute;
		left: 50%;
		width: calc(var(--r) * 2);
		height: calc(var(--r) * 2);
		translate: -50% -50%;
		border: 1.5px solid rgb(160 190 255 / 0.32);
		border-radius: 50%;
		pointer-events: none;
	}
	.space.done .ring {
		border-color: rgb(120 255 190 / 0.6);
		box-shadow: 0 0 14px rgb(90 240 170 / 0.25);
		transition:
			border-color 0.5s,
			box-shadow 0.5s;
		transition-delay: calc(var(--i) * 120ms);
	}
	.sun {
		position: absolute;
		left: 50%;
		width: 8.6rem;
		translate: -50% -50%;
		border-radius: 50%;
		box-shadow:
			0 0 46px 14px rgb(255 140 30 / 0.5),
			0 0 110px 40px rgb(255 110 20 / 0.22);
		animation: blaze 4s ease-in-out infinite;
	}
	.sun :global(img) {
		width: 100%;
	}
	.sun-name {
		position: absolute;
		top: 0.35rem;
		left: 50%;
		translate: -50% 0;
		padding: 0.05rem 0.5rem;
		border-radius: 999px;
		background: rgb(60 20 0 / 0.55);
		color: #ffe7b0;
		font: 600 0.74rem var(--font-display);
		letter-spacing: 0.04em;
	}
	@keyframes blaze {
		50% {
			box-shadow:
				0 0 58px 18px rgb(255 150 40 / 0.6),
				0 0 130px 50px rgb(255 110 20 / 0.28);
		}
	}

	.places {
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.place {
		position: absolute;
		display: grid;
		justify-items: center;
		gap: 0.1rem;
		width: 6.6rem;
		min-height: 3.4rem;
		translate: -50% -1.55rem;
		border-radius: 1.2rem;
	}
	.place:global(.zone-hover) {
		background: rgb(255 210 63 / 0.16);
		outline: 2px dashed #ffd23f;
	}
	.empty {
		display: grid;
		place-items: center;
		width: 3.1rem;
		height: 3.1rem;
		border: 2px dashed rgb(190 210 255 / 0.6);
		border-radius: 50%;
		background: rgb(10 16 40 / 0.6);
		color: #cfe0ff;
		font: 600 1rem var(--font-display);
	}
	.hint {
		color: rgb(200 215 255 / 0.75);
		font: 700 0.68rem var(--font-body);
	}
	.planet {
		display: grid;
		justify-items: center;
		gap: 0.1rem;
		padding: 0;
		border: 0;
		background: transparent;
		color: #fff;
		cursor: grab;
		touch-action: none;
	}
	.planet:disabled {
		cursor: default;
	}
	.planet:global(.dragging) {
		z-index: 50;
	}
	.globe {
		position: relative;
		display: grid;
		place-items: center;
		width: 3.1rem;
		height: 3.1rem;
		border-radius: 50%;
		filter: drop-shadow(0 4px 8px rgb(0 0 0 / 0.6));
	}
	.planet.wide .globe {
		width: 5.4rem;
	}
	.globe :global(img) {
		width: 100%;
	}
	.planet.ok .globe {
		outline: 3px solid var(--good);
		outline-offset: 2px;
	}
	.planet.off .globe {
		outline: 3px solid var(--almost);
		outline-offset: 2px;
	}
	.planet.wide.ok .globe,
	.planet.wide.off .globe {
		border-radius: 1.6rem;
	}
	.name {
		max-width: 6.4rem;
		padding: 0.05rem 0.45rem;
		border-radius: 999px;
		background: rgb(5 8 20 / 0.8);
		font: 700 0.76rem/1.25 var(--font-body);
		overflow-wrap: anywhere;
	}
	.planet.ok .name {
		background: var(--good);
	}
	.planet.off .name {
		background: var(--almost);
	}
	.should {
		padding: 0 0.4rem;
		border-radius: 999px;
		background: #fff1e6;
		color: #8a3b12;
		font: 800 0.7rem/1.4 var(--font-body);
		white-space: nowrap;
	}
	/* something that is not a body the library knows: a plain grey rock, never a planet it is not */
	.rock {
		display: block;
		width: 100%;
		aspect-ratio: 1;
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, #d4d7de, #7b808c 60%, #454954);
	}
	.scale {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0.3rem;
		color: rgb(190 205 240 / 0.6);
		font-size: 0.66rem;
		text-align: center;
	}
	/* in the pile */
	.mini {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.3rem;
	}
	.mini.wide {
		width: 3.4rem;
	}
	.mini :global(img) {
		width: 100%;
		filter: drop-shadow(0 2px 3px rgb(0 0 0 / 0.35));
	}
	@media (prefers-reduced-motion: reduce) {
		.sun {
			animation: none;
		}
	}
</style>
