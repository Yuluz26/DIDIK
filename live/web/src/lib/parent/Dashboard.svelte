<!--
	"Papan pemuka saya": the parent's overview, in the shape of a soft dashboard: three stat cards with mini
	bars, a bar chart of the questions they have written, their latest quizzes, and two colour cards (the
	rooms open now, and Legenda Story Mode). Every number comes from the parent's real quizzes and rooms.
-->
<script lang="ts">
	import { storyArt } from '$lib/games/legenda/data';
	import { session } from '$lib/session.svelte';
	import { TYPE_NAMES, parent } from './store.svelte';
	import Kawaii from './ui/Kawaii.svelte';
	import NmIcon from './ui/NmIcon.svelte';
	import StatCard from './ui/StatCard.svelte';

	const TYPE_KEYS = Object.keys(TYPE_NAMES);
	const SHORT: Record<string, string> = {
		single: 'Pilihan',
		multiple: 'Banyak',
		truefalse: 'B/S',
		text: 'Taip',
		number: 'Nombor',
		order: 'Susun',
		match: 'Padan',
		blank: 'Isi'
	};
	const TINY: Record<string, string> = { single: 'Pil', multiple: 'Ban', truefalse: 'B/S', text: 'Tai', number: 'Nom', order: 'Sus', match: 'Pad', blank: 'Isi' };
	const WORLDS = ['chini', 'lupar', 'larut', 'kancil', 'ledang'];

	let scope = $state<'semua' | 'mine' | 'samples'>('semua');

	const first = $derived(session.user?.name?.split(' ')[0] ?? '');
	const counts = (quizzes: typeof parent.mine) => TYPE_KEYS.map((t) => quizzes.reduce((n, q) => n + (q.types[t] ?? 0), 0));
	const mineByType = $derived(counts(parent.mine));
	const sampleByType = $derived(counts(parent.samples));
	const top = $derived(Math.max(4, ...(scope === 'samples' ? [] : mineByType), ...(scope === 'mine' ? [] : sampleByType)));
	const step = $derived(top <= 8 ? 2 : top <= 20 ? 5 : top <= 50 ? 10 : 20);
	const ceil = $derived(Math.ceil(top / step) * step);
	const ticks = $derived(Array.from({ length: ceil / step + 1 }, (_, i) => ceil - i * step));

	const recent = $derived(parent.recent.length ? parent.recent.slice(0, 4) : parent.samples.slice(0, 4));
	const recentIsSample = $derived(!parent.recent.length);
	const room = $derived(parent.rooms[0]);
	const playable = $derived(parent.mine.find((q) => q.questionCount >= 10) ?? parent.samples.find((q) => q.questionCount >= 10));

	const fmt = (n: number) => n.toLocaleString('ms-MY');
</script>

<div class="nm-head">
	<div>
		<h1>Papan pemuka saya</h1>
		<p>Selamat datang{first ? `, ${first}` : ''}! Apa kita mainkan hari ini?</p>
	</div>
	<a class="btn btn--sun" href="/ibu-bapa/kuiz/baru"><NmIcon name="plus" size={18} /> Kuiz baharu</a>
</div>

