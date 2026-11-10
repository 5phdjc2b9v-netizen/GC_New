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
    ...document.querySelectorAll('.section-kicker,.story-grid,.category,.service-row,.history-band,.partner-band,.cta-inner,.info-card,.market-card,.timeline article,.portfolio-world,.portfolio-discovery,.globe-copy,.history-card,.history-mini-timeline,.geokatalog-grid,.subhero-register,.services-principle-grid,.services-section-head,.services-sales-grid,.services-feedback-top,.feedback-questions,.services-backoffice-intro,.service-words,.services-logistics-grid,.services-more-grid,.services-final-links')
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


  const productScenes=[...document.querySelectorAll('[data-product-scene]')];
  productScenes.forEach(scene=>{
    const products=[...scene.querySelectorAll('.product[data-depth]')];
    if(!products.length)return;
    scene.addEventListener('pointermove',(e)=>{
      const rect=scene.getBoundingClientRect();
      const x=(e.clientX-rect.left)/rect.width-.5;
      const y=(e.clientY-rect.top)/rect.height-.5;
      products.forEach(product=>{
        if(product.matches(':hover'))return;
        const depth=parseFloat(product.dataset.depth||'1');
        product.style.translate=`${x*9*depth}px ${y*7*depth}px`;
      });
    });
    scene.addEventListener('pointerleave',()=>products.forEach(product=>product.style.translate=''));
  });

  const globe=document.querySelector('[data-parallax-globe]');
  if(globe){
    let globeTicking=false;
    const updateGlobe=()=>{
      const rect=globe.parentElement.getBoundingClientRect();
      const viewport=window.innerHeight||1;
      const progress=Math.max(-1,Math.min(1,(viewport/2-(rect.top+rect.height/2))/(viewport*.78)));
      const mobile=window.matchMedia('(max-width: 760px)').matches;
      const strength=mobile?42:64;
      const scale=mobile?1.08:1.10;
      globe.style.transform=`scale(${scale}) translate3d(0,${progress*strength}px,0)`;
      globeTicking=false;
    };
    const requestGlobeUpdate=()=>{
      if(globeTicking)return;
      globeTicking=true;
      requestAnimationFrame(updateGlobe);
    };
    updateGlobe();
    window.addEventListener('scroll',requestGlobeUpdate,{passive:true});
    window.addEventListener('resize',requestGlobeUpdate,{passive:true});
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

  // Global scroll depth and parallax layer
  const parallaxMedia=[
    ...document.querySelectorAll(
      '.story-media-boutique,.about-hero-media,.about-photo-break figure,.leadership-scene'
    )
  ];
  parallaxMedia.forEach(el=>el.classList.add('scroll-parallax-media'));

  const catalogParallax=[...document.querySelectorAll('.catalog-card')];
  catalogParallax.forEach(el=>el.classList.add('scroll-parallax-cover'));

  const depthLightTargets=[
    ...document.querySelectorAll('.portfolio-world,.history-card,.topic-tile')
  ];

  const heroGeometry=document.querySelector('.hero-book-geometry');

  const clamp=(min,value,max)=>Math.max(min,Math.min(max,value));
  let depthTicking=false;

  const updateScrollDepth=()=>{
    const viewport=window.innerHeight||1;

    parallaxMedia.forEach((el,index)=>{
      const rect=el.getBoundingClientRect();
      if(rect.bottom<-180||rect.top>viewport+180)return;
      const center=rect.top+rect.height/2;
      const progress=clamp(-1,(viewport/2-center)/(viewport*.72),1);
      const strength=index===0?18:14;
      el.style.setProperty('--parallax-y',`${progress*strength}px`);
    });

    catalogParallax.forEach(el=>{
      const rect=el.getBoundingClientRect();
      if(rect.bottom<-140||rect.top>viewport+140)return;
      const center=rect.top+rect.height/2;
      const progress=clamp(-1,(viewport/2-center)/(viewport*.78),1);
      el.style.setProperty('--cover-parallax-y',`${progress*7}px`);
    });

    depthLightTargets.forEach((el,index)=>{
      const rect=el.getBoundingClientRect();
      if(rect.bottom<-180||rect.top>viewport+180)return;
      const center=rect.top+rect.height/2;
      const progress=clamp(-1,(viewport/2-center)/(viewport*.75),1);
      const x=50+progress*(index%2===0?9:-9);
      const y=50-progress*11;
      el.style.setProperty('--depth-light-x',`${x}%`);
      el.style.setProperty('--depth-light-y',`${y}%`);
    });

    if(heroGeometry){
      const rect=heroGeometry.getBoundingClientRect();
      const center=rect.top+rect.height/2;
      const progress=clamp(-1,(viewport/2-center)/(viewport*.8),1);
      heroGeometry.style.setProperty('--hero-spine-1',`${progress*-8}px`);
      heroGeometry.style.setProperty('--hero-spine-2',`${progress*5}px`);
      heroGeometry.style.setProperty('--hero-spine-3',`${progress*-4}px`);
      heroGeometry.style.setProperty('--hero-spine-4',`${progress*7}px`);
      heroGeometry.style.setProperty('--hero-spine-5',`${progress*-6}px`);
    }

    depthTicking=false;
  };

  const requestDepthUpdate=()=>{
    if(depthTicking)return;
    depthTicking=true;
    requestAnimationFrame(updateScrollDepth);
  };

  updateScrollDepth();
  window.addEventListener('scroll',requestDepthUpdate,{passive:true});
  window.addEventListener('resize',requestDepthUpdate,{passive:true});

}
