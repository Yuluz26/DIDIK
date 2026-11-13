<!--
	Huruf Hijaiyah: a wooden luh (writing board) with the answers carved as tiles in a clear naskh hand.
	Tap the right one; it lifts and glows. Semak to send it.
-->
<script lang="ts">
	import '@fontsource/amiri/arabic-700.css';
	import { play } from '$lib/sound';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	const choices = $derived(p.question.choices ?? []);
	const locked = $derived(isLocked(p));
	let chosen = $state<string | null>(null);
	const pick = $derived<string | null>(p.mine !== undefined ? p.mine : p.reveal ? p.reveal.correct[0] : chosen);
	const right = $derived<string | null>(p.reveal ? p.reveal.correct[0] : null);
	const arabic = (t: string) => /[؀-ۿ]/.test(t);
	import { asset } from '../assets';
	// real arabesque carving, as the board's frame
	const CARVING = asset('isl/arabesque');
</script>

<div class="luh" style:--carving={CARVING ? `url(${CARVING.src})` : 'none'}>
	<span class="handle" aria-hidden="true"></span>
	<div class="board">
		{#each choices as c (c.id)}
			{@const ok = right ? c.id === right : null}
			<button
				type="button"
				class="tile"
				class:ar={arabic(c.text)}
				class:on={pick === c.id}
				class:ok={ok === true}
				class:off={ok === false && pick === c.id}
				disabled={locked}
				dir="auto"
				onclick={() => ((chosen = c.id), play('pop'))}
				aria-pressed={pick === c.id}
			>
				{c.text}
				{#if right && (pick === c.id || c.id === right)}<Mark ok={c.id === right} />{/if}
			</button>
		{/each}
	</div>
</div>
{#if !locked}
	<Checks tip={chosen ? 'Semak bila pasti.' : 'Ketik huruf yang betul.'} ready={!!chosen} dirty={!!chosen} onreset={() => (chosen = null)} oncheck={() => p.onanswer?.(chosen)} />
{/if}

<style>
	.luh {
		background-image: linear-gradient(rgb(110 60 20 / 0.35), rgb(80 40 10 / 0.45)), var(--carving) !important;
		background-size: cover !important;
		background-position: center !important;
	}
	.luh {
		position: relative;
		padding: 1.6rem 0.9rem 1rem;
		border-radius: 1.4rem 1.4rem 0.8rem 0.8rem;
		background:
			repeating-linear-gradient(95deg, rgb(255 255 255 / 0.05) 0 3px, transparent 3px 11px),
			linear-gradient(180deg, #b77b45, #8c5a2c);
		box-shadow:
			inset 0 0 0 4px #6b4220,
			inset 0 0 30px rgb(60 30 10 / 0.35),
			0 10px 18px rgb(60 30 10 / 0.3);
	}
	.handle {
		position: absolute;
		left: 50%;
		top: -1rem;
		width: 4.4rem;
		height: 2.4rem;
		translate: -50% 0;
		border-radius: 1.2rem 1.2rem 0 0;
		background: radial-gradient(circle at 50% 75%, transparent 0 0.8rem, #8c5a2c 0.85rem);
	}
	.board {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(5.5rem, 1fr));
		gap: 0.7rem;
	}
	.tile {
		position: relative;
		display: grid;
		place-items: center;
		min-height: 5.5rem;
		padding: 0.4rem;
		border: 0;
		border-radius: 14px;
		background: linear-gradient(180deg, #fff9ec, #f1e2c0);
		color: #2b1a0a;
		font: 700 1.2rem/1.2 var(--font-display);
		box-shadow:
			0 5px 0 #c9a46a,
			0 8px 14px rgb(60 30 10 / 0.25);
		cursor: pointer;
		transition: transform var(--t-state) var(--spring);
	}
	.tile.ar {
		font: 700 3rem/1.3 'Amiri', 'Scheherazade New', 'Traditional Arabic', serif;
	}
	.tile:not(:disabled):hover {
		transform: translateY(-3px);
	}
	.tile.on {
		transform: translateY(-5px);
		background: linear-gradient(180deg, #fffbe6, #ffe39a);
		box-shadow:
			0 5px 0 #d1a33a,
			0 0 0 3px #ffd23f,
			0 0 22px rgb(255 210 63 / 0.7);
	}
	.tile.ok {
		box-shadow:
			0 5px 0 #2f8a55,
			0 0 0 3px var(--good);
	}
	.tile.off {
		box-shadow:
			0 5px 0 #b05a1e,
			0 0 0 3px var(--almost);
	}
	.tile:disabled {
		cursor: default;
	}
</style>
