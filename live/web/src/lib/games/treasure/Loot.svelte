<!-- What can be found under the sand on Pulau Harta Karun. -->
<script lang="ts">
	let { kind, size = 48 }: { kind: string; size?: number } = $props();
</script>

<svg viewBox="0 0 48 48" width={size} height={size} aria-hidden="true" focusable="false">
	{#if kind === 'coins'}
		<ellipse cx="24" cy="36" rx="14" ry="5" fill="#c98400" />
		<ellipse cx="24" cy="33" rx="14" ry="5" fill="#ffd34d" />
		<ellipse cx="24" cy="28" rx="14" ry="5" fill="#c98400" />
		<ellipse cx="24" cy="25" rx="14" ry="5" fill="#ffd34d" />
		<ellipse cx="30" cy="18" rx="9" ry="9" fill="#ffd34d" stroke="#c98400" stroke-width="2.5" />
		<path d="M30 13v10" stroke="#c98400" stroke-width="2.5" stroke-linecap="round" />
	{:else if kind === 'chest'}
		<rect x="8" y="20" width="32" height="20" rx="3" fill="#a8432f" />
		<path d="M8 22 Q24 6 40 22z" fill="#c9572e" />
		<rect x="8" y="20" width="32" height="4" fill="#7a2f1f" />
		<rect x="21" y="22" width="6" height="8" rx="1.5" fill="#ffd34d" />
		<circle cx="15" cy="13" r="3" fill="#ffd34d" /><circle cx="33" cy="12" r="2.5" fill="#ffd34d" />
	{:else if kind === 'gem'}
		<path d="M14 16h20l6 8-16 18L8 24z" fill="#2bb0a6" />
		<path d="M14 16l4 8h12l4-8M8 24h32M18 24l6 18 6-18" stroke="#0b665e" stroke-width="1.6" fill="none" stroke-linejoin="round" />
		<path d="M17 18l-3 5" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".8" />
	{:else if kind === 'map'}
		<path d="M8 12l10-4 12 4 10-4v28l-10 4-12-4-10 4z" fill="#f6e3b4" stroke="#b98a4a" stroke-width="2" stroke-linejoin="round" />
		<path d="M18 8v28M30 12v28" stroke="#b98a4a" stroke-width="1.5" />
		<path d="M12 28q6-10 14-4t10-8" stroke="#e8553f" stroke-width="2" stroke-dasharray="3 3" fill="none" />
		<path d="M33 13l4 4M37 13l-4 4" stroke="#e8553f" stroke-width="2.4" stroke-linecap="round" />
	{:else if kind === 'parrot'}
		<path d="M18 40c-6-6-6-18 4-24 8-5 16 0 16 8 0 10-10 14-20 16z" fill="#e2483d" />
		<path d="M20 38c-2-6 0-12 6-14" stroke="#2bb0a6" stroke-width="5" stroke-linecap="round" fill="none" />
		<path d="M30 16c4-2 8 0 8 4l-6 2z" fill="#ffd34d" />
		<circle cx="29" cy="19" r="2" fill="#1f2d27" />
		<path d="M16 42l-4 4M20 42l0 5" stroke="#e8553f" stroke-width="2.5" stroke-linecap="round" />
	{:else if kind === 'crab'}
		<ellipse cx="24" cy="30" rx="12" ry="8" fill="#e2483d" />
		<path d="M12 26c-6-2-8-8-4-12 2 4 6 4 6 8M36 26c6-2 8-8 4-12-2 4-6 4-6 8" fill="#e2483d" />
		<path d="M14 34l-6 4M15 37l-4 6M34 34l6 4M33 37l4 6" stroke="#c03a30" stroke-width="2.4" stroke-linecap="round" />
		<circle cx="20" cy="22" r="2.5" fill="#fff" /><circle cx="28" cy="22" r="2.5" fill="#fff" />
		<circle cx="20" cy="22" r="1.2" fill="#1f2d27" /><circle cx="28" cy="22" r="1.2" fill="#1f2d27" />
	{:else}
		<ellipse cx="24" cy="34" rx="15" ry="7" fill="#e5c07a" />
		<ellipse cx="24" cy="31" rx="10" ry="5" fill="#f2d49b" />
		<circle cx="18" cy="30" r="1.2" fill="#c9a061" /><circle cx="27" cy="29" r="1.2" fill="#c9a061" />
	{/if}
</svg>
