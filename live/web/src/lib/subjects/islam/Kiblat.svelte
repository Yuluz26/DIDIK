<!--
	Kompas Kiblat: a brass compass with the answers around its dial. When the answers are directions
	(utara, barat laut...), each sits at its true bearing; otherwise they are spaced evenly round. Turn
	the needle by tapping an answer (or dragging round the dial); Semak sends the one it points at.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Sticker from '$ui/Sticker.svelte';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	const BEARINGS: [RegExp, number][] = [
		[/barat\s*laut|northwest/i, 315],
		[/timur\s*laut|northeast/i, 45],
		[/barat\s*daya|southwest/i, 225],
		[/tenggara|southeast/i, 135],
		[/utara|north/i, 0],
		[/selatan|south/i, 180],
		[/timur|east/i, 90],
		[/barat|west/i, 270]
	];
	const choices = $derived(p.question.choices ?? []);
	const allDirections = $derived(choices.every((c) => BEARINGS.some(([re]) => re.test(c.text))));
	// Directions point where they really are. Other answers are spread round the dial, four of them on the
	// diagonals, where a long answer has more room than in the narrow strip east or west of the dial.
	const angles = $derived(
		choices.map((c, i) =>
			allDirections ? (BEARINGS.find(([re]) => re.test(c.text))?.[1] ?? 0) : (i * 360) / choices.length + (choices.length === 4 ? 45 : 0)
		)
	);

	const locked = $derived(isLocked(p));
	let chosen = $state<string | null>(null);
	const pick = $derived<string | null>(p.mine !== undefined ? p.mine : p.reveal ? p.reveal.correct[0] : chosen);
	const right = $derived<string | null>(p.reveal ? p.reveal.correct[0] : null);
	const needle = $derived(pick ? angles[choices.findIndex((c) => c.id === pick)] : -20);
	let dial: HTMLDivElement;
	let turning = false;

	function point(i: number) {
		if (locked) return;
		chosen = choices[i].id;
		play('tick');
	}
	function turn(event: PointerEvent) {
		if (!turning || locked) return;
		const box = dial.getBoundingClientRect();
		const a = (Math.atan2(event.clientX - (box.left + box.width / 2), -(event.clientY - (box.top + box.height / 2))) * 180) / Math.PI;
		const deg = (a + 360) % 360;
		let best = 0;
		let gap = 999;
		angles.forEach((b, i) => {
			const d = Math.min(Math.abs(b - deg), 360 - Math.abs(b - deg));
			if (d < gap) [best, gap] = [i, d];
		});
		if (choices[best].id !== chosen) point(best);
	}
</script>

