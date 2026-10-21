<!-- The eight stickers children can send in the lobby and during games. Drawn, not emoji. -->
<script lang="ts">
	let { name, size = 40 }: { name: string; size?: number } = $props();
</script>

<svg viewBox="0 0 48 48" width={size} height={size} aria-hidden="true" focusable="false">
	{#if name === 'hati'}
		<path d="M24 41S7 31 7 18.5A9.5 9.5 0 0 1 24 12.6 9.5 9.5 0 0 1 41 18.5C41 31 24 41 24 41z" fill="#e8553f" />
		<ellipse cx="16" cy="18" rx="3.5" ry="2.4" fill="#fff" opacity=".55" transform="rotate(-30 16 18)" />
	{:else if name === 'bintang'}
		<path d="M24 5l5.6 11.6 12.6 1.6-9.3 8.8 2.4 12.6L24 33.4l-11.3 6.2 2.4-12.6-9.3-8.8 12.6-1.6z" fill="#ffb627" stroke="#c98400" stroke-width="2" stroke-linejoin="round" />
	{:else if name === 'ketawa'}
		<circle cx="24" cy="24" r="19" fill="#ffd34d" />
		<path d="M15 19q3-4 6 0M27 19q3-4 6 0" stroke="#5a3b00" stroke-width="2.6" fill="none" stroke-linecap="round" />
		<path d="M13 26h22q-2 11-11 11t-11-11z" fill="#7a2b2b" />
		<path d="M16 30q8 4 16 0" stroke="#f27b8b" stroke-width="3" fill="none" />
		<path d="M10 20q-3 3-1 6M38 20q3 3 1 6" stroke="#4fc3f7" stroke-width="2.6" fill="none" stroke-linecap="round" />
	{:else if name === 'tepuk'}
		<path d="M17 38l-7-13a3 3 0 0 1 5-3l4 6V11a3 3 0 0 1 6 0v12-15a3 3 0 0 1 6 0v15-12a3 3 0 0 1 6 0v18c0 6-4 11-11 11-6 0-10-3-15-2z" fill="#f2c08a" stroke="#b97a3f" stroke-width="2" stroke-linejoin="round" />
		<path d="M8 10l3 3M14 5l1 4M4 17l4 1" stroke="#ffb627" stroke-width="2.6" stroke-linecap="round" />
	{:else if name === 'wah'}
		<circle cx="24" cy="24" r="19" fill="#ffd34d" />
		<circle cx="17" cy="20" r="3.2" fill="#5a3b00" />
		<circle cx="31" cy="20" r="3.2" fill="#5a3b00" />
		<ellipse cx="24" cy="31" rx="5" ry="6" fill="#7a2b2b" />
		<path d="M13 13l4 2M35 13l-4 2" stroke="#5a3b00" stroke-width="2.4" stroke-linecap="round" />
	{:else if name === 'ok'}
		<path d="M14 22h6l5-11c3 0 5 2 4 6l-1 4h9a3 3 0 0 1 3 4l-3 12a4 4 0 0 1-4 3H20l-6-2z" fill="#f2c08a" stroke="#b97a3f" stroke-width="2" stroke-linejoin="round" />
		<rect x="6" y="21" width="8" height="18" rx="2" fill="#14958a" />
	{:else if name === 'api'}
		<path d="M24 43c-8 0-13-6-13-13 0-8 7-11 8-19 4 3 6 7 6 10 2-2 3-4 3-7 6 4 9 10 9 16 0 7-5 13-13 13z" fill="#e8553f" />
		<path d="M24 43c-4 0-7-3-7-7 0-4 4-6 5-10 3 2 4 4 4 6 1-1 2-2 2-4 3 2 3 5 3 8 0 4-3 7-7 7z" fill="#ffb627" />
	{:else}
		<path d="M5 36a19 19 0 0 1 38 0" stroke="#e8553f" stroke-width="5" fill="none" />
		<path d="M10 36a14 14 0 0 1 28 0" stroke="#ffb627" stroke-width="5" fill="none" />
		<path d="M15 36a9 9 0 0 1 18 0" stroke="#6cb33f" stroke-width="5" fill="none" />
		<path d="M20 36a4 4 0 0 1 8 0" stroke="#2f7fcf" stroke-width="5" fill="none" />
		<ellipse cx="9" cy="38" rx="7" ry="4" fill="#fff" />
		<ellipse cx="39" cy="38" rx="7" ry="4" fill="#fff" />
	{/if}
</svg>
