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
	import Kawaii from '$lib/parent/ui/Kawaii.svelte';
	import NmIcon from '$lib/parent/ui/NmIcon.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';
	import DashShell from '$lib/parent/DashShell.svelte';

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

<DashShell>
	<div class="nm-head">
		<div>
			<a class="back" href="/ibu-bapa/kuiz"><NmIcon name="back" size={16} /> Kuiz saya</a>
			<h1>Pilih permainan</h1>
			{#if title}<p>untuk <strong>{title}</strong> · {count} soalan</p>{/if}
		</div>
	</div>
	{#if problem}<p class="problem" role="alert">{problem}</p>{/if}

	{#if !modes.length && !problem}
		<div class="loading"><Kawaii seed="muat" size={90} mood="wow" /></div>
	{/if}

	<ul class="games">
		{#each modes as mode, i (mode.key)}
			<li style:--i={i} class:wide={mode.key === 'legenda'}>
				{#if mode.key === 'legenda'}
					<div class="game nm-card legend" class:off={!!mode.reason}>
						<span class="badge"><WorldBadge world={mode.world} size={64} /></span>
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
					<button type="button" class="game nm-card" class:off={!!mode.reason} disabled={!!mode.reason || !!opening} onclick={() => open(mode)}>
						<span class="badge"><WorldBadge world={mode.world} size={64} /></span>
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
						<span class="go" aria-hidden="true">{opening === mode.key ? '…' : ''}<NmIcon name="next" size={20} /></span>
					</button>
				{/if}
			</li>
		{/each}
	</ul>
	<p class="after">Selepas memilih, anda akan dapat pautan, kod QR dan kod 6 digit untuk dikongsi. Tetapan boleh diubah di lobi.</p>
</DashShell>

<style>
	.back {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		margin-bottom: 0.4rem;
		color: var(--ink-2);
		font: 600 0.9rem/1 var(--font-display);
		text-decoration: none;
	}
	.back:hover {
		color: var(--brand-ink);
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
		animation: rise-in var(--t-enter) var(--ease-out) both;
		animation-delay: calc(var(--i) * 50ms);
	}
	.games li.wide {
		grid-column: 1 / -1;
	}
	.game {
		display: flex;
		align-items: center;
		gap: 1rem;
		width: 100%;
		height: 100%;
		padding: 1.1rem 1.2rem;
		border: 0;
		text-align: left;
		cursor: pointer;
		transition:
			transform 200ms var(--spring),
			box-shadow 200ms;
	}
	button.game:not(:disabled):hover {
		transform: translateY(-3px);
		box-shadow: 12px 12px 26px rgb(163 172 198 / 0.5), -12px -12px 26px rgb(255 255 255 / 0.95);
	}
	button.game:not(:disabled):active {
		transform: scale(0.985);
		box-shadow: var(--nm-in);
	}
	.game.legend {
		cursor: default;
		flex-wrap: wrap;
		background: linear-gradient(145deg, #f1ecff, #e5ddff);
	}
	.game.off {
		cursor: not-allowed;
		opacity: 0.6;
	}
	.badge {
		display: grid;
		place-items: center;
		flex: none;
		width: 4.6rem;
		height: 4.6rem;
		border-radius: 50%;
		background: #eceef5;
		box-shadow: inset 3px 3px 7px rgb(163 172 198 / 0.4), inset -3px -3px 7px rgb(255 255 255 / 0.95);
	}
	.text {
		display: grid;
		gap: 0.2rem;
		flex: 1;
		min-width: 0;
	}
	.kind {
		color: var(--brand-ink);
		font: 600 0.72rem/1 var(--font-display);
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}
	.title {
		font: 500 1.3rem/1.15 var(--font-display);
		color: var(--ink);
	}
	.tagline {
		color: var(--ink-2);
		font-weight: 600;
		font-size: 0.93rem;
	}
	.reason {
		color: #b04a00;
		font-weight: 800;
		font-size: 0.88rem;
	}
	.fit {
		color: #0f8a6f;
		font: 600 0.85rem/1.2 var(--font-display);
	}
	.go {
		display: inline-flex;
		align-items: center;
		color: var(--ink-3);
	}
	.pair {
		display: flex;
		flex-wrap: wrap;
		gap: 0.6rem;
	}
	.after {
		margin-top: 1.2rem;
		color: var(--ink-2);
	}
	.problem {
		color: #b04a00;
		font-weight: 800;
	}
	.loading {
		display: grid;
		place-items: center;
		padding: 3rem;
	}
</style>
