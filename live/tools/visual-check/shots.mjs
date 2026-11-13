// node shots.mjs <outdir> <states: play,right,wrong,host> <game...>
// Screenshots of the dev gallery's card for each game, at phone size, in each state asked for.
// Also reports anything wider than the phone and any error the page logged.
import { launch } from './cdp.mjs';

const [out, statesArg, ...games] = process.argv.slice(2);
const states = statesArg.split(',');
const port = Number(process.env.PORT || 5175);
const width = Number(process.env.WIDTH || 390);
const page = await launch({ width, height: 844, scale: Number(process.env.SCALE || 1.5) });
const problems = [];
for (const game of games) {
	for (const state of states) {
		const url = `http://localhost:${port}/gaya/subjek?g=${game}${state === 'play' ? '' : `&state=${state}`}`;
		try {
			await page.goto(url);
			await page.until(`!!document.querySelector('#${game} .game-wrap')`, { timeout: 20000 });
			// let lazy pictures and entrance animations finish
			await page.until(`[...document.querySelectorAll('#${game} img')].every((i) => i.complete)`, { timeout: 15000 }).catch(() => problems.push(`${game}/${state}: pictures still loading`));
			await page.sleep(Number(process.env.SETTLE || 900));
			const wide = await page.eval(`document.documentElement.scrollWidth > innerWidth + 1 ? document.documentElement.scrollWidth : 0`);
			if (wide) problems.push(`${game}/${state}: page is ${wide}px wide`);
			const broken = await page.eval(`[...document.querySelectorAll('#${game} img')].filter((i) => !i.naturalWidth && getComputedStyle(i).display !== 'none').map((i) => i.getAttribute('src'))`);
			if (broken.length) problems.push(`${game}/${state}: broken pictures ${broken.join(', ')}`);
			await page.shot(`${out}/${game}${state === 'play' ? '' : '-' + state}.png`, { selector: `#${game} .card`, margin: 6 });
		} catch (error) {
			problems.push(`${game}/${state}: ${error.message}`);
		}
	}
}
for (const line of page.logs.splice(0)) problems.push('log: ' + line);
await page.close();
console.log(problems.length ? problems.join('\n') : 'no problems');
