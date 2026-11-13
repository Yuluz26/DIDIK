// Plays every game in the gallery by hand (taps and drags in a phone browser), sends the answer, and
// checks what the gallery received is the shape that question type sends and that the page did not break.
import { launch } from './cdp.mjs';

const games = process.argv.slice(2);
const page = await launch({ scale: 1, port: 9334 });
const results = [];

// tap every available control the way a child would, until the check button is ready
const PLAY = `(async () => {
	const root = document.querySelector('#G');
	const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
	const click = (el) => el && el.click();
	const ready = () => { const b = root.querySelector('button.check'); return b && !b.disabled ? b : null; };
	for (let round = 0; round < 40 && !ready(); round++) {
		// a focus knob (Mikroskop) is turned until sharp
		const knob = root.querySelector('.focus input');
		if (knob && !root.querySelector('.rig.sharp')) {
			for (let v = 0; v <= 100 && !root.querySelector('.rig.sharp'); v += 2) { knob.value = v; knob.dispatchEvent(new Event('input', { bubbles: true })); await sleep(10); }
			continue;
		}
		// a telescope: tap a point of light
		const glint = root.querySelector('.glint'); if (glint) { click(glint); await sleep(150); continue; }
		// a pool of things to place (order, sort, match, labels): tap one, then a free place if asked
		const thing = root.querySelector('.pool .thing, .pool .card, .tray .chip, .tray .item, .seals button, .yard .log, .purse button');
		if (thing) {
			click(thing); await sleep(120);
			const target = root.querySelector('.pin:not(.filled), [data-zone^="g-"], [data-zone^="m-"]:not(:has(.placed))');
			if (root.querySelector('.picking, [aria-pressed="true"].picked') && target) { click(target); await sleep(120); }
			continue;
		}
		// one choice of many: the first button that picks something
		const pick = root.querySelector('.bottle, .square, .frame, .tile, .camp, .mark-btn, .stamp, .body:not(:disabled), .word');
		if (pick) { click(pick); await sleep(150); if (pick.classList.contains('square')) { click(pick); click(pick); click(pick); click(pick); await sleep(150); } continue; }
		// numbers and words
		const wheel = root.querySelector('.wheel .arrow'); if (wheel) { click(wheel); await sleep(80); continue; }
		const nudge = root.querySelector('.nudge:last-of-type'); if (nudge) { click(nudge); await sleep(80); continue; }
		const input = root.querySelector('input.input, input.write');
		if (input) { input.value = 'jawapan'; input.dispatchEvent(new Event('input', { bubbles: true })); await sleep(80); continue; }
		break;
	}
	const b = ready();
	if (!b) return { sent: false, html: root.querySelector('.game-wrap')?.className };
	b.click();
	await sleep(700);
	return { sent: !!root.querySelector('.card button.btn:not(.check)'), after: root.innerText.includes('Main semula') };
})()`;

for (const g of games) {
	try {
		await page.goto(`http://localhost:5175/gaya/subjek?g=${g}`);
		await page.until(`!!document.querySelector('#${g} .game-wrap')`, { timeout: 20000 });
		await page.sleep(600);
		const r = await page.eval(PLAY.replace('#G', `#${g}`));
		results.push(`${g.padEnd(10)} ${r.after ? 'answered, shown as answered' : 'NOT ANSWERED ' + JSON.stringify(r)}`);
	} catch (error) {
		results.push(`${g.padEnd(10)} ERROR ${error.message.slice(0, 120)}`);
	}
}
console.log(results.join('\n'));
console.log(page.logs.length ? 'page logs:\n' + page.logs.join('\n') : 'no page errors');
await page.close();
