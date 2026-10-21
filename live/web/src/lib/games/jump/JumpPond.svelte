<!--
	Lompat!'s pond. Each answer is an island; children's animals stand on the island they chose and
	hop across when they change their mind (crossfade). When time is up, wrong islands sink.
-->
<script lang="ts">
	import { crossfade } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import type { Person } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';
	import Icon from '$ui/Icon.svelte';

	interface Pond {
		pads: { id: string; text: string }[];
		picks: Record<string, string>;
		hearts: Record<string, number>;
		correctPads: string[];
		fell: string[];
		revived: string[];
	}

	let {
		pond,
		people,
		me = null,
		stage,
		interactive = false,
		big = false,
		onpick
	}: {
		pond: Pond;
		people: Map<string, Person>;
		me?: string | null;
		stage: string;
		interactive?: boolean;
		big?: boolean;
		onpick?: (pad: string) => void;
	} = $props();

	const [send, receive] = crossfade({
		duration: 520,
		easing: quintOut,
		fallback: (node) => ({ duration: 300, css: (t) => `opacity: ${t}; transform: scale(${0.6 + 0.4 * t})` })
	});

	const LETTERS = 'ABCD';
	const revealing = $derived(stage === 'reveal');
	const everyone = $derived([...people.values()].filter((p) => p.approved && pond.hearts[p.id] !== undefined));
	const onLand = $derived(everyone.filter((p) => (pond.hearts[p.id] ?? 3) > 0));
	const fish = $derived(everyone.filter((p) => (pond.hearts[p.id] ?? 3) === 0));
	const waiting = $derived(onLand.filter((p) => !pond.picks[p.id]));
	const visible = $derived(big ? 10 : 6);

	function standing(pad: string) {
		return onLand.filter((p) => pond.picks[p.id] === pad);
	}

	function colour(index: number, id: string) {
		if (id === 'true') return 't1';
		if (id === 'false') return 't0';
		return `t${index % 6}`;
	}
</script>

