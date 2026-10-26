/** Capture the real DIDIK Story Mode canvases using Chromium. Run from live/web. */
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const folder = '../../screenshots/story-mode';
await mkdir(folder, {recursive:true});
const browser = await chromium.launch({headless:true,args:['--no-sandbox']});
const page = await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1.5, reducedMotion:'reduce'});
const names = ['tasik-chini','batang-lupar','hutan-larut','rimba-bayangan','gunung-ledang'];
try {
  await page.goto('http://127.0.0.1:5173/',{waitUntil:'networkidle',timeout:60000});
  const section = page.locator('#legenda');
  await section.waitFor({state:'visible'});
  await section.scrollIntoViewIfNeeded();
  const buttons = section.locator('.realms button');
  for(let i=0;i<5;i++){
    await buttons.nth(i).click();
    await page.waitForTimeout(450);
    await section.locator('.preview').screenshot({path:folder+'/'+String(i+1).padStart(2,'0')+'-'+names[i]+'.png',animations:'disabled'});
    console.log('Captured genuine 8-bit world:', names[i]);
  }
  await page.setViewportSize({width:390,height:844});
  await section.scrollIntoViewIfNeeded();
  await buttons.first().click();
  await page.waitForTimeout(350);
  await section.screenshot({path:folder+'/mobile-story-mode.png',animations:'disabled'});
}finally{
  await browser.close();
}
