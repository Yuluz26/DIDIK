<!--
	The strip at the top of a child's screen: who you are, your place, your score, full screen, sound.
	A game's own counters (keys, hearts) come in as children: on a line of their own under the name on a
	phone, beside the score once the screen is wide enough, so nothing has to squeeze. A streak joins
	the name, which shortens to make room, so it comes and goes without moving the rest. The strip
	publishes its height as --hud-h for the screens that fit themselves under it.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { Me } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';
	import FullscreenToggle from '$ui/FullscreenToggle.svelte';
	import SoundToggle from '$ui/SoundToggle.svelte';
	import StickerArt from '$ui/StickerArt.svelte';

	let {
		me,
		score = 0,
		rank = null,
		unit = 'mata',
		streak = 0,
		children
	}: { me: Me; score?: number; rank?: number | null; unit?: string; streak?: number; children?: Snippet } = $props();

	let height = $state(0);

	$effect(() => {
		if (!height) return;
		const root = document.documentElement.style;
		root.setProperty('--hud-h', `${height}px`);
		return () => root.removeProperty('--hud-h');
	});
</script>

<header class="hud" class:has-extra={!!children} bind:offsetHeight={height}>
	<span class="me"><Avatar animal={me.avatar} colour={me.colour} skin={me.skin} size={40} /></span>
	<div class="who">
		<span class="line">
			<span class="name">{me.name}</span>
			{#if streak >= 2}
				<span class="streak" title="Betul berturut-turut">
					<StickerArt name="api" size={16} />
					{streak}
				</span>
			{/if}
		</span>
		{#if rank}<span class="rank">Tempat ke-{rank}</span>{/if}
	</div>
	{#if children}<div class="extra">{@render children()}</div>{/if}
	<span class="score"><strong>{score.toLocaleString('ms-MY')}</strong> <span class="unit">{unit}</span></span>
	<span class="tools">
		<FullscreenToggle />
		<SoundToggle />
	</span>
</header>

<style>
	.hud {
		position: sticky;
		top: env(safe-area-inset-top, 0px);
		z-index: 20;
		display: grid;
		grid-template-columns: auto minmax(0, 1fr) auto auto;
		grid-template-areas: 'me who score tools';
		align-items: center;
		gap: 0.4rem 0.6rem;
		padding: 0.5rem var(--gutter-r) 0.5rem var(--gutter);
		background: var(--paper);
		border-bottom: 2px solid var(--edge, var(--line));
	}
	/* A phone has no room for the game's counters beside the score: they take the line under the name. */
	.has-extra {
		grid-template-areas:
			'me who score tools'
			'. extra extra extra';
	}
	@media (min-width: 48rem) {
		.has-extra {
			grid-template-columns: auto minmax(0, 1fr) auto auto auto;
			grid-template-areas: 'me who extra score tools';
		}
	}

	.me {
		grid-area: me;
		line-height: 0;
	}

	.who {
		grid-area: who;
		display: grid;
		min-width: 0;
		line-height: 1.15;
	}
	.line {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		min-width: 0;
	}
	.name,
	.rank {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.name {
		font: 600 1.05rem var(--font-display);
	}
	.rank {
		color: var(--ink-2);
		font-size: 0.85rem;
		font-weight: 800;
	}
	.streak {
		display: inline-flex;
		flex: none;
		align-items: center;
		gap: 0.1rem;
		padding: 0 0.35rem 0 0.15rem;
		border-radius: var(--r-pill);
		border: 2px solid var(--edge, transparent);
		background: #ffe3d6;
		color: var(--coral-deep);
		font: 600 0.95rem/1 var(--font-display);
		animation: pop-in 400ms var(--spring);
	}

	.extra {
		grid-area: extra;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.5rem;
		min-width: 0;
	}

	.score {
		grid-area: score;
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

	.tools {
		grid-area: tools;
		display: flex;
		gap: 0.4rem;
	}

	@media (max-width: 420px) {
		.hud {
			column-gap: 0.45rem;
		}
		.score {
			padding: 0.25rem 0.55rem;
		}
		.score strong {
			font-size: 1rem;
		}
	}
	/* The smallest phones keep the number and let the unit go, so the name and place still read. */
	@media (max-width: 359px) {
		.unit {
			position: absolute;
			width: 1px;
			height: 1px;
			overflow: hidden;
			clip-path: inset(50%);
			white-space: nowrap;
		}
	}
</style>
