<!--
	The front page's Kuiz Interaktif section: a candy-floss cloud floating over the sea, with what the
	game is, its hands-on kinds of question, and a small demo to play right here (InteraktifDemo). Under it,
	the four kinds of Kuiz Interaktif a room can be opened in (InteraktifKinds).
	Stickers bob around it; with reduced motion they stay still.
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import DidiSoft from '$lib/games/interaktif/DidiSoft.svelte';
	import InteraktifDemo from './InteraktifDemo.svelte';
	import InteraktifKinds from './InteraktifKinds.svelte';
	import { reveal } from './reveal';

	const KINDS = [
		{ sticker: 'epal', name: 'Kira dan masukkan', line: 'Seret epal ke bakul sehingga cukup.' },
		{ sticker: 'buku', name: 'Susun huruf', line: 'Huruf bercampur menjadi perkataan.' },
		{ sticker: 'huruf', name: 'Huruf hilang', line: 'Isi huruf yang tertinggal.' },
		{ sticker: 'bakul', name: 'Isih kumpulan', line: 'Darat atau laut? Seret ke bakulnya.' },
		{ sticker: 'kucing', name: 'Cantum gambar', line: 'Susun 4 atau 9 kepingan gambar.' },
		{ sticker: 'nombor', name: 'Bina nombor', line: 'Blok ratus, puluh dan sa.' },
		{ sticker: 'jam', name: 'Laraskan jam', line: 'Pusing jarum ke masa yang betul.' },
		{ sticker: 'syiling', name: 'Bayar dengan wang', line: 'Syiling dan wang kertas Malaysia.' }
	];
	// at the cloud's edges, clear of its words; on a phone only the two on the right
	const FLOATERS = [
		{ key: 'kucing', x: '-1.4rem', y: '-1.6rem', s: 56, d: 0, side: 'left' },
		{ key: 'belon', x: 'calc(100% - 2.6rem)', y: '-2.2rem', s: 64, d: 0.6, side: 'right' },
		{ key: 'tembikai', x: '-1.4rem', y: 'calc(100% - 2.4rem)', s: 52, d: 1.2, side: 'left' },
		{ key: 'roket', x: 'calc(100% - 2.2rem)', y: 'calc(100% - 3rem)', s: 58, d: 1.8, side: 'right' }
	];
</script>

<section id="interaktif" class="ik-home wrap" aria-labelledby="interaktif-tajuk">
	<div class="cloud" {@attach reveal()}>
		{#each FLOATERS as f (f.key)}
			<span class="floater {f.side}" style:left={f.x} style:top={f.y} style:--d="{f.d}s" aria-hidden="true"><Sticker key={f.key} size={f.s} alt="" /></span>
		{/each}
		<div class="copy">
			<p class="kicker"><span class="new">Baharu</span> Kuiz Interaktif</p>
			<h2 id="interaktif-tajuk">Sentuh, seret dan susun bersama Didi</h2>
			<p class="lead">
				Setiap soalan menjadi permainan kecil, ikut kadar sendiri, dengan gambar untuk setiap soalan. Betul dapat
				tiga bintang; jika belum betul, Didi tunjukkan jawapannya dan terangkan kenapa. Ibu bapa dan guru menulis
				soalannya.
			</p>
			<ul class="kinds">
				{#each KINDS as k, i (k.name)}
					<li style:--i={i}>
						<span class="art"><Sticker key={k.sticker} size={44} alt="" /></span>
						<span><strong>{k.name}</strong>{k.line}</span>
					</li>
				{/each}
			</ul>
			<div class="actions">
				<a class="btn btn--big write" href="/ibu-bapa">Tulis kuiz interaktif <Icon name="next" /></a>
				<span class="didi" aria-hidden="true"><DidiSoft mood="wave" size={78} /></span>
			</div>
		</div>
		<div class="play" {@attach reveal(140)}>
			<InteraktifDemo />
		</div>
	</div>
	<InteraktifKinds />
</section>

<style>
	.ik-home {
		position: relative;
		z-index: 1;
		padding-block: 1.5rem 3rem;
		scroll-margin-top: 1rem;
	}
	.cloud {
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
		align-items: center;
		gap: clamp(1.2rem, 3vw, 2.6rem);
		padding: clamp(1.4rem, 1rem + 2.5vw, 2.8rem);
		border-radius: 44px;
		background:
			radial-gradient(circle at 12% 18%, rgb(255 255 255 / 0.9) 0 8%, transparent 9%),
			radial-gradient(circle at 88% 10%, rgb(255 246 194 / 0.9), transparent 26%),
			linear-gradient(160deg, #ffe1ef 0%, #ece0ff 45%, #d9f1ff 100%);
		color: #2c2340;
		box-shadow:
			0 10px 0 rgb(255 255 255 / 0.55),
			0 30px 60px rgb(10 40 80 / 0.35);
	}
	.copy {
		display: grid;
		gap: 0.9rem;
	}
	.kicker {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: #6c3fb8;
		font: 600 1rem var(--font-display);
		letter-spacing: 0.04em;
	}
	.new {
		padding: 0.2rem 0.65rem;
		border-radius: 999px;
		background: linear-gradient(135deg, #ff7eb0, #ffb36e);
		color: #fff;
		font-size: 0.78rem;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		box-shadow: 0 3px 0 #d9567f;
	}
	h2 {
		font: 600 var(--fs-h1) / 1.05 'Fredoka Variable', ui-rounded, sans-serif;
		color: #3a2268;
		text-wrap: balance;
	}
	.lead {
		max-width: 34rem;
		color: #4a3d63;
		font-size: var(--fs-lead);
	}
	.kinds {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 0.6rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.kinds li {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.45rem 0.6rem 0.45rem 0.4rem;
		border-radius: 20px;
		background: rgb(255 255 255 / 0.75);
		box-shadow: 0 4px 0 rgb(214 200 240 / 0.8);
		color: #4a3d63;
		font-size: 0.9rem;
		line-height: 1.3;
	}
	.kinds strong {
		display: block;
		color: #2c2340;
		font: 600 1.02rem var(--font-display);
	}
	.art {
		display: grid;
		place-items: center;
		flex: none;
		width: 3.1rem;
		height: 3.1rem;
		border-radius: 50%;
		background: #fff;
	}
	.actions {
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	.write {
		--edge: #b3477a;
		border-radius: 999px;
		background: linear-gradient(135deg, #ff6fa6, #ff9a5e);
		color: #fff;
	}
	.play {
		min-width: 0;
	}
	.floater {
		position: absolute;
		z-index: 2;
		filter: drop-shadow(0 8px 8px rgb(30 20 60 / 0.25));
		animation: bob-sticker 3.6s ease-in-out infinite;
		animation-delay: var(--d);
		pointer-events: none;
	}
	@keyframes bob-sticker {
		50% {
			transform: translateY(-10px) rotate(-6deg);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.floater {
			animation: none;
		}
	}
	@media (max-width: 900px) {
		.cloud {
			grid-template-columns: minmax(0, 1fr);
			border-radius: 32px;
		}
	}
	@media (max-width: 560px) {
		.kinds li {
			font-size: 0.8rem;
		}
		.kinds strong {
			font-size: 0.92rem;
		}
		.art {
			width: 2.5rem;
			height: 2.5rem;
		}
		.art :global(img) {
			width: 34px;
			height: 34px;
		}
		.cloud {
			padding: 1.1rem 0.9rem;
		}
		.floater.left {
			display: none;
		}
		.didi {
			display: none;
		}
	}
</style>
