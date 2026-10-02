const menu=document.querySelector('.menu-btn');
const nav=document.querySelector('.nav');
if(menu&&nav){
  menu.addEventListener('click',()=>{
    nav.classList.toggle('open');
    menu.setAttribute('aria-expanded',nav.classList.contains('open'));
  });
}

const reduceMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if(!reduceMotion){
  document.documentElement.classList.add('motion-enabled');

  const revealTargets=[
    ...document.querySelectorAll('.section-kicker,.story-grid,.category,.service-row,.history-band,.partner-band,.cta-inner,.info-card,.market-card,.timeline article')
  ];
  revealTargets.forEach((el,i)=>{
    el.classList.add('reveal');
    el.style.setProperty('--reveal-delay',Math.min((i%6)*55,275)+'ms');
  });

  const io=new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  },{threshold:.14,rootMargin:'0px 0px -6% 0px'});
  revealTargets.forEach(el=>io.observe(el));

  const heroTiles=[...document.querySelectorAll('.hero-visual .tile')];
  const heroVisual=document.querySelector('.hero-visual');
  if(heroVisual&&heroTiles.length){
    heroVisual.addEventListener('pointermove',(e)=>{
      const rect=heroVisual.getBoundingClientRect();
      const x=(e.clientX-rect.left)/rect.width-.5;
      const y=(e.clientY-rect.top)/rect.height-.5;
      heroTiles.forEach((tile,index)=>{
        const depth=(index+1)*3;
        tile.style.transform=`translate3d(${x*depth}px,${y*depth}px,0) rotate(${x*(index===0?-.35:.35)}deg)`;
      });
    });
    heroVisual.addEventListener('pointerleave',()=>heroTiles.forEach(tile=>tile.style.transform=''));
  }

  const counters=[...document.querySelectorAll('.fact strong')];
  const counterObserver=new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
      if(!entry.isIntersecting)return;
      const el=entry.target;
      const original=el.textContent.trim();
      const match=original.match(/^([\d.,]+)(.*)$/);
      if(!match){counterObserver.unobserve(el);return;}
      const numeric=match[1].replace(/\./g,'').replace(',','.');
      const target=parseFloat(numeric);
      if(!Number.isFinite(target)){counterObserver.unobserve(el);return;}
      const suffix=match[2];
      const duration=1100;
      const start=performance.now();
      const decimals=match[1].includes(',')?1:0;
      const step=(now)=>{
        const p=Math.min((now-start)/duration,1);
        const eased=1-Math.pow(1-p,3);
        const value=target*eased;
        if(original.includes('.')){
          el.textContent=Math.round(value).toLocaleString('de-DE')+suffix;
        }else{
          el.textContent=(decimals?value.toFixed(decimals).replace('.',','):Math.round(value))+suffix;
        }
        if(p<1)requestAnimationFrame(step);else el.textContent=original;
      };
      requestAnimationFrame(step);
      counterObserver.unobserve(el);
    });
  },{threshold:.6});
  counters.forEach(el=>counterObserver.observe(el));

  const header=document.querySelector('.site-header');
  let lastY=window.scrollY;
  let ticking=false;
  window.addEventListener('scroll',()=>{
    if(ticking)return;
    ticking=true;
    requestAnimationFrame(()=>{
      const y=window.scrollY;
      header?.classList.toggle('is-scrolled',y>20);
      header?.classList.toggle('is-hidden',y>lastY&&y>180);
      lastY=y;
      ticking=false;
    });
  },{passive:true});
}
