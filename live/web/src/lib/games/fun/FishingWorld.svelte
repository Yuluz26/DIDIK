<!--
	A child's Pancing Ikan: the lake with fish swimming in it, the child on the jetty with a rod, their
	bait, and the bucket of what they caught. A right answer is bait; tap the lake (or the button) to cast.
	What bites shows on a card that splashes up from the water.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { confetti } from '$lib/confetti';
	import { play } from '$lib/sound';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Chibi from '$ui/Chibi.svelte';
	import Icon from '$ui/Icon.svelte';
	import { fish } from './art';

	interface Fish {
		name: string;
		value: number;
	}
	let {
		client,
		world,
		me
	}: { client: RoomClient; world: { fish: Record<string, Fish>; bait: number; gold: number; net: string[]; caught: number; best: string | null }; me: Person } = $props();

	let catchCard = $state<{ key: number; fish: string; value: number; gold: boolean } | null>(null);
	let casting = $state(false);
	let n = 0;
	// the fish that swim about, for show
	const SWIMMERS = ['bilis', 'puyu', 'keli', 'patin', 'kelah', 'bilis', 'puyu'];

	function cast(gold = false) {
		if (casting || (gold ? world.gold < 1 : world.bait < 1)) return;
		casting = true;
		play('pop');
		client.send({ t: 'cast', gold });
		setTimeout(() => (casting = false), 900);
	}

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind !== 'catch') return;
			const key = ++n;
			catchCard = { key, fish: fx.fish, value: fx.value, gold: fx.gold };
			play(fx.value ? 'coin' : 'almost');
			if (fx.fish === 'arowana' || fx.fish === 'kelah') confetti({ count: 60 });
			setTimeout(() => catchCard?.key === key && (catchCard = null), 2200);
		})
	);
</script>

