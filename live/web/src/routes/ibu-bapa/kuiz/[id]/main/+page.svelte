<!--
	"Main bersama": choose one of the games for this quiz and open a room, in three kinds: Kuiz
	Interaktif, the 2D island games and the story mode. Every game suits any class; the teacher or
	parent picks by taste. Games the quiz cannot support
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
	import Sticker from '$ui/Sticker.svelte';
	import { byFamily } from '$lib/families';
	import { interaktifKind, kindGames } from '$lib/interaktifKinds';
	import { SUBJECTS } from '$lib/subjects/games';

	const id = page.params.id;
	let title = $state('');
	let count = $state(0);
	let modes = $state<ModeInfo[]>([]);
	let opening = $state<string | null>(null);
	let problem = $state<string | null>(null);
	let lockedGame = $state('');
	let lockDialog = $state<HTMLDialogElement>();

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
		problem = null;
		play('pop');
		opening = mode.key + (solo ? ':solo' : '');
		try {
			const body: Record<string, unknown> = { quiz_id: Number(id), mode: mode.key };
			if (solo) body.settings = { max_players: 1 };
			const room = await api.post<{ code: string }>('/api/rooms', body);
			await goto(`/hos/${room.code}`);
		} catch (error) {
			if (error instanceof ApiError && error.status === 403 && error.code === 'membership_required') {
				lockedGame = mode.title;
				lockDialog?.showModal();
			} else {
				problem = error instanceof ApiError ? error.message : 'Bilik tidak dapat dibuka. Cuba lagi.';
			}
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

	{#each byFamily(modes) as group, g (group.family.key)}
	<section class="family fam-{group.family.key}" aria-labelledby="fam-{group.family.key}">
		<header class="fam-head">
			<span class="fam-art" aria-hidden="true"><Sticker key={group.family.sticker} size={40} alt="" /></span>
			<div>
				<h2 id="fam-{group.family.key}">{group.family.name} {#if group.family.key === 'interaktif'}<span class="new">Baharu</span>{/if}</h2>
				<p>{group.family.note}</p>
			</div>
		</header>
	<ul class="games">
		{#each group.modes as mode, i (mode.key)}
			<li style:--i={i + g * 3} class:wide={mode.key === 'legenda'}>
				{#if mode.family === 'interaktif'}
					{@const kind = interaktifKind(mode.key)}
					{@const games = kind ? kindGames(kind) : []}
					<button
						type="button"
						class="game nm-card ik"
						class:off={!!mode.reason}
						style:--tint={kind?.tint}
						style:--kind-ink={kind?.ink}
						disabled={!!mode.reason || !!opening}
						onclick={() => open(mode)}
					>
						<span class="ik-stickers" aria-hidden="true">
							{#each kind?.stickers ?? ['epal', 'bakul', 'buku'] as s, k (s)}<Sticker key={s} size={k === 1 ? 58 : 46} alt="" />{/each}
						</span>
						<span class="text">
							<span class="kind">{kind?.kicker ?? mode.style}</span>
							<span class="title">{mode.title}</span>
							<span class="tagline">{mode.tagline}</span>
							{#if games.length}
								<span class="chips" aria-label="Permainan">
									{#each games.slice(0, 4) as game (game.key)}<span class="chip">{game.title}</span>{/each}
									<span class="chip more">+{games.length - 4} lagi</span>
								</span>
							{/if}
							{#if mode.reason}
								<span class="reason">{mode.reason}</span>
							{:else if mode.subject}
								<span class="fit">
									{mode.eligible === count ? `Kesemua ${count} soalan` : `${mode.eligible} daripada ${count} soalan`} menjadi permainan {SUBJECTS.find((s) => s.key === mode.subject)?.name}.{mode.eligible === count ? '' : ' Yang lain dimainkan seperti biasa.'}
								</span>
							{:else}
								<span class="fit">Semua jenis soalan boleh dimainkan. Paling seronok dengan Kira, Susun huruf dan Isih.</span>
							{/if}
						</span>
						<span class="go" aria-hidden="true">{opening === mode.key ? '…' : ''}<NmIcon name="next" size={20} /></span>
					</button>
				{:else if mode.key === 'legenda'}
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
	</section>
	{/each}
	<p class="after">Selepas memilih, anda akan dapat pautan, kod QR dan kod 6 digit untuk dikongsi. Tetapan boleh diubah di lobi.</p>
</DashShell>

<dialog
	bind:this={lockDialog}
	class="access-dialog"
	role="alertdialog"
	aria-labelledby="access-title"
	aria-describedby="access-description"
	onclick={(event) => { if (event.target === lockDialog) lockDialog?.close(); }}
>
	<div class="access-sheet">
		<button type="button" class="access-close" aria-label="Tutup popup" onclick={() => lockDialog?.close()}><NmIcon name="close" size={20} /></button>
		<div class="access-art" aria-hidden="true">
			<span class="access-star"><Sticker key="bintang-bersinar" size={56} alt="" /></span>
			<Kawaii seed="akses-keahlian" size={104} mood="sleepy" />
		</div>
		<p class="access-kicker">Pintu permainan terkunci sekejap</p>
		<h2 id="access-title">Alamak, belum boleh main!</h2>
		<p id="access-description"><strong>{lockedGame}</strong> tersedia untuk keahlian DIDIK Premium atau Family. Jika baru menghantar bukti bayaran, tunggu admin sahkan dahulu ya.</p>
		<div class="access-actions">
			<a class="access-upgrade" href="/ibu-bapa/keahlian">Lihat pelan keahlian <NmIcon name="next" size={18} /></a>
			<button type="button" class="access-back" onclick={() => lockDialog?.close()}>Pilih permainan lain</button>
		</div>
	</div>
</dialog>

<style>
	.access-dialog{width:min(31rem,calc(100vw - 2rem));max-height:calc(100dvh - 2rem);margin:auto;padding:0;border:2px solid #6f519b;border-radius:24px;background:#fff9f0;color:var(--ink);box-shadow:0 18px 65px rgb(32 25 62 / .28);overflow:auto;animation:access-pop 260ms cubic-bezier(.23,1,.32,1) both}
	.access-dialog::backdrop{background:rgb(24 20 49 / .55);backdrop-filter:blur(3px)}
	.access-sheet{position:relative;display:grid;justify-items:center;padding:2rem clamp(1.2rem,5vw,2.5rem) 2.2rem;text-align:center;isolation:isolate}
	.access-sheet::before{content:'';position:absolute;z-index:-1;inset:0 0 auto;height:8rem;background:#eee3ff;border-radius:22px 22px 50% 50%}
	.access-close{position:absolute;top:.85rem;right:.85rem;display:grid;place-items:center;width:2.7rem;height:2.7rem;border:0;border-radius:50%;background:#fff;color:#584475;cursor:pointer;transition:transform 160ms cubic-bezier(.23,1,.32,1)}
	.access-art{position:relative;margin:.5rem 0 .8rem;line-height:0}.access-star{position:absolute;right:-1.3rem;top:-.5rem;transform:rotate(12deg);animation:access-twinkle 2.4s ease-in-out infinite}
	.access-kicker{margin:.3rem 0 .4rem;color:#7050a7;font:800 .78rem/1.3 var(--font-body);letter-spacing:.08em;text-transform:uppercase}
	.access-dialog h2{font:700 clamp(1.8rem,6vw,2.35rem)/1.1 var(--font-display);margin:0;color:#3d3154}
	.access-dialog p#access-description{max-width:35ch;margin:.9rem 0 1.5rem;color:#574e60;line-height:1.6}
	.access-actions{display:grid;width:100%;gap:.7rem}.access-upgrade,.access-back{display:flex;align-items:center;justify-content:center;gap:.4rem;min-height:3.1rem;border-radius:12px;font:800 1rem var(--font-body);text-decoration:none;cursor:pointer}
	.access-upgrade{background:#6e50b8;color:#fff;box-shadow:0 4px 0 #453478;transition:transform 160ms cubic-bezier(.23,1,.32,1),box-shadow 160ms ease}.access-back{border:2px solid #d9c9e9;background:#fff;color:#55436d}.access-dialog :is(a,button):focus-visible{outline:3px solid #db5c8e;outline-offset:3px}
	@media(hover:hover) and (pointer:fine){.access-close:hover{transform:rotate(90deg)}.access-upgrade:hover{transform:translateY(-2px);box-shadow:0 6px 0 #453478}}
	@keyframes access-pop{from{opacity:0;transform:translateY(14px) scale(.96)}to{opacity:1;transform:translateY(0) scale(1)}}
	@keyframes access-twinkle{50%{transform:rotate(-8deg) scale(1.08)}}
	@media(prefers-reduced-motion:reduce){.access-dialog,.access-star{animation:none}.access-close,.access-upgrade{transition:none}.access-close:hover,.access-upgrade:hover{transform:none}}
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
	.family {
		display: grid;
		gap: 0.9rem;
	}
	.family + .family {
		margin-top: 2rem;
	}
	.fam-head {
		display: flex;
		align-items: center;
		gap: 0.8rem;
	}
	.fam-art {
		display: grid;
		place-items: center;
		flex: none;
		width: 3.2rem;
		height: 3.2rem;
		border-radius: 50%;
		background: #fff;
		box-shadow: 0 4px 10px rgb(163 172 198 / 0.35);
	}
	.fam-head h2 {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.5rem;
		font: 600 1.35rem/1.15 var(--font-display);
	}
	.fam-head p {
		color: var(--ink-2);
		font-size: 0.93rem;
	}
	.new {
		padding: 0.15rem 0.6rem;
		border-radius: 999px;
		background: linear-gradient(135deg, #ff7eb0, #ffb36e);
		color: #fff;
		font-size: 0.75rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
	}
	/* The four kinds of Kuiz Interaktif side by side: stickers on top, the words under them, each kind in
	   its own colours. */
	.game.ik {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		grid-template-areas: 'art go' 'text text';
		align-items: center;
		align-content: start;
		gap: 0.6rem 0.8rem;
		background: var(--tint, linear-gradient(135deg, #ffe8f3, #eee6ff 50%, #e3f6ff));
	}
	.game.ik .ik-stickers {
		grid-area: art;
	}
	.game.ik .text {
		grid-area: text;
	}
	.game.ik .go {
		grid-area: go;
	}
	.game.ik .kind,
	.game.ik .title {
		color: var(--kind-ink, var(--brand-ink));
	}
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem;
		margin-block: 0.2rem;
	}
	.chip {
		padding: 0.15rem 0.55rem;
		border-radius: 999px;
		background: rgb(255 255 255 / 0.75);
		color: var(--ink-2);
		font: 600 0.78rem/1.3 var(--font-display);
	}
	.chip.more {
		background: transparent;
		color: var(--kind-ink, var(--brand-ink));
	}
	.ik-stickers {
		display: flex;
		align-items: flex-end;
		flex: none;
		gap: 0.1rem;
	}
	.ik-stickers :global(img:nth-child(2)) {
		animation: float-y 3s ease-in-out infinite;
	}
	@keyframes float-y {
		50% {
			transform: translateY(-5px) rotate(-3deg);
		}
	}
	/* On a phone the stickers sit on their own row, so the words get the card's whole width. */
	@media (max-width: 560px) {
		.fam-head {
			align-items: flex-start;
			gap: 0.6rem;
		}
		.fam-art {
			width: 2.6rem;
			height: 2.6rem;
		}
		.fam-art :global(img) {
			width: 30px;
			height: 30px;
		}
		.fam-head h2 {
			font-size: 1.2rem;
		}
		.fam-head p {
			font-size: 0.88rem;
		}
		.game.ik {
			padding: 1rem;
		}
		.game.ik .title {
			font-size: 1.45rem;
		}
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
	/* The words keep room to read; where the card is narrow (a phone), Solo and Party drop to their
	   own row under them instead of squeezing them. */
	.game.legend .text {
		flex: 1 1 14rem;
	}
	.game.legend .pair {
		flex: 1 1 12rem;
		justify-content: flex-end;
	}
	.game.legend .pair :global(.btn) {
		flex: 1 1 0;
		max-width: 11rem;
		min-height: 3rem;
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
