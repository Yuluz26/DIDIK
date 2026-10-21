<!-- Everyone in the room, each animal popping in as they join. Hosts can remove a child from here. -->
<script lang="ts">
	import type { Person } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';
	import Icon from '$ui/Icon.svelte';

	let {
		people,
		me = null,
		size = 64,
		onremove = undefined
	}: { people: Person[]; me?: string | null; size?: number; onremove?: (person: Person) => void } = $props();
</script>

<ul class="wall" style:--size="{size}px">
	{#each people as person (person.id)}
		<li class="person" class:me={person.id === me} class:away={!person.online} data-player={person.id}>
			<Avatar animal={person.avatar} colour={person.colour} {size} bob mood={person.online ? 'happy' : 'sleep'} />
			<span class="name">{person.id === me ? 'Kamu' : person.name}</span>
			{#if person.bot}<span class="tag">bot</span>{/if}
			{#if onremove}
				<button type="button" class="remove" onclick={() => onremove(person)} aria-label="Keluarkan {person.name}">
					<Icon name="close" size={16} />
				</button>
			{/if}
		</li>
	{/each}
</ul>

<style>
	.wall {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(calc(var(--size) + 2.6rem), 1fr));
		gap: 0.8rem 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.person {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.25rem;
		animation: pop-in 520ms var(--spring) both;
	}
	.person:hover :global(svg) {
		animation: wiggle 0.6s ease-in-out;
	}
	.name {
		max-width: 100%;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-weight: 800;
		font-size: 0.9rem;
	}
	.me .name {
		padding: 0 0.5rem;
		border-radius: var(--r-pill);
		background: var(--sun);
	}
	.away {
		opacity: 0.55;
	}
	.tag {
		position: absolute;
		top: 0;
		left: 50%;
		translate: calc(var(--size) / 2 - 0.4rem) 0;
		padding: 0 0.4rem;
		border-radius: var(--r-pill);
		background: var(--ink);
		color: #fff;
		font-size: 0.7rem;
	}
	.remove {
		position: absolute;
		top: -0.3rem;
		right: calc(50% - var(--size) / 2 - 0.6rem);
		display: grid;
		place-items: center;
		width: 1.7rem;
		height: 1.7rem;
		border: 0;
		border-radius: 50%;
		background: var(--card);
		color: var(--ink-2);
		box-shadow: 0 2px 0 var(--line);
		cursor: pointer;
		opacity: 0;
		transition: opacity var(--t-state);
	}
	.person:hover .remove,
	.remove:focus-visible {
		opacity: 1;
	}
	@media (hover: none) {
		.remove {
			opacity: 1;
		}
	}
</style>
