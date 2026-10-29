<!--
	The air of a battle: drifting motes for the world (petals, embers, leaves, spirit wisps, mist) and
	the sparks of a hit. One canvas over the whole stage, sized to it and drawn every frame; nothing at
	all when the device asks for reduced motion.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { reducedMotion } from './data';

	let { motes = 'petals', calm = false }: { motes?: 'petals' | 'embers' | 'leaves' | 'wisps' | 'mist'; calm?: boolean } = $props();

	interface Bit {
		x: number;
		y: number;
		vx: number;
		vy: number;
		life: number;
		age: number;
		size: number;
		colour: string;
		spin: number;
		kind: 'mote' | 'spark' | 'ring';
	}

	let canvas: HTMLCanvasElement;
	const bits: Bit[] = [];
	let still = false;

	const MOTE: Record<string, { colours: string[]; count: number; rise: number; size: [number, number] }> = {
		petals: { colours: ['#ffc4dd', '#ffe3ef', '#fff6c8'], count: 26, rise: -0.15, size: [3, 6] },
		embers: { colours: ['#ffcf6b', '#ff8a3c', '#fff1b8'], count: 30, rise: 0.35, size: [1.5, 3.2] },
		leaves: { colours: ['#9be36b', '#5fbf4a', '#d9f59a'], count: 22, rise: -0.25, size: [3, 6] },
		wisps: { colours: ['#c9a2ff', '#8ee9ff', '#f0d8ff'], count: 28, rise: 0.22, size: [1.8, 3.6] },
		mist: { colours: ['#ffffff', '#e8f7ff'], count: 16, rise: 0.05, size: [16, 34] }
	};

	export function burst(x: number, y: number, colours: string[], count = 46, ring = true): void {
		if (still || !canvas) return;
		const w = canvas.width;
		for (let i = 0; i < count; i++) {
			const angle = Math.random() * Math.PI * 2;
			const speed = (0.004 + Math.random() * 0.012) * w;
			bits.push({
				x: x * w,
				y: y * canvas.height,
				vx: Math.cos(angle) * speed,
				vy: Math.sin(angle) * speed - 0.002 * w,
				life: 34 + Math.random() * 26,
				age: 0,
				size: (0.002 + Math.random() * 0.004) * w,
				colour: colours[i % colours.length],
				spin: 0,
				kind: 'spark'
			});
		}
		if (ring) bits.push({ x: x * w, y: y * canvas.height, vx: 0, vy: 0, life: 26, age: 0, size: 0.02 * w, colour: colours[0], spin: 0, kind: 'ring' });
	}

	function mote(spec: (typeof MOTE)[string], fresh: boolean): Bit {
		const w = canvas.width;
		const h = canvas.height;
		const size = (spec.size[0] + Math.random() * (spec.size[1] - spec.size[0])) * (w / 960);
		return {
			x: Math.random() * w,
			y: fresh ? Math.random() * h : spec.rise > 0 ? h + 10 : -10,
			vx: (Math.random() - 0.3) * 0.0006 * w,
			vy: -spec.rise * 0.0009 * w * (0.6 + Math.random() * 0.8),
			life: 400 + Math.random() * 500,
			age: 0,
			size,
			colour: spec.colours[Math.floor(Math.random() * spec.colours.length)],
			spin: Math.random() * Math.PI,
			kind: 'mote'
		};
	}

	onMount(() => {
		still = reducedMotion();
		if (still) return;
		const ctx = canvas.getContext('2d')!;
		const fit = () => {
			const box = canvas.getBoundingClientRect();
			const dpr = Math.min(2, window.devicePixelRatio || 1);
			canvas.width = Math.max(1, Math.round(box.width * dpr));
			canvas.height = Math.max(1, Math.round(box.height * dpr));
		};
		fit();
		const observer = new ResizeObserver(fit);
		observer.observe(canvas);
		const spec = () => MOTE[motes] ?? MOTE.petals;
		for (let i = 0; i < spec().count; i++) bits.push(mote(spec(), true));
		let frame = 0;
		const draw = () => {
			frame = requestAnimationFrame(draw);
			if (document.hidden) return;
			const s = spec();
			const w = canvas.width;
			const h = canvas.height;
			ctx.clearRect(0, 0, w, h);
			let count = 0;
			for (let i = bits.length - 1; i >= 0; i--) {
				const b = bits[i];
				b.age++;
				if (b.kind === 'mote') {
					count++;
					b.x += b.vx + Math.sin((b.age + b.spin * 50) / 40) * 0.0004 * w;
					b.y += b.vy * (calm ? 0.4 : 1);
					b.spin += 0.02;
					if (b.age > b.life || b.y < -40 || b.y > h + 40 || b.x < -40 || b.x > w + 40) {
						bits.splice(i, 1);
						continue;
					}
					const fade = Math.min(1, b.age / 60, (b.life - b.age) / 60);
					ctx.globalAlpha = (motes === 'mist' ? 0.18 : 0.75) * fade;
					ctx.fillStyle = b.colour;
					if (motes === 'petals' || motes === 'leaves') {
						ctx.save();
						ctx.translate(b.x, b.y);
						ctx.rotate(b.spin);
						ctx.beginPath();
						ctx.ellipse(0, 0, b.size, b.size * 0.5, 0, 0, Math.PI * 2);
						ctx.fill();
						ctx.restore();
					} else {
						ctx.beginPath();
						ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2);
						ctx.fill();
						if (motes !== 'mist') {
							ctx.globalAlpha *= 0.35;
							ctx.beginPath();
							ctx.arc(b.x, b.y, b.size * 3, 0, Math.PI * 2);
							ctx.fill();
						}
					}
				} else {
					const t = b.age / b.life;
					if (t >= 1) {
						bits.splice(i, 1);
						continue;
					}
					ctx.globalAlpha = 1 - t;
					if (b.kind === 'ring') {
						ctx.strokeStyle = b.colour;
						ctx.lineWidth = 0.006 * w * (1 - t);
						ctx.beginPath();
						ctx.arc(b.x, b.y, b.size + t * 0.16 * w, 0, Math.PI * 2);
						ctx.stroke();
					} else {
						b.x += b.vx;
						b.y += b.vy;
						b.vx *= 0.94;
						b.vy = b.vy * 0.94 + 0.0004 * w;
						ctx.fillStyle = b.colour;
						ctx.beginPath();
						ctx.arc(b.x, b.y, b.size * (1 - t * 0.6), 0, Math.PI * 2);
						ctx.fill();
					}
				}
			}
			ctx.globalAlpha = 1;
			while (count < s.count) {
				bits.push(mote(s, false));
				count++;
			}
		};
		frame = requestAnimationFrame(draw);
		return () => {
			cancelAnimationFrame(frame);
			observer.disconnect();
		};
	});
</script>

<canvas bind:this={canvas} class="air" aria-hidden="true"></canvas>

<style>
	.air {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		pointer-events: none;
	}
</style>
