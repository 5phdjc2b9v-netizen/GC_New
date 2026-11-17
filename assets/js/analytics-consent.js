/* GeoCenter GA4: consent-first, production-domain-only analytics. */
(function () {
  'use strict';
  const GA4_MEASUREMENT_ID = 'G-NBK3M2W9P7';
  if (!/^G-[A-Z0-9]+$/.test(GA4_MEASUREMENT_ID)) return;
  // Keep preview and temporary Pages URLs out of the production reporting.
  if (!['www.geocenter.de', 'geocenter.de'].includes(location.hostname)) return;

  const STORAGE_KEY = 'geocenter.analytics_consent.v1';
  const STYLE_ID = 'gc-analytics-consent-style';
  const CONSENT_ID = 'gc-analytics-consent';
  const loadGA4 = () => {
    if (window.__gcGaLoaded) return;
    window.__gcGaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA4_MEASUREMENT_ID, {
      anonymize_ip: true,
      send_page_view: true
    });
    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA4_MEASUREMENT_ID);
    document.head.appendChild(s);

    /* B2B conversion signals, without form field content or personal data. */
    document.addEventListener('click', function (e) {
      const link = e.target.closest('a[href]');
      if (!link) return;
      let destination;
      try { destination = new URL(link.getAttribute('href'), document.baseURI); }
      catch (_) { return; }
      const proto = destination.protocol;
      if (proto === 'mailto:') {
        window.gtag('event', 'contact_email_click', { event_category: 'lead', page_path: location.pathname });
      } else if (proto === 'tel:') {
        window.gtag('event', 'contact_phone_click', { event_category: 'lead', page_path: location.pathname });
      } else if (destination.pathname.toLowerCase().endsWith('.pdf')) {
        window.gtag('event', 'file_download', { file_extension: 'pdf', page_path: location.pathname });
      }
    });
  };

  const ensureStyles = () => {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = [
      '#gc-analytics-consent{position:fixed;z-index:99999;bottom:20px;left:20px;right:20px;max-width:600px;margin:auto;padding:20px 22px;border:1px solid #e4ded5;border-radius:16px;background:#fff;color:#221f1c;box-shadow:0 18px 55px rgba(0,0,0,.2);font:15px/1.5 system-ui,sans-serif}',
      '#gc-analytics-consent strong{display:block;font-size:18px;margin-bottom:5px}',
      '#gc-analytics-consent p{margin:0 0 14px}',
      '#gc-analytics-consent .gc-consent-actions{display:flex;gap:10px;flex-wrap:wrap}',
      '#gc-analytics-consent button{border:1px solid #242424;border-radius:8px;padding:10px 15px;cursor:pointer;font:inherit;background:white;color:#222}',
      '#gc-analytics-consent button.gc-accept{background:#222;color:#fff}',
      '#gc-analytics-consent a{color:inherit;text-decoration:underline}'
    ].join('');
    document.head.appendChild(style);
  };
  const getConsent = () => {
    try { return localStorage.getItem(STORAGE_KEY); } catch (_) { return null; }
  };
  const setConsent = (value) => {
    try { localStorage.setItem(STORAGE_KEY, value); } catch (_) { /* no persisted choice */ }
    document.getElementById(CONSENT_ID)?.remove();
    if (value === 'accepted') loadGA4();
  };
  const showBanner = () => {
    if (document.getElementById(CONSENT_ID)) return;
    ensureStyles();
    const el = document.createElement('aside');
    el.id = CONSENT_ID;
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-label', 'Analyse-Cookies');
    el.innerHTML = '<strong>Website-Analyse</strong><p>Wir möchten mit Google Analytics nachvollziehen, wie unsere Website genutzt wird. Die Analyse ist freiwillig und startet nur mit Ihrer Zustimmung. <a href="/datenschutz">Datenschutz</a></p><div class="gc-consent-actions"><button type="button" data-analytics-consent="reject">Ablehnen</button><button type="button" class="gc-accept" data-analytics-consent="accept">Zustimmen</button></div>';
    el.addEventListener('click', function (e) {
      const val = e.target.closest('button[data-analytics-consent]')?.dataset.analyticsConsent;
      if (val === 'accept') setConsent('accepted');
      if (val === 'reject') setConsent('rejected');
    });
    document.body.appendChild(el);
  };
  const addPreferencesControl = () => {
    const footer = document.querySelector('footer');
    if (!footer) return;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = 'Analyse-Einstellungen';
    btn.setAttribute('aria-label', 'Analyse-Einwilligung ändern');
    btn.style.cssText = 'background:transparent;border:0;color:inherit;text-decoration:underline;cursor:pointer;font:inherit;padding:8px';
    btn.addEventListener('click', function () {
      // Immediately stop tracking requests by reloading without stored consent.
      try { localStorage.removeItem(STORAGE_KEY); } catch (_) {}
      // Remove first-party GA cookies when consent is withdrawn.
      document.cookie.split(';').forEach(function (part) {
        const name = part.trim().split('=')[0];
        if (/^_ga(?:_|$)/.test(name)) {
          document.cookie = name + '=; Max-Age=0; path=/; SameSite=Lax';
          document.cookie = name + '=; Max-Age=0; path=/; domain=.geocenter.de; SameSite=Lax';
        }
      });
      location.reload();
    });
    footer.appendChild(btn);
  };
  const start = () => {
    const choice = getConsent();
    if (choice === 'accepted') loadGA4();
    else if (choice !== 'rejected') showBanner();
    addPreferencesControl();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
