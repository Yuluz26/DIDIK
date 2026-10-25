<!--
	Lompat!'s pond, in the worlds' 3/4 view. Each answer is a small island with a sandy edge; children's
	characters stand on the island they chose and hop across when they change their mind. When time
	is up, the wrong islands sink. Children still on the shore wait at the bottom; children out of
	hearts swim as fish until two right answers bring them back to land.
-->
<script lang="ts">
	import { crossfade } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { snapScale, prescale, urlOf } from '$lib/pixel/cache';
	import { CW } from '$lib/pixel/chibi';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import type { Person } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';
	import Chibi from '$ui/Chibi.svelte';
	import Icon from '$ui/Icon.svelte';
	import { HEADROOM, ISLAND, STAND, fishTail, island, pondWater, shoreSand, splash } from './sprites';

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
	const visible = 4;

	// Every picture in the pond is drawn at one pixel size, chosen so an island fits its column.
	let width = $state(0);
	let innerHeight = $state(800);
	const cols = $derived(pond.pads.length === 3 && width >= 420 ? 3 : 2);
	const rows = $derived(Math.ceil(pond.pads.length / cols));
	const padWidth = $derived(Math.min((width - 26 - 13 * (cols - 1)) / cols, big ? 340 : 400));
	// On the big screen the whole pond stays within about half the screen's height, so the
	// statement above it is never pushed away: more rows of islands mean smaller pixels.
	const padHeight = $derived(big ? ((innerHeight * 0.55 - 90) / rows - 48) / (ISLAND.h + HEADROOM) : Infinity);
	const s = $derived(snapScale(Math.min(padWidth / ISLAND.w, padHeight), 1));
	const k = $derived(prescale(s));
	const water = $derived(urlOf(pondWater(), k));
	const sand = $derived(urlOf(shoreSand(), k));

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

<svelte:window bind:innerHeight />

<figure class="pond" class:big class:revealing bind:clientWidth={width} style:--s="{s}px">
	<div class="water" aria-hidden="true" style:background-image="url({water})" style:background-size="{48 * s}px {48 * s}px"></div>

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
				<span class="island" style:width="{ISLAND.w * s}px" style:height="{(ISLAND.h + HEADROOM) * s}px">
					<span class="art" style:top="{HEADROOM * s}px"><Sprite sheet={island(i)} {s} /></span>
					<span class="crowd" style:left="{STAND.left * s}px" style:width="{STAND.width * s}px" style:bottom="{(ISLAND.h - STAND.y - 2) * s}px" style:--overlap="{-CW * 0.4 * s}px">
						{#each crowd.slice(0, visible) as person (person.id)}
							<span class="who" class:me={person.id === me} in:receive={{ key: person.id }} out:send={{ key: person.id }}>
								<Chibi
									animal={person.avatar}
									colour={person.colour}
									skin={person.skin}
									{s}
									mood={revealing ? (right ? 'cheer' : 'oops') : 'happy'}
								/>
							</span>
						{/each}
						{#if crowd.length > visible}<span class="more">+{crowd.length - visible}</span>{/if}
					</span>
					{#if revealing && !right}<span class="splash" aria-hidden="true" style:left="{(ISLAND.w / 2 - 28) * s}px" style:bottom="{3 * s}px"><Sprite sheet={splash()} {s} frames={3} ms={900} /></span>{/if}
				</span>
				{#if revealing && right}<span class="badge"><Icon name="check" size={20} /></span>{/if}
			</button>
		{/each}
	</div>

	{#if fish.length}
		<div class="swim">
			<span class="hint">Ikan</span>
			{#each fish.slice(0, 10) as person (person.id)}
				<span class="fish" title="{person.name} jadi ikan">
					<span class="tail"><Sprite sheet={fishTail(person.colour)} s={2} /></span>
					<Avatar animal={person.avatar} colour={person.colour} skin={person.skin} size={26} />
				</span>
			{/each}
		</div>
	{/if}

	{#if waiting.length && stage === 'question'}
		<div class="shore" style:background-image="url({sand})" style:background-size="{32 * s}px {32 * s}px">
			<span class="hint">Belum lompat</span>
			<span class="waiting">
				{#each waiting.slice(0, 10) as person (person.id)}
					<span class="who" in:receive={{ key: person.id }} out:send={{ key: person.id }}>
						<Chibi animal={person.avatar} colour={person.colour} skin={person.skin} {s} />
					</span>
				{/each}
				{#if waiting.length > 10}<span class="more">+{waiting.length - 10}</span>{/if}
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
		background-color: #2a88a6;
		animation: pond-drift 16s steps(48) infinite;
	}
	/* The water slides one sprite pixel at a time. */
	@keyframes pond-drift {
		to {
			background-position: calc(var(--s) * 48) 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.water {
			animation: none;
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
		transform: translateY(calc(var(--s) * -2));
	}
	.pad:not(:disabled):active .island {
		transform: translateY(var(--s));
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
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: var(--c);
		color: #fff;
		font: 700 1.05rem var(--font-pixel);
		box-shadow: 0 3px 0 #2a1f2d;
	}
	.label {
		min-width: 0;
		padding: 0.1rem 0.6rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		color: #2a1f2d;
		font: 600 clamp(0.95rem, 0.85rem + 0.5vw, 1.2rem) / 1.2 var(--font-pixel);
		text-align: center;
		overflow-wrap: break-word;
		box-shadow: 0 3px 0 #2a1f2d;
	}
	.big .label {
		font-size: 1.4rem;
	}
	.big .flag {
		width: 2.5rem;
		height: 2.5rem;
	}
	.pad.mine .label {
		background: var(--sun);
	}
	/* The island picture; the characters stand on its grass. */
	.island {
		position: relative;
		display: block;
		transition: transform var(--t-state) var(--spring);
	}
	.art {
		position: absolute;
		left: 0;
		line-height: 0;
	}
	.crowd {
		position: absolute;
		display: flex;
		justify-content: center;
		align-items: flex-end;
		line-height: 0;
	}
	.crowd .who + .who {
		margin-left: var(--overlap);
	}
	/* The child's own character has a plain white edge, drawn a sprite pixel wide. */
	.who.me {
		position: relative;
		z-index: 1;
		filter: drop-shadow(var(--s) 0 0 #fff) drop-shadow(calc(var(--s) * -1) 0 0 #fff) drop-shadow(0 var(--s) 0 #fff) drop-shadow(0 calc(var(--s) * -1) 0 #fff);
	}
	.more {
		align-self: center;
		margin-left: 0.2rem;
		padding: 0 0.35rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		color: #2a1f2d;
		font: 700 0.85rem/1.4 var(--font-pixel);
	}
	.pad.sink .island {
		transform: translateY(calc(var(--s) * 5));
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
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		color: var(--good);
		box-shadow: 0 3px 0 #2a1f2d;
		animation: pop-in 500ms var(--spring) 200ms both;
	}
	.splash {
		position: absolute;
		line-height: 0;
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
		background-color: #e9c78d;
		box-shadow: inset 0 calc(var(--s) * 2) 0 #fff0cc;
	}
	.hint {
		align-self: center;
		color: #6b4a2e;
		font: 700 0.85rem var(--font-pixel);
	}
	.waiting {
		display: flex;
		align-items: flex-end;
		line-height: 0;
	}
	.waiting .who + .who {
		margin-left: calc(var(--s) * -7);
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
		animation: bob 2s steps(2) infinite;
	}
	.tail {
		margin-right: -0.25rem;
		line-height: 0;
	}
</style>
