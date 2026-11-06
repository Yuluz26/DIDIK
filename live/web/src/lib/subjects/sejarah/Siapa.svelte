<!--
	Siapakah Aku?: a hall of portrait frames, each behind a velvet curtain. Draw a curtain to see the name
	behind it (the frames hold no faces, only a name plate and an emblem), then pick the one the clues
	describe.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Sticker from '$ui/Sticker.svelte';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked, stickerFor } from '../kit.svelte';

	let p: GameProps = $props();

	const choices = $derived(p.question.choices ?? []);
	const locked = $derived(isLocked(p));
	let chosen = $state<string | null>(null);
	let drawn = $state<Record<string, boolean>>({});
	const pick = $derived<string | null>(p.mine !== undefined ? p.mine : p.reveal ? p.reveal.correct[0] : chosen);
	const right = $derived<string | null>(p.reveal ? p.reveal.correct[0] : null);
	const EMBLEMS = ['mahkota', 'keris', 'skrol', 'pen', 'perisai', 'akhbar'];

	function tap(id: string) {
		if (locked) return;
		if (!drawn[id]) {
			drawn = { ...drawn, [id]: true };
			play('whoosh');
		} else {
			chosen = id;
			play('pop');
		}
	}
</script>

<div class="hall">
	<div class="frames" style:--n={Math.min(3, choices.length)}>
		{#each choices as c, i (c.id)}
			{@const open = locked || drawn[c.id]}
			<button type="button" class="frame" class:open class:on={pick === c.id} disabled={locked} onclick={() => tap(c.id)} aria-label={open ? c.text : `Bingkai ${i + 1}: buka tirai`}>
				<span class="canvas">
					<Sticker key={c.sticker ?? stickerFor(c.text) ?? EMBLEMS[i % EMBLEMS.length]} size={46} alt="" />
				</span>
				<span class="plate">{open ? c.text : '?'}</span>
				<span class="curtain l" aria-hidden="true"></span>
				<span class="curtain r" aria-hidden="true"></span>
				{#if right && (pick === c.id || c.id === right)}<Mark ok={c.id === right} />{/if}
			</button>
		{/each}
	</div>
	{#if !locked}
		<Checks
			tip={chosen ? 'Pilihan dibuat. Semak bila pasti.' : 'Ketik bingkai untuk membuka tirai, ketik sekali lagi untuk memilih.'}
			ready={!!chosen}
			dirty={!!chosen}
			onreset={() => (chosen = null)}
			oncheck={() => p.onanswer?.(chosen)}
		/>
	{/if}
</div>

<style>
	.hall {
		display: grid;
		gap: 0.6rem;
	}
	.frames {
		display: grid;
		grid-template-columns: repeat(var(--n), minmax(0, 1fr));
		gap: 0.7rem;
		padding: 0.9rem 0.7rem;
		border-radius: var(--r-lg);
		background:
			repeating-linear-gradient(90deg, rgb(255 255 255 / 0.03) 0 2px, transparent 2px 40px),
			linear-gradient(180deg, #4a2a3a, #2e1724);
		box-shadow: inset 0 0 0 3px #1d0d16;
	}
	.frame {
		position: relative;
		display: grid;
		grid-template-rows: 1fr auto;
		gap: 0.3rem;
		min-height: 9rem;
		padding: 0.55rem;
		border: 0;
		border-radius: 6px;
		background: linear-gradient(135deg, #e7c46a, #a87a26 50%, #e7c46a);
		box-shadow:
			inset 0 0 0 3px #7a5414,
			0 8px 14px rgb(0 0 0 / 0.4);
		cursor: pointer;
		overflow: hidden;
	}
	.frame.on {
		box-shadow:
			inset 0 0 0 3px #7a5414,
			0 0 0 4px #ffd23f,
			0 0 22px #ffd23f;
	}
	.frame:disabled {
		cursor: default;
	}
	.canvas {
		display: grid;
		place-items: center;
		border-radius: 3px;
		background: radial-gradient(circle at 50% 40%, #f3e6c8, #c9b089);
		box-shadow: inset 0 0 12px rgb(80 50 20 / 0.4);
	}
	.plate {
		padding: 0.15rem 0.3rem;
		border-radius: 3px;
		background: #2b1a0a;
		color: #f6dc8c;
		font: 700 0.8rem/1.15 var(--font-display);
		text-align: center;
	}
	.curtain {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 52%;
		background: repeating-linear-gradient(90deg, #8e1730 0 8px, #6c1024 8px 14px);
		box-shadow: inset 0 -10px 20px rgb(0 0 0 / 0.35);
		transition: translate 0.6s var(--ease-out, ease-out);
	}
	.curtain.l {
		left: 0;
		border-radius: 0 0 40% 0;
	}
	.curtain.r {
		right: 0;
		border-radius: 0 0 0 40%;
	}
	.open .curtain.l {
		translate: -92% 0;
	}
	.open .curtain.r {
		translate: 92% 0;
	}
	@media (prefers-reduced-motion: reduce) {
		.curtain {
			transition: none;
		}
	}
</style>
