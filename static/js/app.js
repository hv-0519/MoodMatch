/* =====================================================
   MoodMatch - Application JavaScript
   ===================================================== */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all modules
  initNavbar();
  initMoodSelector();
  initFilters();
  initActivityCards();
  initFavorites();
  initHistory();
  initSmoothScroll();
  initHeroAnimation();
});

/* =====================================================
   Navbar Toggle (Mobile)
   ===================================================== */
function initNavbar() {
  const toggle = document.getElementById('navbarToggle');
  const menu = document.getElementById('navbarMenu');
  
  if (!toggle || !menu) return;
  
  toggle.addEventListener('click', function() {
    toggle.classList.toggle('active');
    menu.classList.toggle('active');
    document.body.style.overflow = menu.classList.contains('active') ? 'hidden' : '';
  });
  
  // Close menu when clicking outside
  document.addEventListener('click', function(e) {
    if (!toggle.contains(e.target) && !menu.contains(e.target)) {
      toggle.classList.remove('active');
      menu.classList.remove('active');
      document.body.style.overflow = '';
    }
  });
  
  // Close menu when clicking a link
  menu.querySelectorAll('a').forEach(function(link) {
    link.addEventListener('click', function() {
      toggle.classList.remove('active');
      menu.classList.remove('active');
      document.body.style.overflow = '';
    });
  });
}

/* =====================================================
   Mood Selector
   ===================================================== */
function initMoodSelector() {
  const moodCards = document.querySelectorAll('.mood-card');
  
  moodCards.forEach(function(card) {
    card.addEventListener('click', function() {
      // Remove selected class from all cards
      moodCards.forEach(function(c) {
        c.classList.remove('selected');
      });
      
      // Add selected class to clicked card
      this.classList.add('selected');
      
      // Get mood value
      const mood = this.dataset.mood;
      
      // Store selected mood
      sessionStorage.setItem('selectedMood', mood);
      
      // Animate scroll to filters
      setTimeout(function() {
        const filtersSection = document.getElementById('filters');
        if (filtersSection) {
          filtersSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 300);
      
      // Trigger mood change event
      document.dispatchEvent(new CustomEvent('moodSelected', { detail: { mood: mood } }));
    });
    
    // Add hover micro-animation
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-4px)';
    });
    
    card.addEventListener('mouseleave', function() {
      if (!this.classList.contains('selected')) {
        this.style.transform = '';
      }
    });
  });
  
  // Restore selected mood from session
  const savedMood = sessionStorage.getItem('selectedMood');
  if (savedMood) {
    const savedCard = document.querySelector(`.mood-card[data-mood="${savedMood}"]`);
    if (savedCard) {
      savedCard.classList.add('selected');
    }
  }
}

/* =====================================================
   Filters
   ===================================================== */
