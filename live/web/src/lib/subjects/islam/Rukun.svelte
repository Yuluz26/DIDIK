<!--
	Tiang Rukun: a mosque's roof with its dome waits on empty plinths; the answers are carved pillars lying
	in the courtyard. Tap a pillar to raise it under the roof (tap again to lower it), as many as the
	question asks. Once the answer is shown, wrong pillars crack.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	const choices = $derived(p.question.choices ?? []);
	const need = $derived(p.question.pick ?? 1);
	const locked = $derived(isLocked(p));
	let raised = $state<string[]>([]);
	const up = $derived<string[]>(p.mine !== undefined ? (Array.isArray(p.mine) ? p.mine : [p.mine]) : p.reveal ? p.reveal.correct : raised);
	const right = $derived<string[] | null>(p.reveal ? p.reveal.correct : null);
	const text = (id: string) => choices.find((c) => c.id === id)?.text ?? '';

	function toggle(id: string) {
		if (locked) return;
		if (raised.includes(id)) {
			raised = raised.filter((x) => x !== id);
			play('tap');
		} else if (raised.length < need) {
			raised = [...raised, id];
			play('build');
		}
	}
	import { asset } from '../assets';
	// Masjid Sultan Salahuddin Abdul Aziz, Shah Alam, behind the pillars
	const MASJID = asset('isl/salahuddin');
</script>

<div class="mosque" style:--masjid={MASJID ? `url(${MASJID.src})` : 'none'}>
	<div class="dome" aria-hidden="true"><span class="crescent"></span></div>
	<div class="roof" aria-hidden="true"></div>
	<div class="colonnade" style:--n={need}>
		{#each Array(need) as _, i (i)}
			{@const id = up[i]}
			{@const ok = right && id ? right.includes(id) : null}
			<div class="bay">
				{#if id}
					<button type="button" class="pillar" class:crack={ok === false} disabled={locked} onclick={() => toggle(id)} aria-label="{text(id)}. Ketik untuk turunkan">
						<span class="cap" aria-hidden="true"></span>
						<span class="shaft">{text(id)}</span>
						{#if ok !== null}<Mark {ok} />{/if}
					</button>
				{:else}
					<span class="gap">Tiang {i + 1}</span>
				{/if}
			</div>
		{/each}
	</div>
	<div class="floor" aria-hidden="true"></div>
</div>

{#if !locked}
	<ul class="yard" aria-label="Tiang di halaman">
		{#each choices.filter((c) => !raised.includes(c.id)) as c (c.id)}
			<li><button type="button" class="log" onclick={() => toggle(c.id)} disabled={raised.length >= need}>{c.text}</button></li>
		{/each}
	</ul>
	<Checks
		tip={`Dirikan ${need} tiang yang betul. ${raised.length}/${need} sudah berdiri.`}
		ready={raised.length === need}
		dirty={raised.length > 0}
		onreset={() => (raised = [])}
		oncheck={() => p.onanswer?.(raised)}
	/>
{:else if right}
	{@const missed = right.filter((r) => !up.includes(r))}
	{#if missed.length}<p class="should">Tiang yang betul juga: <strong>{missed.map(text).join(', ')}</strong></p>{/if}
{/if}

<style>
	.mosque {
		background-image: linear-gradient(180deg, rgb(230 245 255 / 0.55), rgb(255 255 255 / 0.75) 55%), var(--masjid) !important;
		background-size: cover !important;
		background-position: center 35% !important;
	}
	.mosque {
		display: grid;
		justify-items: center;
		padding: 0.8rem 0.6rem 0;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #cfe9ff, #eaf6ff 70%);
		box-shadow: inset 0 0 0 3px #a9cde8;
		overflow: hidden;
	}
	.dome {
		position: relative;
		width: 9rem;
		height: 4.6rem;
		border-radius: 4.6rem 4.6rem 0 0;
		background: radial-gradient(circle at 35% 30%, #a7f0d0, #2f9e74 70%);
		box-shadow: inset -8px -4px 0 rgb(0 0 0 / 0.12);
	}
	.crescent {
		position: absolute;
		left: 50%;
		top: -1.4rem;
		width: 1.2rem;
		height: 1.2rem;
		translate: -50% 0;
		border-radius: 50%;
		box-shadow: inset -4px 2px 0 0 #e7b622;
	}
	.roof {
		width: 96%;
		height: 1.4rem;
		border-radius: 6px 6px 2px 2px;
		background: linear-gradient(180deg, #f7f2e6, #d9cfb8);
		box-shadow: 0 4px 0 #b8ab8d;
	}
	.colonnade {
		display: grid;
		grid-template-columns: repeat(var(--n), minmax(0, 1fr));
		gap: 0.4rem;
		width: 92%;
		min-height: 10rem;
	}
	.bay {
		display: grid;
		place-items: stretch;
	}
	.gap {
		display: grid;
		place-items: center;
		border: 2px dashed #9fbfd6;
		border-top: 0;
		color: #6f93ad;
		font-weight: 800;
		font-size: 0.8rem;
	}
	.pillar {
		position: relative;
		display: grid;
		grid-template-rows: auto 1fr;
		padding: 0;
		border: 0;
		background: transparent;
		cursor: pointer;
		animation: rise 0.45s var(--spring, ease-out);
	}
	.pillar:disabled {
		cursor: default;
	}
	.cap {
		height: 0.8rem;
		border-radius: 3px;
		background: #e6dcc3;
		box-shadow: 0 2px 0 #b8ab8d;
	}
	.shaft {
		display: grid;
		place-items: center;
		padding: 0.4rem 0.2rem;
		background: repeating-linear-gradient(90deg, #fbf7ec 0 6px, #ece3cd 6px 9px);
		color: #3d3320;
		font: 700 0.78rem/1.15 var(--font-body);
		text-align: center;
		writing-mode: horizontal-tb;
		overflow-wrap: anywhere;
		box-shadow: inset -4px 0 0 rgb(0 0 0 / 0.08);
	}
	.crack .shaft {
		background:
			linear-gradient(115deg, transparent 45%, #8a5a3a 46% 48%, transparent 49%),
			repeating-linear-gradient(90deg, #f1e3d3 0 6px, #e0cdb6 6px 9px);
		filter: sepia(0.3);
	}
	.floor {
		width: 100%;
		height: 0.9rem;
		background: linear-gradient(180deg, #c9b99a, #a8977a);
	}
	.yard {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.5rem;
		margin: 0;
		padding: 0.6rem;
		border-radius: var(--r-lg);
		background: repeating-linear-gradient(45deg, #efe6d2 0 10px, #e6dcc4 10px 20px);
		list-style: none;
	}
	.log {
		min-height: 2.8rem;
		padding: 0.35rem 0.8rem;
		border: 0;
		border-radius: 999px;
		background: linear-gradient(180deg, #fbf7ec, #e2d7bd);
		color: #3d3320;
		font: 700 0.92rem/1.15 var(--font-body);
		box-shadow: 0 4px 0 #b8ab8d;
		cursor: pointer;
	}
	.log:disabled {
		opacity: 0.55;
		cursor: not-allowed;
	}
	.should {
		padding: 0.5rem 0.8rem;
		border-radius: var(--r-md);
		background: var(--almost-soft, #fff1e6);
		color: var(--on-almost-soft, #8a3b12);
		font-weight: 700;
	}
	@keyframes rise {
		from {
			transform: translateY(40%) scaleY(0.4);
			opacity: 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.pillar {
			animation: none;
		}
	}
</style>
