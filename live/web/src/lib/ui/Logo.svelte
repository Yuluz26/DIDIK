<script lang="ts">
	let { href = '/', light = false }: { href?: string; light?: boolean } = $props();
</script>

<a class="logo" class:light {href} aria-label="DIDIK Main Bersama, laman utama">
	<svg viewBox="0 0 48 48" aria-hidden="true" focusable="false">
		<rect width="48" height="48" rx="14" fill="#1c6b4a" />
		<g transform="rotate(26 10 20)"><ellipse cx="10" cy="20" rx="7" ry="4" fill="#e7b98a" /></g>
		<g transform="rotate(-26 38 20)"><ellipse cx="38" cy="20" rx="7" ry="4" fill="#e7b98a" /></g>
		<ellipse cx="24" cy="23" rx="12.5" ry="10" fill="#e7b98a" />
		<ellipse cx="24" cy="31" rx="7" ry="7" fill="#e7b98a" />
		<ellipse cx="24" cy="35" rx="4.8" ry="2.8" fill="#fff4e6" />
		<ellipse cx="18.5" cy="22" rx="2.3" ry="2.8" fill="#17241d" />
		<ellipse cx="29.5" cy="22" rx="2.3" ry="2.8" fill="#17241d" />
		<ellipse cx="24" cy="32" rx="1.9" ry="1.4" fill="#17241d" />
	</svg>
	<span class="word">didik <span>main bersama</span></span>
</a>

<style>
	.logo {
		display: inline-flex;
		align-items: center;
		gap: 0.6rem;
		color: var(--ink);
		text-decoration: none;
		font: 600 1.35rem/1 var(--font-display);
	}
	.logo.light {
		color: #fff;
	}
	svg {
		flex: none;
		width: 2.4rem;
		height: 2.4rem;
		transition: transform var(--t-state) var(--spring);
	}
	.logo:hover svg {
		transform: rotate(-8deg) scale(1.06);
	}
	.word {
		white-space: nowrap;
	}
	.word span {
		color: var(--brand);
		font-weight: 500;
	}
	.light .word span {
		color: inherit;
	}
</style>
