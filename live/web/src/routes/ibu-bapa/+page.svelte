<!--
	The parent area: sign in, then your quizzes, the sample quizzes, and rooms still open.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { session } from '$lib/session.svelte';
	import Didi from '$ui/Didi.svelte';
	import Icon from '$ui/Icon.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';
	import ParentHeader from '$lib/parent/ParentHeader.svelte';
	import SignIn from '$lib/parent/SignIn.svelte';

	interface QuizSummary {
		id: number;
		title: string;
		description: string;
		questionCount: number;
		types: Record<string, number>;
		isSample: boolean;
		updatedAt: string | null;
	}

	interface ActiveRoom {
		code: string;
		slug: string;
		quizTitle: string;
		mode: { title: string; world: string };
		phase: string;
		players: number;
	}

	const TYPE_NAMES: Record<string, string> = {
		single: 'Pilihan',
		multiple: 'Pilih semua',
		truefalse: 'Betul/Salah',
		text: 'Taip',
		number: 'Nombor',
		order: 'Susun',
		match: 'Padan',
		blank: 'Isi kosong'
	};

	let mine = $state<QuizSummary[]>([]);
	let samples = $state<QuizSummary[]>([]);
	let rooms = $state<ActiveRoom[]>([]);
	let loading = $state(true);
	let deleting = $state<number | null>(null);
	let problem = $state<string | null>(null);

	async function load() {
		loading = true;
		try {
			const data = await api.get<{ mine: QuizSummary[]; samples: QuizSummary[] }>('/api/quizzes');
			mine = data.mine;
			samples = data.samples;
			rooms = (await api.get<{ rooms: ActiveRoom[] }>('/api/rooms/mine')).rooms;
		} catch (error) {
			problem = (error as Error).message;
		}
		loading = false;
	}

	let loadedFor: number | null = null;

	onMount(() => {
		void session.load();
	});

	$effect(() => {
		// Load the quizzes for whoever is signed in, including right after signing in on this page.
		const user = session.user;
		if (user && loadedFor !== user.id) {
			loadedFor = user.id;
			void load();
		}
	});

	async function copy(quiz: QuizSummary) {
		const copied = await api.post<{ id: number }>(`/api/quizzes/${quiz.id}/copy`);
		await goto(`/ibu-bapa/kuiz/${copied.id}`);
	}

	async function remove(quiz: QuizSummary) {
		await api.del(`/api/quizzes/${quiz.id}`);
		deleting = null;
		mine = mine.filter((q) => q.id !== quiz.id);
	}
</script>

<svelte:head><title>Kuiz saya · DIDIK Main Bersama</title></svelte:head>

<ParentHeader />

