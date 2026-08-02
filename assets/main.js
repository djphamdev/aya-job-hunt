// AYA Search Job Hunt - Interactive Features (Clean - No PII)
(function() {
  'use strict';

  // ===== Theme Toggle (dark default) =====
  const THEME_KEY = 'aya-theme';
  
  function getTheme() {
    return localStorage.getItem(THEME_KEY) || 'dark';
  }
  
  function setTheme(theme) {
    if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem(THEME_KEY, theme);
    const btn = document.getElementById('themeToggle');
    if (btn) btn.textContent = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
  }
  
  // Apply on load (before render)
  setTheme(getTheme());
  
  document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('themeToggle');
    if (btn) {
      btn.textContent = getTheme() === 'dark' ? '☀️ Light' : '🌙 Dark';
      btn.addEventListener('click', function() {
        const next = getTheme() === 'dark' ? 'light' : 'dark';
        setTheme(next);
      });
    }
  });

  // ===== Back to Top Button =====
  document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('backToTop');
    if (!btn) return;
    
    let ticking = false;
    
    function updateBtn() {
      if (window.scrollY > 300) {
        btn.classList.add('visible');
      } else {
        btn.classList.remove('visible');
      }
      ticking = false;
    }
    
    window.addEventListener('scroll', function() {
      if (!ticking) {
        window.requestAnimationFrame(updateBtn);
        ticking = true;
      }
    }, { passive: true });
    
    btn.addEventListener('click', function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  // ===== Lead List Filtering =====
  document.addEventListener('DOMContentLoaded', function() {
    const filterSelect = document.getElementById('fitFilter');
    const searchInput = document.getElementById('searchFilter');
    if (!filterSelect && !searchInput) return;
    
    const cards = Array.from(document.querySelectorAll('.lead-card'));
    
    function applyFilters() {
      const filterVal = filterSelect ? filterSelect.value : 'all';
      const searchTerm = (searchInput ? searchInput.value : '').toLowerCase();
      
      cards.forEach(function(card) {
        const band = card.getAttribute('data-band') || '';
        const text = (card.textContent || '').toLowerCase();
        
        const bandMatch = filterVal === 'all' || band === filterVal;
        const searchMatch = !searchTerm || text.includes(searchTerm);
        
        if (bandMatch && searchMatch) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    }
    
    if (filterSelect) filterSelect.addEventListener('change', applyFilters);
    if (searchInput) {
      let timer;
      searchInput.addEventListener('input', function() {
        clearTimeout(timer);
        timer = setTimeout(applyFilters, 200);
      });
    }
  });

})();