<div class="fun pancing">
	<ul class="stats" aria-label="Simpanan kamu">
		<li><Icon name="drop" size={20} /><strong>{world.bait}</strong> umpan</li>
		<li class="gold"><Icon name="star" size={20} /><strong>{world.gold}</strong> umpan emas</li>
		<li><strong>{world.caught}</strong> ekor ditangkap</li>
	</ul>

	<div class="scene lake">
		<button type="button" class="water" onclick={() => cast(false)} disabled={world.bait < 1} aria-label="Lempar joran ke tasik">
			{#each SWIMMERS as kind, i (i)}
				<span class="swim" style:--y="{18 + ((i * 37) % 60)}%" style:--x="{8 + ((i * 29) % 80)}%" style:--d="{9 + (i % 4) * 2.5}s" style:--delay="{-i * 1.7}s">
					<Sprite sheet={fish(kind)} s={3} flip />
				</span>
			{/each}
			{#if casting}<span class="bob" aria-hidden="true"></span>{/if}
		</button>
		<div class="jetty" aria-hidden="true">
			<span class="angler"><Chibi animal={me.avatar} colour={me.colour} skin={me.skin} s={3} mood={casting ? 'cheer' : 'happy'} /></span>
			<span class="rod" class:cast={casting}></span>
		</div>
		{#if catchCard}
			{#key catchCard.key}
				<div class="catch" class:gold={catchCard.gold} role="status">
					<Sprite sheet={fish(catchCard.fish)} s={4} />
					<p><strong>{world.fish[catchCard.fish]?.name}</strong> {catchCard.value ? `+${catchCard.value} mata` : 'Alamak!'}</p>
				</div>
			{/key}
		{/if}
	</div>

	<div class="acts">
		<button type="button" class="btn btn--sea btn--big" onclick={() => cast(false)} disabled={world.bait < 1 || casting}>Lempar joran</button>
		{#if world.gold > 0}
			<button type="button" class="btn btn--sun btn--big" onclick={() => cast(true)} disabled={casting}>Guna umpan emas</button>
		{/if}
	</div>
	<p class="hint" aria-live="polite">{world.bait || world.gold ? 'Ketik tasik untuk memancing!' : 'Jawab soalan untuk dapat umpan.'}</p>

	{#if world.net.length}
		<section class="bucket" aria-label="Tangkapan terkini">
			{#each world.net as kind, i (i)}<span title={world.fish[kind]?.name}><Sprite sheet={fish(kind)} s={2} /></span>{/each}
		</section>
	{/if}
</div>

<style>
	.fun {
		display: grid;
		gap: 0.7rem;
	}
	.stats {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.stats li {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0.35rem 0.8rem;
		border-radius: var(--r-pill);
		background: var(--card);
		box-shadow: var(--card-shadow);
		font-weight: 800;
	}
	.stats .gold {
		background: #fff3cf;
	}
	.scene {
		position: relative;
		overflow: hidden;
		border-radius: var(--r-lg);
		box-shadow: var(--card-shadow);
		image-rendering: pixelated;
	}
	.lake {
		aspect-ratio: 16 / 10;
		background: linear-gradient(180deg, #8fd6ef 0 22%, #3b9fc2 22% 30%, #2a88a6 30% 100%);
	}
	.water {
		position: absolute;
		inset: 22% 0 0;
		width: 100%;
		border: 0;
		padding: 0;
		background: repeating-linear-gradient(180deg, transparent 0 18px, rgb(255 255 255 / 0.08) 18px 20px);
		cursor: pointer;
	}
	.water:disabled {
		cursor: default;
	}
	.swim {
		position: absolute;
		top: var(--y);
		left: -15%;
		animation: swim var(--d) linear var(--delay) infinite;
		opacity: 0.85;
	}
	.bob {
		position: absolute;
		left: 58%;
		top: 30%;
		width: 14px;
		height: 14px;
		border: 3px solid #fff;
		border-radius: 50%;
		animation: ripple 0.9s ease-out infinite;
	}
	.jetty {
		position: absolute;
		left: 4%;
		bottom: 0;
		width: 38%;
		height: 34%;
		background: repeating-linear-gradient(90deg, #946541 0 14px, #b98657 14px 28px);
		border-top: 4px solid #6e4a30;
	}
	.angler {
		position: absolute;
		left: 18%;
		bottom: 60%;
	}
	.rod {
		position: absolute;
		left: 46%;
		bottom: 120%;
		width: 60%;
		height: 4px;
		background: #4a2c22;
		transform-origin: left center;
		transform: rotate(-24deg);
		transition: transform 0.3s ease;
	}
	.rod.cast {
		transform: rotate(-6deg);
	}
	.catch {
		position: absolute;
		left: 50%;
		top: 18%;
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		translate: -50% 0;
		padding: 0.7rem 1.1rem;
		border-radius: var(--r-lg);
		background: var(--paper);
		box-shadow: var(--card-shadow);
		font-weight: 800;
		text-align: center;
		animation: splash 2.2s ease-out both;
	}
	.catch.gold {
		background: #fff3cf;
	}
	.acts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.6rem;
	}
	.acts .btn {
		flex: 1 1 12rem;
	}
	.hint {
		color: var(--ink-2);
		font-weight: 800;
		text-align: center;
	}
	.bucket {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		padding: 0.6rem;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	@keyframes swim {
		to {
			left: 110%;
			transform: translateY(-6px);
		}
	}
	@keyframes ripple {
		from {
			transform: scale(0.4);
			opacity: 1;
		}
		to {
			transform: scale(2.2);
			opacity: 0;
		}
	}
	@keyframes splash {
		0% {
			opacity: 0;
			transform: translateY(40%) scale(0.7);
		}
		15%,
		80% {
			opacity: 1;
			transform: translateY(0) scale(1);
		}
		100% {
			opacity: 0;
			transform: translateY(-20%);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.swim,
		.bob,
		.catch {
			animation: none;
		}
		.swim {
			left: var(--x);
		}
	}
</style>
