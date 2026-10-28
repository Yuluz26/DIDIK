<!--
	"Main bersama": choose one of the games for this quiz and open a room. Every game suits any
	class; the teacher or parent picks by taste. Games the quiz cannot support
	(e.g. Lompat! needs Betul/Salah or 2-4 choices) say why instead of failing later. Legenda opens
	either a Solo room (one child) or a Party room; nothing else needs setting up.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { api, ApiError } from '$lib/api';
	import { session } from '$lib/session.svelte';
	import type { ModeInfo } from '$lib/types';
	import { play } from '$lib/sound';
	import Didi from '$ui/Didi.svelte';
	import Icon from '$ui/Icon.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';
	import ParentHeader from '$lib/parent/ParentHeader.svelte';

	const id = page.params.id;
	let title = $state('');
	let count = $state(0);
	let modes = $state<ModeInfo[]>([]);
	let opening = $state<string | null>(null);
	let problem = $state<string | null>(null);

	onMount(async () => {
		if (!(await session.load())) {
			await goto('/ibu-bapa');
			return;
		}
		try {
			const quiz = await api.get<{ title: string; questionCount: number }>(`/api/quizzes/${id}`);
			title = quiz.title;
			count = quiz.questionCount;
			modes = (await api.get<{ modes: ModeInfo[] }>(`/api/modes?quiz_id=${id}`)).modes;
		} catch (error) {
			problem = (error as Error).message;
		}
	});

	async function open(mode: ModeInfo, solo = false) {
		if (mode.reason || opening) return;
		play('pop');
		opening = mode.key + (solo ? ':solo' : '');
		try {
			const body: Record<string, unknown> = { quiz_id: Number(id), mode: mode.key };
			if (solo) body.settings = { max_players: 1 };
			const room = await api.post<{ code: string }>('/api/rooms', body);
			await goto(`/hos/${room.code}`);
		} catch (error) {
			problem = error instanceof ApiError ? error.message : 'Bilik tidak dapat dibuka. Cuba lagi.';
			opening = null;
		}
	}
</script>

<svelte:head><title>Pilih permainan · DIDIK Main Bersama</title></svelte:head>

<ParentHeader />

<main class="wrap pick">
	<a class="back" href="/ibu-bapa"><Icon name="back" size={18} /> Kuiz saya</a>
	<div class="head">
		<h1>Pilih permainan</h1>
		{#if title}<p class="quiz">untuk <strong>{title}</strong> · {count} soalan</p>{/if}
	</div>
	{#if problem}<p class="problem" role="alert">{problem}</p>{/if}

	{#if !modes.length && !problem}
		<div class="loading"><Didi mood="think" size={100} /></div>
	{/if}

	<ul class="games">
		{#each modes as mode, i (mode.key)}
			<li style:--i={i} class:wide={mode.key === 'legenda'}>
				{#if mode.key === 'legenda'}
					<div class="game legend" class:off={!!mode.reason}>
						<WorldBadge world={mode.world} size={92} />
						<span class="text">
							<span class="kind">{mode.style} · Baharu</span>
							<span class="title">{mode.title}</span>
							<span class="tagline">{mode.tagline}</span>
							{#if mode.reason}<span class="reason">{mode.reason}</span>{:else}<span class="fit">Lima dunia, lima boss. Tiada tetapan lain.</span>{/if}
						</span>
						<span class="pair">
							<button type="button" class="btn btn--sun" disabled={!!mode.reason || !!opening} onclick={() => open(mode, true)}>
								{opening === 'legenda:solo' ? '…' : 'Solo'}
							</button>
							<button type="button" class="btn" disabled={!!mode.reason || !!opening} onclick={() => open(mode)}>
								{opening === 'legenda' ? '…' : 'Party'}
							</button>
						</span>
					</div>
				{:else}
				<button type="button" class="game" class:off={!!mode.reason} disabled={!!mode.reason || !!opening} onclick={() => open(mode)}>
					<WorldBadge world={mode.world} size={92} />
					<span class="text">
						<span class="kind">{mode.style}</span>
						<span class="title">{mode.title}</span>
						<span class="tagline">{mode.tagline}</span>
						{#if mode.reason}
							<span class="reason">{mode.reason}</span>
						{:else if mode.needs}
							<span class="fit">{mode.eligible} soalan sesuai</span>
						{/if}
					</span>
					<span class="go" aria-hidden="true">{opening === mode.key ? '…' : ''}<Icon name="next" /></span>
				</button>
				{/if}
			</li>
		{/each}
	</ul>
	<p class="after">Selepas memilih, anda akan dapat pautan, kod QR dan kod 6 digit untuk dikongsi. Tetapan boleh diubah di lobi.</p>
</main>

<style>
	.pick {
		display: grid;
		gap: 1.2rem;
		padding-block: 1.6rem 4rem;
	}
	.back {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-weight: 800;
		text-decoration: none;
		width: fit-content;
	}
	.head h1 {
		font-size: var(--fs-h1);
	}
	.quiz {
		margin-top: 0.3rem;
		color: var(--ink-2);
		font-size: 1.1rem;
	}
	.games {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 22rem), 1fr));
		gap: 1rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.games li {
		animation: rise-in var(--t-enter) var(--ease-out) both;
		animation-delay: calc(var(--i) * 60ms);
	}
	.game {
		display: flex;
		align-items: center;
		gap: 1rem;
		width: 100%;
		height: 100%;
		padding: 1rem 1.1rem;
		border: 0;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
		text-align: left;
		cursor: pointer;
		transition: transform var(--t-state) var(--spring), box-shadow var(--t-state);
	}
	.game:not(:disabled):hover {
		transform: translateY(-4px) rotate(-0.5deg);
		box-shadow: 0 2px 0 var(--line), 0 18px 34px rgb(31 45 39 / 0.14);
	}
	.game:not(:disabled):hover :global(.badge) {
		animation: wiggle 0.6s ease-in-out;
	}
	.game:not(:disabled):active {
		transform: scale(0.98);
	}
	.games li.wide {
		grid-column: 1 / -1;
	}
	.legend {
		cursor: default;
		background:
			radial-gradient(ellipse at 0% 0%, rgb(255 200 90 / 0.18), transparent 50%),
			var(--card);
		box-shadow: inset 0 0 0 2px #d9a441, var(--card-shadow);
	}
	.pair {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.game.off {
		cursor: not-allowed;
		opacity: 0.6;
	}
	.text {
		display: grid;
		gap: 0.15rem;
		flex: 1;
		min-width: 0;
	}
	.title {
		font: 600 1.4rem/1.15 var(--font-display);
	}
	.tagline {
		color: var(--ink-2);
		font-weight: 600;
		font-size: 0.95rem;
	}
	.reason {
		color: #9a4a00;
		font-weight: 800;
		font-size: 0.88rem;
	}
	.fit {
		color: var(--good);
		font-weight: 800;
		font-size: 0.88rem;
	}
	.go {
		display: inline-flex;
		align-items: center;
		color: var(--ink-3);
	}
	.after {
		color: var(--ink-2);
	}
	.problem {
		color: #9a4a00;
		font-weight: 800;
	}
	.loading {
		display: grid;
		place-items: center;
		padding: 3rem;
	}
</style>
