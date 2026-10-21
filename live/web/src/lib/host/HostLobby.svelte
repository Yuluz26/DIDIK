<!--
	The host's waiting room: how to join, who has joined, the game and its settings, practice bots,
	and Mula. Settings and the game can change until the game starts.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person, RoomSettings, View } from '$lib/types';
	import Icon from '$ui/Icon.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';
	import PlayerWall from '$lib/play/PlayerWall.svelte';
	import Stickers from '$lib/play/Stickers.svelte';
	import JoinPanel from './JoinPanel.svelte';

	let { client, view }: { client: RoomClient; view: View } = $props();

	let wallEl = $state<HTMLElement>();
	const players = $derived(client.roster.filter((p) => p.approved));
	const pending = $derived(client.roster.filter((p) => !p.approved));
	const bots = $derived(client.roster.filter((p) => p.bot).length);
	const settings = $derived(view.settings as RoomSettings);
	const mode = $derived(view.room.mode);
	const modes = $derived(view.modes ?? []);
	const blocked = $derived(modes.find((m) => m.key === mode.key)?.reason ?? null);

	function set(patch: Partial<RoomSettings>) {
		client.send({ t: 'settings', settings: patch });
	}

	function remove(person: Person) {
		client.send({ t: 'kick', id: person.id });
	}
</script>

