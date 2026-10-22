<!--
	"Main bersama": choose a game for this quiz and open a room. The games are grouped by who they are
	made for, Tahun 1-6 and Tingkatan 1-5; any class can play any of them. Games the quiz cannot support
	(e.g. Lompat! needs Betul/Salah or 2-4 choices) say why instead of failing later.
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

	const LEVELS = [
		{ key: 'rendah', school: 'Sekolah rendah', title: 'Tahun 1–6', note: 'Dunia 2D yang ceria, arahan ringkas.' },
		{ key: 'menengah', school: 'Sekolah menengah', title: 'Tingkatan 1–5', note: 'Permainan 3D yang lebih mencabar: perlumbaan, pasukan, rampasan dan binaan bersama.' }
	] as const;

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

	async function open(mode: ModeInfo) {
		if (mode.reason || opening) return;
		play('pop');
		opening = mode.key;
		try {
			const room = await api.post<{ code: string }>('/api/rooms', { quiz_id: Number(id), mode: mode.key });
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

	{#each LEVELS as level (level.key)}
		{@const group = modes.filter((m) => m.level === level.key)}
		{#if group.length}
			<section class="level" aria-labelledby="level-{level.key}">
				<div class="level-head">
					<p class="kind">{level.school}</p>
					<h2 id="level-{level.key}">{level.title}</h2>
					<p class="level-note">{level.note}</p>
				</div>
				<ul class="games">
					{#each group as mode, i (mode.key)}
						<li style:--i={i}>
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
						</li>
					{/each}
				</ul>
			</section>
		{/if}
	{/each}
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
	.level {
		display: grid;
		gap: 0.9rem;
		margin-top: 0.6rem;
	}
	.level-head h2 {
		font-size: var(--fs-h2);
	}
	.level-note {
		margin-top: 0.2rem;
		color: var(--ink-2);
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
