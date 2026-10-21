<!--
	A small set of line icons drawn for this app (24px grid, round caps). Decorative by default;
	pass `label` when the icon is the only content of a control.
-->
<script lang="ts">
	let { name, size = 22, label = '' }: { name: string; size?: number; label?: string } = $props();

	const PATHS: Record<string, string> = {
		play: 'M8 5.5v13l10.5-6.5z',
		pause: 'M8 5v14M16 5v14',
		skip: 'M6 5.5v13l9-6.5zM18 5v14',
		stop: 'M6.5 6.5h11v11h-11z',
		sound: 'M4 9.5h3.5L12 5.5v13l-4.5-4H4zM15.5 9a4.5 4.5 0 0 1 0 6M18 6.5a8 8 0 0 1 0 11',
		mute: 'M4 9.5h3.5L12 5.5v13l-4.5-4H4zM16 9.5l5 5M21 9.5l-5 5',
		speak: 'M4 9.5h3.5L12 5.5v13l-4.5-4H4zM15.5 9a4.5 4.5 0 0 1 0 6',
		link: 'M10 14a4 4 0 0 0 5.66 0l3.17-3.17a4 4 0 0 0-5.66-5.66L11.5 6.8M14 10a4 4 0 0 0-5.66 0l-3.17 3.17a4 4 0 0 0 5.66 5.66l1.67-1.63',
		copy: 'M9 9h10v11H9zM5 15V4h10',
		lock: 'M6.5 11h11v9h-11zM8.5 11V8a3.5 3.5 0 0 1 7 0v3',
		unlock: 'M6.5 11h11v9h-11zM8.5 11V8a3.5 3.5 0 0 1 6.6-1.6',
		plus: 'M12 5v14M5 12h14',
		minus: 'M5 12h14',
		trash: 'M5 7h14M10 7V4.5h4V7M7 7l1 13h8l1-13',
		edit: 'M4 20l1-4.5L15.5 5a2.1 2.1 0 0 1 3 3L8 18.5zM13.5 7l3 3',
		check: 'M5 12.5l4.5 4.5L19 7.5',
		close: 'M6 6l12 12M18 6L6 18',
		back: 'M14.5 6l-6 6 6 6',
		next: 'M9.5 6l6 6-6 6',
		users: 'M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM3 20a6 6 0 0 1 12 0M16 4.5a3.5 3.5 0 0 1 0 6.5M18 14a6 6 0 0 1 3 6',
		bot: 'M7 9h10v9H7zM12 5v4M9.5 13h.01M14.5 13h.01M4 13v2M20 13v2',
		gear: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19 12l2-1.5-2-3.5-2.5 1a7 7 0 0 0-2-1.2L14 4h-4l-.5 2.8a7 7 0 0 0-2 1.2L5 7 3 10.5 5 12l-2 1.5L5 17l2.5-1a7 7 0 0 0 2 1.2L10 20h4l.5-2.8a7 7 0 0 0 2-1.2l2.5 1 2-3.5z',
		heart: 'M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z',
		star: 'M12 4l2.4 5 5.4.6-4 3.7 1.1 5.4L12 16l-4.9 2.7 1.1-5.4-4-3.7 5.4-.6z',
		key: 'M8 15a4 4 0 1 1 3.5-6L20 9v3h-2v2h-2v-2h-4.5A4 4 0 0 1 8 15z',
		flag: 'M6 21V4M6 4.5h11l-2 4 2 4H6',
		drop: 'M12 4c3 4 5.5 7 5.5 10a5.5 5.5 0 0 1-11 0C6.5 11 9 8 12 4z',
		coin: 'M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM12 8v8M9.5 10.2c.4-1.2 4.6-1.4 4.8.6.2 2.4-5 1.2-4.8 3.6.2 1.8 4.4 1.8 5-.2',
		crown: 'M4 17l1.5-9 4.5 4 2-6 2 6 4.5-4L20 17zM5 20h14',
		qr: 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h2v2h-2zM18 18h2v2h-2zM14 18h2M18 14h2',
		share: 'M8 12.5l8-4.5M8 12.5l8 4.5M6 15a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM18 9a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM18 21a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z',
		shuffle: 'M4 7h3c4 0 6 10 10 10h3M17 14l3 3-3 3M4 17h3c1.6 0 2.8-1.5 3.8-3.3M13.2 9.3C14.2 7.5 15.4 7 17 7h3M17 4l3 3-3 3',
		home: 'M4 11l8-7 8 7M6 9.5V20h12V9.5',
		door: 'M6 20V4h10v16M6 20h12M13 12h.01',
		eye: 'M2.5 12s3.5-6.5 9.5-6.5S21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
		image: 'M4 5h16v14H4zM4 16l5-5 4 4 3-3 4 4M15 9.5h.01',
		up: 'M6 14l6-6 6 6',
		down: 'M6 10l6 6 6-6',
		grip: 'M9 6h.01M15 6h.01M9 12h.01M15 12h.01M9 18h.01M15 18h.01',
		sticker: 'M12 21a9 9 0 1 1 9-9c0 1-.2 2-.6 3l-5.4 5.4a9 9 0 0 1-3 .6zM20.4 15H15v5.4M9 10h.01M15 10h.01M9 14.5c1.5 1.3 4.5 1.3 6 0'
	};
</script>

<svg
	class="icon"
	viewBox="0 0 24 24"
	width={size}
	height={size}
	focusable="false"
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	aria-hidden={label ? undefined : 'true'}
>
	<path d={PATHS[name] ?? ''} />
</svg>

<style>
	.icon {
		flex: none;
		fill: none;
		stroke: currentColor;
		stroke-width: 2.2;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
</style>
