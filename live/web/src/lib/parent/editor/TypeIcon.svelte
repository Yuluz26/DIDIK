<!-- A small line drawing for each question type, on the same 24px grid as the app's icons. -->
<script lang="ts">
	let { type, size = 22 }: { type: string; size?: number } = $props();

	const PATHS: Record<string, string> = {
		single: 'M7 7.5a2.2 2.2 0 1 1-.01 0M11.5 7.5H20M7 16.5a2.2 2.2 0 1 1-.01 0M11.5 16.5H20',
		multiple: 'M4.5 5.5h5v5h-5zM5.7 8l1.2 1.2 2-2.4M4.5 13.5h5v5h-5zM5.7 16l1.2 1.2 2-2.4M12.5 8H20M12.5 16H20',
		truefalse: 'M3.5 12.5l3 3 5.5-6.5M14 8.5l6 6M20 8.5l-6 6',
		text: 'M4 6.5h16v11H4zM8 9.5v5M7 9.5h2M7 14.5h2M11.5 12h5',
		number: 'M9.5 4.5l-2 15M16.5 4.5l-2 15M5 9h15M4 15h15',
		order: 'M4 6h10M4 12h7M4 18h4M18 5v14M15 16l3 3 3-3',
		match: 'M5 7a1.8 1.8 0 1 1-.01 0M5 17a1.8 1.8 0 1 1-.01 0M19 7a1.8 1.8 0 1 1-.01 0M19 17a1.8 1.8 0 1 1-.01 0M7 7.5l10 9M7 16.5l10-9',
		blank: 'M3 9h6M15 9h6M3 15h4M11 15h10M10 7.5h4v3h-4z',
		count: 'M4 12h16l-1.8 7H5.8zM8 12l2.5-6M16 12l-2.5-6M9.5 15.5v1M14.5 15.5v1M12 15.5v1',
		spell: 'M3.5 7.5h5v6h-5zM9.5 7.5h5v6h-5zM15.5 7.5h5v6h-5zM6 10.5h.01M12 10.5h.01M18 10.5h.01M4 17.5h16',
		sort: 'M3.5 13h7l-1 6h-5zM13.5 13h7l-1 6h-5zM7 4.5v5M5 7.5l2 2 2-2M17 4.5v5M15 7.5l2 2 2-2',
		missing: 'M3.5 8h4v7h-4zM10 8h4v7h-4zM16.5 8h4v7h-4zM12 10.5v.01M12 13v.01',
		puzzle: 'M4 4h7v3a2 2 0 1 0 0 4v2H4zM13 4h7v9h-3a2 2 0 1 0-4 0zM4 15h9v5H4zM15 15h5v5h-5z',
		blocks: 'M4 20V6h3v14zM9 20V10h3v10zM15 17h3v3h-3zM19.5 17h.01',
		clock: 'M12 3.5a8.5 8.5 0 1 1-.01 0M12 7v5l3.5 2',
		money: 'M3.5 7h17v10h-17zM12 9.5a2.5 2.5 0 1 1-.01 0M6 10v4M18 10v4'
	};
</script>

<svg class="type-icon" viewBox="0 0 24 24" width={size} height={size} aria-hidden="true" focusable="false">
	<path d={PATHS[type] ?? PATHS.single} fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" />
</svg>

<style>
	.type-icon {
		flex: none;
	}
</style>
