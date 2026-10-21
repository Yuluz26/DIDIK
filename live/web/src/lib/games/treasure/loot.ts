// Names for what Pulau Harta Karun's sand hides; the art is in Loot.svelte.
export const LOOT_NAMES: Record<string, string> = {
	coins: 'Syiling',
	chest: 'Peti harta',
	gem: 'Permata',
	map: 'Peta harta',
	parrot: 'Burung kakak tua',
	crab: 'Ketam',
	sand: 'Pasir sahaja'
};

export function lootLine(found: { found: string; amount: number; from?: string | null }): string {
	const name = LOOT_NAMES[found.found] ?? 'Sesuatu';
	if (found.found === 'parrot') return found.from ? `Burung kakak tua mencuri ${found.amount} syiling untuk kamu!` : `Burung kakak tua membawa ${found.amount} syiling!`;
	if (found.found === 'crab') return found.amount ? `Aduh, ketam menyepit! ${found.amount} syiling.` : 'Ketam lalu sahaja. Fuh!';
	if (found.found === 'map') return `Peta harta! Syiling kamu berganda: +${found.amount}.`;
	return `Jumpa ${name.toLowerCase()}: +${found.amount} syiling.`;
}
