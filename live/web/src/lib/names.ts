// Avatars, colours and suggested nicknames. Mirrors live/server/didik_live/game/names.py.

export const ANIMALS: Record<string, string> = {
	kancil: 'Kancil',
	harimau: 'Harimau',
	penyu: 'Penyu',
	enggang: 'Enggang',
	gajah: 'Gajah',
	kucing: 'Kucing',
	arnab: 'Arnab',
	beruang: 'Beruang'
};

export const COLOURS: Record<string, string> = {
	jingga: '#f28c28',
	kuning: '#f5c518',
	hijau: '#3daa5c',
	biru: '#2f7fcf',
	ungu: '#8a5cd1',
	merah: '#e2483d',
	jambu: '#ec6ca5',
	teal: '#14958a'
};

// Skin tones for the chibi characters, chosen on the join screen.
export const SKINS: Record<string, string> = {
	s1: '#fde3d1',
	s2: '#f3c9a4',
	s3: '#dca57a',
	s4: '#b77a4d',
	s5: '#7e4e2c'
};

export const COLOUR_NAMES: Record<string, string> = {
	jingga: 'Jingga',
	kuning: 'Kuning',
	hijau: 'Hijau',
	biru: 'Biru',
	ungu: 'Ungu',
	merah: 'Merah',
	jambu: 'Merah jambu',
	teal: 'Hijau laut'
};

const ADJECTIVES = [
	'Ceria', 'Pantas', 'Bijak', 'Riang', 'Berani', 'Comel', 'Lincah', 'Gagah', 'Tenang', 'Ajaib',
	'Cergas', 'Hebat', 'Pelangi', 'Kilat', 'Mentari', 'Lucu', 'Rajin', 'Bintang', 'Sopan', 'Tangkas'
];

export function suggestName(animal: string, avoid = ''): string {
	const base = ANIMALS[animal] ?? 'Kancil';
	let name = avoid;
	while (name === avoid) {
		name = `${base} ${ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]}`;
	}
	return name;
}

export function randomOf<T>(items: T[]): T {
	return items[Math.floor(Math.random() * items.length)];
}

export const TEAM_COLOURS: Record<string, { name: string; colour: string; deep: string; soft: string }> = {
	harimau: { name: 'Pasukan Harimau', colour: '#f28c28', deep: '#b35f0c', soft: '#ffe3c4' },
	penyu: { name: 'Pasukan Penyu', colour: '#14958a', deep: '#0b665e', soft: '#c9efe9' }
};