{#if !session.loaded}
	<main class="wrap loading" aria-busy="true"><Didi mood="think" size={110} /></main>
{:else if !session.user}
	<main class="wrap welcome">
		<section class="pitch">
			<p class="kind">Untuk ibu bapa dan guru</p>
			<h1>Tulis kuiz anda sendiri. Anak-anak main bersama.</h1>
			<p class="lead">Lapan jenis soalan, dua belas permainan, satu pautan untuk masuk. Tiada akaun untuk kanak-kanak, tiada iklan, percuma.</p>
			<ul class="points">
				<li><Icon name="edit" /> Anda tulis setiap soalan. Tiada soalan dijana oleh AI.</li>
				<li><Icon name="link" /> Kongsi pautan, kod QR atau kod 6 digit.</li>
				<li><Icon name="heart" /> Nama samaran sahaja; tiada sembang bebas.</li>
			</ul>
		</section>
		<SignIn />
	</main>
{:else}
	<main class="wrap dash">
		{#if rooms.length}
			<section class="rooms">
				<h2>Bilik yang masih dibuka</h2>
				<ul>
					{#each rooms as room (room.code)}
						<li>
							<WorldBadge world={room.mode.world} size={44} />
							<div class="room-text">
								<strong>{room.mode.title}</strong>
								<span>{room.quizTitle} · kod {room.code} · {room.players} pemain</span>
							</div>
							<a class="btn btn--sea" href="/hos/{room.code}">Buka skrin hos <Icon name="next" /></a>
						</li>
					{/each}
				</ul>
			</section>
		{/if}

		<section class="block">
			<div class="block-head">
				<h1>Kuiz saya</h1>
				<a class="btn btn--sun" href="/ibu-bapa/kuiz/baru"><Icon name="plus" /> Kuiz baharu</a>
			</div>
			{#if problem}<p class="problem" role="alert">{problem}</p>{/if}
			{#if !loading && !mine.length}
				<div class="empty">
					<Didi mood="wave" size={110} />
					<div>
						<h2>Belum ada kuiz anda sendiri</h2>
						<p>Mulakan dengan kuiz kosong, atau salin satu contoh di bawah dan ubah ikut anak anda.</p>
					</div>
				</div>
			{/if}
			<ul class="quizzes">
				{#each mine as quiz (quiz.id)}
					<li class="quiz">
						<div class="info">
							<h3><a href="/ibu-bapa/kuiz/{quiz.id}">{quiz.title}</a>{#if quiz.isSample}<span class="chip sample-chip">Contoh</span>{/if}</h3>
							{#if quiz.description}<p>{quiz.description}</p>{/if}
							<p class="types">
								<span class="count">{quiz.questionCount} soalan</span>
								{#each Object.entries(quiz.types) as [type, n] (type)}<span class="chip">{TYPE_NAMES[type] ?? type} ×{n}</span>{/each}
							</p>
						</div>
						<div class="actions">
							<a class="btn btn--sun" href="/ibu-bapa/kuiz/{quiz.id}/main" aria-disabled={!quiz.questionCount}><Icon name="play" /> Main bersama</a>
							<a class="btn btn--plain" href="/ibu-bapa/kuiz/{quiz.id}"><Icon name="edit" /> Sunting</a>
							<button type="button" class="btn btn--plain btn--icon" onclick={() => copy(quiz)} aria-label="Salin {quiz.title}"><Icon name="copy" /></button>
							{#if deleting === quiz.id}
								<span class="confirm">Padam kuiz ini?
									<button type="button" class="btn btn--coral" onclick={() => remove(quiz)}>Ya, padam</button>
									<button type="button" class="btn btn--plain" onclick={() => (deleting = null)}>Batal</button>
								</span>
							{:else}
								<button type="button" class="btn btn--plain btn--icon" onclick={() => (deleting = quiz.id)} aria-label="Padam {quiz.title}"><Icon name="trash" /></button>
							{/if}
						</div>
					</li>
				{/each}
			</ul>
		</section>

		{#if samples.length}
			<section class="block">
				<div class="block-head">
					<h2>Contoh kuiz</h2>
					<p class="note">Sedia untuk dimainkan. Salin untuk mengubah soalannya.</p>
				</div>
				<ul class="quizzes">
					{#each samples as quiz (quiz.id)}
						<li class="quiz sample">
							<div class="info">
								<h3>{quiz.title}</h3>
								{#if quiz.description}<p>{quiz.description}</p>{/if}
								<p class="types">
									<span class="count">{quiz.questionCount} soalan</span>
									{#each Object.entries(quiz.types) as [type, n] (type)}<span class="chip">{TYPE_NAMES[type] ?? type} ×{n}</span>{/each}
								</p>
							</div>
							<div class="actions">
								<a class="btn btn--sun" href="/ibu-bapa/kuiz/{quiz.id}/main"><Icon name="play" /> Main bersama</a>
								<button type="button" class="btn btn--plain" onclick={() => copy(quiz)}><Icon name="copy" /> Salin dan ubah</button>
							</div>
						</li>
					{/each}
				</ul>
			</section>
		{/if}
	</main>
{/if}

<style>
	.loading {
		display: grid;
		place-items: center;
		min-height: 60vh;
	}
	.welcome {
		display: grid;
		grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
		gap: 3rem;
		align-items: center;
		padding-block: 3rem 4rem;
	}
	.pitch h1 {
		margin: 0.6rem 0 1rem;
		font-size: var(--fs-h1);
	}
	.lead {
		font-size: var(--fs-lead);
		color: var(--ink-2);
	}
	.points {
		display: grid;
		gap: 0.7rem;
		margin: 1.6rem 0 0;
		padding: 0;
		list-style: none;
		font-weight: 700;
	}
	.points li {
		display: flex;
		align-items: center;
		gap: 0.6rem;
	}
	.points :global(.icon) {
		color: var(--brand-ink);
	}
	.dash {
		display: grid;
		gap: 2.6rem;
		padding-block: 2rem 4rem;
	}
	.block {
		display: grid;
		gap: 1rem;
	}
	.block-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		flex-wrap: wrap;
	}
	.block-head h1,
	.block-head h2 {
		font-size: var(--fs-h1);
	}
	.note {
		color: var(--ink-2);
	}
	.quizzes {
		display: grid;
		gap: 0.8rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.quiz {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1.2rem;
		padding: 1rem 1.2rem;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
		flex-wrap: wrap;
	}
	.info {
		display: grid;
		gap: 0.3rem;
		min-width: 0;
		flex: 1 1 22rem;
	}
	.info h3 {
		font-size: 1.35rem;
	}
	.info h3 a {
		color: var(--ink);
		text-decoration: none;
	}
	.sample-chip {
		margin-left: 0.6rem;
		vertical-align: middle;
		background: var(--brand-soft);
		color: var(--brand-deep);
	}
	.info h3 a:hover {
		color: var(--brand-ink);
	}
	.info p {
		color: var(--ink-2);
	}
	.types {
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem;
		align-items: center;
	}
	.count {
		margin-right: 0.3rem;
		font-weight: 800;
		color: var(--ink);
	}
	.actions {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	.confirm {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		font-weight: 800;
	}
	.empty {
		display: flex;
		align-items: center;
		gap: 1.4rem;
		padding: 1.4rem;
		border: 2px dashed var(--line);
		border-radius: var(--r-lg);
	}
	.empty h2 {
		font-size: 1.4rem;
	}
	.empty p {
		color: var(--ink-2);
	}
	.rooms {
		display: grid;
		gap: 0.7rem;
		padding: 1rem 1.2rem;
		border-radius: var(--r-lg);
		background: var(--brand-soft);
	}
	.rooms h2 {
		font-size: 1.2rem;
	}
	.rooms ul {
		display: grid;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.rooms li {
		display: flex;
		align-items: center;
		gap: 0.8rem;
		flex-wrap: wrap;
	}
	.room-text {
		display: grid;
		flex: 1;
		min-width: 12rem;
	}
	.room-text span {
		color: var(--ink-2);
		font-size: 0.92rem;
	}
	.problem {
		color: #9a4a00;
		font-weight: 800;
	}
	@media (max-width: 860px) {
		.welcome {
			grid-template-columns: minmax(0, 1fr);
			gap: 2rem;
			padding-block: 2rem;
		}
	}
</style>