<div class="lobby">
	<div class="main">
		<JoinPanel room={view.room} />

		{#if pending.length}
			<section class="pending">
				<h2>Menunggu kebenaran ({pending.length})</h2>
				<ul>
					{#each pending as person (person.id)}
						<li>
							<strong>{person.name}</strong>
							<button type="button" class="btn btn--sea" onclick={() => client.send({ t: 'approve', id: person.id, yes: true })}><Icon name="check" /> Benarkan</button>
							<button type="button" class="btn btn--plain" onclick={() => client.send({ t: 'approve', id: person.id, yes: false })}>Tolak</button>
						</li>
					{/each}
				</ul>
			</section>
		{/if}

		<section class="room" bind:this={wallEl}>
			<div class="room-head">
				<h2><Icon name="users" /> {players.length} dalam bilik</h2>
				{#if view.botsAllowed}
					<div class="bots" role="group" aria-label="Pemain bot untuk uji">
						<span><Icon name="bot" /> Bot</span>
						<button type="button" class="btn btn--plain btn--icon" disabled={bots === 0} onclick={() => client.send({ t: 'bots', change: -1 })} aria-label="Kurangkan bot"><Icon name="minus" /></button>
						<output>{bots}</output>
						<button type="button" class="btn btn--plain btn--icon" disabled={bots >= 12} onclick={() => client.send({ t: 'bots', change: 1 })} aria-label="Tambah bot"><Icon name="plus" /></button>
					</div>
				{/if}
			</div>
			{#if players.length}
				<PlayerWall people={players} size={72} onremove={remove} />
			{:else}
				<p class="empty">Belum ada sesiapa. Kongsi pautan atau tunjuk kod QR di atas. Untuk mencuba seorang diri, tambah beberapa bot.</p>
			{/if}
			<Stickers {client} within={wallEl} />
		</section>
	</div>

	<aside class="side">
		<section class="game card">
			<div class="game-head">
				<WorldBadge world={mode.world} size={64} />
				<div>
					<p class="style">{mode.style}</p>
					<h2>{mode.title}</h2>
				</div>
			</div>
			<p class="how">{mode.how}</p>
			<label class="field">
				<span>Tukar permainan</span>
				<select class="input" value={mode.key} onchange={(e) => client.send({ t: 'mode', key: (e.target as HTMLSelectElement).value })}>
					{#each modes as m (m.key)}
						<option value={m.key} disabled={!!m.reason}>{m.title}{m.reason ? ' (tidak sesuai)' : ''}</option>
					{/each}
				</select>
			</label>
			{#if blocked}<p class="warn">{blocked}</p>{/if}
		</section>

		<section class="settings card">
			<h2>Tetapan</h2>
			{#if mode.pace === 'sync'}
				<label class="field">
					<span>Masa menjawab</span>
					<select class="input" value={settings.timing} onchange={(e) => set({ timing: (e.target as HTMLSelectElement).value as RoomSettings['timing'] })}>
						<option value="normal">Ikut soalan</option>
						<option value="longer">Lebih lama (×1.5)</option>
						<option value="relaxed">Santai (×2)</option>
					</select>
				</label>
			{:else}
				<label class="field">
					<span>Tempoh permainan</span>
					<select class="input" value={settings.minutes} onchange={(e) => set({ minutes: Number((e.target as HTMLSelectElement).value) })}>
						{#each [3, 5, 7, 10, 15] as m (m)}<option value={m}>{m} minit</option>{/each}
					</select>
				</label>
			{/if}
			<label class="toggle"><input type="checkbox" checked={settings.shuffle} onchange={(e) => set({ shuffle: (e.target as HTMLInputElement).checked })} /> Kocok soalan</label>
			<label class="toggle"><input type="checkbox" checked={settings.custom_names} onchange={(e) => set({ custom_names: (e.target as HTMLInputElement).checked })} /> Benarkan nama sendiri (ditapis)</label>
			<label class="toggle"><input type="checkbox" checked={settings.waiting_room} onchange={(e) => set({ waiting_room: (e.target as HTMLInputElement).checked })} /> Saya benarkan setiap pemain dahulu</label>
			<label class="toggle"><input type="checkbox" checked={settings.late_join} onchange={(e) => set({ late_join: (e.target as HTMLInputElement).checked })} /> Boleh masuk selepas mula</label>
			{#if mode.key === 'harta'}
				<label class="toggle"><input type="checkbox" checked={settings.naughty} onchange={(e) => set({ naughty: (e.target as HTMLInputElement).checked })} /> Kejutan nakal (burung kakak tua, ketam)</label>
			{/if}
			<button type="button" class="btn btn--plain lock" onclick={() => client.send({ t: 'lock', on: !view.room.locked })}>
				<Icon name={view.room.locked ? 'lock' : 'unlock'} /> {view.room.locked ? 'Bilik dikunci' : 'Kunci bilik'}
			</button>
		</section>

		<button type="button" class="btn btn--sun btn--big start" class:btn--ready={players.length > 0} disabled={!players.length || !!blocked} onclick={() => client.send({ t: 'start' })}>
			<Icon name="play" /> Mula
		</button>
	</aside>
</div>

<style>
	.lobby {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(18rem, 24rem);
		gap: 1.4rem;
		align-items: start;
	}
	.main {
		display: grid;
		gap: 1.4rem;
		min-width: 0;
	}
	.room {
		position: relative;
		display: grid;
		gap: 1rem;
	}
	.room-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		flex-wrap: wrap;
	}
	.room-head h2 {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		font-size: 1.5rem;
	}
	.bots {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		font-weight: 800;
	}
	.bots span {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		color: var(--ink-2);
	}
	.bots output {
		min-width: 1.6rem;
		text-align: center;
		font: 600 1.2rem var(--font-display);
	}
	.empty {
		padding: 1.4rem;
		border: 2px dashed var(--line);
		border-radius: var(--r-lg);
		color: var(--ink-2);
		text-align: center;
	}
	.pending {
		display: grid;
		gap: 0.6rem;
		padding: 1rem;
		border-radius: var(--r-lg);
		background: #fff3cf;
	}
	.pending h2 {
		font-size: 1.15rem;
	}
	.pending ul {
		display: grid;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.pending li {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		flex-wrap: wrap;
	}
	.pending strong {
		flex: 1;
	}
	.side {
		display: grid;
		gap: 1rem;
		position: sticky;
		top: 1rem;
	}
	.card {
		display: grid;
		gap: 0.8rem;
		padding: 1.1rem;
	}
	.card h2 {
		font-size: 1.3rem;
	}
	.game-head {
		display: flex;
		align-items: center;
		gap: 0.8rem;
	}
	.style {
		color: var(--brand);
		font-weight: 800;
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	.how {
		color: var(--ink-2);
	}
	.warn {
		color: #9a4a00;
		font-weight: 800;
	}
	.toggle {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		font-weight: 700;
		cursor: pointer;
	}
	.toggle input {
		width: 1.3rem;
		height: 1.3rem;
		accent-color: var(--brand);
	}
	.lock {
		justify-self: start;
	}
	.start {
		width: 100%;
		font-size: 1.6rem;
	}
	@media (max-width: 900px) {
		.lobby {
			grid-template-columns: minmax(0, 1fr);
		}
		.side {
			position: static;
		}
	}
</style>
