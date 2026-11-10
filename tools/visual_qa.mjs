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
fs.mkdirSync('qa/sections',{recursive:true});
const report=[];

const safe=s=>s.replace(/[^a-z0-9_-]+/gi,'-').replace(/-+/g,'-').replace(/^-|-$/g,'').slice(0,80);

for (const pageName of pages){
  for (const [label,width,height] of viewports){
    const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
    await page.emulateMedia({reducedMotion:'reduce'});
    page.setDefaultNavigationTimeout(15000);
    await page.goto('http://127.0.0.1:4173/'+pageName,{waitUntil:'domcontentloaded'});

    await page.evaluate(async()=>{
      document.querySelectorAll('img').forEach(img=>img.loading='eager');
      const step=Math.max(500,window.innerHeight*.8);
      for(let y=0;y<document.body.scrollHeight;y+=step){
        window.scrollTo(0,y);
        await new Promise(r=>setTimeout(r,45));
      }
      window.scrollTo(0,0);
      await new Promise(r=>setTimeout(r,500));
    });

    const metrics=await page.evaluate(({pageName,label,width,height})=>{
      const visible=el=>{
        const cs=getComputedStyle(el);
        const r=el.getBoundingClientRect();
        return cs.display!=='none'&&cs.visibility!=='hidden'&&r.width>0&&r.height>0;
      };
      const desc=el=>{
        const cls=(el.className&&typeof el.className==='string')?'.'+el.className.trim().split(/\s+/).slice(0,3).join('.'):'';
        return el.tagName.toLowerCase()+cls;
      };
      const clippedText=[];
      document.querySelectorAll('h1,h2,h3,h4,p,a,span,strong,small,blockquote,figcaption').forEach(el=>{
        if(!visible(el)||!el.textContent.trim())return;
        const cs=getComputedStyle(el);
        const clipped=(el.scrollHeight>el.clientHeight+2||el.scrollWidth>el.clientWidth+2) &&
          ['hidden','clip'].includes(cs.overflow) || ['hidden','clip'].includes(cs.overflowX) || ['hidden','clip'].includes(cs.overflowY);
        if(clipped) clippedText.push({el:desc(el),text:el.textContent.trim().slice(0,120),client:[el.clientWidth,el.clientHeight],scroll:[el.scrollWidth,el.scrollHeight]});
      });
      const offscreen=[];
      document.querySelectorAll('main *').forEach(el=>{
        if(!visible(el))return;
        const r=el.getBoundingClientRect();
        if(r.right>width+3||r.left<-3) offscreen.push({el:desc(el),left:Math.round(r.left),right:Math.round(r.right),w:Math.round(r.width)});
      });
      const images=[...document.images].map(img=>{
        const r=img.getBoundingClientRect(),cs=getComputedStyle(img);
        return {
          src:img.getAttribute('src')||'',
          ok:img.complete&&img.naturalWidth>0,
          natural:[img.naturalWidth,img.naturalHeight],
          rendered:[Math.round(r.width),Math.round(r.height)],
          objectFit:cs.objectFit,
          objectPosition:cs.objectPosition
        };
      });
      const sections=[...document.querySelectorAll('section')].map((s,i)=>{
        const r=s.getBoundingClientRect();
        return {i,cls:s.className,h:Math.round(r.height),w:Math.round(r.width)};
      });
      return {
        page:pageName,viewport:label,size:[width,height],
        doc:{scrollWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,scrollHeight:document.documentElement.scrollHeight},
        clippedText,
        offscreen:offscreen.slice(0,100),
        missingImages:images.filter(x=>!x.ok),
        images,
        sections
      };
    },{pageName,label,width,height});
    report.push(metrics);

    await page.screenshot({
      path:`qa/screenshots/${pageName.replace('.html','')}__${label}.jpg`,
      fullPage:true,type:'jpeg',quality:68
    });

    if(label==='desktop-1440'||label==='mobile-390'){
      const sections=page.locator('section');
      const count=await sections.count();
      for(let i=0;i<count;i++){
        const sec=sections.nth(i);
        await sec.scrollIntoViewIfNeeded();
        await page.waitForTimeout(90);
        const cls=await sec.getAttribute('class')||'section';
        await sec.screenshot({
          path:`qa/sections/${pageName.replace('.html','')}__${label}__${String(i).padStart(2,'0')}-${safe(cls)}.jpg`,
          type:'jpeg',quality:78
        });
      }
    }
    await page.close();
  }
}

fs.writeFileSync('qa/report.json',JSON.stringify(report,null,2));
await browser.close();
server.kill('SIGTERM');