function initFilters() {
  const filterChips = document.querySelectorAll('.filter-chips');
  const clearBtn = document.getElementById('clearFilters');
  const applyBtn = document.getElementById('applyFilters');
  
  // Handle chip selection
  filterChips.forEach(function(group) {
    const chips = group.querySelectorAll('.chip');
    
    chips.forEach(function(chip) {
      chip.addEventListener('click', function() {
        // Toggle selection
        if (this.classList.contains('selected')) {
          this.classList.remove('selected');
        } else {
          // Remove selected from siblings (single select)
          chips.forEach(function(c) {
            c.classList.remove('selected');
          });
          this.classList.add('selected');
        }
        
        // Store filter value
        const filterType = group.dataset.filter;
        const value = this.classList.contains('selected') ? this.dataset.value : null;
        
        if (value) {
          sessionStorage.setItem(`filter_${filterType}`, value);
        } else {
          sessionStorage.removeItem(`filter_${filterType}`);
        }
      });
    });
  });
  
  // Clear all filters
  if (clearBtn) {
    clearBtn.addEventListener('click', function() {
      document.querySelectorAll('.chip.selected').forEach(function(chip) {
        chip.classList.remove('selected');
      });
      
      // Clear session storage
      ['time', 'budget', 'energy', 'environment', 'distance'].forEach(function(filter) {
        sessionStorage.removeItem(`filter_${filter}`);
      });
    });
  }
  
  // Apply filters
  if (applyBtn) {
    applyBtn.addEventListener('click', function() {
      const filters = getSelectedFilters();
      const mood = sessionStorage.getItem('selectedMood');
      
      // Scroll to activities
      const activitiesSection = document.getElementById('activities');
      if (activitiesSection) {
        activitiesSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
      
      // Trigger filter event
      document.dispatchEvent(new CustomEvent('filtersApplied', { 
        detail: { mood: mood, filters: filters } 
      }));
    });
  }
  
  // Restore filters from session
  restoreFilters();
}

function getSelectedFilters() {
  const filters = {};
  
  document.querySelectorAll('.filter-chips').forEach(function(group) {
    const filterType = group.dataset.filter;
    const selected = group.querySelector('.chip.selected');
    if (selected) {
      filters[filterType] = selected.dataset.value;
    }
  });
  
  return filters;
}

function restoreFilters() {
  ['time', 'budget', 'energy', 'environment', 'distance'].forEach(function(filter) {
    const value = sessionStorage.getItem(`filter_${filter}`);
    if (value) {
      const chip = document.querySelector(`.filter-chips[data-filter="${filter}"] .chip[data-value="${value}"]`);
      if (chip) {
        chip.classList.add('selected');
      }
    }
  });
}

/* =====================================================
   Activity Cards
   ===================================================== */
function initActivityCards() {
  // Expand/collapse tips
  document.querySelectorAll('.expand-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const card = this.closest('.activity-card');
      card.classList.toggle('expanded');
      
      // Update button text
      const text = this.querySelector('span');
      if (text) {
        text.textContent = card.classList.contains('expanded') ? 'Hide Tips' : 'View Tips';
      }
    });
  });
  
  // Favorite buttons
  document.querySelectorAll('.favorite-btn').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      
      const activityId = this.dataset.activityId;
      const isFavorited = this.classList.contains('favorited');
      
      if (isFavorited) {
        removeFavorite(activityId);
        this.classList.remove('favorited');
      } else {
        addFavorite(activityId);
        this.classList.add('favorited');
      }
      
      // Animate heart
      this.style.transform = 'scale(1.2)';
      setTimeout(() => {
        this.style.transform = '';
      }, 200);
    });
  });
  
  // Restore favorite states
  const favorites = getFavorites();
  favorites.forEach(function(id) {
    const btn = document.querySelector(`.favorite-btn[data-activity-id="${id}"]`);
    if (btn) {
      btn.classList.add('favorited');
    }
  });
}

/* =====================================================
   Favorites Management (localStorage)
   ===================================================== */
function initFavorites() {
  // Clear all favorites button
  const clearAllBtn = document.getElementById('clearAllFavorites');
  if (clearAllBtn) {
    clearAllBtn.addEventListener('click', function() {
      if (confirm('Are you sure you want to remove all favorites?')) {
        localStorage.removeItem('moodmatch_favorites');
        location.reload();
      }
    });
  }
  
  // Remove individual favorite
  document.querySelectorAll('.remove-favorite-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const activityId = this.dataset.activityId;
      const card = this.closest('.activity-card');
      
      // Animate removal
      card.style.opacity = '0';
      card.style.transform = 'scale(0.95)';
      
      setTimeout(function() {
        removeFavorite(activityId);
        card.remove();
        
        // Check if empty
        const grid = document.querySelector('.favorites-grid');
        if (grid && grid.children.length === 0) {
          location.reload();
        }
      }, 200);
    });
  });
}

function getFavorites() {
  try {
    return JSON.parse(localStorage.getItem('moodmatch_favorites')) || [];
  } catch (e) {
    return [];
  }
}

function addFavorite(activityId) {
  const favorites = getFavorites();
  if (!favorites.includes(activityId)) {
    favorites.push(activityId);
    localStorage.setItem('moodmatch_favorites', JSON.stringify(favorites));
  }
}

function removeFavorite(activityId) {
  const favorites = getFavorites();
  const index = favorites.indexOf(activityId);
  if (index > -1) {
    favorites.splice(index, 1);
    localStorage.setItem('moodmatch_favorites', JSON.stringify(favorites));
  }
}

/* =====================================================
   History Management
   ===================================================== */
