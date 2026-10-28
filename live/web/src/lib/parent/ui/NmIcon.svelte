<!--
	The dashboard's icons: soft, round-capped outlines on a 24 grid, drawn here so the parent area does
	not use the pixel glyphs the games use. They take the colour of the text around them.
-->
<script lang="ts">
	let { name, size = 22, label = '' }: { name: string; size?: number; label?: string } = $props();

	const PATHS: Record<string, string> = {
		dashboard: 'M4 4h6.5v6.5H4zM13.5 4H20v6.5h-6.5zM4 13.5h6.5V20H4zM13.5 13.5H20V20h-6.5z',
		quiz: 'M6 3h9l4 4v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM14.5 3.5V8H19M8.5 12.5h7M8.5 16h5',
		sparkle: 'M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9zM18.5 15.5l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z',
		plus: 'M12 5v14M5 12h14',
		room: 'M3.5 12a8.5 8.5 0 0 1 17 0M7 12a5 5 0 0 1 10 0M12 12.2v.01M12 16v4M9.5 20h5',
		game: 'M7 8h10a4 4 0 0 1 4 4.2l-.6 3.6a2.6 2.6 0 0 1-4.6 1.2L14.4 15h-4.8l-1.4 2a2.6 2.6 0 0 1-4.6-1.2L3 12.2A4 4 0 0 1 7 8zM8 10.5v3M6.5 12h3M15.5 11.5v.01M17.5 13.2v.01',
		user: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4.5 20.5a7.5 7.5 0 0 1 15 0',
		logout: 'M10 4.5H6.5a1.5 1.5 0 0 0-1.5 1.5v12a1.5 1.5 0 0 0 1.5 1.5H10M15 8l4 4-4 4M19 12H9.5',
		play: 'M8 5.5v13l11-6.5z',
		edit: 'M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16zM13.5 6.5l4 4',
		copy: 'M9 9h10v11H9zM15 9V5H5v11h4',
		trash: 'M4.5 7h15M9.5 7V4.5h5V7M6.5 7l.8 12.5h9.4L17.5 7M10 11v5M14 11v5',
		more: 'M12 5.5v.01M12 12v.01M12 18.5v.01',
		next: 'M9 5l7 7-7 7',
		back: 'M15 5l-7 7 7 7',
		down: 'M6 9l6 6 6-6',
		link: 'M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1',
		home: 'M4 11l8-7 8 7M6 9.5V20h4.5v-5h3v5H18V9.5',
		menu: 'M4 7h16M4 12h16M4 17h16',
		close: 'M6 6l12 12M18 6L6 18',
		heart: 'M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.4a4.3 4.3 0 0 1 7.5 2.4C19.5 15.4 12 20 12 20z',
		star: 'M12 3.8l2.5 5.2 5.7.8-4.1 4 1 5.7-5.1-2.7-5.1 2.7 1-5.7-4.1-4 5.7-.8z',
		check: 'M5 12.5l4.5 4.5L19 7.5',
		clock: 'M12 7v5l3 2M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z'
	};
</script>

<svg
	class="nm-icon"
	viewBox="0 0 24 24"
	width={size}
	height={size}
	fill="none"
	stroke="currentColor"
	stroke-width="1.9"
	stroke-linecap="round"
	stroke-linejoin="round"
	focusable="false"
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	aria-hidden={label ? undefined : 'true'}
>
	<path d={PATHS[name] ?? PATHS.star} />
</svg>

<style>
	.nm-icon {
		flex: none;
	}
</style>
