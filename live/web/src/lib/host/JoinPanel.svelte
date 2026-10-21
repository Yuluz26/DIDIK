<!-- How children get in: the word link, the QR code and the six-digit code, big enough for a TV. -->
<script lang="ts">
	import type { RoomInfo } from '$lib/types';
	import Icon from '$ui/Icon.svelte';

	let { room, compact = false }: { room: RoomInfo; compact?: boolean } = $props();

	const link = $derived(`${location.origin}/m/${room.slug}`);
	const host = $derived(`${location.host}/m/`);
	let copied = $state(false);

	async function copy() {
		try {
			await navigator.clipboard.writeText(link);
			copied = true;
			setTimeout(() => (copied = false), 1800);
		} catch {
			copied = false;
		}
	}
</script>

<section class="join" class:compact aria-label="Cara masuk bilik">
	<div class="qr">
		<img src="/api/rooms/{room.code}/qr.svg" alt="Kod QR untuk masuk bilik {room.slug}" width="240" height="240" />
	</div>
	<div class="ways">
		<p class="label">Buka pautan ini</p>
		<p class="link">{host}<span class="slug">{room.slug}</span></p>
		<button type="button" class="btn btn--plain" onclick={copy}>
			<Icon name={copied ? 'check' : 'copy'} /> {copied ? 'Disalin' : 'Salin pautan'}
		</button>
		<p class="label">atau masukkan kod di laman utama</p>
		<p class="code" aria-label="Kod bilik {room.code.split('').join(' ')}">{room.code.slice(0, 3)} {room.code.slice(3)}</p>
	</div>
</section>

<style>
	.join {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr);
		align-items: center;
		gap: 1.4rem;
		padding: 1.2rem;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	.qr img {
		display: block;
		width: clamp(9rem, 16vw, 15rem);
		height: auto;
		border-radius: var(--r-md);
	}
	.ways {
		display: grid;
		gap: 0.35rem;
		justify-items: start;
		min-width: 0;
	}
	.label {
		color: var(--ink-2);
		font-weight: 800;
		font-size: 0.95rem;
	}
	.link {
		max-width: 100%;
		font: 600 clamp(1.3rem, 0.9rem + 1.6vw, 2.2rem) / 1.15 var(--font-display);
		color: var(--brand);
		overflow-wrap: anywhere;
	}
	.slug {
		white-space: nowrap;
	}
	.code {
		font: 600 clamp(2.2rem, 1.2rem + 3vw, 3.6rem) / 1 var(--font-display);
		letter-spacing: 0.08em;
		font-variant-numeric: tabular-nums;
	}
	.ways .btn {
		margin-bottom: 0.6rem;
	}
	.compact {
		grid-template-columns: auto minmax(0, 1fr);
		padding: 0.8rem;
		gap: 0.9rem;
	}
	.compact .qr img {
		width: 6.5rem;
	}
	.compact .link {
		font-size: 1.1rem;
	}
	.compact .code {
		font-size: 1.8rem;
	}
	@media (max-width: 560px) {
		.join {
			grid-template-columns: minmax(0, 1fr);
			justify-items: center;
			text-align: center;
		}
		.ways {
			justify-items: center;
		}
	}
</style>
