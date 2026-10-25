<!--
	The host's waiting room: how to join and Mula across the top, the town square where children
	appear and walk about, and the game and its settings beside it. Settings and the game can change
	until the game starts.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person, RoomSettings, View } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';
	import Icon from '$ui/Icon.svelte';
	import LobbyPlaza from '$lib/worlds/LobbyPlaza.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';
	import JoinPanel from './JoinPanel.svelte';

	let { client, view }: { client: RoomClient; view: View } = $props();

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
	<div class="strip">
		<JoinPanel room={view.room} />
		<button type="button" class="btn btn--sun btn--big start" class:btn--ready={players.length > 0} disabled={!players.length || !!blocked} onclick={() => client.send({ t: 'start' })}>
			<Icon name="play" size={30} /> Mula
		</button>
	</div>

	<div class="main">
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

		<section class="square" aria-labelledby="square-title">
			<div class="square-head">
				<h2 id="square-title"><Icon name="users" /> {players.length} dalam bilik</h2>
				{#if view.botsAllowed}
					<div class="bots" role="group" aria-label="Pemain bot untuk uji">
						<span><Icon name="bot" /> Bot</span>
						<button type="button" class="btn btn--plain btn--icon" disabled={bots === 0} onclick={() => client.send({ t: 'bots', change: -1 })} aria-label="Kurangkan bot"><Icon name="minus" /></button>
						<output>{bots}</output>
						<button type="button" class="btn btn--plain btn--icon" disabled={bots >= 12} onclick={() => client.send({ t: 'bots', change: 1 })} aria-label="Tambah bot"><Icon name="plus" /></button>
					</div>
				{/if}
			</div>

			<div class="stage">
				<LobbyPlaza people={players} spots={view.plaza ?? []} {client} />
				{#if !players.length}
					<p class="empty">Dataran masih kosong. Kanak-kanak akan muncul di bawah gerbang sebaik sahaja mereka masuk.{view.botsAllowed ? ' Untuk mencuba seorang diri, tambah beberapa bot.' : ''}</p>
				{/if}
			</div>

			{#if players.length}
				<ul class="roster" aria-label="Dalam bilik">
					{#each players as person (person.id)}
						<li class:away={!person.online}>
							<Avatar animal={person.avatar} colour={person.colour} skin={person.skin} size={30} mood={person.online ? 'happy' : 'sleep'} />
							<span class="name">{person.name}</span>
							{#if person.bot}<span class="bot">bot</span>{/if}
							<button type="button" class="tool" onclick={() => remove(person)} aria-label="Keluarkan {person.name}"><Icon name="close" size={16} /></button>
						</li>
					{/each}
				</ul>
			{/if}
		</section>
	</div>

	<aside class="side">
		<section class="game card">
			<div class="game-head">
				<WorldBadge world={mode.world} size={64} />
				<div>
					<p class="kind">{mode.style}</p>
					<h2>{mode.title}</h2>
				</div>
			</div>
			<p class="how">{mode.how}</p>
			<label class="field">
				<span>Tukar permainan</span>
				<select class="input" value={mode.key} onchange={(e) => client.send({ t: 'mode', key: (e.target as HTMLSelectElement).value })}>
					{#each modes as m (m.key)}
						<option value={m.key} disabled={!!m.reason}>{m.title}{m.look === '3d' ? ' (3D)' : ''}{m.reason ? ' (tidak sesuai)' : ''}</option>
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
			<label class="check-row"><input type="checkbox" checked={settings.shuffle} onchange={(e) => set({ shuffle: (e.target as HTMLInputElement).checked })} /> Kocok soalan</label>
			<label class="check-row"><input type="checkbox" checked={settings.custom_names} onchange={(e) => set({ custom_names: (e.target as HTMLInputElement).checked })} /> Benarkan nama sendiri (ditapis)</label>
			<label class="check-row"><input type="checkbox" checked={settings.waiting_room} onchange={(e) => set({ waiting_room: (e.target as HTMLInputElement).checked })} /> Saya benarkan setiap pemain dahulu</label>
			<label class="check-row"><input type="checkbox" checked={settings.late_join} onchange={(e) => set({ late_join: (e.target as HTMLInputElement).checked })} /> Boleh masuk selepas mula</label>
			{#if mode.key === 'harta'}
				<label class="check-row"><input type="checkbox" checked={settings.naughty} onchange={(e) => set({ naughty: (e.target as HTMLInputElement).checked })} /> Kejutan nakal (burung kakak tua, ketam)</label>
			{/if}
			<button type="button" class="btn btn--plain lock" onclick={() => client.send({ t: 'lock', on: !view.room.locked })}>
				<Icon name={view.room.locked ? 'lock' : 'unlock'} /> {view.room.locked ? 'Bilik dikunci' : 'Kunci bilik'}
			</button>
		</section>
	</aside>
</div>

<style>
	.lobby {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(17rem, 21rem);
		gap: 1.2rem 1.4rem;
		align-items: start;
	}
	.strip {
		grid-column: 1 / -1;
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		gap: 1.2rem;
	}
	/* Mula stands at the end of the join strip, as tall as it, so it is the first thing the host finds. */
	.start {
		align-self: stretch;
		min-width: 11rem;
		flex-direction: column;
		gap: 0.2rem;
		font-size: 1.9rem;
	}
	.main {
		display: grid;
		gap: 1.2rem;
		min-width: 0;
	}
	.square {
		display: grid;
		gap: 0.6rem;
	}
	.square-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		flex-wrap: wrap;
	}
	.square-head h2 {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		font-size: 1.35rem;
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
	.stage {
		position: relative;
	}
	.empty {
		position: absolute;
		left: 50%;
		bottom: 1.2rem;
		translate: -50% 0;
		width: min(30rem, calc(100% - 2rem));
		padding: 0.8rem 1.1rem;
		border-radius: var(--r-md);
		background: rgb(255 255 255 / 0.94);
		color: var(--on-bright);
		font-weight: 700;
		text-align: center;
		box-shadow: var(--lift-low);
	}
	.roster {
		display: flex;
		flex-wrap: wrap;
		gap: 0.45rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.roster li {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.2rem 0.2rem 0.2rem 0.3rem;
		border-radius: var(--r-pill);
		background: var(--card);
		box-shadow: 0 2px 0 var(--line);
		animation: pop-in 420ms var(--spring) both;
	}
	.roster .away {
		opacity: 0.55;
	}
	.roster .name {
		font-weight: 800;
		font-size: 0.92rem;
		white-space: nowrap;
	}
	.roster .bot {
		padding: 0 0.4rem;
		border-radius: var(--r-pill);
		background: var(--ink);
		color: #fff;
		font-size: 0.7rem;
	}
	.roster .tool {
		position: relative;
		width: 2rem;
		height: 2rem;
		border-radius: var(--r-sm);
	}
	.roster .tool::after {
		content: '';
		position: absolute;
		inset: -0.4rem;
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
	.how {
		color: var(--ink-2);
	}
	.warn {
		color: #9a4a00;
		font-weight: 800;
	}
	.settings .check-row {
		align-items: center;
	}
	.settings .check-row input {
		width: 1.3rem;
		height: 1.3rem;
		margin: 0;
	}
	.lock {
		justify-self: start;
	}
	@media (max-width: 1000px) {
		.lobby {
			grid-template-columns: minmax(0, 1fr);
		}
		.side {
			position: static;
		}
	}
	@media (max-width: 640px) {
		.strip {
			grid-template-columns: minmax(0, 1fr);
		}
		.start {
			flex-direction: row;
			min-height: 4.2rem;
		}
	}
</style>
