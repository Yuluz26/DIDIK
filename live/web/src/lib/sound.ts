// Every sound is synthesised with the Web Audio API: no audio files to download, nothing to license,
// and it works offline. Browsers only allow sound after a tap, so `unlock()` runs on the first one.

type Wave = OscillatorType;

let ctx: AudioContext | null = null;
let master: GainNode | null = null;
let muted = read();
const listeners = new Set<(muted: boolean) => void>();

function read(): boolean {
	try {
		return localStorage.getItem('didik-live:muted') === '1';
	} catch {
		return false;
	}
}

export function unlock(): void {
	if (typeof window === 'undefined') return;
	if (!ctx) {
		const Ctor = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
		if (!Ctor) return;
		ctx = new Ctor();
		master = ctx.createGain();
		master.gain.value = 0.55;
		master.connect(ctx.destination);
	}
	if (ctx.state === 'suspended') void ctx.resume();
}

export function isMuted(): boolean {
	return muted;
}

export function setMuted(value: boolean): void {
	muted = value;
	try {
		localStorage.setItem('didik-live:muted', value ? '1' : '0');
	} catch {
		/* private mode: the choice lasts for this visit */
	}
	listeners.forEach((fn) => fn(value));
}

export function onMuteChange(fn: (muted: boolean) => void): () => void {
	listeners.add(fn);
	return () => listeners.delete(fn);
}

function tone(freq: number, at: number, dur: number, wave: Wave = 'sine', gain = 0.25, slideTo?: number): void {
	if (!ctx || !master) return;
	const start = ctx.currentTime + at;
	const osc = ctx.createOscillator();
	const amp = ctx.createGain();
	osc.type = wave;
	osc.frequency.setValueAtTime(freq, start);
	if (slideTo) osc.frequency.exponentialRampToValueAtTime(slideTo, start + dur);
	amp.gain.setValueAtTime(0.0001, start);
	amp.gain.exponentialRampToValueAtTime(gain, start + 0.012);
	amp.gain.exponentialRampToValueAtTime(0.0001, start + dur);
	osc.connect(amp).connect(master);
	osc.start(start);
	osc.stop(start + dur + 0.02);
}

function noise(at: number, dur: number, filter: BiquadFilterType, freq: number, gain = 0.25, sweepTo?: number): void {
	if (!ctx || !master) return;
	const start = ctx.currentTime + at;
	const length = Math.max(1, Math.floor(ctx.sampleRate * dur));
	const buffer = ctx.createBuffer(1, length, ctx.sampleRate);
	const data = buffer.getChannelData(0);
	for (let i = 0; i < length; i++) data[i] = Math.random() * 2 - 1;
	const source = ctx.createBufferSource();
	source.buffer = buffer;
	const shape = ctx.createBiquadFilter();
	shape.type = filter;
	shape.frequency.setValueAtTime(freq, start);
	if (sweepTo) shape.frequency.exponentialRampToValueAtTime(sweepTo, start + dur);
	const amp = ctx.createGain();
	amp.gain.setValueAtTime(gain, start);
	amp.gain.exponentialRampToValueAtTime(0.0001, start + dur);
	source.connect(shape).connect(amp).connect(master);
	source.start(start);
}

const C5 = 523.25;
const E5 = 659.25;
const G5 = 783.99;
const C6 = 1046.5;

const SOUNDS: Record<string, () => void> = {
	tap: () => tone(700, 0, 0.05, 'triangle', 0.16),
	pop: () => tone(380, 0, 0.11, 'sine', 0.3, 980),
	join: () => {
		tone(C5, 0, 0.09, 'triangle', 0.22);
		tone(G5, 0.08, 0.14, 'triangle', 0.22);
	},
	correct: () => [C5, E5, G5, C6].forEach((f, i) => tone(f, i * 0.075, 0.18, 'triangle', 0.24)),
	almost: () => {
		tone(440, 0, 0.13, 'sine', 0.22);
		tone(349, 0.12, 0.24, 'sine', 0.2);
	},
	tick: () => tone(1250, 0, 0.035, 'square', 0.05),
	go: () => {
		[C5, E5, G5].forEach((f) => tone(f, 0, 0.35, 'triangle', 0.16));
		tone(C6, 0.12, 0.4, 'triangle', 0.18);
	},
	coin: () => {
		tone(988, 0, 0.07, 'square', 0.07);
		tone(1319, 0.07, 0.2, 'square', 0.07);
	},
	dig: () => {
		noise(0, 0.16, 'lowpass', 700, 0.35);
		tone(140, 0, 0.12, 'sine', 0.25);
	},
	splash: () => {
		noise(0, 0.55, 'bandpass', 1800, 0.35, 280);
		tone(300, 0.02, 0.25, 'sine', 0.12, 120);
	},
	whoosh: () => noise(0, 0.4, 'highpass', 500, 0.18, 3200),
	kick: () => {
		tone(110, 0, 0.12, 'sine', 0.4, 60);
		noise(0, 0.07, 'lowpass', 900, 0.3);
	},
	goal: () => {
		noise(0, 1.1, 'bandpass', 900, 0.22, 1600);
		[C5, E5, G5].forEach((f, i) => tone(f, 0.08 + i * 0.09, 0.3, 'triangle', 0.18));
	},
	engine: () => tone(90, 0, 0.6, 'sawtooth', 0.05, 220),
	build: () => {
		tone(196, 0, 0.09, 'triangle', 0.3);
		tone(220, 0.14, 0.09, 'triangle', 0.3);
		noise(0, 0.05, 'lowpass', 1200, 0.2);
	},
	capture: () => {
		noise(0, 0.25, 'highpass', 800, 0.14, 2600);
		tone(E5, 0.15, 0.16, 'triangle', 0.2);
		tone(G5, 0.24, 0.2, 'triangle', 0.2);
	},
	steal: () => {
		tone(620, 0, 0.18, 'sine', 0.2, 1400);
		tone(1400, 0.18, 0.22, 'sine', 0.18, 500);
	},
	water: () => tone(1300, 0, 0.12, 'sine', 0.2, 520),
	harvest: () => {
		tone(G5, 0, 0.1, 'triangle', 0.22);
		tone(C6, 0.09, 0.22, 'triangle', 0.22);
		tone(1568, 0.2, 0.25, 'sine', 0.12);
	},
	key: () => [G5, C6, 1568].forEach((f, i) => tone(f, i * 0.09, 0.22, 'sine', 0.2)),
	fanfare: () => {
		const notes = [G5, G5, G5, C6, G5, C6];
		const times = [0, 0.12, 0.24, 0.42, 0.66, 0.8];
		notes.forEach((f, i) => tone(f, times[i], i === notes.length - 1 ? 0.6 : 0.14, 'triangle', 0.22));
	},
	sticker: () => tone(560, 0, 0.09, 'sine', 0.24, 1100),
	tiles: () => [E5, G5, C6].forEach((f, i) => tone(f, i * 0.05, 0.1, 'sine', 0.14)),
	wrongGuess: () => tone(260, 0, 0.18, 'sine', 0.2, 200)
};

export function play(name: keyof typeof SOUNDS | string): void {
	if (muted || !ctx || ctx.state !== 'running') return;
	SOUNDS[name]?.();
}
