import { chromium } from 'playwright-core';
import fs from 'fs';
import { spawn } from 'child_process';

const server=spawn('python3',['-m','http.server','4173','--bind','127.0.0.1'],{stdio:'ignore'});
await new Promise(r=>setTimeout(r,1200));

const browser=await chromium.launch({
  headless:true,
  executablePath:'/usr/bin/google-chrome',
  args:['--no-sandbox','--disable-dev-shm-usage']
});

const pages=['index.html','leistungen.html','programm.html','unternehmen.html','kontakt.html'];
const viewports=[
  ['desktop-2560',2560,1440],
  ['desktop-1440',1440,1000],
  ['tablet-768',768,1024],
  ['mobile-390',390,844]
];
fs.mkdirSync('qa/screenshots',{recursive:true});

for (const pageName of pages){
  for (const [label,width,height] of viewports){
    const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
    page.setDefaultNavigationTimeout(15000);
    await page.goto('http://127.0.0.1:4173/'+pageName,{waitUntil:'domcontentloaded'});
    await page.waitForTimeout(1200);
    await page.evaluate(()=>window.scrollTo(0,0));
    await page.screenshot({
      path:`qa/screenshots/${pageName.replace('.html','')}__${label}.png`,
      fullPage:true
    });
    await page.close();
  }
}

await browser.close();
server.kill('SIGTERM');