function initHistory() {
  // Clear history button
  const clearBtn = document.getElementById('clearHistory');
  if (clearBtn) {
    clearBtn.addEventListener('click', function() {
      if (confirm('Are you sure you want to clear your history?')) {
        localStorage.removeItem('moodmatch_history');
        location.reload();
      }
    });
  }
  
  // Delete individual history item
  document.querySelectorAll('.delete-history-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const historyId = this.dataset.historyId;
      const item = this.closest('.history-item');
      
      // Animate removal
      item.style.opacity = '0';
      item.style.transform = 'translateX(-20px)';
      
      setTimeout(function() {
        removeHistoryItem(historyId);
        item.remove();
        
        // Check if empty
        const list = document.querySelector('.history-list');
        if (list && list.children.length === 0) {
          location.reload();
        }
      }, 200);
    });
  });
  
  // Add to favorites from history
  document.querySelectorAll('.favorite-from-history').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const activityId = this.dataset.activityId;
      addFavorite(activityId);
      
      // Visual feedback
      const originalText = this.querySelector('span').textContent;
      this.querySelector('span').textContent = 'Saved!';
      this.disabled = true;
      
      setTimeout(() => {
        this.querySelector('span').textContent = originalText;
        this.disabled = false;
      }, 2000);
    });
  });
}

function getHistory() {
  try {
    return JSON.parse(localStorage.getItem('moodmatch_history')) || [];
  } catch (e) {
    return [];
  }
}

function addHistoryItem(item) {
  const history = getHistory();
  item.id = Date.now().toString();
  item.timestamp = new Date().toISOString();
  history.unshift(item);
  
  // Keep only last 50 items
  if (history.length > 50) {
    history.pop();
  }
  
  localStorage.setItem('moodmatch_history', JSON.stringify(history));
}

function removeHistoryItem(historyId) {
  const history = getHistory();
  const index = history.findIndex(function(item) {
    return item.id === historyId;
  });
  
  if (index > -1) {
    history.splice(index, 1);
    localStorage.setItem('moodmatch_history', JSON.stringify(history));
  }
}

/* =====================================================
   Smooth Scroll
   ===================================================== */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
}

/* =====================================================
   Hero Animation
   ===================================================== */
function initHeroAnimation() {
  const heroBtn = document.querySelector('.hero-actions .btn-primary');
  
  if (heroBtn) {
    // Micro-motion on hover
    heroBtn.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-2px) scale(1.02)';
    });
    
    heroBtn.addEventListener('mouseleave', function() {
      this.style.transform = '';
    });
  }
  
  // Animate stats on scroll
  const stats = document.querySelector('.hero-stats');
  if (stats) {
    const observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          animateStats();
          observer.disconnect();
        }
      });
    }, { threshold: 0.5 });
    
    observer.observe(stats);
  }
}

function animateStats() {
  document.querySelectorAll('.stat-value').forEach(function(stat) {
    const finalValue = stat.textContent;
    const isNumber = !isNaN(parseInt(finalValue));
    
    if (isNumber) {
      const target = parseInt(finalValue);
      let current = 0;
      const increment = Math.ceil(target / 30);
      const duration = 1000;
      const stepTime = duration / (target / increment);
      
      const counter = setInterval(function() {
        current += increment;
        if (current >= target) {
          stat.textContent = finalValue;
          clearInterval(counter);
        } else {
          stat.textContent = current;
        }
      }, stepTime);
    }
  });
}

/* =====================================================
   Event Listeners for Flask Integration
   ===================================================== */

// Listen for mood selection
document.addEventListener('moodSelected', function(e) {
  console.log('Mood selected:', e.detail.mood);
  // This can be used to make AJAX calls to Flask backend
});

// Listen for filters applied
document.addEventListener('filtersApplied', function(e) {
  console.log('Filters applied:', e.detail);
  // This can be used to make AJAX calls to Flask backend
  
  // Add to history
  if (e.detail.mood) {
    addHistoryItem({
      mood: e.detail.mood,
      filters: e.detail.filters
    });
  }
});

/* =====================================================
   Utility Functions
   ===================================================== */

// Debounce function for performance
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = function() {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Format date for display
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

function formatTime(dateString) {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit'
  });
}
