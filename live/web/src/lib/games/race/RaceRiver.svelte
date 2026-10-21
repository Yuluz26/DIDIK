<!--
	Lumba Sampan's river. Every boat carries its child's animal; distance is drawn to scale against
	the finish line. On a phone the river shows you and the boats nearest you; on the host screen it
	shows everyone.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import { COLOURS } from '$lib/names';
	import Avatar from '$ui/Avatar.svelte';

	interface Race {
		length: number;
		rapids: boolean;
		boats: { id: string; m: number }[];
	}

	let {
		race,
		people,
		me = null,
		compact = false
	}: { race: Race; people: Map<string, Person>; me?: string | null; compact?: boolean } = $props();

	// Remember who moved, so their paddle swings for a moment.
	let previous = new Map<string, number>();
	let rowing = $state(new Set<string>());

	$effect(() => {
		const moved = new Set<string>();
		for (const boat of race.boats) {
			if ((previous.get(boat.id) ?? 0) !== boat.m) moved.add(boat.id);
		}
		previous = new Map(race.boats.map((b) => [b.id, b.m]));
		if (!moved.size) return;
		rowing = moved;
		const timer = setTimeout(() => (rowing = new Set()), 1400);
		return () => clearTimeout(timer);
	});

	const lanes = $derived.by(() => {
		const sorted = [...race.boats].sort((a, b) => b.m - a.m);
		if (!compact || !me) return sorted;
		const at = sorted.findIndex((b) => b.id === me);
		if (at < 0) return sorted.slice(0, 4);
		const from = Math.max(0, Math.min(at - 2, sorted.length - 5));
		return sorted.slice(from, from + 5);
	});

	const progress = (m: number) => Math.min(1, m / Math.max(1, race.length));
</script>

