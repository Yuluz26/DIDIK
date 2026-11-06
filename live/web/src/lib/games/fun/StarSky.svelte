<!--
	Kejar Bintang's night sky, on a phone and on the host's screen: the sky split between Pasukan
	Harimau (over the jungle) and Pasukan Penyu (over the sea), each half a pixel night that fills with
	the stars its team has caught. Every ten stars light a constellation, drawn joined up by faint lines;
	a star caught streaks down into its team's half with a tail.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import { memo } from '$lib/pixel/cache';
	import { Pix } from '$lib/pixel/pix';
	import Scene from '$lib/pixel/Scene.svelte';
	import { type G, dot, hash, hex, line, put, stillWanted } from '$lib/pixel/scene';
	import { star } from './art';
	import { M, NIGHT, bands, hills, moon, noise, ramp, rgba, stars, treeline } from './scenery';

	interface Team {
		key: string;
		name: string;
		stars: number;
		lit: number;
		players: number;
	}
	let {
		client,
		world,
		big = false
	}: { client: RoomClient; world: { teams: Team[]; constellations: string[]; per: number; myTeam?: string | null; mine?: number }; big?: boolean } = $props();

	const W = 96;
	const H = $derived(big ? 96 : 80);
	const HORIZON = $derived(H - 14);
	const still = stillWanted();

	let falls = $state<{ key: number; team: string; at: number }[]>([]);
	let n = 0;
	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind !== 'star') return;
			const key = ++n;
			falls = [...falls, { key, team: fx.team, at: performance.now() }];
			if (fx.by === undefined || fx.team === world.myTeam) play('pop');
			setTimeout(() => (falls = falls.filter((f) => f.key !== key)), 1200);
		})
	);
	const leader = $derived(world.teams[0].stars === world.teams[1].stars ? null : world.teams[0].stars > world.teams[1].stars ? world.teams[0].key : world.teams[1].key);

	/** The night over a team's land: the jungle for Harimau, the sea and a beach for Penyu. */
	function night(team: string, h: number): Pix {
		return memo(`stars:night:${team}:${h}`, () => {
			const horizon = h - 14;
			const p = new Pix(W, h);
			bands(p, 0, horizon + 2, NIGHT, 3);
			stars(p, 0, horizon - 6, 0.01, team === 'harimau' ? 3 : 4);
			if (team === 'harimau') {
				moon(p, 80, 10, 4, NIGHT[0]);
				hills(p, horizon - 2, 6, h, ramp(['#0e1a14', '#13241a', '#1a3022', '#223c2a', '#2c4a34']), 2.1);
				treeline(p, -4, W + 4, horizon + 3, ramp(['#08120c', '#0d1a12', '#122218', '#182c1e', '#1e3624']), 7, true);
				for (let y = horizon + 3; y < h; y++) for (let x = 0; x < W; x++) p.set(x, y, noise(x, y, 2) < 0.1 ? rgba('#0d1a12') : rgba('#10201a'));
			} else {
				moon(p, 14, 10, 4, NIGHT[0]);
				for (let y = horizon; y < h - 4; y++) {
					for (let x = 0; x < W; x++) p.set(x, y, noise(x >> 2, y, 6) < 0.25 ? rgba('#2a3a66') : rgba('#18203e'));
				}
				// the moon's path on the water
				for (let y = horizon + 1; y < h - 4; y += 2) for (let x = 10; x < 19; x++) if (noise(x, y, 9) < 0.45) p.set(x, y, rgba('#c8c0a0'));
				for (let y = h - 4; y < h; y++) for (let x = 0; x < W; x++) p.set(x, y, noise(x, y, 3) < 0.2 ? rgba('#3a3448') : rgba('#2c283a'));
				// a turtle coming ashore
				const t = M.leaf;
				p.ellipse(70, h - 4, 4, 2, t.c[1], t.ink).set(75, h - 4, t.c[2]).set(65, h - 3, t.c[1]);
			}
			return p;
		});
	}

	/** Where a team's `i`th caught star sits: scattered over its sky, never in the land. */
	const spot = (i: number, h: number): [number, number] => [3 + Math.round(hash(i, 1) * (W - 12)), 3 + Math.round(hash(i, 2) * (h - 26))];

	function painter(team: Team) {
		return (g: G, t: number) => {
			const now = still ? 0 : t;
			const h = H;
			put(g, night(team.key, h), 0, 0);
			const count = Math.min(team.stars, 80);
			// each lit constellation: its ten stars joined up, left to right
			for (let c = 0; c < Math.min(team.lit, 8); c++) {
				const group = Array.from({ length: 10 }, (_, k) => spot(c * 10 + k, h)).sort((a, b) => a[0] - b[0]);
				g.globalAlpha = 0.35;
				for (let k = 0; k + 1 < group.length; k++) line(g, group[k][0] + 4, group[k][1] + 4, group[k + 1][0] + 4, group[k + 1][1] + 4, hex('#9fb8ff'));
				g.globalAlpha = 1;
			}
			const fallen = falls.filter((f) => f.team === team.key);
			for (let i = 0; i < count; i++) {
				// the newest star waits until the falling one reaches it
				if (fallen.length && i === count - 1 && !still) continue;
				const [x, y] = spot(i, h);
				const twinkle = (((now / 500) | 0) + i) % 7 === 0;
				g.globalAlpha = twinkle ? 0.6 : 1;
				put(g, star(true).pix, x, y);
				g.globalAlpha = 1;
			}
			// shooting stars: a streak from the top corner to where the new star will sit, with a tail
			for (const f of fallen) {
				const u = Math.min(1, (now - f.at) / 900);
				const [tx, ty] = spot(Math.max(0, count - 1), h);
				const sx = team.key === 'harimau' ? -10 : W + 10;
				const x = sx + (tx - sx) * u;
				const y = -10 + (ty + 10) * u;
				for (let k = 1; k < 9; k++) {
					g.globalAlpha = (1 - k / 9) * 0.9;
					dot(g, x + 4 - (tx - sx) * 0.02 * k, y + 4 - (ty + 10) * 0.02 * k, hex('#fff6b0'));
				}
				g.globalAlpha = 1;
				put(g, star(true).pix, x, y);
			}
		};
	}
	const painters = $derived(Object.fromEntries(world.teams.map((t) => [t.key, painter(t)])));
