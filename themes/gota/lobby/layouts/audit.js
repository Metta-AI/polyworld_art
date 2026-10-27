// Record the exact text sizes, font loading, image loading and layout bounds.
window.addEventListener('load', async () => {
  await document.fonts.ready;
  const textElements = [...document.querySelectorAll('body *')].filter(el =>
    el.tagName !== 'SCRIPT' && el.tagName !== 'STYLE' &&
    (el.matches('input, select, textarea') ||
      [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())));
  const sizes = [...new Set(textElements.map(el => getComputedStyle(el).fontSize))].sort((a, b) => parseFloat(a) - parseFloat(b));
  const clipped = textElements.filter(el => el.clientWidth &&
    (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1))
    .map(el => ({ text: el.textContent.trim(), width: el.clientWidth, scrollWidth: el.scrollWidth }));
  const missingImages = [...document.images].filter(im => !im.complete || !im.naturalWidth).map(im => im.getAttribute('src'));
  const bounds = [...document.querySelectorAll('.panel, .footer, .header')].map(el => {
    const r = el.getBoundingClientRect();
    return { class: el.className, x: r.x, y: r.y, width: r.width, height: r.height };
  });
  const result = { sizes, fontsLoaded: document.fonts.check('20px Rubik') && document.fonts.check('700 48px Rubik'), clipped, missingImages, bounds };
  const audit = document.createElement('script');
  audit.id = 'layout-audit';
  audit.type = 'application/json';
  audit.textContent = JSON.stringify(result);
  document.body.appendChild(audit);
});
