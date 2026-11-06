<!--
	Rantai Makanan: a chain of living things rising up a sunny field, the producer at the foot and the top
	predator at the top, each joined to the next by an arrow that reads "dimakan oleh", as energy flows.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();
</script>

<OrderPlay {p} pool="Hidupan" tip="Mula dengan pengeluar (tumbuhan). Ketik atau seret ke rantai.">
	{#snippet board(v: OrderView)}
		<div class="field">
			<span class="sun" aria-hidden="true"><Sticker key="matahari" size={54} alt="" /></span>
			<ol class="chain">
				{#each v.slots as id, i (i)}
					{@const ok = v.ok(i)}
					<li class="link">
						<div class="ring" class:filled={!!id} data-zone={v.zone(i)}>
							{#if id}
								<button type="button" class="who" disabled={v.locked} {@attach v.grab(i)} aria-label="{v.text(id)}, kedudukan {i + 1}">
									{#if v.sticker(id)}<Sticker key={v.sticker(id) ?? ''} size={46} alt="" />{:else}<span class="dot">{v.text(id).slice(0, 1)}</span>{/if}
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
		background: linear-gradient(180deg, #bfe6ff 0%, #e6f6ff 45%, #9fd36b 46%, #6fb84a 100%);
		box-shadow: inset 0 0 0 3px #5e9d3e;
		overflow: hidden;
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
		color: #1f3d12;
		font-weight: 800;
		font-size: 0.98rem;
		line-height: 1.1;
		text-shadow: 0 1px 0 rgb(255 255 255 / 0.6);
	}
	.should {
		grid-column: 2;
		color: #8a2a00;
		font-weight: 800;
		font-size: 0.82rem;
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
