<!-- Bilik langsung: the rooms still open, each with the way into its host screen. -->
<script lang="ts">
	import DashShell from '$lib/parent/DashShell.svelte';
	import Kawaii from '$lib/parent/ui/Kawaii.svelte';
	import NmIcon from '$lib/parent/ui/NmIcon.svelte';
	import { parent } from '$lib/parent/store.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';
</script>

<svelte:head><title>Bilik langsung · DIDIK Main Bersama</title></svelte:head>

<DashShell>
	<div class="nm-head">
		<div>
			<h1>Bilik langsung</h1>
			<p>Bilik yang masih dibuka. Buka semula skrin hos jika tertutup.</p>
		</div>
		<a class="btn btn--sun" href="/ibu-bapa/kuiz"><NmIcon name="play" size={16} /> Mulakan bilik baharu</a>
	</div>

	{#if parent.rooms.length}
		<ul class="rooms">
			{#each parent.rooms as room (room.code)}
				<li class="nm-card">
					<span class="badge"><WorldBadge world={room.mode.world} size={52} /></span>
					<div class="text">
						<strong>{room.mode.title}</strong>
						<span>{room.quizTitle}</span>
					</div>
					<p class="code" aria-label="Kod bilik {room.code}">{room.code.slice(0, 3)} {room.code.slice(3)}</p>
					<p class="players"><NmIcon name="heart" size={14} /> {room.players} pemain</p>
					<a class="btn btn--sea" href="/hos/{room.code}">Buka skrin hos <NmIcon name="next" size={16} /></a>
				</li>
			{/each}
		</ul>
	{:else}
		<div class="empty nm-card">
			<Kawaii seed="bilik" size={90} mood="sleepy" />
			<div>
				<h2>{parent.loading ? 'Membuka senarai…' : 'Tiada bilik dibuka'}</h2>
				<p>Pilih kuiz dan tekan Main bersama. Pautan, kod QR dan kod 6 digit akan muncul di skrin hos.</p>
			</div>
		</div>
	{/if}
</DashShell>

<style>
	.rooms {
		display: grid;
		gap: 1.1rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.rooms li {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.8rem 1.4rem;
		padding: 1rem 1.3rem;
	}
	.badge {
		display: grid;
		place-items: center;
		width: 3.8rem;
		height: 3.8rem;
		border-radius: 50%;
		background: #eceef5;
		box-shadow: inset 3px 3px 7px rgb(163 172 198 / 0.4), inset -3px -3px 7px rgb(255 255 255 / 0.95);
	}
	.text {
		display: grid;
		flex: 1 1 12rem;
		min-width: 0;
	}
	.text strong {
		font: 500 1.15rem/1.2 var(--font-display);
	}
	.text span {
		color: var(--ink-2);
		font-weight: 700;
	}
	.code {
		font: 500 1.6rem/1 var(--font-display);
		letter-spacing: 0.06em;
		color: var(--brand-ink);
	}
	.players {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		color: #d2255f;
		font: 600 0.9rem/1 var(--font-display);
	}
	.empty {
		display: flex;
		align-items: center;
		gap: 1.6rem;
		padding: 1.8rem;
	}
	.empty h2 {
		font: 500 1.4rem/1.2 var(--font-display);
	}
	.empty p {
		margin-top: 0.3rem;
		color: var(--ink-2);
	}
	@media (max-width: 560px) {
		.empty {
			flex-direction: column;
			text-align: center;
		}
	}
</style>