<figure class="pond" class:big class:revealing>
	<div class="ripples" aria-hidden="true"><span></span><span></span><span></span></div>

	<div class="pads pads-{pond.pads.length}">
		{#each pond.pads as pad, i (pad.id)}
			{@const right = pond.correctPads.includes(pad.id)}
			{@const people_here = standing(pad.id)}
			<button
				type="button"
				class="pad {colour(i, pad.id)}"
				class:mine={!!me && pond.picks[me] === pad.id}
				class:right={revealing && right}
				class:sink={revealing && !right}
				disabled={!interactive}
				onclick={() => onpick?.(pad.id)}
				aria-label="Lompat ke {pad.text}"
			>
				<span class="flag">
					{#if pad.id === 'true'}<Icon name="check" size={22} />{:else if pad.id === 'false'}<Icon name="close" size={22} />{:else}{LETTERS[i]}{/if}
				</span>
				<span class="label">{pad.text}</span>
				<span class="crowd">
					{#each people_here.slice(0, visible) as person (person.id)}
						<span class="who" class:me={person.id === me} in:receive={{ key: person.id }} out:send={{ key: person.id }}>
							<Avatar animal={person.avatar} colour={person.colour} skin={person.skin} size={big ? 44 : 34} mood={revealing ? (right ? 'cheer' : 'oops') : 'happy'} />
						</span>
					{/each}
					{#if people_here.length > visible}<span class="more">+{people_here.length - visible}</span>{/if}
				</span>
				<svg class="land" viewBox="0 0 200 80" preserveAspectRatio="none" aria-hidden="true">
					<ellipse cx="100" cy="52" rx="96" ry="26" fill="#e5c07a" />
					<ellipse cx="100" cy="42" rx="92" ry="28" fill="#8fd05e" />
					<ellipse cx="70" cy="34" rx="26" ry="8" fill="#a6dd75" opacity=".7" />
				</svg>
				{#if revealing && right}<span class="badge"><Icon name="check" size={20} /></span>{/if}
				{#if revealing && !right}<span class="splash" aria-hidden="true"></span>{/if}
			</button>
		{/each}
	</div>

	<div class="shore">
		{#if waiting.length && stage === 'question'}
			<span class="hint">Belum lompat:</span>
			{#each waiting.slice(0, 10) as person (person.id)}
				<span class="who" in:receive={{ key: person.id }} out:send={{ key: person.id }}>
					<Avatar animal={person.avatar} colour={person.colour} skin={person.skin} size={28} />
				</span>
			{/each}
		{/if}
		{#if fish.length}
			<span class="fishes">
				<span class="hint">Ikan:</span>
				{#each fish.slice(0, 10) as person (person.id)}
					<span class="fish" title="{person.name} jadi ikan"><Avatar animal={person.avatar} colour={person.colour} skin={person.skin} size={26} /></span>
				{/each}
			</span>
		{/if}
	</div>
</figure>

<style>
	.pond {
		position: relative;
		display: grid;
		gap: 0.6rem;
		margin: 0;
		padding: 1rem 0.8rem 0.7rem;
		border-radius: var(--r-lg);
		background: radial-gradient(ellipse at 50% 120%, #2a9bb8 0%, #4fc3d9 60%);
		overflow: hidden;
		box-shadow: var(--card-shadow);
	}
	.ripples span {
		position: absolute;
		width: 9rem;
		height: 3rem;
		border: 3px solid rgb(255 255 255 / 0.35);
		border-radius: 50%;
		animation: ripple 4.5s ease-out infinite;
	}
	.ripples span:nth-child(1) {
		left: 8%;
		top: 18%;
	}
	.ripples span:nth-child(2) {
		right: 10%;
		top: 52%;
		animation-delay: 1.5s;
	}
	.ripples span:nth-child(3) {
		left: 40%;
		bottom: 8%;
		animation-delay: 3s;
	}
	@keyframes ripple {
		from {
			transform: scale(0.3);
			opacity: 1;
		}
		to {
			transform: scale(1.4);
			opacity: 0;
		}
	}
	.pads {
		position: relative;
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 0.8rem;
	}
	.pads-3 {
		grid-template-columns: repeat(3, minmax(0, 1fr));
	}
	.pad {
		--c: var(--coral);
		position: relative;
		display: grid;
		grid-template-rows: auto auto 1fr;
		justify-items: center;
		gap: 0.3rem;
		min-height: 9.5rem;
		padding: 0.6rem 0.4rem 1.4rem;
		border: 0;
		background: transparent;
		color: var(--ink);
		cursor: pointer;
		transition:
			transform 600ms var(--spring),
			opacity 600ms,
			filter 600ms;
	}
	.big .pad {
		min-height: 13rem;
	}
	.pad.t0 { --c: var(--coral); }
	.pad.t1 { --c: var(--sea); }
	.pad.t2 { --c: var(--sun); }
	.pad.t3 { --c: var(--sky); }
	.pad:disabled {
		cursor: default;
	}
	.pad:not(:disabled):hover {
		transform: translateY(-4px) scale(1.02);
	}
	.pad:not(:disabled):active {
		transform: scale(0.96, 0.92);
	}
	.land {
		position: absolute;
		inset: auto 0 0;
		width: 100%;
		height: 62%;
		z-index: 0;
		filter: drop-shadow(0 6px 0 rgb(0 0 0 / 0.12));
	}
	.flag,
	.label,
	.crowd,
	.badge {
		position: relative;
		z-index: 1;
	}
	.flag {
		display: grid;
		place-items: center;
		width: 2.4rem;
		height: 2.4rem;
		border-radius: 0.8rem;
		background: var(--c);
		color: #fff;
		font: 600 1.15rem var(--font-display);
		box-shadow: 0 3px 0 rgb(0 0 0 / 0.18);
	}
	.label {
		max-width: 100%;
		padding: 0.15rem 0.7rem;
		border-radius: var(--r-pill);
		background: #fff;
		font: 600 clamp(0.95rem, 0.85rem + 0.5vw, 1.25rem) / 1.2 var(--font-display);
		text-align: center;
		overflow-wrap: anywhere;
		box-shadow: 0 2px 0 rgb(0 0 0 / 0.1);
	}
	.big .label {
		font-size: 1.5rem;
	}
	.pad.mine .label {
		outline: 3px solid var(--ink);
	}
	.crowd {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		align-content: end;
		gap: 0.1rem;
		min-height: 2.4rem;
		margin-top: 0.2rem;
	}
	.who.me {
		filter: drop-shadow(0 0 0 #fff) drop-shadow(0 3px 0 var(--ink));
	}
	.more {
		align-self: center;
		padding: 0 0.4rem;
		border-radius: var(--r-pill);
		background: #fff;
		font-weight: 800;
		font-size: 0.85rem;
	}
	.pad.sink {
		transform: translateY(16%) rotate(-3deg);
		opacity: 0.5;
		filter: saturate(0.5);
	}
	.pad.right {
		animation: pop-in 600ms var(--spring);
	}
	.badge {
		position: absolute;
		top: 0.4rem;
		left: calc(50% + 1.6rem);
		display: grid;
		place-items: center;
		width: 2rem;
		height: 2rem;
		border-radius: 50%;
		background: #fff;
		color: var(--good);
		animation: pop-in 500ms var(--spring) 200ms both;
	}
	.splash {
		position: absolute;
		left: 50%;
		bottom: 18%;
		width: 70%;
		height: 2.4rem;
		translate: -50% 0;
		border-radius: 50%;
		border: 4px solid rgb(255 255 255 / 0.8);
		animation: ripple 900ms ease-out 2;
		z-index: 2;
	}
	.shore {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.3rem 0.5rem;
		min-height: 1.8rem;
	}
	.hint {
		color: #fff;
		font-weight: 800;
		font-size: 0.85rem;
	}
	.fishes {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		margin-left: auto;
	}
	.fish {
		display: inline-block;
		animation: bob 2s ease-in-out infinite;
		filter: saturate(0.6) brightness(1.1);
	}
	@media (max-width: 420px) {
		.pads-3 {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}
</style>
