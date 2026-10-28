<!-- Permainan: every game a room can play, and what each one needs from a quiz. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { session } from '$lib/session.svelte';
	import DashShell from '$lib/parent/DashShell.svelte';
	import Kawaii from '$lib/parent/ui/Kawaii.svelte';
	import NmIcon from '$lib/parent/ui/NmIcon.svelte';
	import type { ModeInfo } from '$lib/types';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';

	let modes = $state<ModeInfo[]>([]);
	let problem = $state('');
	let loading = $state(true);

	onMount(() => {
		void (async () => {
			if (!(await session.load())) return;
			try {
				modes = (await api.get<{ modes: ModeInfo[] }>('/api/modes')).modes;
			} catch (error) {
				problem = (error as Error).message;
			}
			loading = false;
		})();
	});
</script>

<svelte:head><title>Permainan · DIDIK Main Bersama</title></svelte:head>

<DashShell>
	<div class="nm-head">
		<div>
			<h1>Permainan</h1>
			<p>Semua permainan boleh dimainkan dengan mana-mana kuiz yang sesuai. Pilih pada halaman kuiz.</p>
		</div>
		<a class="btn btn--sun" href="/ibu-bapa/kuiz"><NmIcon name="play" size={16} /> Pilih kuiz untuk dimain</a>
	</div>

	{#if problem}<p role="alert" class="problem">{problem}</p>{/if}
	{#if loading}
		<div class="wait"><Kawaii seed="main" size={70} mood="wow" /></div>
	{/if}

	<ul class="games">
		{#each modes as mode (mode.key)}
			<li class="nm-card" class:story={mode.key === 'legenda'}>
				<span class="badge"><WorldBadge world={mode.world} size={60} /></span>
				<div class="text">
					<p class="kind">{mode.style}</p>
					<h2>{mode.title}</h2>
					<p class="tagline">{mode.tagline}</p>
					<p class="how">{mode.how}</p>
					{#if mode.needs}<p class="needs"><NmIcon name="check" size={14} /> Soalan {mode.needs}</p>{/if}
				</div>
			</li>
		{/each}
	</ul>
</DashShell>

<style>
	.problem {
		color: #b04a00;
		font-weight: 800;
	}
	.wait {
		display: grid;
		place-items: center;
		padding: 3rem;
	}
	.games {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 22rem), 1fr));
		gap: 1.2rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.games li {
		display: flex;
		gap: 1rem;
		padding: 1.2rem 1.3rem;
	}
	.games li.story {
		background: linear-gradient(145deg, #efe9ff, #e4dcff);
		grid-column: 1 / -1;
	}
	.badge {
		display: grid;
		place-items: center;
		flex: none;
		width: 4.4rem;
		height: 4.4rem;
		border-radius: 50%;
		background: #eceef5;
		box-shadow: inset 3px 3px 7px rgb(163 172 198 / 0.4), inset -3px -3px 7px rgb(255 255 255 / 0.95);
	}
	.text {
		display: grid;
		gap: 0.25rem;
		min-width: 0;
	}
	.kind {
		color: var(--brand-ink);
		font: 600 0.74rem/1 var(--font-display);
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}
	h2 {
		font: 500 1.3rem/1.15 var(--font-display);
	}
	.tagline {
		color: var(--ink);
		font-weight: 700;
	}
	.how {
		color: var(--ink-2);
		font-size: 0.93rem;
	}
	.needs {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		margin-top: 0.2rem;
		color: #0f8a6f;
		font: 600 0.85rem/1.2 var(--font-display);
	}
</style>
