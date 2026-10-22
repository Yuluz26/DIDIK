// What a chest held, in words: under the result on a phone, and as the label over an opened chest.

import type { Person } from '$lib/types';

export interface Reward {
	kind: string;
	amount?: number;
	gain?: number;
	other?: string | null;
	alone?: boolean;
}

export function chestLabel(found: { kind: string; amount?: number }): string {
	switch (found.kind) {
		case 'emas':
		case 'besar':
			return `+${found.amount ?? 0}`;
		case 'ganda':
			return 'Ganda dua';
		case 'curi':
			return 'Rampas';
		case 'tukar':
			return 'Tukar';
		case 'ribut':
			return 'Ribut';
		default:
			return '';
	}
}

export function rewardLine(reward: Reward, people: Map<string, Person>): string {
	const gain = reward.gain ?? 0;
	const name = reward.other ? (people.get(reward.other)?.name ?? 'kapal lain') : '';
	switch (reward.kind) {
		case 'chest':
			return 'Pilih satu daripada tiga peti!';
		case 'emas':
		case 'besar':
			return reward.alone ? `Tiada kapal lain untuk dirompak, jadi +${gain} emas.` : `+${gain} emas!`;
		case 'ganda':
			return `Emas kamu berganda: +${gain}!`;
		case 'curi':
			return `Kamu merampas ${gain} emas daripada ${name}!`;
		case 'tukar':
			if (!reward.other) return 'Kamu tidak jadi bertukar.';
			return gain >= 0 ? `Bertukar emas dengan ${name}: +${gain}!` : `Bertukar emas dengan ${name}: ${gain}.`;
		case 'ribut':
			return gain < 0 ? `Ribut! ${-gain} emas hanyut ke laut.` : 'Ribut melanda, tetapi tiada emas untuk hanyut.';
		default:
			return '';
	}
}