<div class="desk">
	<div
		class="dial"
		bind:this={dial}
		role="application"
		aria-label="Kompas. Pusingkan jarum ke jawapan."
		onpointerdown={(e) => ((turning = true), turn(e))}
		onpointermove={turn}
		onpointerup={() => (turning = false)}
		onpointerleave={() => (turning = false)}
	>
		<span class="rose" aria-hidden="true"></span>
		{#each ['U', 'T', 'S', 'B'] as letter, i (letter)}
			<span class="cardinal" style:--a="{i * 90}deg" aria-hidden="true">{letter}</span>
		{/each}
		<span class="needle" style:--a="{needle}deg" aria-hidden="true"><i></i></span>
		<span class="hub" aria-hidden="true"><Sticker key="kaabah" size={34} alt="" /></span>
		{#each choices as c, i (c.id)}
			{@const ok = right ? c.id === right : null}
			<button
				type="button"
				class="mark-btn"
				class:on={pick === c.id}
				class:ok={ok === true}
				class:off={ok === false && pick === c.id}
				style:--sx={Math.sin((angles[i] * Math.PI) / 180).toFixed(3)}
				style:--cy={Math.cos((angles[i] * Math.PI) / 180).toFixed(3)}
				style:--ax={Math.abs(Math.sin((angles[i] * Math.PI) / 180)).toFixed(3)}
				disabled={locked}
				onpointerdown={(e) => e.stopPropagation()}
				onclick={() => point(i)}
				aria-pressed={pick === c.id}
			>
				<span>{c.text}</span>
				{#if right && (pick === c.id || c.id === right)}<Mark ok={c.id === right} />{/if}
			</button>
		{/each}
	</div>
</div>
{#if !locked}
	<Checks tip={chosen ? 'Jarum sudah menunjuk. Semak bila pasti.' : 'Ketik jawapan atau putar jarum kompas.'} ready={!!chosen} dirty={!!chosen} onreset={() => (chosen = null)} oncheck={() => p.onanswer?.(chosen)} />
{/if}

<style>
	/* The dial is sized from the board, so the answers around it always fit beside it on a phone. */
	.desk {
		container-type: inline-size;
		display: grid;
		place-items: center;
		padding: 2.6rem 0.5rem;
		border-radius: var(--r-lg);
		background:
			radial-gradient(circle at 50% 50%, rgb(255 255 255 / 0.25), transparent 60%),
			linear-gradient(135deg, #2f6b5a, #1e4a3e);
		box-shadow: inset 0 0 0 3px #173a31;
	}
	.dial {
		--r: min(25cqi, 7.5rem);
		position: relative;
		width: calc(var(--r) * 2);
		aspect-ratio: 1;
		border-radius: 50%;
		background: radial-gradient(circle, #fffaf0 0 62%, #e8d6a8 63% 66%, #c79a3a 67% 74%, #8a6418 75%);
		box-shadow:
			0 12px 24px rgb(0 0 0 / 0.35),
			inset 0 0 0 2px #fff3cf;
		touch-action: none;
		cursor: grab;
	}
	.rose {
		position: absolute;
		inset: 18%;
		background:
			conic-gradient(from -22.5deg, transparent 0 45deg, rgb(140 100 30 / 0.15) 45deg 90deg, transparent 90deg 135deg, rgb(140 100 30 / 0.15) 135deg 180deg, transparent 180deg 225deg, rgb(140 100 30 / 0.15) 225deg 270deg, transparent 270deg 315deg, rgb(140 100 30 / 0.15) 315deg 360deg);
		border-radius: 50%;
	}
	.cardinal {
		position: absolute;
		left: 50%;
		top: 50%;
		translate: -50% -50%;
		rotate: var(--a);
		transform: translateY(calc(var(--r) * -0.59)) rotate(calc(-1 * var(--a)));
		color: #7a1f1f;
		font: 700 0.85rem var(--font-display);
	}
	.cardinal:not(:first-of-type) {
		color: #5a4318;
	}
	.needle {
		position: absolute;
		left: 50%;
		top: 50%;
		width: 0;
		height: 0;
		rotate: var(--a);
		transition: rotate 0.6s cubic-bezier(0.3, 1.6, 0.5, 1);
	}
	.needle i {
		position: absolute;
		left: -0.45rem;
		bottom: -0.2rem;
		width: 0.9rem;
		height: calc(var(--r) * 0.72);
		background: linear-gradient(180deg, #c62f2f 0 55%, #2b2f3a 55%);
		clip-path: polygon(50% 0, 100% 52%, 62% 100%, 38% 100%, 0 52%);
		filter: drop-shadow(0 2px 2px rgb(0 0 0 / 0.35));
	}
	.hub {
		position: absolute;
		left: 50%;
		top: 50%;
		translate: -50% -50%;
		display: grid;
		place-items: center;
		width: 2.6rem;
		height: 2.6rem;
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, #fff3cf, #c79a3a);
		box-shadow: 0 2px 4px rgb(0 0 0 / 0.3);
	}
	/* each answer's inner edge touches the rim at its bearing, so it grows away from the dial */
	.mark-btn {
		position: absolute;
		left: calc(50% + (var(--r) + 0.3rem) * var(--sx));
		top: calc(50% - (var(--r) + 0.3rem) * var(--cy));
		width: max-content;
		/* the room between the rim and the board's edge on this answer's side: all of it at the top and
		   bottom, only the strip beside the dial at east and west */
		max-width: min(9rem, calc((50cqi - (var(--r) + 0.3rem) * var(--ax) - 0.4rem) * 2 / (1 + var(--ax))));
		padding: 0;
		border: 0;
		background: transparent;
		translate: calc(-50% + 50% * var(--sx)) calc(-50% - 50% * var(--cy));
		cursor: pointer;
	}
	.mark-btn span {
		display: inline-block;
		max-width: 100%;
		text-align: center;
		padding: 0.25rem 0.55rem;
		border-radius: 999px;
		background: #fffdf3;
		color: #2b1a0a;
		font: 700 0.85rem/1.1 var(--font-body);
		overflow-wrap: break-word;
		box-shadow: 0 3px 0 #c9a46a;
	}
	.mark-btn.on span {
		background: #ffd23f;
	}
	.mark-btn.ok span {
		background: var(--good);
		color: #fff;
	}
	.mark-btn.off span {
		background: var(--almost);
		color: #fff;
	}
	.mark-btn:disabled {
		cursor: default;
	}
	@media (prefers-reduced-motion: reduce) {
		.needle {
			transition: none;
		}
	}
</style>
