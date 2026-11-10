import { memo, sheetOf, type Sheet } from '$lib/pixel/cache';
import { Pix, noise, ramp, rgba } from '$lib/pixel/pix';

const wood = ramp(['#663b2f', '#92583a', '#bc7b4a', '#dba46a', '#f3c990'], '#422a2b');
const chairWood = ramp(['#53393a', '#795348', '#a87557', '#d3a273', '#efd0a0'], '#3d2c34');
const green = ramp(['#244942', '#356a58', '#4e8b6a', '#79b18a', '#b5d3a7'], '#243c3c');
export const CHAIR_COLOURS = [
	{ name: 'Merah jambu', seat: '#e997a6', light: '#ffd0d1' },
	{ name: 'Biru', seat: '#6dafe0', light: '#b8dcf4' },
	{ name: 'Kuning', seat: '#e6bc59', light: '#ffe5a0' },
	{ name: 'Hijau', seat: '#76b996', light: '#bce3b5' },
	{ name: 'Ungu', seat: '#a897d6', light: '#ddd0ef' },
	{ name: 'Jingga', seat: '#e99b60', light: '#ffd2a1' },
	{ name: 'Turkuois', seat: '#62b9b4', light: '#b8e6dc' },
	{ name: 'Merah', seat: '#dc7c78', light: '#ffc2b4' }
];

function desk(variant: number): Pix {
	const p = new Pix(32, 23);
	p.shadow(16, 21, 14, 2);
	p.rect(4, 12, 3, 8, wood.c[0], wood.ink).rect(25, 12, 3, 8, wood.c[0], wood.ink);
	p.box(2, 9, 28, 9, wood, 3);
	p.rect(2, 7, 28, 4, wood.c[4], wood.ink);
	p.hline(4, 8, 23, wood.c[3]);
	p.hline(5, 15, 22, wood.c[1]);
	p.rect(11, 12, 10, 3, wood.c[0]);
	// Books, pencil and a little exercise sheet make each desk feel used.
	p.rect(7, 4, 7, 3, variant % 3 === 0 ? rgba('#6ba6bf') : rgba('#efb37a'), rgba('#35485a'));
	p.hline(8, 5, 5, rgba('#fff6d8'));
	p.rect(19, 4, 7, 3, rgba('#f5eed9'), rgba('#9b8572'));
	p.hline(20, 5, 5, rgba('#b3a795'));
	p.line(24, 3, 28, 1, rgba('#d88a3e'));
	return p.outline();
}

function chair(variant: number): Pix {
	const p = new Pix(17, 20);
	const colour = CHAIR_COLOURS[variant % CHAIR_COLOURS.length];
	p.shadow(8, 18, 7, 1.5);
	p.rect(2, 1, 13, 9, chairWood.c[2], chairWood.ink);
	p.rect(3, 2, 11, 6, rgba(colour.seat), chairWood.ink);
	p.hline(4, 3, 9, rgba(colour.light));
	p.hline(2, 8, 13, chairWood.c[0]);
	p.box(1, 10, 15, 5, chairWood, 2);
	p.rect(3, 11, 11, 2, rgba(colour.seat));
	p.rect(3, 14, 3, 5, chairWood.c[0], chairWood.ink);
	p.rect(11, 14, 3, 5, chairWood.c[0], chairWood.ink);
	return p.outline();
}

function teacherDesk(): Pix {
	const p = new Pix(47, 28);
	p.shadow(23, 26, 20, 2);
	p.rect(4, 10, 39, 16, wood.c[1], wood.ink);
	p.box(2, 10, 43, 15, wood, 4);
	p.rect(2, 8, 43, 5, wood.c[4], wood.ink);
	p.hline(4, 9, 39, wood.c[3]);
	p.rect(7, 16, 10, 6, wood.c[0], wood.ink);
	p.rect(19, 15, 24, 2, wood.c[1]);
	p.rect(21, 4, 12, 4, rgba('#f8edd1'), rgba('#7b6c5b'));
	p.rect(35, 2, 5, 7, rgba('#b3d8c9'), rgba('#547067'));
	p.rect(36, 1, 3, 2, rgba('#fff1c4'));
	return p.outline();
}

function bookcase(): Pix {
	const p = new Pix(22, 39);
	p.shadow(11, 37, 9, 2);
	p.box(1, 1, 20, 36, wood, 3);
	for (const y of [8, 19, 30]) {
		p.rect(3, y, 16, 2, wood.c[4], wood.ink);
		for (let x = 4; x < 18; x += 3) {
			p.rect(x, y - 7, 2, 7, [rgba('#75a9aa'), rgba('#e58e72'), rgba('#e6c869'), rgba('#8cae80')][(x + y) % 4], wood.ink);
		}
	}
	return p.outline();
}

