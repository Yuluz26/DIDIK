<!--
	A small round kawaii face on a pastel blob: the parent area's friendly little characters. The colour
	and the face come from a seed (a quiz's title, say), so every quiz keeps its own face.
-->
<script lang="ts">
	let { seed = '', size = 44, mood }: { seed?: string; size?: number; mood?: 'happy' | 'wink' | 'wow' | 'sleepy' } = $props();

	const PALETTE: [string, string][] = [
		['#ffd9e4', '#ff9bb9'],
		['#d7e6ff', '#8fb3ff'],
		['#dcf6ea', '#7fdcb4'],
		['#e6dcff', '#b49cff'],
		['#fff0cc', '#ffcc66'],
		['#d8f3f6', '#7fd3dd']
	];
	const MOODS = ['happy', 'wink', 'wow', 'sleepy'] as const;

	function hash(text: string): number {
		let h = 7;
		for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) >>> 0;
		return h;
	}

	const h = $derived(hash(seed || 'didik'));
	const [soft, strong] = $derived(PALETTE[h % PALETTE.length]);
	const face = $derived(mood ?? MOODS[(h >> 3) % MOODS.length]);
	const uid = $derived(`k${h.toString(36)}`);
</script>

<svg viewBox="0 0 48 48" width={size} height={size} aria-hidden="true" focusable="false">
	<defs>
		<radialGradient id="{uid}-g" cx="0.35" cy="0.3" r="0.9">
			<stop offset="0" stop-color="#fff" stop-opacity="0.9" />
			<stop offset="0.45" stop-color={soft} />
			<stop offset="1" stop-color={strong} />
		</radialGradient>
	</defs>
	<!-- ears -->
	<circle cx="11" cy="12" r="6" fill={strong} opacity="0.85" />
	<circle cx="37" cy="12" r="6" fill={strong} opacity="0.85" />
	<circle cx="11" cy="12" r="3" fill="#fff" opacity="0.7" />
	<circle cx="37" cy="12" r="3" fill="#fff" opacity="0.7" />
	<!-- head -->
	<ellipse cx="24" cy="26" rx="19" ry="17.5" fill="url(#{uid}-g)" />
	<ellipse cx="14" cy="17" rx="5" ry="2.6" fill="#fff" opacity="0.55" transform="rotate(-25 14 17)" />
	<!-- cheeks -->
	<circle cx="12.5" cy="30" r="3.2" fill="#ff7d9d" opacity="0.5" />
	<circle cx="35.5" cy="30" r="3.2" fill="#ff7d9d" opacity="0.5" />
	<!-- eyes -->
	{#if face === 'sleepy'}
		<path d="M14 25.5q3.2 3 6.4 0M27.6 25.5q3.2 3 6.4 0" fill="none" stroke="#3b2d4f" stroke-width="2.2" stroke-linecap="round" />
	{:else if face === 'wink'}
		<circle cx="17.5" cy="25" r="2.7" fill="#3b2d4f" />
		<circle cx="16.6" cy="24" r="0.9" fill="#fff" />
		<path d="M27.6 25.5q3.2-3 6.4 0" fill="none" stroke="#3b2d4f" stroke-width="2.2" stroke-linecap="round" />
	{:else if face === 'wow'}
		<circle cx="17.5" cy="25" r="3.1" fill="#3b2d4f" />
		<circle cx="30.5" cy="25" r="3.1" fill="#3b2d4f" />
		<circle cx="16.5" cy="23.8" r="1.1" fill="#fff" />
		<circle cx="29.5" cy="23.8" r="1.1" fill="#fff" />
	{:else}
		<circle cx="17.5" cy="25" r="2.7" fill="#3b2d4f" />
		<circle cx="30.5" cy="25" r="2.7" fill="#3b2d4f" />
		<circle cx="16.6" cy="24" r="0.9" fill="#fff" />
		<circle cx="29.6" cy="24" r="0.9" fill="#fff" />
	{/if}
	<!-- mouth -->
	{#if face === 'wow'}
		<ellipse cx="24" cy="32.5" rx="2.2" ry="2.8" fill="#3b2d4f" />
	{:else}
		<path d="M20.5 31q3.5 3.8 7 0" fill="none" stroke="#3b2d4f" stroke-width="2" stroke-linecap="round" />
	{/if}
</svg>
