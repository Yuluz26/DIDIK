<!--
	Hierarki Istana: a pyramid of the court, narrowest at the top under the crown. Place the highest at the
	top and work down, layer by layer, in velvet and gold.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();
</script>

<OrderPlay {p} pool="Kedudukan" tip="Yang paling tinggi di puncak. Susun ke bawah.">
	{#snippet board(v: OrderView)}
		{@const n = v.slots.length}
		<div class="hall" class:won={v.allRight}>
			<span class="crown" aria-hidden="true"><Sticker key="mahkota" size={58} alt="" /></span>
			<ol class="pyramid">
				{#each v.slots as id, i (i)}
					{@const ok = v.ok(i)}
					<li class="layer" class:filled={!!id} style:--w="{38 + (i / Math.max(1, n - 1)) * 62}%" style:--shade={i / Math.max(1, n - 1)} data-zone={v.zone(i)}>
						{#if id}
							<button type="button" class="who" disabled={v.locked} {@attach v.grab(i)} aria-label="{v.text(id)}, lapisan {i + 1}">
								{v.text(id)}
								{#if ok !== null}<Mark {ok} />{/if}
							</button>
						{:else}
							<span class="empty">{i + 1}</span>
						{/if}
					</li>
					{#if v.should(i)}<li class="should">Lapisan {i + 1}: {v.should(i)}</li>{/if}
				{/each}
			</ol>
		</div>
	{/snippet}
</OrderPlay>

<style>
	.hall {
		display: grid;
		justify-items: center;
		padding: 0.6rem 0.6rem 1rem;
		border-radius: var(--r-lg);
		background:
			radial-gradient(circle at 50% 0%, rgb(255 215 120 / 0.35), transparent 55%),
			linear-gradient(180deg, #5b1530, #3a0c1f);
		box-shadow:
			inset 0 0 0 3px #c9a13b,
			inset 0 0 0 7px #5b1530,
			inset 0 0 0 8px #c9a13b;
	}
	.crown {
		filter: drop-shadow(0 0 12px rgb(255 210 80 / 0.7));
		animation: shine 2.4s ease-in-out infinite;
	}
	.won .crown {
		animation-duration: 0.8s;
	}
	.pyramid {
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		width: 100%;
		margin: 0.2rem 0 0;
		padding: 0;
		list-style: none;
	}
	.layer {
		position: relative;
		display: grid;
		place-items: center;
		width: var(--w);
		min-width: 9rem;
		min-height: 3rem;
		padding: 0.3rem 1.4rem;
		clip-path: polygon(6% 0, 94% 0, 100% 100%, 0 100%);
		background: rgb(255 230 170 / 0.12);
		outline: 2px dashed rgb(240 200 110 / 0.5);
		outline-offset: -6px;
	}
	.layer.filled {
		outline: 0;
		background: linear-gradient(180deg, hsl(43 80% calc(72% - var(--shade) * 18%)), hsl(36 70% calc(52% - var(--shade) * 14%)));
		box-shadow: inset 0 -3px 0 rgb(0 0 0 / 0.2);
	}
	.layer:global(.zone-hover) {
		background: rgb(255 210 80 / 0.4);
	}
	.who {
		position: relative;
		padding: 0.2rem 0.4rem;
		border: 0;
		background: transparent;
		color: #3a1606;
		font: 700 0.98rem/1.15 var(--font-display);
		text-align: center;
		cursor: grab;
		touch-action: none;
	}
	.who:disabled {
		cursor: default;
	}
	.empty {
		color: #f3d38a;
		font: 700 1rem var(--font-display);
	}
	.should {
		color: #ffd2b0;
		font-size: 0.8rem;
		font-weight: 800;
	}
	@keyframes shine {
		50% {
			transform: translateY(-3px) scale(1.05);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.crown {
			animation: none;
		}
	}
</style>
