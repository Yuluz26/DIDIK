// Every sound is synthesised with the Web Audio API, in the chiptune style of the pictures: no audio files
// to download, nothing to license, and it works offline. Browsers only allow sound after a tap, so `unlock()` runs on the first one.

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

// The sounds are chiptune: square and triangle voices that start at once and stop short, pitch
// slides that climb in steps of a semitone, and noise that crunches (random values held for a few
// samples) instead of hissing. A square wave carries more energy than a sine, so it is turned down.
const SQUARE = 0.55;

function semitones(freq: number, to: number, steps: number): number[] {
	const from = Math.round(12 * Math.log2(freq / 440));
	const end = Math.round(12 * Math.log2(to / 440));
	return Array.from({ length: steps }, (_, i) => 440 * 2 ** ((from + Math.round(((end - from) * i) / Math.max(1, steps - 1))) / 12));
}

function tone(freq: number, at: number, dur: number, wave: Wave = 'square', gain = 0.25, slideTo?: number): void {
	if (!ctx || !master) return;
	const start = ctx.currentTime + at;
	const osc = ctx.createOscillator();
	const amp = ctx.createGain();
	osc.type = wave === 'sine' ? 'triangle' : wave;
	if (slideTo) {
		const steps = Math.max(3, Math.round(dur / 0.014));
		semitones(freq, slideTo, steps).forEach((f, i) => osc.frequency.setValueAtTime(f, start + (dur * i) / steps));
	} else osc.frequency.setValueAtTime(freq, start);
	const level = osc.type === 'square' ? gain * SQUARE : gain;
	amp.gain.setValueAtTime(0.0001, start);
	amp.gain.linearRampToValueAtTime(level, start + 0.004);
	amp.gain.setValueAtTime(level, start + dur * 0.55);
	amp.gain.linearRampToValueAtTime(0.0001, start + dur);
	osc.connect(amp).connect(master);
	osc.start(start);
	osc.stop(start + dur + 0.02);
}

function noise(at: number, dur: number, filter: BiquadFilterType, freq: number, gain = 0.25, sweepTo?: number, hold = 3): void {
	if (!ctx || !master) return;
	const start = ctx.currentTime + at;
	const length = Math.max(1, Math.floor(ctx.sampleRate * dur));
	const buffer = ctx.createBuffer(1, length, ctx.sampleRate);
	const data = buffer.getChannelData(0);
	for (let i = 0; i < length; i++) data[i] = i % hold === 0 ? Math.random() * 2 - 1 : data[i - 1];
	const source = ctx.createBufferSource();
	source.buffer = buffer;
	const shape = ctx.createBiquadFilter();
	shape.type = filter;
	shape.frequency.setValueAtTime(freq, start);
	if (sweepTo) shape.frequency.exponentialRampToValueAtTime(sweepTo, start + dur);
	const amp = ctx.createGain();
	amp.gain.setValueAtTime(gain, start);
	amp.gain.linearRampToValueAtTime(0.0001, start + dur);
	source.connect(shape).connect(amp).connect(master);
	source.start(start);
}

const C5 = 523.25;
const E5 = 659.25;
const G5 = 783.99;
const C6 = 1046.5;

const SOUNDS: Record<string, () => void> = {
	tap: () => tone(880, 0, 0.04, 'square', 0.14),
	pop: () => tone(392, 0, 0.1, 'square', 0.22, 988),
	join: () => {
		tone(C5, 0, 0.07, 'square', 0.2);
		tone(G5, 0.07, 0.12, 'square', 0.2);
	},
	correct: () => [C5, E5, G5, C6].forEach((f, i) => tone(f, i * 0.065, 0.12, 'square', 0.22)),
	almost: () => {
		tone(440, 0, 0.11, 'triangle', 0.26);
		tone(349, 0.11, 0.22, 'triangle', 0.26);
	},
	tick: () => tone(1250, 0, 0.025, 'square', 0.07),
	go: () => {
		[C5, E5, G5].forEach((f) => tone(f, 0, 0.3, 'square', 0.12));
		tone(C6, 0.12, 0.36, 'square', 0.14);
	},
	coin: () => {
		tone(988, 0, 0.06, 'square', 0.12);
		tone(1319, 0.06, 0.2, 'square', 0.12);
	},
	dig: () => {
		noise(0, 0.14, 'lowpass', 900, 0.4, undefined, 6);
		tone(140, 0, 0.1, 'triangle', 0.3, 70);
	},
	splash: () => {
		noise(0, 0.14, 'bandpass', 2200, 0.35, 900, 2);
		noise(0.14, 0.16, 'bandpass', 1500, 0.28, 500, 3);
		noise(0.3, 0.2, 'bandpass', 900, 0.2, 300, 5);
	},
	whoosh: () => noise(0, 0.34, 'highpass', 500, 0.2, 3200, 2),
	kick: () => {
		tone(130, 0, 0.12, 'triangle', 0.5, 45);
		noise(0, 0.06, 'lowpass', 1100, 0.3, undefined, 4);
	},
	goal: () => {
		noise(0, 0.9, 'bandpass', 900, 0.2, 1600, 3);
		[C5, E5, G5, C6].forEach((f, i) => tone(f, 0.08 + i * 0.09, 0.22, 'square', 0.18));
	},
	engine: () => tone(80, 0, 0.5, 'square', 0.08, 200),
	build: () => {
		tone(196, 0, 0.08, 'square', 0.22);
		tone(262, 0.1, 0.1, 'square', 0.22);
		noise(0, 0.05, 'lowpass', 1400, 0.2, undefined, 5);
	},
	capture: () => {
		noise(0, 0.2, 'highpass', 800, 0.14, 2600, 2);
		tone(E5, 0.14, 0.1, 'square', 0.18);
		tone(G5, 0.22, 0.16, 'square', 0.18);
	},
	steal: () => {
		tone(620, 0, 0.16, 'square', 0.16, 1400);
		tone(1400, 0.16, 0.2, 'square', 0.16, 500);
	},
	water: () => tone(1300, 0, 0.1, 'square', 0.14, 520),
	harvest: () => {
		tone(G5, 0, 0.08, 'square', 0.18);
		tone(C6, 0.08, 0.1, 'square', 0.18);
		tone(1568, 0.18, 0.22, 'square', 0.14);
	},
	key: () => [G5, C6, 1568].forEach((f, i) => tone(f, i * 0.08, 0.14, 'square', 0.16)),
	fanfare: () => {
		const notes = [G5, G5, G5, C6, G5, C6];
		const times = [0, 0.12, 0.24, 0.42, 0.66, 0.8];
		notes.forEach((f, i) => tone(f, times[i], i === notes.length - 1 ? 0.55 : 0.1, 'square', 0.2));
	},
	sticker: () => tone(560, 0, 0.09, 'square', 0.16, 1100),
	tiles: () => [E5, G5, C6].forEach((f, i) => tone(f, i * 0.05, 0.08, 'square', 0.12)),
	wrongGuess: () => tone(260, 0, 0.16, 'triangle', 0.26, 190)
};

export function play(name: keyof typeof SOUNDS | string): void {
	if (muted || !ctx || ctx.state !== 'running') return;
	SOUNDS[name]?.();
}
