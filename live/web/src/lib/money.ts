// Malaysian money, written as a child reads it: "50 sen", "RM2", "RM2.50".

export function ringgit(sen: number): string {
	if (sen < 100) return `${sen} sen`;
	const whole = Math.floor(sen / 100);
	const rest = sen % 100;
	return rest ? `RM${whole}.${String(rest).padStart(2, '0')}` : `RM${whole}`;
}

/** Coins are round, notes are long: what each piece of money looks like. */
export function moneyLook(sen: number): { kind: 'coin' | 'note'; fill: string; edge: string; ink: string; size: number } {
	switch (sen) {
		case 5:
			return { kind: 'coin', fill: '#e3e6ea', edge: '#a8b0b8', ink: '#4a525a', size: 2.6 };
		case 10:
			return { kind: 'coin', fill: '#e8eaee', edge: '#a3abb4', ink: '#4a525a', size: 2.9 };
		case 20:
			return { kind: 'coin', fill: '#f1d98b', edge: '#c9a63e', ink: '#5e4a10', size: 3.2 };
		case 50:
			return { kind: 'coin', fill: '#eceef1', edge: '#c9a63e', ink: '#4a525a', size: 3.5 };
		case 100:
			return { kind: 'note', fill: '#9fc4ef', edge: '#4f86c9', ink: '#123a6b', size: 0 };
		case 500:
			return { kind: 'note', fill: '#a8dfa0', edge: '#4f9a45', ink: '#1d4a17', size: 0 };
		case 1000:
			return { kind: 'note', fill: '#f2a6a0', edge: '#c9574d', ink: '#5e1712', size: 0 };
		default:
			return { kind: 'note', fill: '#9fdcd0', edge: '#3c9a88', ink: '#12463d', size: 0 };
	}
}
