<!-- A small round window into each game's world, used wherever a game is named. -->
<script lang="ts">
	let { world, size = 72 }: { world: string; size?: number } = $props();
	const clip = `w-${Math.random().toString(36).slice(2, 8)}`;
</script>

<svg class="badge" viewBox="0 0 100 100" width={size} height={size} aria-hidden="true" focusable="false">
	<defs><clipPath id={clip}><circle cx="50" cy="50" r="48" /></clipPath></defs>
	<g clip-path="url(#{clip})">
		{#if world === 'sungai'}
			<rect width="100" height="100" fill="#cdebff" />
			<path d="M0 46 Q25 30 50 40 T100 36 V60 H0z" fill="#7dbe4e" />
			<circle cx="22" cy="38" r="9" fill="#3e8e57" /><circle cx="74" cy="34" r="10" fill="#3e8e57" />
			<rect y="56" width="100" height="44" fill="#3ba7d9" />
			<path d="M8 70 q8 -4 16 0 M60 86 q8 -4 16 0" stroke="#bfe6f6" stroke-width="3" fill="none" stroke-linecap="round" />
			<path d="M30 70 H70 Q66 82 58 82 H42 Q34 82 30 70z" fill="#c9572e" />
			<rect x="30" y="68" width="40" height="4" rx="2" fill="#a8432f" />
			<circle cx="50" cy="61" r="8" fill="#e7b98a" />
			<path d="M60 52 v16" stroke="#8e5a2e" stroke-width="2.5" />
			<path d="M60 52 l10 4 -10 4z" fill="#ffb627" />
		{:else if world === 'kolam'}
			<rect width="100" height="100" fill="#4fc3d9" />
			<path d="M0 30 q12 -5 24 0 t24 0 t24 0 t28 0" stroke="#9fe0ee" stroke-width="3" fill="none" />
			<ellipse cx="28" cy="64" rx="20" ry="10" fill="#6cb33f" /><ellipse cx="28" cy="61" rx="20" ry="10" fill="#8fd05e" />
			<ellipse cx="74" cy="66" rx="18" ry="9" fill="#d97a5f" /><ellipse cx="74" cy="63" rx="18" ry="9" fill="#f29c7a" />
			<path d="M20 60 l5 5 11 -10" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" />
			<path d="M68 57 l12 12 M80 57 l-12 12" stroke="#fff" stroke-width="4" stroke-linecap="round" />
			<circle cx="50" cy="36" r="9" fill="#9aa7b3" /><path d="M44 30 q6 -10 12 0" fill="#9aa7b3" />
			<path d="M50 44 q-14 -6 -22 8" stroke="#1f2d27" stroke-width="2" stroke-dasharray="3 3" fill="none" />
		{:else if world === 'pulau'}
			<rect width="100" height="100" fill="#3ba7d9" />
			<ellipse cx="50" cy="68" rx="40" ry="18" fill="#f6d58e" />
			<path d="M58 66 q-4 -24 6 -40" stroke="#8e5a2e" stroke-width="4" fill="none" />
			<path d="M64 26 q-16 -4 -24 8 q12 -4 24 -8 q-2 -14 -16 -16 q10 6 16 16 q8 -12 22 -8 q-14 0 -22 8 q16 0 18 14 q-6 -10 -18 -14" fill="#4fa35b" />
			<path d="M26 62 l8 8 M34 62 l-8 8" stroke="#c0503a" stroke-width="4" stroke-linecap="round" />
			<rect x="38" y="70" width="16" height="11" rx="2" fill="#a8432f" /><rect x="38" y="68" width="16" height="5" rx="2" fill="#c9572e" />
			<circle cx="46" cy="75" r="2" fill="#ffd34d" />
		{:else if world === 'hutan'}
			<rect width="100" height="100" fill="#8fd05e" />
			<path d="M40 100 Q46 70 60 56 T70 0" stroke="#e8c98f" stroke-width="12" fill="none" />
			<circle cx="16" cy="24" r="16" fill="#2e6e43" /><circle cx="84" cy="20" r="16" fill="#3e8e57" />
			<circle cx="12" cy="70" r="15" fill="#3e8e57" /><circle cx="88" cy="72" r="16" fill="#2e6e43" />
			<rect x="28" y="50" width="20" height="14" rx="3" fill="#a8432f" /><rect x="28" y="47" width="20" height="6" rx="3" fill="#c9572e" />
			<circle cx="38" cy="56" r="2.5" fill="#ffd34d" />
			<circle cx="66" cy="40" r="7" fill="#e7b98a" />
			<path d="M58 80 q-2 -6 4 -8" stroke="#e8553f" stroke-width="7" stroke-linecap="round" />
			<circle cx="60" cy="80" r="4" fill="#fff" />
		{:else if world === 'peta'}
			<rect width="100" height="100" fill="#3ba7d9" />
			{#each [[30, 34, '#f28c28'], [50, 34, '#f28c28'], [70, 34, '#e9d7b0'], [20, 52, '#f28c28'], [40, 52, '#e9d7b0'], [60, 52, '#14958a'], [80, 52, '#14958a'], [30, 70, '#e9d7b0'], [50, 70, '#14958a'], [70, 70, '#14958a']] as [x, y, fill] (`${x}-${y}`)}
				<path d="M{Number(x)} {Number(y) - 10} l9 5 v10 l-9 5 l-9 -5 v-10z" fill={String(fill)} stroke="#fff" stroke-width="2" />
			{/each}
			<path d="M50 20 v-10 l10 4 -10 4" fill="#ffd34d" stroke="#8e5a2e" stroke-width="2" />
		{:else if world === 'kampung'}
			<rect width="100" height="100" fill="#cdebff" />
			<rect y="66" width="100" height="34" fill="#8bcb6b" />
			<rect x="28" y="48" width="44" height="22" rx="2" fill="#d9a066" />
			<path d="M20 50 L50 26 L80 50z" fill="#c0503a" />
			<rect x="44" y="54" width="12" height="16" fill="#8e5a2e" />
			<rect x="31" y="70" width="4" height="10" fill="#8e5a2e" /><rect x="65" y="70" width="4" height="10" fill="#8e5a2e" />
			<path d="M86 66 q-2 -20 4 -30" stroke="#8e5a2e" stroke-width="3" fill="none" />
			<path d="M90 36 q-10 -2 -14 6 q8 -4 14 -6 q6 -8 14 -4 q-8 0 -14 4" fill="#4fa35b" />
			<circle cx="14" cy="22" r="8" fill="#ffd34d" />
		{:else if world === 'galeri'}
			<rect width="100" height="100" fill="#ffe7a3" />
			<rect x="18" y="20" width="64" height="60" rx="6" fill="#8e5a2e" />
			<rect x="24" y="26" width="52" height="48" fill="#bde7f5" />
			<circle cx="44" cy="52" r="12" fill="#f29c4b" />
			<path d="M34 42 l3 -10 7 7z M54 42 l-3 -10 -7 7z" fill="#f29c4b" />
			{#each [[24, 26], [50, 26], [50, 50], [24, 50]] as [x, y], i (i)}
				{#if i !== 2}<rect x={x} y={y} width="26" height="24" fill="#2bb0a6" stroke="#fff" stroke-width="2" />{/if}
			{/each}
			<text x="37" y="44" font-size="16" font-weight="700" fill="#fff" font-family="sans-serif" text-anchor="middle">?</text>
		{:else if world === 'kebun'}
			<rect width="100" height="100" fill="#cdebff" />
			<circle cx="80" cy="20" r="10" fill="#ffd34d" />
			<rect y="54" width="100" height="46" fill="#9b6a43" />
			<path d="M0 66 H100 M0 82 H100" stroke="#83552f" stroke-width="5" />
			<path d="M22 66 v-12 M22 56 q-8 -6 -10 -2 q4 4 10 2 q6 -8 10 -4 q-4 4 -10 4" stroke="#4fa35b" stroke-width="3" fill="#6cb33f" />
			<circle cx="52" cy="60" r="7" fill="#e8553f" /><path d="M52 53 v-6" stroke="#4fa35b" stroke-width="3" />
			<path d="M78 80 v-12" stroke="#4fa35b" stroke-width="3" /><ellipse cx="78" cy="66" rx="9" ry="7" fill="#6cb33f" />
			<path d="M32 30 q4 6 0 9 q-4 -3 0 -9z" fill="#4fc3f7" />
		{:else if world === 'litar'}
			<rect width="100" height="100" fill="#2d4f72" />
			<circle cx="74" cy="44" r="11" fill="#ffb627" />
			<rect y="46" width="100" height="54" fill="#3d7d47" />
			<path d="M-6 96 C24 68 58 82 106 64" stroke="#d0452f" stroke-width="3" stroke-dasharray="4 4" fill="none" />
			<path d="M-6 84 C24 56 58 70 106 52" stroke="#2c3236" stroke-width="20" fill="none" />
			<path d="M-6 84 C24 56 58 70 106 52" stroke="#fff" stroke-width="1.5" stroke-dasharray="5 5" fill="none" opacity=".7" />
			<rect x="26" y="59" width="24" height="7" rx="3" fill="#d0452f" />
			<circle cx="30" cy="67" r="3.6" fill="#1f2d27" /><circle cx="46" cy="66.5" r="3.6" fill="#1f2d27" />
			<circle cx="39" cy="55" r="4.8" fill="#ffb627" />
			<rect x="39" y="53.4" width="5.5" height="2.6" rx="1.2" fill="#1f2d27" />
			<path d="M20 61 h-9 M21 64 h-12" stroke="#ffd34d" stroke-width="2" stroke-linecap="round" />
		{:else if world === 'stadium'}
			<rect width="100" height="100" fill="#13303d" />
			<path d="M0 40 L100 31 V48 L0 56z" fill="#1d4757" />
			<circle cx="18" cy="16" r="5" fill="#fff4cf" /><circle cx="84" cy="12" r="5" fill="#fff4cf" />
			<path d="M0 56 L100 48 V100 H0z" fill="#2f8a4e" />
			<path d="M0 70 L100 63 V72 L0 79z M0 88 L100 81 V90 L0 97z" fill="#3a9a59" />
			<path d="M31 44 V61 M39 44 V60.5 M47 44 V60 M55 44 V59.5 M63 44 V59 M29 50 H71 M29 55 H71" stroke="#cfe3d6" stroke-width="0.8" opacity=".55" />
			<path d="M27 62 V42 H73 V58" stroke="#fff" stroke-width="3" fill="none" stroke-linejoin="round" />
			<circle cx="44" cy="47" r="3.6" fill="#e7b98a" />
			<rect x="39.5" y="50" width="9" height="9" rx="2" fill="#ffb627" />
			<circle cx="57" cy="82" r="6.5" fill="#fff" />
			<path d="M57 78 l3 2.2 -1.1 3.6 h-3.8 l-1.1 -3.6z" fill="#1f2d27" />
		{:else if world === 'lanun'}
			<rect width="100" height="100" fill="#f08a4b" />
			<circle cx="50" cy="40" r="14" fill="#ffd34d" />
			<rect y="38" width="100" height="16" fill="#1f5f86" />
			<path d="M0 46 q10 -3 20 0 t20 0 t20 0 t20 0 t20 0" stroke="#5fa3c8" stroke-width="1.5" fill="none" />
			<rect y="54" width="100" height="46" fill="#9a6235" />
			<path d="M0 66 H100 M0 79 H100 M0 92 H100" stroke="#7f4d27" stroke-width="2" />
			<path d="M36 60 Q50 42 64 60z" fill="#ffd34d" opacity=".85" />
			<path d="M30 62 L34 49 H66 L70 62z" fill="#8e4a22" />
			<rect x="30" y="62" width="40" height="22" rx="3" fill="#7a3f1d" />
			<rect x="30" y="70" width="40" height="4" fill="#ffb627" />
			<rect x="47" y="69" width="6" height="7" rx="1" fill="#ffd34d" />
			<circle cx="44" cy="58" r="3.5" fill="#ffb627" stroke="#c98400" /><circle cx="55" cy="57" r="3.5" fill="#ffb627" stroke="#c98400" />
		{:else if world === 'menara'}
			<rect width="100" height="100" fill="#21405f" />
			<circle cx="22" cy="24" r="7" fill="#ffd9a0" />
			<path d="M0 74 H10 V60 H18 V68 H28 V56 H37 V100 H0z M63 100 V62 H71 V52 H80 V66 H90 V58 H100 V100z" fill="#183247" />
			<path d="M5 66 h2 M22 62 h2 M31 63 h2 M74 58 h2 M84 72 h2 M94 64 h2" stroke="#ffd34d" stroke-width="2" />
			<path d="M50 6 V30" stroke="#cfe9e6" stroke-width="2" />
			<path d="M42 100 L44 40 L50 30 L56 40 L58 100z" fill="#7fc8c4" />
			<path d="M50 30 L56 40 L58 100 H50z" fill="#5aa9a6" />
			<path d="M43 84 H57 M43.4 70 H56.6 M43.8 56 H56.2" stroke-width="3" stroke="#ffb627" />
			<path d="M43.2 77 H56.8" stroke-width="3" stroke="#d0452f" />
			<path d="M43.6 63 H56.4" stroke-width="3" stroke="#2d78c4" />
		{:else}
			<rect width="100" height="100" fill="#d7eee1" />
			<circle cx="50" cy="50" r="22" fill="#e7b98a" />
		{/if}
	</g>
	<circle cx="50" cy="50" r="47" fill="none" stroke="#fff" stroke-width="3" />
</svg>

<style>
	.badge {
		flex: none;
		filter: drop-shadow(0 4px 0 rgb(31 45 39 / 0.12));
	}
</style>