<figure class="river" class:compact class:rapids={race.rapids} style:--lanes={Math.max(lanes.length, compact ? 3 : 4)}>
	<svg class="bank far" viewBox="0 0 800 70" preserveAspectRatio="none" aria-hidden="true">
		<path d="M0 70 V38 Q60 18 120 34 T240 30 T360 36 T480 26 T600 34 T720 28 T800 32 V70 Z" fill="#7dbe4e" />
		<g fill="#3e8e57">
			<circle cx="70" cy="30" r="20" /><circle cx="96" cy="24" r="16" />
			<circle cx="300" cy="26" r="22" /><circle cx="330" cy="32" r="15" />
			<circle cx="560" cy="22" r="20" /><circle cx="590" cy="28" r="16" />
			<circle cx="740" cy="26" r="18" />
		</g>
		<g fill="#2e6e43"><rect x="80" y="40" width="5" height="22" /><rect x="310" y="40" width="5" height="22" /><rect x="570" y="38" width="5" height="22" /></g>
	</svg>

	<div class="water">
		<div class="waves" aria-hidden="true"></div>
		<div class="finish" aria-hidden="true"></div>
		{#each lanes as boat (boat.id)}
			{@const person = people.get(boat.id)}
			<div class="lane">
				<div class="runner" style:transform="translateX({progress(boat.m) * 100}%)">
					<div class="boat" class:mine={boat.id === me} class:rowing={rowing.has(boat.id)}>
						<span class="head"><Avatar animal={person?.avatar} colour={person?.colour} size={compact ? 24 : 34} /></span>
						<svg class="hull" viewBox="0 0 80 30" aria-hidden="true">
							<path class="paddle" d="M50 4 L66 28" stroke="#8e5a2e" stroke-width="3.5" stroke-linecap="round" />
							<path d="M2 10 H78 Q72 28 56 28 H24 Q8 28 2 10 Z" fill="#c9572e" />
							<path d="M6 15 H74" stroke="#f7c948" stroke-width="3" />
							<rect x="2" y="7" width="76" height="5" rx="2.5" fill="#a8432f" />
							<path d="M10 7 V-6 L22 -1 L10 3" fill={COLOURS[person?.colour ?? 'hijau']} />
						</svg>
						{#if !compact || boat.id === me}
							<span class="label">{boat.id === me ? 'Kamu' : person?.name ?? ''}</span>
						{/if}
					</div>
				</div>
			</div>
		{/each}
	</div>

	<svg class="bank near" viewBox="0 0 800 40" preserveAspectRatio="none" aria-hidden="true">
		<path d="M0 0 Q80 14 160 6 T320 8 T480 4 T640 10 T800 4 V40 H0 Z" fill="#e9c98b" />
		<g stroke="#4a8424" stroke-width="4" stroke-linecap="round">
			<path d="M40 20 v-14 M48 22 v-18 M56 20 v-12" /><path d="M420 18 v-14 M428 20 v-16" /><path d="M700 20 v-12 M708 22 v-16" />
		</g>
		<circle cx="240" cy="22" r="6" fill="#ff7aa2" /><circle cx="252" cy="26" r="5" fill="#ffd34d" /><circle cx="600" cy="24" r="6" fill="#ff7aa2" />
	</svg>

	{#if race.rapids}
		<figcaption class="rapids-banner">Arus deras! Semua sampan meluncur ke depan</figcaption>
	{/if}
</figure>

<style>
	.river {
		position: relative;
		margin: 0;
		border-radius: var(--r-lg);
		overflow: hidden;
		background: #cdebff;
		box-shadow: var(--card-shadow);
	}
	.bank {
		display: block;
		width: 100%;
	}
	.far {
		height: 3.2rem;
	}
	.compact .far {
		height: 1.3rem;
	}
	.compact .near {
		height: 0.9rem;
	}
	.near {
		height: 1.6rem;
		margin-top: -2px;
	}
	.water {
		position: relative;
		display: grid;
		grid-template-rows: repeat(var(--lanes), minmax(2.2rem, 1fr));
		min-height: calc(var(--lanes) * 2.9rem);
		padding: 0.4rem 0.6rem 0.6rem;
		background: #3ba7d9;
		overflow: hidden;
	}
	.compact .water {
		min-height: calc(var(--lanes) * 2.25rem);
		padding-block: 0.2rem 0.4rem;
	}
	.waves {
		position: absolute;
		inset: 0 -40% 0 0;
		background-image: repeating-linear-gradient(100deg, transparent 0 46px, rgb(255 255 255 / 0.18) 46px 52px, transparent 52px 120px);
		animation: flow 6s linear infinite;
		pointer-events: none;
	}
	.rapids .waves {
		animation-duration: 1.2s;
	}
	@keyframes flow {
		to {
			transform: translateX(-120px);
		}
	}
	.finish {
		position: absolute;
		top: 0;
		bottom: 0;
		right: 1.2rem;
		width: 0.7rem;
		background: repeating-conic-gradient(#fff 0 25%, #1f2d27 0 50%) 0 0 / 0.7rem 0.7rem;
		opacity: 0.85;
	}
	.lane {
		position: relative;
		padding-right: calc(var(--boat, 5.5rem) + 1.2rem);
	}
	.compact .lane {
		--boat: 3.4rem;
	}
	.runner {
		width: 100%;
		height: 100%;
		transition: transform 1.1s var(--spring);
	}
	.boat {
		position: relative;
		display: grid;
		justify-items: center;
		width: var(--boat, 5.5rem);
		height: 100%;
		align-content: end;
		animation: float 2.8s ease-in-out infinite;
	}
	.compact .boat {
		width: 3.4rem;
	}
	.compact .head {
		margin-bottom: -0.7rem;
	}
	.head {
		position: relative;
		z-index: 1;
		margin-bottom: -0.9rem;
	}
	.hull {
		width: 100%;
		height: auto;
		overflow: visible;
	}
	.paddle {
		transform-origin: 50px 4px;
	}
	.rowing .paddle {
		animation: row 0.45s ease-in-out 3;
	}
	.label {
		position: absolute;
		left: 100%;
		bottom: 0.4rem;
		margin-left: 0.3rem;
		padding: 0.05rem 0.45rem;
		border-radius: var(--r-pill);
		background: rgb(255 255 255 / 0.85);
		font-size: 0.78rem;
		font-weight: 800;
		white-space: nowrap;
	}
	.mine .label {
		background: var(--sun);
	}
	.rapids-banner {
		position: absolute;
		top: 0.6rem;
		left: 50%;
		transform: translateX(-50%);
		padding: 0.35rem 1rem;
		border-radius: var(--r-pill);
		background: #fff;
		color: var(--sky-deep);
		font: 600 1.05rem var(--font-display);
		white-space: nowrap;
		box-shadow: var(--lift-low);
		animation: pop-in 500ms var(--spring);
	}
	@keyframes float {
		0%,
		100% {
			transform: translateY(0) rotate(-1deg);
		}
		50% {
			transform: translateY(-3px) rotate(1deg);
		}
	}
	@keyframes row {
		50% {
			transform: rotate(-28deg);
		}
	}
</style>
