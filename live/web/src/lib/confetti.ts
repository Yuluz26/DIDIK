// A burst of paper confetti on a canvas above everything. One shared canvas, created on first use,
// removed when the last piece has landed. Skipped entirely when the device asks for less motion.

const COLOURS = ['#ffb627', '#e8553f', '#14958a', '#2f7fcf', '#6cb33f', '#d63e94', '#ffffff'];

interface Piece {
	x: number;
	y: number;
	vx: number;
	vy: number;
	spin: number;
	angle: number;
	size: number;
	colour: string;
	life: number;
}

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
			spin: (Math.random() - 0.5) * 0.4,
			angle: Math.random() * Math.PI,
			size: 6 + Math.random() * 7,
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
		p.angle += p.spin;
		g.save();
		g.translate(p.x, p.y);
		g.rotate(p.angle);
		g.scale(1, Math.cos(p.life * 0.18));
		g.fillStyle = p.colour;
		g.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
		g.restore();
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
