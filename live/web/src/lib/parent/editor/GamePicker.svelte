<!--
	"Main sebagai": the way a question is played. "Biasa" is the type's own way; the subject games that can
	play this type are offered under their subject (Sains, Sejarah, Pendidikan Islam), each with its
	sticker and a line saying what the child does. Only games that fit the type are shown.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import { SUBJECTS, gamesFor, gameOf } from '$lib/subjects/games';

	let { game = $bindable(), type }: { game: string | null; type: string } = $props();

	const fits = $derived(gamesFor(type));
	const chosen = $derived(gameOf(game));
	let open = $state(false);
</script>

{#if fits.length}
	<section class="games" aria-label="Main sebagai permainan subjek">
		<button type="button" class="head" aria-expanded={open} onclick={() => (open = !open)}>
			{#if chosen}<Sticker key={chosen.icon} size={30} alt="" />{/if}
			<span>
				<small>Main sebagai</small>
				<strong>{chosen ? chosen.title : 'Biasa (tiada permainan subjek)'}</strong>
			</span>
			<span class="count">{fits.length} permainan sesuai</span>
		</button>
		{#if open}
			<div class="choices">
				<button type="button" class="game" class:on={!game} onclick={() => ((game = null), (open = false))}>
					<span class="plain" aria-hidden="true">Aa</span>
					<span><strong>Biasa</strong><small>Cara jawab jenis soalan ini sendiri.</small></span>
				</button>
				{#each SUBJECTS as s (s.key)}
					{@const list = fits.filter((g) => g.subject === s.key)}
					{#if list.length}
						<p class="subject"><Sticker key={s.icon} size={22} alt="" /> {s.name}</p>
						{#each list as g (g.key)}
							<button type="button" class="game" class:on={game === g.key} onclick={() => ((game = g.key), (open = false))}>
								<Sticker key={g.icon} size={38} alt="" />
								<span><strong>{g.title}</strong><small>{g.blurb}</small></span>
							</button>
						{/each}
					{/if}
				{/each}
			</div>
		{/if}
	</section>
{/if}

<style>
	.games {
		display: grid;
		gap: 0.5rem;
		padding: 0.6rem;
		border-radius: var(--r-md);
		background: linear-gradient(135deg, #fff7e0, #eaf6ff);
		box-shadow: inset 0 0 0 2px #f1dfae;
	}
	.head {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		width: 100%;
		min-height: 2.9rem;
		padding: 0.2rem 0.4rem;
		border: 0;
		background: transparent;
		color: var(--ink);
		text-align: left;
		cursor: pointer;
	}
	.head span {
		display: grid;
	}
	.head small {
		color: var(--ink-2);
		font-weight: 700;
		font-size: 0.75rem;
	}
	.count {
		margin-left: auto;
		padding: 0.15rem 0.55rem;
		border-radius: 999px;
		background: #fff;
		color: var(--brand-deep);
		font-size: 0.78rem;
		font-weight: 800;
	}
	.choices {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr));
		gap: 0.4rem;
	}
	.subject {
		grid-column: 1 / -1;
		display: flex;
		align-items: center;
		gap: 0.35rem;
		margin-top: 0.3rem;
		color: var(--ink-2);
		font-weight: 800;
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
	.game {
		display: flex;
		align-items: center;
		gap: 0.55rem;
		padding: 0.45rem 0.6rem;
		border: 2px solid transparent;
		border-radius: var(--r-md);
		background: #fff;
		color: var(--ink);
		text-align: left;
		cursor: pointer;
	}
	.game span {
		display: grid;
		gap: 0.1rem;
	}
	.game small {
		color: var(--ink-2);
		font-size: 0.78rem;
		line-height: 1.25;
	}
	.game.on {
		border-color: var(--brand);
		background: var(--brand-soft, #e5f6ec);
	}
	.plain {
		display: grid;
		place-items: center;
		width: 38px;
		height: 38px;
		border-radius: 10px;
		background: var(--paper-2);
		font: 700 1rem var(--font-display);
	}
</style>
