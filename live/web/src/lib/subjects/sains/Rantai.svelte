<!--
	Rantai Makanan: a chain of living things, the producer at the foot and the top predator at the top, each
	joined to the next by an arrow that reads "dimakan oleh", the way energy flows. Every link is a real
	photograph of the organism (lexicon "living"), set against the place the chain lives: a paddy field for
	a chain on land, the open sea for one in the ocean. The server gives this game only to chains whose
	links are all living things it knows.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import GameImage from '../GameImage.svelte';
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import { asset, find, type Entry } from '../assets';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	interface Living extends Entry {
		home: string;
	}
	const living = (text: string) => find<Living>('living', text);
	// the chain is in the sea if most of its links live there
	const sea = $derived.by(() => {
		const homes = (p.question.items ?? []).map((i) => living(i.text)?.home);
		return homes.filter((h) => h === 'laut').length * 2 > homes.length;
	});
	const scene = $derived(asset(sea ? 'cycle/sea' : 'scene/paddy'));
</script>

<OrderPlay {p} pool="Hidupan" tip="Mula dengan pengeluar di bawah. Ketik atau seret setiap hidupan ke rantai.">
	{#snippet thing(item)}
		<span class="mini">
			<GameImage name={living(item.text)?.key} fit="cover">
				{#snippet fallback()}<span class="dot">{item.text.slice(0, 1)}</span>{/snippet}
			</GameImage>
		</span>
		<span>{item.text}</span>
	{/snippet}
	{#snippet board(v: OrderView)}
		<div class="field" class:sea style:--scene={scene ? `url(${scene.src})` : 'none'}>
			<ol class="chain">
				{#each v.slots as id, i (i)}
					{@const ok = v.ok(i)}
					<li class="link">
						<div class="ring" class:filled={!!id} data-zone={v.zone(i)}>
							{#if id}
								<button type="button" class="who" disabled={v.locked} {@attach v.grab(i)} aria-label="{v.text(id)}, kedudukan {i + 1}">
									<GameImage name={living(v.text(id))?.key} eager fit="cover">
										{#snippet fallback()}
											{#if v.sticker(id)}<Sticker key={v.sticker(id) ?? ''} size={46} alt="" />{:else}<span class="dot">{v.text(id).slice(0, 1)}</span>{/if}
										{/snippet}
									</GameImage>
									{#if ok !== null}<Mark {ok} />{/if}
								</button>
							{:else}
								<span class="q">{i === 0 ? 'Pengeluar' : i + 1}</span>
							{/if}
						</div>
						<span class="name">{id ? v.text(id) : ''}</span>
						{#if v.should(i)}<span class="should">→ {v.should(i)}</span>{/if}
					</li>
					{#if i < v.slots.length - 1}
						<li class="arrow" aria-hidden="true"><span>dimakan oleh</span></li>
					{/if}
				{/each}
			</ol>
		</div>
	{/snippet}
</OrderPlay>

<style>
	.field {
		position: relative;
		padding: 2.6rem 0.6rem 1rem;
		border-radius: var(--r-lg);
		background:
			linear-gradient(180deg, rgb(20 50 20 / 0.25), rgb(20 50 20 / 0.5)),
			var(--scene) 50% 50% / cover no-repeat,
			#5e9d3e;
		box-shadow: inset 0 0 0 3px #3f7a2c;
		overflow: hidden;
	}
	.field.sea {
		background:
			linear-gradient(180deg, rgb(6 40 60 / 0.35), rgb(4 30 50 / 0.6)),
			var(--scene) 50% 50% / cover no-repeat,
			#0e5a78;
		box-shadow: inset 0 0 0 3px #0a4760;
	}
	/* a real photograph of the organism fills its ring */
	.who :global(img.g-img) {
		width: 100%;
		height: 100%;
		border-radius: 50%;
	}
	.mini {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.5rem;
		height: 2.5rem;
		overflow: hidden;
		border-radius: 50%;
		background: #eef4e6;
	}
	.mini :global(img.g-img) {
		width: 100%;
		height: 100%;
	}
	.sun {
		position: absolute;
		top: 0.2rem;
		right: 0.4rem;
		animation: glow 4s ease-in-out infinite;
	}
	.chain {
		display: flex;
		flex-direction: column-reverse;
		align-items: center;
		gap: 0.1rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.link {
		display: grid;
		grid-template-columns: 4.6rem minmax(0, 9rem);
		align-items: center;
		gap: 0.2rem 0.6rem;
	}
	.ring {
		display: grid;
		place-items: center;
		width: 4.6rem;
		height: 4.6rem;
		border: 3px dashed rgb(255 255 255 / 0.9);
		border-radius: 50%;
		background: rgb(255 255 255 / 0.35);
	}
	.ring.filled {
		border-style: solid;
		border-color: #fff;
		background: #fffdf3;
		box-shadow: 0 6px 14px rgb(40 80 20 / 0.25);
	}
	.ring:global(.zone-hover) {
		transform: scale(1.08);
		border-color: #ffd23f;
	}
	.who {
		position: relative;
		display: grid;
		place-items: center;
		width: 100%;
		height: 100%;
		border: 0;
		border-radius: 50%;
		background: transparent;
		cursor: grab;
		touch-action: none;
	}
	.who:disabled {
		cursor: default;
	}
	.dot {
		font: 700 1.6rem var(--font-display);
		color: #3a6b22;
	}
	.q {
		color: #fff;
		font: 700 0.8rem var(--font-display);
		text-shadow: 0 1px 2px rgb(0 0 0 / 0.3);
		text-align: center;
	}
	.name {
		justify-self: start;
		padding: 0.12rem 0.55rem;
		border-radius: 999px;
		background: rgb(255 255 255 / 0.93);
		color: #1f3d12;
		font-weight: 800;
		font-size: 0.95rem;
		line-height: 1.15;
	}
	.name:empty {
		display: none;
	}
	.should {
		grid-column: 2;
		justify-self: start;
		padding: 0.05rem 0.5rem;
		border-radius: 999px;
		background: #fff1e6;
		color: #8a2a00;
		font-weight: 800;
		font-size: 0.8rem;
	}
	.arrow {
		display: grid;
		place-items: center;
		height: 2rem;
	}
	.arrow span {
		position: relative;
		padding: 0.1rem 0.35rem 0.1rem 0.25rem;
		border-radius: 4px;
		background: #fff8e1;
		color: #6a4b00;
		font-size: 0.72rem;
		font-weight: 800;
		box-shadow: 0 2px 0 #d8c58c;
	}
	.arrow span::before {
		content: '↑ ';
	}
	@keyframes glow {
		50% {
			transform: scale(1.08) rotate(8deg);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.sun {
			animation: none;
		}
	}
</style>
