<!--
	Orbit Planet: the Sun blazing at the top, and below it one orbit after another, each further out. Put
	each answer on its orbit, nearest the Sun first. A planet's name gives it its real colours (Zuhal its
	rings); anything else rides a moon-grey sphere.
-->
<script lang="ts">
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	const LOOKS: [RegExp, string, boolean?][] = [
		[/merkur/i, 'radial-gradient(circle at 35% 30%, #d9d6d0, #8d8a85 60%, #5a5753)'],
		[/venus|zuhrah/i, 'radial-gradient(circle at 35% 30%, #fff1c4, #e3b766 55%, #a8772f)'],
		[/bumi/i, 'radial-gradient(circle at 35% 30%, #bfe7ff, #3c86d6 45%, #2d9a5a 62%, #17406e)'],
		[/marikh/i, 'radial-gradient(circle at 35% 30%, #ffc3a3, #d0603f 55%, #7a2b19)'],
		[/musytari/i, 'repeating-linear-gradient(170deg, #e8c99a 0 7%, #c98d57 7% 12%, #f1dcb8 12% 18%, #b9774a 18% 22%)'],
		[/zuhal/i, 'radial-gradient(circle at 35% 30%, #fff3cf, #e2c98e 55%, #a88a4c)', true],
		[/uranus/i, 'radial-gradient(circle at 35% 30%, #e6ffff, #8fd9e3 55%, #3f8d9c)'],
		[/neptun/i, 'radial-gradient(circle at 35% 30%, #a9c4ff, #3b62d8 55%, #1a2f7a)'],
		[/bulan/i, 'radial-gradient(circle at 35% 30%, #ffffff, #c9c9cf 60%, #7c7c86)'],
		[/matahari/i, 'radial-gradient(circle, #fff6b0, #ffb703 60%, #f06d06)']
	];
	const look = (text: string) => LOOKS.find(([re]) => re.test(text)) ?? null;
</script>

<OrderPlay {p} pool="Benda di angkasa" tip="Ketik untuk letak pada orbit kosong yang terdekat, atau seret ke orbitnya.">
	{#snippet board(v: OrderView)}
		<div class="space">
			<div class="sun" aria-hidden="true"></div>
			<p class="sun-name">Matahari</p>
			<ol class="orbits">
				{#each v.slots as id, i (i)}
					{@const l = id ? look(v.text(id)) : null}
					{@const ok = v.ok(i)}
					<li class="orbit" data-zone={v.zone(i)} style:--i={i}>
						<span class="ring" aria-hidden="true"></span>
						<span class="n">{i + 1}</span>
						{#if id}
							<button type="button" class="body" disabled={v.locked} {@attach v.grab(i)} aria-label="{v.text(id)} pada orbit {i + 1}">
								<span class="globe" class:ringed={l?.[2]} style:background={l?.[1] ?? 'radial-gradient(circle at 35% 30%, #fafafa, #a9adb8 60%, #5d616b)'}></span>
								<span class="name">{v.text(id)}</span>
								{#if ok !== null}<Mark {ok} />{/if}
							</button>
							{#if v.should(i)}<span class="should">→ {v.should(i)}</span>{/if}
						{:else}
							<span class="empty">Orbit {i + 1}{i === 0 ? ' (terdekat)' : i === v.slots.length - 1 ? ' (terjauh)' : ''}</span>
						{/if}
					</li>
				{/each}
			</ol>
		</div>
	{/snippet}
</OrderPlay>

<style>
	.space {
		position: relative;
		overflow: hidden;
		padding: 4.6rem 0.8rem 0.9rem;
		border-radius: var(--r-lg);
		background:
			radial-gradient(1px 1px at 12% 30%, #fff, transparent),
			radial-gradient(1px 1px at 72% 18%, #fff, transparent),
			radial-gradient(1.5px 1.5px at 88% 60%, #fff, transparent),
			radial-gradient(1px 1px at 40% 80%, #fff, transparent),
			radial-gradient(1px 1px at 22% 66%, #cfe3ff, transparent),
			radial-gradient(circle at 50% -30%, #3b2a5c, #0d0b1e 60%);
		box-shadow: inset 0 0 0 3px #1c1838;
	}
	.sun {
		position: absolute;
		top: -5.5rem;
		left: 50%;
		width: 10rem;
		height: 10rem;
		translate: -50% 0;
		border-radius: 50%;
		background: radial-gradient(circle, #fff7c2, #ffd23f 45%, #ff8a00 70%, transparent 72%);
		box-shadow: 0 0 60px 20px rgb(255 170 30 / 0.45);
		animation: blaze 3s ease-in-out infinite;
	}
	.sun-name {
		position: absolute;
		top: 0.4rem;
		left: 50%;
		translate: -50% 0;
		color: #4a2600;
		font: 700 0.85rem var(--font-display);
	}
	.orbits {
		display: grid;
		gap: 0.55rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.orbit {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.5rem;
		min-height: 3.6rem;
		padding: 0.4rem 0.6rem 0.4rem calc(1.2rem + var(--i) * 0.9rem);
		border-radius: 999px;
	}
	.ring {
		position: absolute;
		inset: 0;
		border: 2px dashed rgb(180 200 255 / 0.35);
		border-radius: 50% 50% 0 0 / 100% 100% 0 0;
		border-bottom: 0;
		pointer-events: none;
	}
	.orbit:global(.zone-hover) .ring {
		border-color: #ffd23f;
		border-style: solid;
	}
	.n {
		display: grid;
		place-items: center;
		width: 1.6rem;
		height: 1.6rem;
		border-radius: 50%;
		background: rgb(255 255 255 / 0.15);
		color: #fff;
		font: 700 0.85rem var(--font-display);
	}
	.empty {
		color: rgb(200 210 255 / 0.65);
		font-weight: 700;
		font-size: 0.9rem;
	}
	.body {
		position: relative;
		display: inline-flex;
		align-items: center;
		gap: 0.55rem;
		padding: 0.25rem 0.8rem 0.25rem 0.3rem;
		border: 0;
		border-radius: 999px;
		background: rgb(255 255 255 / 0.12);
		color: #fff;
		font: 700 1rem/1.15 var(--font-body);
		cursor: grab;
		touch-action: none;
		backdrop-filter: blur(2px);
	}
	.body:disabled {
		cursor: default;
	}
	.globe {
		position: relative;
		width: 2.6rem;
		height: 2.6rem;
		flex: none;
		border-radius: 50%;
		box-shadow:
			inset -6px -6px 12px rgb(0 0 0 / 0.45),
			0 0 10px rgb(255 255 255 / 0.15);
		animation: spin-in 0.5s var(--spring, ease-out);
	}
	.globe.ringed::after {
		content: '';
		position: absolute;
		inset: 40% -35%;
		border: 3px solid #d8c18a;
		border-radius: 50%;
		rotate: -18deg;
	}
	.should {
		color: #ffd9a8;
		font-weight: 800;
		font-size: 0.85rem;
	}
	@keyframes blaze {
		50% {
			box-shadow: 0 0 80px 28px rgb(255 170 30 / 0.55);
		}
	}
	@keyframes spin-in {
		from {
			transform: scale(0.4) rotate(-90deg);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.sun,
		.globe {
			animation: none;
		}
	}
</style>