function plant(): Pix {
	const p = new Pix(18, 25);
	p.shadow(9, 23, 7, 1.5);
	p.rect(6, 13, 6, 10, rgba('#ca7758'), rgba('#633f40'));
	p.rect(4, 12, 10, 3, rgba('#e19a70'), rgba('#633f40'));
	p.vline(9, 4, 10, green.c[1]);
	for (const [x, y, rx, ry] of [[5, 9, 5, 3], [13, 7, 5, 3], [8, 3, 4, 4], [12, 11, 4, 2]] as const) p.blob(x, y, rx, ry, green, { rim: true });
	return p.outline();
}

export function classroomArt(kind: string, variant = 0): Sheet {
	return memo(`classroom:${kind}:${variant}`, () => sheetOf(kind === 'desk' ? desk(variant) : kind === 'chair' ? chair(variant) : kind === 'teacher' ? teacherDesk() : kind === 'bookcase' ? bookcase() : plant()));
}

export function classroomGround(): Pix {
	return memo('ground:classroom:v1', () => {
		const p = new Pix(256, 144);
		const c = {
			wall: rgba('#f0dcb2'), wallLight: rgba('#f8eac8'), wallShade: rgba('#d8bc91'),
			floor: rgba('#c99061'), floorLight: rgba('#e0ad75'), floorDark: rgba('#9a664c'),
			ink: rgba('#5d483d'), frame: rgba('#825e47'), chalk: rgba('#d9efcd'), board: rgba('#2d5a50')
		};
		// Plastered wall with a softly dithered window glow.
		p.rect(0, 0, 256, 51, (x, y) => {
			const glow = Math.max(0, 1 - Math.abs(x - 37) / 80);
			const n = noise(x, y, 41);
			return n < 0.025 ? c.wallShade : glow > 0.55 && n > 0.35 ? c.wallLight : c.wall;
		});
		p.rect(0, 45, 256, 6, c.wallShade);
		p.hline(0, 50, 256, c.ink);
		for (let y = 51; y < 144; y++) for (let x = 0; x < 256; x++) {
			const row = Math.floor((y - 51) / 13);
			const grain = noise(x, y, 83);
			const seam = (x + (row % 2) * 32) % 64;
			p.set(x, y, (y - 51) % 13 === 0 || seam === 0 ? c.floorDark : grain > 0.92 ? c.floorLight : grain < 0.06 ? c.floorDark : c.floor);
		}
		// Skirting board and board: a broad green chalk surface with real wood trim.
		p.rect(51, 6, 154, 38, c.frame, c.ink);
		p.rect(55, 9, 146, 30, c.board, c.ink);
		p.hline(54, 40, 149, c.floorLight);
		p.rect(76, 19, 22, 2, c.chalk);
		p.rect(78, 24, 18, 1, c.chalk);
		p.rect(155, 16, 22, 2, c.chalk);
		p.rect(160, 22, 17, 1, c.chalk);
		p.rect(108, 15, 40, 19, rgba('#f7e8c6'));
		p.rect(110, 17, 36, 15, rgba('#e9b869'));
		p.rect(114, 20, 28, 9, rgba('#fcf4d6'));
		// A side door gives arriving children a believable entrance.
		p.rect(8, 5, 31, 44, c.frame, c.ink);
		p.rect(11, 8, 25, 39, rgba('#b67855'), c.ink);
		p.rect(14, 11, 19, 13, rgba('#d69c6a'), c.floorDark);
		p.rect(14, 27, 19, 16, rgba('#c78a5e'), c.floorDark);
		p.rect(30, 29, 3, 3, rgba('#f4d887'));
		p.rect(7, 48, 34, 4, c.floorLight, c.ink);
		p.rect(11, 54, 31, 5, rgba('#9c7257'));
		// A sunlit window with a deep wooden sill.
		for (const x of [218]) {
			p.rect(x, 7, 30, 34, c.frame, c.ink);
			p.rect(x + 3, 10, 24, 27, rgba('#9acdd0'));
			p.rect(x + 4, 12, 22, 13, rgba('#bfe8e0'));
			p.vline(x + 14, 10, 27, c.wallLight);
			p.hline(x + 3, 25, 24, c.wallLight);
			p.rect(x - 2, 39, 34, 3, c.floorLight, c.ink);
		}
		// A woven classroom rug marks the teacher's area without hiding floor texture.
		p.rect(85, 53, 86, 20, rgba('#5f9a83'));
		p.rect(88, 55, 80, 16, rgba('#86b49b'));
		for (let x = 92; x < 166; x += 8) { p.rect(x, 56, 2, 2, rgba('#eac57e')); p.rect(x + 4, 68, 2, 2, rgba('#eac57e')); }
		return p;
	});
}
