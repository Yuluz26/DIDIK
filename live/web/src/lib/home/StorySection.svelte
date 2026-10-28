<!--
	The front page's Legenda: Story Mode section: the five worlds' battlefield paintings take turns
	behind the hero and that world's boss, with the world's name, a row of the five worlds to pick from,
	what the mode is, and a way in for parents. The paintings change every few seconds (not while the
	pointer or focus is on the section, and never with reduced motion); only the shown painting and
	the next one are loaded.
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import { ELEMENTS, ELEMENT_NAME, battleBg, bossArt, elementIcon, heroWeaponArt, symbol } from '$lib/games/legenda/data';

	const WORLDS = [
		{ name: 'Tasik Chini', boss: 'Naga Chini' },
		{ name: 'Batang Lupar', boss: 'Bujang Senang' },
		{ name: 'Hutan Larut', boss: 'Gajah Rimba' },
		{ name: 'Rimba Bayangan', boss: 'Sang Kancil Bayangan' },
		{ name: 'Gunung Ledang', boss: 'Penunggu Kabus' }
	];
	const HERO_WEAPON = ['air', 'api', 'tanah', 'petir', 'angin'] as const;

	let shown = $state(0);
	let held = $state(false);
	let section = $state<HTMLElement>();
	let seen = $state(false);

	// Nothing is fetched until the section comes near the screen.
	$effect(() => {
		if (!section || !('IntersectionObserver' in window)) {
			seen = true;
			return;
		}
		const watch = new IntersectionObserver(([entry]) => entry.isIntersecting && ((seen = true), watch.disconnect()), { rootMargin: '300px' });
		watch.observe(section);
		return () => watch.disconnect();
	});

	$effect(() => {
		if (!seen || held || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
		const timer = setInterval(() => (shown = (shown + 1) % WORLDS.length), 5200);
		return () => clearInterval(timer);
	});

	const next = $derived((shown + 1) % WORLDS.length);
</script>

<section
	id="legenda"
	class="story wrap"
	aria-labelledby="legenda-tajuk"
	bind:this={section}
	onpointerenter={() => (held = true)}
	onpointerleave={() => (held = false)}
	onfocusin={() => (held = true)}
	onfocusout={() => (held = false)}
>
	<div class="frame">
		<div class="scene" aria-hidden="true">
			{#if seen}
				{#each WORLDS as _, i (i)}
					{#if i === shown || i === next}
						<img class="field" class:on={i === shown} src={battleBg(i)} alt="" draggable="false" />
					{/if}
				{/each}
				{#key shown}
					<img class="boss" src={bossArt(shown)} alt="" draggable="false" />
					<img class="hero" src={heroWeaponArt(shown % 2 ? 'mahsuri' : 'tuah', HERO_WEAPON[shown])} alt="" draggable="false" />
				{/key}
			{/if}
			<div class="shade"></div>
		</div>

		<div class="copy">
			<p class="badge"><span>Baharu</span> Pengembaraan JRPG</p>
			<h2 id="legenda-tajuk">Legenda: Story Mode</h2>
			<p class="lead">
				Wira kamu mengembara lima dunia legenda Melayu. Setiap jawapan betul ialah serangan, setiap
				jawapan salah dibalas musuh. Kalahkan lima boss dengan kuasa lima elemen.
			</p>
			<p class="now" aria-live="polite">
				<img src={symbol(shown)} alt="" width="34" height="34" />
				<span><strong>{WORLDS[shown].name}</strong> · boss {WORLDS[shown].boss}</span>
			</p>

			<ul class="worlds" aria-label="Lima dunia">
				{#each WORLDS as world, i (world.name)}
					<li>
						<button type="button" class:on={i === shown} aria-pressed={i === shown} onclick={() => (shown = i)} aria-label={world.name}>
							<img src={symbol(i)} alt="" width="40" height="40" />
						</button>
					</li>
				{/each}
			</ul>

			<ul class="facts">
				<li><strong>5</strong> dunia, 5 boss besar</li>
				<li><strong>Solo</strong> atau <strong>Party</strong> bersama kelas</li>
				<li class="elements">
					{#each ELEMENTS as el (el)}<img src={elementIcon(el)} alt={ELEMENT_NAME[el]} title={ELEMENT_NAME[el]} width="26" height="26" />{/each}
					<span>lima elemen</span>
				</li>
			</ul>

			<a class="go" href="/ibu-bapa">Main dengan kuiz anda <Icon name="next" /></a>
		</div>
	</div>
</section>

<style>
	.story {
		position: relative;
		padding-block: 2rem 3rem;
	}
	.frame {
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);
		min-height: 30rem;
		overflow: hidden;
		border-radius: 22px;
		background: #0d1630;
		color: #fff4d8;
		box-shadow:
			inset 0 0 0 3px #d9a441,
			inset 0 0 0 6px rgb(13 22 48 / 0.9),
			0 1.4rem 2.6rem rgb(5 15 40 / 0.45);
	}
	.scene {
		position: absolute;
		inset: 0;
		container-type: inline-size;
	}
	.field {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
		opacity: 0;
		transition: opacity 1.1s ease;
	}
	.field.on {
		opacity: 1;
	}
	.boss {
		position: absolute;
		left: 26%;
		bottom: 6%;
		width: 34%;
		max-height: 72%;
		object-fit: contain;
		object-position: bottom;
		filter: drop-shadow(0 1rem 1.4rem rgb(0 0 0 / 0.55));
		animation:
			rise 900ms cubic-bezier(0.2, 0.9, 0.3, 1.1) both,
			float 4.5s ease-in-out 900ms infinite;
	}
	.hero {
		position: absolute;
		left: 4%;
		bottom: 5%;
		height: 46%;
		width: auto;
		filter: drop-shadow(0 0.6rem 0.8rem rgb(0 0 0 / 0.5));
		animation: rise 700ms 120ms cubic-bezier(0.2, 0.9, 0.3, 1.1) both;
	}
	/* the copy side darkens so the words read over any painting */
	.shade {
		position: absolute;
		inset: 0;
		background: linear-gradient(90deg, rgb(13 22 48 / 0.05) 0%, rgb(13 22 48 / 0.25) 45%, rgb(13 22 48 / 0.88) 62%, rgb(13 22 48 / 0.95) 100%);
	}
	.copy {
		position: relative;
		grid-column: 2;
		display: grid;
		align-content: center;
		gap: 0.9rem;
		padding: 2rem 2rem 2rem 0.5rem;
	}
	.badge {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		font: 700 0.8rem var(--font-display);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #ffd98a;
	}
	.badge span {
		padding: 0.2rem 0.6rem;
		border-radius: 999px;
		background: #e2549f;
		color: #fff;
	}
	h2 {
		font: 700 clamp(1.9rem, 1.3rem + 2.4vw, 3rem) / 1.05 var(--font-display);
		color: #fff4d8;
		text-shadow: 0 3px 0 #7a4a12;
	}
	.lead {
		max-width: 30rem;
		color: #f3e6c8;
		font-size: 1.02rem;
	}
	.now {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		min-height: 2.5rem;
		color: #ffd98a;
	}
	.now strong {
		color: #fff;
	}
	.worlds {
		display: flex;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.worlds button {
		display: grid;
		place-items: center;
		width: 3.2rem;
		height: 3.2rem;
		padding: 0;
		border: 2px solid rgb(217 164 65 / 0.45);
		border-radius: 14px;
		background: rgb(255 255 255 / 0.06);
		cursor: pointer;
		transition:
			transform 160ms ease,
			border-color 160ms ease,
			background 160ms ease;
	}
	.worlds button:hover {
		transform: translateY(-2px);
	}
	.worlds button.on {
		border-color: #ffcf5a;
		background: rgb(255 207 90 / 0.18);
	}
	.worlds button:focus-visible {
		outline: 3px solid #ffcf5a;
		outline-offset: 2px;
	}
	.facts {
		display: grid;
		gap: 0.35rem;
		margin: 0;
		padding: 0;
		list-style: none;
		font-weight: 700;
	}
	.facts strong {
		color: #ffcf5a;
	}
	.elements {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}
	.elements span {
		margin-left: 0.3rem;
	}
	.go {
		justify-self: start;
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		min-height: 3rem;
		padding: 0.7rem 1.3rem;
		border-radius: 999px;
		background: linear-gradient(180deg, #ffd66b, #f4a524);
		color: #3a2306;
		font: 700 1.05rem var(--font-display);
		text-decoration: none;
		box-shadow:
			0 4px 0 #a8650c,
			0 0.8rem 1.4rem rgb(0 0 0 / 0.3);
		transition: transform 140ms ease;
	}
	.go:hover {
		transform: translateY(-2px);
	}
	.go:active {
		transform: translateY(2px);
		box-shadow: 0 2px 0 #a8650c;
	}
	.go:focus-visible {
		outline: 3px solid #fff;
		outline-offset: 3px;
	}
	@keyframes rise {
		from {
			opacity: 0;
			transform: translateY(1.2rem) scale(0.96);
		}
	}
	@keyframes float {
		50% {
			transform: translateY(-0.5rem);
		}
	}
	@media (max-width: 860px) {
		.frame {
			grid-template-columns: minmax(0, 1fr);
			grid-template-rows: 17rem auto;
			min-height: 0;
		}
		.scene {
			bottom: auto;
			height: 17rem;
		}
		.shade {
			background: linear-gradient(180deg, rgb(13 22 48 / 0) 55%, rgb(13 22 48 / 0.95) 100%);
		}
		.boss {
			left: auto;
			right: 4%;
			width: 52%;
		}
		.hero {
			height: 62%;
		}
		.copy {
			grid-column: 1;
			grid-row: 2;
			padding: 1.2rem 1.2rem 1.6rem;
			background: #0d1630;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.field {
			transition: none;
		}
		.boss,
		.hero {
			animation: none;
		}
	}
</style>
