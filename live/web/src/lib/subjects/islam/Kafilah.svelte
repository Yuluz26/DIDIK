<!--
	Kafilah Sirah: a caravan of camels at the edge of the desert, and a tent or oasis for each answer
	across the dunes (two oases, Betul and Salah, for a true-or-false question). Tap a tent and the caravan
	walks there. Semak sends where it stands.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Sticker from '$ui/Sticker.svelte';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	const tf = $derived(p.question.type === 'truefalse');
	const camps = $derived<{ id: string; text: string; value: string | boolean }[]>(
		tf
			? [
					{ id: 'b', text: 'Betul', value: true },
					{ id: 's', text: 'Salah', value: false }
				]
			: (p.question.choices ?? []).map((c) => ({ id: c.id, text: c.text, value: c.id }))
	);
	const locked = $derived(isLocked(p));
	let chosen = $state<string | null>(null);
	const value = (id: string | null) => camps.find((c) => c.id === id)?.value;
	const idOf = (v: unknown) => camps.find((c) => c.value === v)?.id ?? null;
	const pick = $derived<string | null>(p.mine !== undefined ? idOf(p.mine) : p.reveal ? idOf(tf ? p.reveal.correct : p.reveal.correct[0]) : chosen);
	const right = $derived<string | null>(p.reveal ? idOf(tf ? p.reveal.correct : p.reveal.correct[0]) : null);
	const at = (i: number) => (camps.length === 1 ? 50 : 18 + (i / (camps.length - 1)) * 70);
	const caravanX = $derived(pick ? at(camps.findIndex((c) => c.id === pick)) - 9 : 2);
	import GameImage from '../GameImage.svelte';
	import { asset } from '../assets';
	const DUNES = asset('isl/dunes');
</script>

<div class="desert" style:--dunes={DUNES ? `url(${DUNES.src})` : 'none'}>
	<span class="sun" aria-hidden="true"></span>
	<span class="dune d1" aria-hidden="true"></span>
	<span class="dune d2" aria-hidden="true"></span>
	{#each camps as c, i (c.id)}
		{@const ok = right ? c.id === right : null}
		<button
			type="button"
			class="camp"
			class:on={pick === c.id}
			class:ok={ok === true}
			class:off={ok === false && pick === c.id}
			style:left="{at(i)}%"
			style:top="{i % 2 ? 30 : 18}%"
			disabled={locked}
			onclick={() => ((chosen = c.id), play('go'))}
			aria-pressed={pick === c.id}
		>
			<Sticker key={tf ? (c.value ? 'pokok-kelapa' : 'padang-pasir') : i % 2 ? 'pokok-kelapa' : 'khemah'} size={46} alt="" />
			<span class="sign">{c.text}</span>
			{#if right && (pick === c.id || c.id === right)}<Mark ok={c.id === right} />{/if}
		</button>
	{/each}
	<span class="caravan" class:walk={!!pick} style:left="{caravanX}%" aria-hidden="true">
		<span class="train"><GameImage name="isl/caravan" eager fit="cover">{#snippet fallback()}<Sticker key="unta" size={44} alt="" /><Sticker key="unta" size={36} alt="" />{/snippet}</GameImage></span>
	</span>
</div>
{#if !locked}
	<Checks
		tip={chosen ? 'Kafilah sudah tiba. Semak bila pasti.' : 'Ketik khemah jawapan untuk membawa kafilah ke sana.'}
		ready={!!chosen}
		dirty={!!chosen}
		onreset={() => (chosen = null)}
		oncheck={() => p.onanswer?.(value(chosen))}
	/>
{/if}

<style>
	.desert {
		background-image: linear-gradient(180deg, rgb(255 230 180 / 0.15), rgb(120 70 20 / 0.2)), var(--dunes) !important;
		background-size: cover !important;
		background-position: center 60% !important;
	}
	.desert .dune {
		display: none;
	}
	.train {
		display: block;
		width: 5.6rem;
		height: 2.6rem;
		overflow: hidden;
		border: 2px solid #fff6e0;
		border-radius: 0.6rem;
		box-shadow: 0 3px 8px rgb(80 40 0 / 0.4);
	}
	.train :global(img.g-img) {
		width: 100%;
		height: 100%;
	}
	.desert {
		position: relative;
		min-height: 15rem;
		overflow: hidden;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #ffd9a0 0%, #ffe9c4 38%, #f3c77d 38.5%, #e6ac5a 100%);
		box-shadow: inset 0 0 0 3px #c98f3c;
	}
	.sun {
		position: absolute;
		right: 10%;
		top: 6%;
		width: 3rem;
		height: 3rem;
		border-radius: 50%;
		background: radial-gradient(circle, #fff6c8, #ffb84a);
		box-shadow: 0 0 30px 10px rgb(255 184 74 / 0.5);
	}
	.dune {
		position: absolute;
		bottom: -30%;
		border-radius: 50%;
		background: linear-gradient(180deg, #f0bd6a, #d99a45);
	}
	.d1 {
		left: -20%;
		width: 80%;
		height: 70%;
	}
	.d2 {
		right: -25%;
		width: 90%;
		height: 60%;
		background: linear-gradient(180deg, #f5c879, #dfa452);
	}
	.camp {
		position: absolute;
		z-index: 1;
		display: grid;
		justify-items: center;
		gap: 0.1rem;
		translate: -50% 0;
		padding: 0;
		border: 0;
		background: transparent;
		cursor: pointer;
		filter: drop-shadow(0 4px 3px rgb(120 70 10 / 0.3));
		transition: transform var(--t-state) var(--spring);
	}
	.camp:not(:disabled):hover {
		transform: translateY(-3px);
	}
	.sign {
		max-width: 7.5rem;
		padding: 0.15rem 0.45rem;
		border-radius: 6px;
		background: #fff8e6;
		color: #4a2c08;
		font: 700 0.85rem/1.1 var(--font-body);
		text-align: center;
		box-shadow: 0 2px 0 #b98a44;
	}
	.on .sign {
		background: #ffd23f;
	}
	.ok .sign {
		background: var(--good);
		color: #fff;
	}
	.off .sign {
		background: var(--almost);
		color: #fff;
	}
	.camp:disabled {
		cursor: default;
	}
	.caravan {
		position: absolute;
		bottom: 8%;
		z-index: 2;
		display: flex;
		align-items: flex-end;
		gap: 0;
		transition: left 1.2s ease-in-out;
	}
	/* the camels face the way they walk */
	.caravan :global(img) {
		scale: -1 1;
	}
	.caravan.walk :global(img) {
		animation: sway 0.5s ease-in-out infinite alternate;
	}
	@keyframes sway {
		to {
			transform: translateY(-3px) rotate(-3deg);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.caravan {
			transition: none;
		}
		.caravan.walk :global(img) {
			animation: none;
		}
	}
</style>
