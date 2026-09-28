const year = document.querySelector('#year');
if (year) year.textContent = `© ${new Date().getFullYear()}`;

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const reveals = document.querySelectorAll('.reveal');

if (reducedMotion || !('IntersectionObserver' in window)) {
  reveals.forEach((el) => el.classList.add('is-visible'));
} else {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -36px 0px' });
  reveals.forEach((el) => observer.observe(el));
}

if (!reducedMotion) {
  const hero = document.querySelector('.hero');
  const root = document.documentElement;
  if (hero) {
    hero.addEventListener('pointermove', (event) => {
      const rect = hero.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      root.style.setProperty('--gx', `${x * 14}px`);
      root.style.setProperty('--gy', `${y * 10}px`);
      root.style.setProperty('--cx', `${x * -10}px`);
      root.style.setProperty('--cy', `${y * -6}px`);
    }, { passive: true });

    hero.addEventListener('pointerleave', () => {
      root.style.setProperty('--gx', '0px');
      root.style.setProperty('--gy', '0px');
      root.style.setProperty('--cx', '0px');
      root.style.setProperty('--cy', '0px');
    });
  }
}
