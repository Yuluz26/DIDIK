// A burst of confetti on a canvas above everything: pixel squares that snap to a grid as they fall, a
// lit top and a shaded foot on each. One shared canvas, created on first use, removed when the last
// piece has landed. Skipped entirely when the device asks for less motion.

const COLOURS = ['#ffb627', '#e8553f', '#14958a', '#2f7fcf', '#6cb33f', '#d63e94', '#ffffff'];

interface Piece {
	x: number;
	y: number;
	vx: number;
	vy: number;
	/** Side of the square, in pixels of the grid (2 or 3). */
	cells: number;
	colour: string;
	life: number;
}

/** One pixel of the confetti, in CSS pixels. */
const GRID = 4;

let canvas: HTMLCanvasElement | null = null;
let pieces: Piece[] = [];
let frame = 0;

function reduced(): boolean {
	return typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export function confetti(options: { x?: number; y?: number; count?: number; spread?: number } = {}): void {
	if (typeof window === 'undefined' || reduced()) return;
	const x = options.x ?? window.innerWidth / 2;
	const y = options.y ?? window.innerHeight * 0.35;
	const count = options.count ?? 90;
	const spread = options.spread ?? 1;
	for (let i = 0; i < count; i++) {
		const angle = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI * 0.9 * spread;
		const speed = 6 + Math.random() * 9;
		pieces.push({
			x,
			y,
			vx: Math.cos(angle) * speed,
			vy: Math.sin(angle) * speed,
			cells: Math.random() < 0.55 ? 2 : 3,
			colour: COLOURS[Math.floor(Math.random() * COLOURS.length)],
			life: 0
		});
	}
	start();
}

function start(): void {
	if (!canvas) {
		canvas = document.createElement('canvas');
		canvas.setAttribute('aria-hidden', 'true');
		Object.assign(canvas.style, { position: 'fixed', inset: '0', pointerEvents: 'none', zIndex: '1000' });
		document.body.appendChild(canvas);
	}
	canvas.width = window.innerWidth * devicePixelRatio;
	canvas.height = window.innerHeight * devicePixelRatio;
	canvas.style.width = `${window.innerWidth}px`;
	canvas.style.height = `${window.innerHeight}px`;
	if (!frame) frame = requestAnimationFrame(draw);
}

function draw(): void {
	if (!canvas) return;
	const g = canvas.getContext('2d');
	if (!g) return;
	g.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
	g.clearRect(0, 0, canvas.width, canvas.height);
	for (const p of pieces) {
		p.life++;
		p.vy += 0.32;
		p.vx *= 0.985;
		p.x += p.vx;
		p.y += p.vy;
		// drawn on the grid, so the pieces move in steps like everything else on the page
		const x = Math.round(p.x / GRID) * GRID;
		const y = Math.round(p.y / GRID) * GRID;
		const size = p.cells * GRID;
		g.fillStyle = p.colour;
		g.fillRect(x, y, size, size);
		g.fillStyle = 'rgb(0 0 0 / 0.22)';
		g.fillRect(x, y + size - GRID, size, GRID);
		g.fillRect(x + size - GRID, y, GRID, size - GRID);
		g.fillStyle = 'rgb(255 255 255 / 0.55)';
		g.fillRect(x, y, GRID, GRID);
	}
	pieces = pieces.filter((p) => p.y < window.innerHeight + 40 && p.life < 400);
	if (pieces.length) {
		frame = requestAnimationFrame(draw);
	} else {
		frame = 0;
		canvas.remove();
		canvas = null;
	}
}