{#if parent.problem}<p class="problem" role="alert">{parent.problem}</p>{/if}

<div class="grid">
	<section class="stats" aria-label="Ringkasan">
		<StatCard
			title="Kuiz saya"
			value={fmt(parent.mine.length)}
			bars={parent.mine.map((q) => q.questionCount)}
			tone="blue"
			chip={{ text: `${fmt(parent.totalQuestions)} soalan`, tone: 'blue', icon: 'check' }}
		/>
		<StatCard
			title="Kuiz contoh"
			value={fmt(parent.samples.length)}
			bars={parent.samples.map((q) => q.questionCount)}
			tone="purple"
			chip={{ text: 'siap dimain', tone: 'green', icon: 'play' }}
		/>
		<StatCard
			title="Bilik langsung"
			value={fmt(parent.rooms.length)}
			bars={parent.rooms.map((r) => r.players)}
			tone="pink"
			chip={{ text: `${fmt(parent.totalPlayers)} pemain`, tone: 'pink', icon: 'heart' }}
		/>
	</section>

	<section class="nm-card chart" aria-labelledby="chart-title">
		<div class="chart-head">
			<h2 id="chart-title">Soalan mengikut jenis</h2>
			<label class="select">
				<span class="visually-hidden">Tunjukkan</span>
				<select bind:value={scope}>
					<option value="semua">Semua kuiz</option>
					<option value="mine">Kuiz saya</option>
					<option value="samples">Kuiz contoh</option>
				</select>
				<NmIcon name="down" size={16} />
			</label>
		</div>
		<p class="legend">
			{#if scope !== 'samples'}<span><i class="dot blue"></i> Kuiz saya</span>{/if}
			{#if scope !== 'mine'}<span><i class="dot green"></i> Kuiz contoh</span>{/if}
		</p>

		<div class="plot" role="img" aria-label="Carta bar bilangan soalan bagi setiap jenis soalan">
			<ul class="yaxis" aria-hidden="true">
				{#each ticks as t (t)}<li>{t}</li>{/each}
			</ul>
			<div class="bars">
				<div class="grid-lines" aria-hidden="true">{#each ticks as t (t)}<i></i>{/each}</div>
				{#each TYPE_KEYS as key, i (key)}
					<div class="col">
						<div class="pair">
							{#if scope !== 'samples'}
								<span class="bar blue" style:height="{(mineByType[i] / ceil) * 100}%" title="{TYPE_NAMES[key]}: {mineByType[i]} soalan saya"></span>
							{/if}
							{#if scope !== 'mine'}
								<span class="bar green" style:height="{(sampleByType[i] / ceil) * 100}%" title="{TYPE_NAMES[key]}: {sampleByType[i]} soalan contoh"></span>
							{/if}
						</div>
						<span class="x"><span class="long">{SHORT[key]}</span><span class="tiny">{TINY[key]}</span></span>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<section class="nm-card people" aria-labelledby="recent-title">
		<h2 id="recent-title">{recentIsSample ? 'Kuiz contoh' : 'Kuiz terkini'}</h2>
		<ul>
			{#each recent as quiz (quiz.id)}
				<li>
					<span class="face"><Kawaii seed={quiz.title} size={46} /></span>
					<a class="who" href={quiz.isSample ? `/ibu-bapa/kuiz/${quiz.id}/main` : `/ibu-bapa/kuiz/${quiz.id}`}>
						<strong>{quiz.title}</strong>
						<small>{quiz.questionCount} soalan · {Object.keys(quiz.types).length} jenis</small>
					</a>
					<a class="round" href="/ibu-bapa/kuiz/{quiz.id}/main" aria-label="Main bersama: {quiz.title}" aria-disabled={!quiz.questionCount}>
						<NmIcon name="play" size={16} />
					</a>
				</li>
			{:else}
				<li class="none">
					<Kawaii seed="kosong" size={52} mood="sleepy" />
					<p>{parent.loading ? 'Membuka kuiz…' : 'Belum ada kuiz. Tulis yang pertama!'}</p>
				</li>
			{/each}
		</ul>
		<a class="all" href={recentIsSample ? '/ibu-bapa/contoh' : '/ibu-bapa/kuiz'}>Lihat semua <NmIcon name="next" size={14} /></a>
	</section>

	<div class="colour">
		<section class="tile blue" aria-labelledby="room-title">
			<h2 id="room-title">Bilik langsung</h2>
			{#if room}
				<p class="sub">{room.mode.title}<br />{room.quizTitle}</p>
				<p class="big"><span>{room.code.slice(0, 3)}</span> <span>{room.code.slice(3)}</span></p>
				<p class="meta">kod bilik · {room.players} pemain{#if parent.rooms.length > 1} · +{parent.rooms.length - 1} lagi{/if}</p>
				<a class="pill" href="/hos/{room.code}">Buka skrin hos <NmIcon name="next" size={14} /></a>
			{:else}
				<p class="sub">Tiada bilik dibuka<br />Pilih kuiz, tekan Main bersama.</p>
				<div class="mascot-row"><Kawaii seed="bilik" size={62} mood="wink" /></div>
				<a class="pill" href="/ibu-bapa/kuiz">Pilih kuiz <NmIcon name="next" size={14} /></a>
			{/if}
		</section>

		<section class="tile purple" aria-labelledby="story-title">
			<h2 id="story-title">Legenda Story Mode</h2>
			<p class="sub">Lima dunia legenda Melayu<br />Solo atau bersama kawan</p>
			<ul class="worlds" aria-hidden="true">
				{#each WORLDS as w (w)}<li><img src={storyArt(`ui/symbol_${w}.webp`)} alt="" width="34" height="34" /></li>{/each}
			</ul>
			<a class="pill" href={playable ? `/ibu-bapa/kuiz/${playable.id}/main` : '/ibu-bapa/permainan'}>Cuba sekarang <NmIcon name="next" size={14} /></a>
		</section>
	</div>
</div>

<style>
	.problem {
		margin-bottom: 1rem;
		color: #b04a00;
		font-weight: 800;
	}
	.grid {
		display: grid;
		grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr) minmax(0, 0.62fr);
		gap: clamp(1rem, 2vw, 1.6rem);
		align-items: stretch;
	}
	.stats {
		grid-column: 1 / -1;
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: clamp(1rem, 2vw, 1.6rem);
	}

	/* ---- the chart */
	.chart {
		padding: 1.3rem 1.4rem 1.2rem;
		min-width: 0;
	}
	.chart-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.8rem;
	}
	h2 {
		font: 500 1.08rem/1.2 var(--font-display);
	}
	.select {
		position: relative;
		display: inline-flex;
		align-items: center;
	}
	.select select {
		appearance: none;
		padding: 0.45rem 2rem 0.45rem 0.95rem;
		border: 0;
		border-radius: 999px;
		background: #eceef5;
		box-shadow: inset 3px 3px 7px rgb(163 172 198 / 0.45), inset -3px -3px 7px rgb(255 255 255 / 0.95);
		color: var(--ink-2);
		font: 600 0.85rem/1.1 var(--font-display);
		cursor: pointer;
	}
	.select :global(.nm-icon) {
		position: absolute;
		right: 0.7rem;
		pointer-events: none;
		color: var(--ink-3);
	}
	.legend {
		display: flex;
		justify-content: flex-end;
		gap: 1rem;
		margin: 0.5rem 0 0.2rem;
		color: var(--ink-2);
		font-size: 0.8rem;
		font-weight: 700;
	}
	.legend span {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
	}
	.dot {
		width: 0.55rem;
		height: 0.55rem;
		border-radius: 50%;
	}
	.blue {
		--bar: linear-gradient(180deg, #7aa5ff, #4a78ee);
	}
	.green {
		--bar: linear-gradient(180deg, #4de3c3, #14b894);
	}
	.dot.blue {
		background: #5b8cf5;
	}
	.dot.green {
		background: #1fc7a5;
	}
	.plot {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 0.6rem;
		height: 16.5rem;
		padding-bottom: 1.5rem;
	}
	.yaxis {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		margin: 0;
		padding: 0 0 0.2rem;
		list-style: none;
		color: var(--ink-3);
		font-size: 0.72rem;
		font-weight: 700;
		text-align: right;
	}
	.bars {
		position: relative;
		display: grid;
		grid-template-columns: repeat(8, 1fr);
		gap: 0.2rem;
	}
	.grid-lines {
		position: absolute;
		inset: 0 0 0 0;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}
	.grid-lines i {
		height: 0;
		border-top: 1px solid rgb(163 172 198 / 0.28);
	}
	.col {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		min-width: 0;
	}
	.pair {
		display: flex;
		align-items: flex-end;
		justify-content: center;
		gap: 0.28rem;
		width: 100%;
		flex: 1;
	}
	.bar {
		width: clamp(0.4rem, 22%, 0.8rem);
		min-height: 3px;
		border-radius: 999px 999px 3px 3px;
		background: var(--bar);
		box-shadow: 2px 3px 6px rgb(120 130 170 / 0.3);
		transition: height 500ms var(--ease-out);
	}
	.x .tiny {
		display: none;
	}
	.x {
		position: absolute;
		bottom: -1.45rem;
		color: var(--ink-3);
		font-size: 0.7rem;
		font-weight: 700;
		white-space: nowrap;
	}

	/* ---- the latest quizzes */
	.people {
		padding: 1.3rem 1.3rem 1rem;
		display: flex;
		flex-direction: column;
		min-width: 0;
	}
	.people ul {
		display: grid;
		gap: 0.2rem;
		margin: 0.7rem 0 0.4rem;
		padding: 0;
		list-style: none;
	}
	.people li {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.65rem 0;
		border-bottom: 1px solid rgb(255 255 255 / 0.9);
		box-shadow: 0 1px 0 rgb(163 172 198 / 0.2);
	}
	.people li:last-child {
		border-bottom: 0;
		box-shadow: none;
	}
	.face {
		display: grid;
		place-items: center;
		flex: none;
		width: 3rem;
		height: 3rem;
		border-radius: 50%;
		background: #eceef5;
		box-shadow: var(--nm-out-sm);
		line-height: 0;
	}
	.who {
		display: grid;
		flex: 1;
		min-width: 0;
		color: var(--ink);
		text-decoration: none;
	}
	.who strong {
		overflow: hidden;
		font: 500 0.98rem/1.2 var(--font-display);
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.who small {
		color: var(--ink-2);
		font-size: 0.8rem;
		font-weight: 700;
	}
	.who:hover strong {
		color: var(--brand-ink);
	}
	.round {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.5rem;
		height: 2.5rem;
		border-radius: 50%;
		background: var(--nm-surface);
		box-shadow: var(--nm-out-sm);
		color: var(--brand-ink);
		transition:
			box-shadow 180ms,
			transform 180ms;
	}
	.round:hover {
		transform: translateY(-1px);
		color: var(--nm-pink);
	}
	.round:active {
		box-shadow: var(--nm-in);
	}
	.round[aria-disabled='true'] {
		opacity: 0.4;
		pointer-events: none;
	}
	.none {
		flex-direction: column;
		justify-content: center;
		padding: 1.4rem 0 !important;
		color: var(--ink-2);
		font-weight: 700;
		text-align: center;
	}
	.all {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		margin-top: auto;
		align-self: flex-end;
		color: var(--brand-ink);
		font: 600 0.88rem/1 var(--font-display);
		text-decoration: none;
	}

	/* ---- the two colour cards */
	.colour {
		display: grid;
		grid-template-rows: 1fr 1fr;
		gap: clamp(1rem, 2vw, 1.6rem);
	}
	.tile {
		position: relative;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		min-width: 0;
		padding: 1.1rem 1.1rem 1rem;
		border-radius: 1.4rem;
		color: #fff;
		overflow: hidden;
	}
	.tile::before,
	.tile::after {
		content: '';
		position: absolute;
		border-radius: 50%;
		background: rgb(255 255 255 / 0.12);
		pointer-events: none;
	}
	.tile::before {
		right: -2rem;
		top: -2.2rem;
		width: 7rem;
		height: 7rem;
	}
	.tile::after {
		left: -1.5rem;
		bottom: -2.5rem;
		width: 5rem;
		height: 5rem;
		background: rgb(255 255 255 / 0.08);
	}
	.tile.blue {
		background: linear-gradient(145deg, #4a90ff, #2a63e6);
		box-shadow: 0 16px 28px rgb(50 100 230 / 0.35);
	}
	.tile.purple {
		background: linear-gradient(145deg, #9a7bff, #6b4fe0);
		box-shadow: 0 16px 28px rgb(110 80 220 / 0.35);
	}
	.tile h2 {
		font: 600 1rem/1.2 var(--font-display);
		color: #fff;
	}
	.sub {
		font-size: 0.78rem;
		font-weight: 700;
		line-height: 1.35;
		color: rgb(255 255 255 / 0.85);
	}
	.big {
		display: flex;
		gap: 0.5rem;
		font: 500 clamp(1.5rem, 1.1rem + 1vw, 2rem) / 1 var(--font-display);
		letter-spacing: 0.02em;
	}
	.meta {
		font-size: 0.78rem;
		font-weight: 800;
		color: rgb(255 255 255 / 0.9);
	}
	.mascot-row {
		line-height: 0;
	}
	.worlds {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem;
		margin: 0.1rem 0;
		padding: 0;
		list-style: none;
	}
	.worlds li {
		display: grid;
		place-items: center;
		line-height: 0;
	}
	.worlds img {
		width: 1.85rem;
		height: 1.85rem;
		filter: drop-shadow(0 3px 5px rgb(40 20 120 / 0.4));
	}
	.pill {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		align-self: flex-start;
		margin-top: auto;
		padding: 0.4rem 0.85rem;
		border-radius: 999px;
		background: rgb(255 255 255 / 0.22);
		box-shadow: inset 0 1px 0 rgb(255 255 255 / 0.35);
		color: #fff;
		font: 600 0.82rem/1 var(--font-display);
		text-decoration: none;
		transition: background 180ms;
	}
	.pill:hover {
		background: rgb(255 255 255 / 0.34);
	}
	.pill:focus-visible {
		outline-color: #fff;
	}

	@media (max-width: 80rem) {
		.grid {
			grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		}
		.colour {
			grid-column: 1 / -1;
			grid-template-rows: none;
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}
	@media (max-width: 52rem) {
		.grid,
		.stats {
			grid-template-columns: minmax(0, 1fr);
		}
		.colour {
			grid-template-columns: minmax(0, 1fr);
		}
		.plot {
			height: 14rem;
		}
		.x .long {
			display: none;
		}
		.x .tiny {
			display: inline;
		}
	}
</style>
