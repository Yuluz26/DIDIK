<!-- How children get in: the QR code, the word link and the six-digit code, in one strip big enough for a TV. -->
<script lang="ts">
	import { api } from '$lib/api';
	import type { RoomInfo } from '$lib/types';
	import Icon from '$ui/Icon.svelte';

	let { room }: { room: RoomInfo } = $props();

	// The server knows the address children can reach (with `didik-live --lan`, the computer's Wi-Fi
	// address, even when this screen was opened as localhost); the QR code uses the same one.
	let base = $state(location.origin);
	const link = $derived(`${base}/m/${room.slug}`);
	const host = $derived(`${base.replace(/^https?:\/\//, '')}/m/`);
	let copied = $state(false);

	$effect(() => {
		const slug = room.slug;
		api
			.get<{ link: string }>(`/api/rooms/${room.code}`)
			.then((info) => (base = info.link.slice(0, -`/m/${slug}`.length)))
			.catch(() => {});
	});

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

<section class="join" aria-label="Cara masuk bilik">
	<img class="qr" src="/api/rooms/{room.code}/qr.svg" alt="Kod QR untuk masuk bilik {room.slug}" width="240" height="240" />
	<div class="way">
		<p class="label">Imbas kod QR, atau buka pautan ini</p>
		<p class="link">{host}<span class="slug">{room.slug}</span></p>
		<button type="button" class="copy" onclick={copy}>
			<Icon name={copied ? 'check' : 'copy'} size={18} /> {copied ? 'Disalin' : 'Salin pautan'}
		</button>
	</div>
	<div class="way code-way">
		<p class="label">atau masukkan kod di laman utama</p>
		<p class="code" aria-label="Kod bilik {room.code.split('').join(' ')}">{room.code.slice(0, 3)} {room.code.slice(3)}</p>
	</div>
</section>

<style>
	.join {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr) auto;
		align-items: center;
		gap: 1.4rem;
		padding: 0.75rem 1.4rem 0.75rem 0.75rem;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	.qr {
		display: block;
		width: clamp(6.5rem, 8vw, 11rem);
		height: auto;
		border-radius: var(--r-md);
	}
	.way {
		display: grid;
		gap: 0.25rem;
		justify-items: start;
		min-width: 0;
	}
	.label {
		color: var(--ink-2);
		font-weight: 800;
		font-size: 0.92rem;
	}
	.link {
		max-width: 100%;
		font: 600 clamp(1.25rem, 0.8rem + 1.3vw, 2.1rem) / 1.15 var(--font-display);
		color: var(--brand-ink);
		overflow-wrap: anywhere;
	}
	.slug {
		white-space: nowrap;
	}
	.copy {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		margin-top: 0.2rem;
		padding: 0.3rem 0.1rem;
		border: 0;
		background: none;
		color: var(--ink-2);
		font-weight: 800;
		cursor: pointer;
		text-decoration: underline;
		text-decoration-color: var(--line);
		text-decoration-thickness: 2px;
		text-underline-offset: 5px;
		transition:
			color var(--t-state),
			text-decoration-color var(--t-state);
	}
	.copy:hover {
		color: var(--brand-ink);
		text-decoration-color: currentColor;
	}
	.code-way {
		padding-left: 1.4rem;
		border-left: 2px solid var(--line);
	}
	.code {
		font: 600 clamp(2.2rem, 1.2rem + 2.6vw, 3.6rem) / 1 var(--font-display);
		letter-spacing: 0.08em;
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}
	@media (max-width: 760px) {
		.join {
			grid-template-columns: auto minmax(0, 1fr);
		}
		.code-way {
			grid-column: 1 / -1;
			padding: 0.8rem 0 0;
			border-left: 0;
			border-top: 2px solid var(--line);
		}
	}
	@media (max-width: 480px) {
		.join {
			grid-template-columns: minmax(0, 1fr);
			justify-items: center;
			text-align: center;
		}
		.way {
			justify-items: center;
		}
	}
</style>
