<!--
	Lompat!'s pond, in the worlds' 3/4 view. Each answer is a small island with a sandy edge; children's
	characters stand on the island they chose and hop across when they change their mind. When time
	is up, the wrong islands sink. Children still on the shore wait at the bottom; children out of
	hearts swim as fish until two right answers bring them back to land.
-->
<script lang="ts">
	import { crossfade } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import type { Person } from '$lib/types';
	import { COLOURS } from '$lib/names';
	import Avatar from '$ui/Avatar.svelte';
	import Chibi from '$ui/Chibi.svelte';
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
	// One row of characters per island, so a full class never climbs over the answer's sign; a count
	// stands for everyone else on that island.
	const visible = $derived(big ? 5 : 4);
	const size = $derived(big ? 42 : 30);

	function standing(pad: string) {
		// The child's own character stands at the front of the crowd.
		return onLand.filter((p) => pond.picks[p.id] === pad).sort((a, b) => Number(b.id === me) - Number(a.id === me));
	}

	function colour(index: number, id: string) {
		if (id === 'true') return 't1';
		if (id === 'false') return 't0';
		return `t${index % 6}`;
	}
</script>

<figure class="pond" class:big class:revealing>
	<svg class="water" viewBox="0 0 400 300" preserveAspectRatio="none" aria-hidden="true">
		<rect width="400" height="300" fill="#3ba7d9" />
		<g class="ripples" stroke="#9fd8f0" stroke-width="3" fill="none" stroke-linecap="round">
			<path d="M30 40 q12 -6 24 0 t24 0" /><path d="M300 30 q12 -6 24 0" /><path d="M180 150 q12 -6 24 0 t24 0" />
			<path d="M40 210 q12 -6 24 0" /><path d="M330 190 q12 -6 24 0 t24 0" /><path d="M150 270 q12 -6 24 0" />
		</g>
		<g fill="#6cb33f">
			<path d="M372 262 m-16 0 a16 7 0 1 0 32 0 a16 7 0 1 0 -32 0z M372 262 l14 -3 -1 6z" />
			<path d="M20 120 m-13 0 a13 6 0 1 0 26 0 a13 6 0 1 0 -26 0z" />
		</g>
		<circle cx="378" cy="259" r="4" fill="#ff9ec4" />
	</svg>

	<div class="pads pads-{pond.pads.length}">
		{#each pond.pads as pad, i (pad.id)}
			{@const right = pond.correctPads.includes(pad.id)}
			{@const crowd = standing(pad.id)}
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
				<span class="sign">
					<span class="flag">
						{#if pad.id === 'true'}<Icon name="check" size={20} />{:else if pad.id === 'false'}<Icon name="close" size={20} />{:else}{LETTERS[i]}{/if}
					</span>
					<span class="label">{pad.text}</span>
				</span>
				<span class="island">
					<svg class="land" viewBox="0 0 200 110" aria-hidden="true">
						<ellipse cx="100" cy="84" rx="99" ry="24" fill="#bfe6f6" opacity=".75" />
						<ellipse cx="100" cy="74" rx="92" ry="25" fill="#d9a35f" />
						<ellipse cx="100" cy="64" rx="92" ry="25" fill="#e9c98b" />
						<ellipse cx="100" cy="58" rx="82" ry="20" fill="#8fd05e" />
						<ellipse cx="78" cy="52" rx="34" ry="8" fill="#a6dd75" opacity=".8" />
						{#if i % 2 === 0}
							<path d="M28 58 q-4 -26 6 -46" stroke="#8e5a2e" stroke-width="5" fill="none" stroke-linecap="round" />
							<path d="M34 12 q-16 -4 -24 8 q12 -5 24 -8 q-2 -12 -14 -14 q9 5 14 14 q8 -10 20 -6 q-12 0 -20 6 q13 0 16 12 q-5 -9 -16 -12" fill="#3e8e57" />
						{:else}
							<circle cx="170" cy="50" r="11" fill="#3e8e57" /><circle cx="160" cy="54" r="9" fill="#4fa35b" /><circle cx="168" cy="47" r="3" fill="#ff7aa2" />
						{/if}
					</svg>
					<span class="crowd">
						{#each crowd.slice(0, visible) as person (person.id)}
							<span class="who" class:me={person.id === me} in:receive={{ key: person.id }} out:send={{ key: person.id }}>
								<Chibi
									animal={person.avatar}
									colour={person.colour}
									skin={person.skin}
									{size}
									mood={revealing ? (right ? 'cheer' : 'oops') : 'happy'}
								/>
							</span>
						{/each}
						{#if crowd.length > visible}<span class="more">+{crowd.length - visible}</span>{/if}
					</span>
					{#if revealing && !right}<span class="splash" aria-hidden="true"></span>{/if}
				</span>
				{#if revealing && right}<span class="badge"><Icon name="check" size={20} /></span>{/if}
			</button>
		{/each}
	</div>

	{#if fish.length}
		<div class="swim">
			<span class="hint">Ikan</span>
			{#each fish.slice(0, 10) as person (person.id)}
				<span class="fish" title="{person.name} jadi ikan" style:--fin={COLOURS[person.colour] ?? COLOURS.hijau}>
					<svg class="tail" viewBox="0 0 20 20" aria-hidden="true"><path d="M2 10 L18 2 L14 10 L18 18z" /></svg>
					<Avatar animal={person.avatar} colour={person.colour} skin={person.skin} size={26} />
				</span>
			{/each}
		</div>
	{/if}

	{#if waiting.length && stage === 'question'}
		<div class="shore">
			<span class="hint">Belum lompat</span>
			<span class="waiting">
				{#each waiting.slice(0, 10) as person (person.id)}
					<span class="who" in:receive={{ key: person.id }} out:send={{ key: person.id }}>
						<Chibi animal={person.avatar} colour={person.colour} skin={person.skin} size={big ? 34 : 26} />
					</span>
				{/each}
			</span>
		</div>
	{:else}
		<div class="edge"></div>
	{/if}
</figure>

<style>
	.pond {
		position: relative;
		display: grid;
		gap: 0.4rem;
		margin: 0;
		padding: 0.9rem 0.8rem 0;
		border-radius: var(--r-lg);
		overflow: hidden;
		box-shadow: var(--card-shadow);
	}
	.water {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
	}
	.ripples {
		animation: drift 6s ease-in-out infinite alternate;
	}
	@keyframes drift {
		to {
			transform: translateX(12px);
		}
	}
	.pads {
		position: relative;
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 0.4rem 0.8rem;
	}
	.pads-3 {
		grid-template-columns: repeat(3, minmax(0, 1fr));
	}
	.pad {
		--c: var(--coral);
		position: relative;
		display: grid;
		justify-items: center;
		align-content: end;
		gap: 0.2rem;
		padding: 0.2rem 0 0;
		border: 0;
		background: transparent;
		color: var(--ink);
		cursor: pointer;
		transition:
			transform 700ms var(--spring),
			opacity 700ms,
			filter 700ms;
	}
	.pad.t0 { --c: var(--coral); }
	.pad.t1 { --c: var(--sea); }
	.pad.t2 { --c: var(--sun); }
	.pad.t3 { --c: var(--sky); }
	.pad:disabled {
		cursor: default;
	}
	.pad:not(:disabled):hover .island {
		transform: translateY(-4px);
	}
	.pad:not(:disabled):active .island {
		transform: scale(0.97, 0.94);
	}
	.pad:focus-visible {
		outline: none;
	}
	.pad:focus-visible .label {
		outline: 3px solid var(--sun);
		outline-offset: 2px;
	}
	.sign {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		max-width: 100%;
	}
	.flag {
		display: grid;
		place-items: center;
		flex: none;
		width: 2rem;
		height: 2rem;
		border-radius: 0.65rem;
		background: var(--c);
		color: #fff;
		font: 600 1.05rem var(--font-display);
		box-shadow: 0 3px 0 rgb(0 0 0 / 0.18);
	}
	.label {
		min-width: 0;
		padding: 0.15rem 0.7rem;
		border-radius: var(--r-pill);
		background: #fff;
		font: 600 clamp(0.95rem, 0.85rem + 0.5vw, 1.2rem) / 1.2 var(--font-display);
		text-align: center;
		overflow-wrap: break-word;
		box-shadow: 0 2px 0 rgb(0 0 0 / 0.1);
	}
	.big .label {
		font-size: 1.45rem;
	}
	.big .flag {
		width: 2.5rem;
		height: 2.5rem;
	}
	.pad.mine .label {
		outline: 3px solid var(--ink);
	}
	/* The island: a 200 x 110 drawing whose grass top is where the characters stand. */
	.island {
		position: relative;
		display: block;
		width: 100%;
		aspect-ratio: 200 / 110;
		transition: transform var(--t-state) var(--spring);
	}
	/* On the big screen the islands stay a size that leaves the question in view on a laptop. */
	.big .island {
		max-width: 16rem;
	}
	.land {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		overflow: visible;
	}
	.crowd {
		position: absolute;
		left: 6%;
		right: 6%;
		bottom: 40%;
		display: flex;
		justify-content: center;
		align-items: flex-end;
		line-height: 0;
	}
	.crowd .who + .who {
		margin-left: -0.5rem;
	}
	.who.me {
		position: relative;
		z-index: 1;
		filter: drop-shadow(0 0 2px #fff) drop-shadow(0 2px 0 var(--sun-deep));
	}
	.more {
		align-self: center;
		margin-left: 0.2rem;
		padding: 0 0.4rem;
		border-radius: var(--r-pill);
		background: #fff;
		font-weight: 800;
		font-size: 0.85rem;
		line-height: 1.6;
	}
	.pad.sink .island {
		transform: translateY(14%);
		opacity: 0.45;
		filter: saturate(0.4);
	}
	.pad.sink .sign {
		opacity: 0.6;
	}
	.pad.right .island {
		animation: pop-in 600ms var(--spring);
	}
	.badge {
		position: absolute;
		top: 0;
		right: 0.4rem;
		display: grid;
		place-items: center;
		width: 2rem;
		height: 2rem;
		border-radius: 50%;
		background: #fff;
		color: var(--good);
		box-shadow: 0 2px 0 rgb(0 0 0 / 0.15);
		animation: pop-in 500ms var(--spring) 200ms both;
	}
	.splash {
		position: absolute;
		left: 50%;
		bottom: 22%;
		width: 80%;
		height: 30%;
		translate: -50% 0;
		border-radius: 50%;
		border: 4px solid rgb(255 255 255 / 0.85);
		animation: splash 900ms ease-out 2;
	}
	@keyframes splash {
		from {
			transform: scale(0.4);
			opacity: 1;
		}
		to {
			transform: scale(1.3);
			opacity: 0;
		}
	}
	/* The near shore, where children who have not hopped yet wait, and the fish swim by. */
	.shore {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		align-items: flex-end;
		gap: 0.3rem 0.6rem;
		min-height: 2.6rem;
		margin-inline: -0.8rem;
		padding: 0.5rem 0.9rem 0.6rem;
		background: #e9cf98;
		box-shadow: inset 0 3px 0 #f6e2b5;
	}
	.hint {
		align-self: center;
		color: #6b4a2e;
		font-weight: 800;
		font-size: 0.85rem;
	}
	.waiting {
		display: flex;
		align-items: flex-end;
		line-height: 0;
	}
	.waiting .who + .who {
		margin-left: -0.3rem;
	}
	.swim {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.25rem 0.4rem;
	}
	.swim .hint {
		color: #fff;
	}
	.edge {
		height: 0.6rem;
	}
	.fish {
		position: relative;
		display: inline-flex;
		align-items: center;
		animation: bob 2s ease-in-out infinite;
	}
	.tail {
		width: 0.9rem;
		height: 0.9rem;
		margin-right: -0.25rem;
		fill: var(--fin);
	}
	@media (max-width: 420px) {
		.pads-3 {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}
</style>
