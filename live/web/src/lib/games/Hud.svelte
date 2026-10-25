<!-- The strip at the top of a child's screen: who you are, your score and place, sound. -->
<script lang="ts">
	import type { Me } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';
	import SoundToggle from '$ui/SoundToggle.svelte';
	import StickerArt from '$ui/StickerArt.svelte';

	let {
		me,
		score = 0,
		rank = null,
		unit = 'mata',
		streak = 0,
		children
	}: { me: Me; score?: number; rank?: number | null; unit?: string; streak?: number; children?: import('svelte').Snippet } = $props();
</script>

<header class="hud">
	<Avatar animal={me.avatar} colour={me.colour} skin={me.skin} size={40} />
	<div class="who">
		<span class="name">{me.name}</span>
		{#if rank}<span class="rank">Tempat ke-{rank}</span>{/if}
	</div>
	{#if streak >= 2}
		<span class="streak" title="Betul berturut-turut">
			<StickerArt name="api" size={20} />
			{streak}
		</span>
	{/if}
	{@render children?.()}
	<span class="score"><strong>{score.toLocaleString('ms-MY')}</strong> {unit}</span>
	<SoundToggle />
</header>

<style>
	.hud {
		position: sticky;
		top: env(safe-area-inset-top, 0px);
		z-index: 20;
		display: flex;
		align-items: center;
		gap: 0.6rem;
		padding: 0.5rem var(--gutter-r) 0.5rem var(--gutter);
		background: var(--paper);
		border-bottom: 2px solid var(--edge, var(--line));
	}
	.who {
		display: grid;
		flex: 1;
		min-width: 0;
		line-height: 1.15;
	}
	.name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font: 600 1.05rem var(--font-display);
	}
	.rank {
		color: var(--ink-2);
		font-size: 0.85rem;
		font-weight: 800;
		white-space: nowrap;
	}
	@media (max-width: 420px) {
		.hud {
			gap: 0.4rem;
		}
		.score {
			padding: 0.25rem 0.55rem;
		}
		.score strong {
			font-size: 1rem;
		}
	}
	.streak {
		display: inline-flex;
		align-items: center;
		gap: 0.15rem;
		padding: 0.15rem 0.55rem 0.15rem 0.3rem;
		border-radius: var(--r-pill);
		border: 2px solid var(--edge, transparent);
		background: #ffe3d6;
		color: var(--coral-deep);
		font: 600 1rem var(--font-display);
		animation: pop-in 400ms var(--spring);
	}

	.score {
		padding: 0.3rem 0.75rem;
		border-radius: var(--r-pill);
		border: 2px solid var(--edge, transparent);
		background: var(--card);
		box-shadow: 0 2px 0 var(--edge, var(--line));
		font-size: 0.85rem;
		font-weight: 800;
		color: var(--ink-2);
		white-space: nowrap;
	}
	.score strong {
		color: var(--ink);
		font: 600 1.15rem var(--font-display);
		font-variant-numeric: tabular-nums;
	}
</style>
