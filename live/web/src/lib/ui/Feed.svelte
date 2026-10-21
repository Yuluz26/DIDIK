<!-- What just happened in the room: gems found, buildings finished, children escaping the forest. -->
<script lang="ts">
	import { flip } from 'svelte/animate';
	import type { FeedItem, Person } from '$lib/types';
	import Avatar from './Avatar.svelte';

	let { items, people, limit = 6 }: { items: FeedItem[]; people: Map<string, Person>; limit?: number } = $props();

	const shown = $derived([...items].reverse().slice(0, limit));
</script>

{#if shown.length}
	<ol class="feed" aria-live="polite">
		{#each shown as item (item.id)}
			{@const person = item.player ? people.get(item.player) : null}
			<li class="item kind-{item.kind}" animate:flip={{ duration: 300 }}>
				{#if person}<Avatar animal={person.avatar} colour={person.colour} skin={person.skin} size={30} />{/if}
				<span>{item.text}</span>
			</li>
		{/each}
	</ol>
{/if}

<style>
	.feed {
		display: grid;
		gap: 0.4rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.item {
		display: flex;
		align-items: center;
		gap: 0.55rem;
		padding: 0.45rem 0.75rem 0.45rem 0.45rem;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: 0 2px 0 var(--line);
		font-weight: 700;
		font-size: 0.95rem;
		animation: rise-in var(--t-enter) var(--spring);
	}
	.kind-gem,
	.kind-built,
	.kind-escape,
	.kind-durian {
		background: #fff3cf;
	}
	.kind-steal {
		background: #ffe3d6;
	}
</style>