</script>

<div class="sky" class:big>
	{#each world.teams as team (team.key)}
		<section class="half {team.key}" class:mine={team.key === world.myTeam} aria-label="{team.name}: {team.stars} bintang">
			<header>
				<strong>{team.name}</strong>
				<span>{team.stars} bintang{leader === team.key ? ' · mendahului' : ''}</span>
			</header>
			<div class="field">
				<Scene w={W} h={H} paint={painters[team.key]} fps={12} />
			</div>
			<ul class="lit" aria-label="Buruj menyala">
				{#each world.constellations.slice(0, Math.max(1, team.lit + 1)) as name, i (name)}
					<li class:on={i < team.lit}>{name}</li>
				{/each}
			</ul>
		</section>
	{/each}
	{#if world.mine !== undefined}<p class="mine-count">Kamu sudah menangkap <strong>{world.mine}</strong> bintang untuk pasukan kamu.</p>{/if}
</div>

<style>
	.sky {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.5rem;
	}
	.half {
		display: grid;
		grid-template-rows: auto auto auto;
		align-content: start;
		gap: 0.4rem;
		padding: 0.5rem;
		border: 3px solid #2a1f2d;
		border-radius: 6px;
		background: #17152a;
		color: #fff4d8;
		box-shadow: 0 4px 0 #2a1f2d;
	}
	.harimau {
		background: #2a1a12;
		border-color: #6a3414;
	}
	.penyu {
		background: #0f2430;
		border-color: #14504a;
	}
	.mine {
		outline: 3px solid #ffcf5a;
		outline-offset: 2px;
	}
	header {
		display: grid;
		font-family: var(--font-display);
	}
	header span {
		color: #ffd98a;
		font-size: 0.85rem;
		font-weight: 700;
	}
	.field {
		overflow: hidden;
		border: 2px solid #0c0b16;
		border-radius: 3px;
	}
	.lit {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem;
		margin: 0;
		padding: 0;
		list-style: none;
		font-size: 0.75rem;
		font-weight: 800;
	}
	.lit li {
		padding: 0.1rem 0.5rem;
		border-radius: 4px;
		background: rgb(255 255 255 / 0.1);
		color: #a8a4bc;
	}
	.lit li.on {
		background: #ffcf5a;
		color: #3a2306;
	}
	.mine-count {
		grid-column: 1 / -1;
		text-align: center;
		font-weight: 800;
	}
</style>
