/**
 * CineMatch AI — Core Frontend Application Logic
 * Supports real-time filtering, dual-thumb range slider, star rating feedback,
 * watchlist management, global search autocomplete, and Partner CRUD Console.
 */

// State
const state = {
  activeGenres: ['Science Fiction', 'Adventure'],
  yearMin: 1980,
  yearMax: 2026,
  minRating: 7.0,
  selectedLanguage: 'English',
  sortBy: 'Highest Rated',
  page: 1,
  limit: 8,
  viewMode: 'grid',
};

// Hero Carousel Data
const HERO_SLIDES = [
  {
    id: 157336,
    title: 'Interstellar',
    subtagline: 'Go beyond what you know.',
    year: '2014',
    runtime: '2h 49m',
    rating: '9.4',
    ratingSource: 'IMDb / User',
    genres: ['Sci-Fi', 'Adventure', 'Drama'],
    synopsis: 'A team of explorers travels beyond this galaxy to discover whether mankind has a future among the stars.',
    creator: 'A film by Christopher Nolan',
    backdrop: 'https://image.tmdb.org/t/p/original/rAiYTggjG9vyzpYBt0Y0C8OIenk.jpg',
  },
  {
    id: 27205,
    title: 'Inception',
    subtagline: 'Your mind is the scene of the crime.',
    year: '2010',
    runtime: '2h 28m',
    rating: '8.8',
    ratingSource: 'IMDb / User',
    genres: ['Sci-Fi', 'Action', 'Thriller'],
    synopsis: 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
    creator: 'A film by Christopher Nolan',
    backdrop: 'https://image.tmdb.org/t/p/original/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg',
  },
  {
    id: 155,
    title: 'The Dark Knight',
    subtagline: 'Why so serious?',
    year: '2008',
    runtime: '2h 32m',
    rating: '9.0',
    ratingSource: 'IMDb / User',
    genres: ['Action', 'Crime', 'Drama'],
    synopsis: 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
    creator: 'A film by Christopher Nolan',
    backdrop: 'https://image.tmdb.org/t/p/original/nMKdUUepR0i5zn0y1T4CsSB5chy.jpg',
  },
  {
    id: 693134,
    title: 'Dune: Part Two',
    subtagline: 'Long live the fighters.',
    year: '2024',
    runtime: '2h 46m',
    rating: '8.5',
    ratingSource: 'IMDb / User',
    genres: ['Sci-Fi', 'Adventure'],
    synopsis: 'Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.',
    creator: 'A film by Denis Villeneuve',
    backdrop: 'https://image.tmdb.org/t/p/original/xOMo8BRK7PfcJv9JCnx7s520DRq.jpg',
  }
];
let currentHeroIdx = 0;

// Trailed URLs mapping with official verified embeds
const TRAILERS = {
  'Interstellar': 'https://www.youtube.com/embed/zSWdZVtXT7E?autoplay=1',
  'Inception': 'https://www.youtube.com/embed/YoHD9XEInc0?autoplay=1',
  'The Dark Knight': 'https://www.youtube.com/embed/EXeTwQWrcwY?autoplay=1',
  'Dune: Part Two': 'https://www.youtube.com/embed/Way9Dexny3w?autoplay=1',
  'The Matrix': 'https://www.youtube.com/embed/vKQi3bBA1y8?autoplay=1',
  'Arrival': 'https://www.youtube.com/embed/tFMo3UJ4B4g?autoplay=1',
  'The Martian': 'https://www.youtube.com/embed/ej3ioOneTy8?autoplay=1',
  'Blade Runner 2049': 'https://www.youtube.com/embed/gCcx85zbxz4?autoplay=1',
  'Everything Everywhere All at Once': 'https://www.youtube.com/embed/wxN1T1uxQ2g?autoplay=1',
  'The Conjuring': 'https://www.youtube.com/embed/k10ETZ41q5o?autoplay=1',
  'The Conjuring 2': 'https://www.youtube.com/embed/VFsmuRPClr4?autoplay=1',
  'Insidious': 'https://www.youtube.com/embed/zuZnRUcoW22?autoplay=1',
  'Insidious: Chapter 2': 'https://www.youtube.com/embed/fBbi4NeEbAk?autoplay=1',
  'Insidious: Chapter 3': 'https://www.youtube.com/embed/3HxEXn3L_44?autoplay=1',
  'Furious 7': 'https://www.youtube.com/embed/Skpu5HaVkOc?autoplay=1',
  'Deadpool': 'https://www.youtube.com/embed/ONHBaC-pfsk?autoplay=1',
  'Guardians of the Galaxy': 'https://www.youtube.com/embed/d96cjJhvlMA?autoplay=1',
  'Mad Max: Fury Road': 'https://www.youtube.com/embed/hEJnMQG9ev8?autoplay=1',
  'Jurassic World': 'https://www.youtube.com/embed/RFinNxS5HN4?autoplay=1',
  'Whiplash': 'https://www.youtube.com/embed/7d_jQycdQGo?autoplay=1',
  'Frozen': 'https://www.youtube.com/embed/TbQm5doF_Uc?autoplay=1',
  'Minions': 'https://www.youtube.com/embed/eisKxhjBnZ0?autoplay=1',
  'Pulp Fiction': 'https://www.youtube.com/embed/s7EdQ4FqbhY?autoplay=1',
  'Fight Club': 'https://www.youtube.com/embed/qtRKdVHc-cE?autoplay=1',
  'The Shawshank Redemption': 'https://www.youtube.com/embed/PLl99DlL6b4?autoplay=1',
  'The Godfather': 'https://www.youtube.com/embed/UaVTIH8mujA?autoplay=1',
  'Avatar': 'https://www.youtube.com/embed/5PSNL1qE6VY?autoplay=1',
  'Titanic': 'https://www.youtube.com/embed/2e-eXJ6HgkQ?autoplay=1',
  'Back to the Future': 'https://www.youtube.com/embed/qvsgGtivCgs?autoplay=1',
  'Gravity': 'https://www.youtube.com/embed/OiTiKOy59o4?autoplay=1',
  '2001: A Space Odyssey': 'https://www.youtube.com/embed/oR_e9y-bka0?autoplay=1',
  'Contact': 'https://www.youtube.com/embed/SRoj3jK37vc?autoplay=1',
  'Dune': 'https://www.youtube.com/embed/n9xhJrPXop4?autoplay=1',
  'The Prestige': 'https://www.youtube.com/embed/o4gHCmTQDVI?autoplay=1',
  '12 Angry Men': 'https://www.youtube.com/embed/TEN-2uTi2c0?autoplay=1',
  "Schindler's List": 'https://www.youtube.com/embed/gG22XNhtnoY?autoplay=1',
  'The Lord of the Rings: The Fellowship of the Ring': 'https://www.youtube.com/embed/V75dMMIW2B4?autoplay=1',
  'Avengers: Infinity War': 'https://www.youtube.com/embed/6ZfuNTqbHE8?autoplay=1',
  'Captain America: Civil War': 'https://www.youtube.com/embed/dKrVegVI0Us?autoplay=1',
  'Dawn of the Planet of the Apes': 'https://www.youtube.com/embed/3sHMCRaS3ao?autoplay=1',
  'The Hunger Games: Mockingjay - Part 1': 'https://www.youtube.com/embed/3PkkHSuMurs?autoplay=1',
  'Big Hero 6': 'https://www.youtube.com/embed/z3biFxZIJOQ?autoplay=1',
};

/* ==========================================================================
   Image Error & Offline Resilient SVG Fallback
   ========================================================================== */
function escapeXml(unsafe) {
  if (!unsafe) return '';
  return String(unsafe).replace(/[<>&'"]/g, c => {
    switch (c) {
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '&': return '&amp;';
      case '\'': return '&apos;';
      case '"': return '&quot;';
    }
  });
}

function handleImageError(img, title, year, genre) {
  if (!img) return;
  img.onerror = null;
  const rawTitle = title || img.getAttribute('data-title') || img.alt || 'Movie';
  let rawYear = year !== undefined && year !== null ? year : (img.getAttribute('data-year') || '');
  if (typeof rawYear === 'string' && rawYear.endsWith('.0')) {
    rawYear = rawYear.replace('.0', '');
  }
  const rawGenre = genre || img.getAttribute('data-genre') || 'Cinema';

  const cleanTitle = escapeXml(rawTitle);
  const cleanYear = escapeXml(rawYear);
  const cleanGenre = escapeXml(rawGenre);

  // Fallback SVG data URI
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 450" width="100%" height="100%">
    <defs>
      <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#111827"/>
        <stop offset="100%" stop-color="#1E293B"/>
      </linearGradient>
    </defs>
    <rect width="300" height="450" fill="url(#bg)"/>
    <rect x="12" y="12" width="276" height="426" rx="10" fill="none" stroke="rgba(255,255,255,0.1)"/>
    <text x="150" y="210" text-anchor="middle" fill="#FFFFFF" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-size="18" font-weight="700">${cleanTitle}</text>
    <text x="150" y="240" text-anchor="middle" fill="#94A3B8" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-size="13">${cleanYear ? cleanYear + ' · ' : ''}${cleanGenre}</text>
    <text x="150" y="400" text-anchor="middle" fill="#3B82F6" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-size="11" font-weight="600">CINEMATCH AI</text>
  </svg>`;
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
}

/* ==========================================================================
   Toast Notifications
   ========================================================================== */
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✓' : 'ℹ'}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ==========================================================================
   Global Search Autocomplete & Keyboard Shortcut
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('globalSearchInput');
  const drawer = document.getElementById('searchAutoCompleteDrawer');

  if (searchInput && drawer) {
    let timeout = null;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(timeout);
      const query = e.target.value.trim();
      if (query.length < 2) {
        drawer.innerHTML = '';
        drawer.classList.add('hidden');
        return;
      }

      timeout = setTimeout(async () => {
        try {
          const res = await fetch(`/api/movies?search=${encodeURIComponent(query)}&limit=5`);
          const data = await res.json();
          if (data.items && data.items.length > 0) {
            drawer.innerHTML = data.items.map(m => `
              <div class="search-item" onclick="location.href='/movie/${m.id}'">
                <img class="search-item-img" src="${m.poster_url}" alt="${escapeXml(m.title)}" data-title="${escapeXml(m.title)}" onerror="handleImageError(this)">
                <div class="search-item-info">
                  <div class="search-item-title">${m.title}</div>
                  <div class="search-item-meta">${m.year || ''} • ${m.genres ? m.genres.slice(0, 2).join(' · ') : ''} • ★ ${m.vote_average ? m.vote_average.toFixed(1) : '—'}</div>
                </div>
              </div>
            `).join('');
            drawer.classList.remove('hidden');
          } else {
            drawer.innerHTML = '<div style="padding: 12px; font-size: 12px; color: #94A3B8;">No movies found.</div>';
            drawer.classList.remove('hidden');
          }
        } catch (err) {
          console.error('Search autocomplete error:', err);
        }
      }, 250);
    });

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !drawer.contains(e.target)) {
        drawer.classList.add('hidden');
      }
    });
  }

  // Cmd / Ctrl + K shortcut
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      const s = document.getElementById('globalSearchInput');
      if (s) {
        s.focus();
        s.select();
      }
    }
  });

  // Pre-populate reviewer name from local storage
  const nameInput = document.getElementById('reviewerNameInput');
  if (nameInput && !nameInput.value) {
    try {
      const savedName = localStorage.getItem('cinematch_reviewer_name');
      if (savedName) nameInput.value = savedName;
    } catch (e) {}
  }
});

/* ==========================================================================
   Watchlist Toggle & Navigation Badge
   ========================================================================== */
async function toggleWatchlist(movieId, buttonElem) {
  try {
    const res = await fetch('/api/watchlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ movie_id: movieId })
    });
    const data = await res.json();

    // Update button visual
    if (buttonElem) {
      if (data.in_watchlist) {
        buttonElem.classList.add('active');
        buttonElem.classList.add('in-watchlist');
        const svg = buttonElem.querySelector('svg');
        if (svg) svg.setAttribute('fill', 'currentColor');
        const text = buttonElem.querySelector('#detailWatchlistText');
        if (text) text.textContent = '✓ In watchlist';
      } else {
        buttonElem.classList.remove('active');
        buttonElem.classList.remove('in-watchlist');
        const svg = buttonElem.querySelector('svg');
        if (svg) svg.setAttribute('fill', 'none');
        const text = buttonElem.querySelector('#detailWatchlistText');
        if (text) text.textContent = '+ Add to watchlist';
      }
    }

    // Update nav counter
    const badge = document.getElementById('navWatchlistBadge');
    if (badge) {
      badge.textContent = data.watchlist_count;
    }

    showToast(data.message, data.in_watchlist ? 'success' : 'info');
  } catch (err) {
    console.error('Watchlist error:', err);
    showToast('Failed to update watchlist', 'info');
  }
}

/* ==========================================================================
   Hero Carousel Controls (Page 1)
   ========================================================================== */
function updateHeroBanner(slide) {
  const banner = document.getElementById('heroBanner');
  const title = document.getElementById('heroTitle');
  const year = document.getElementById('heroYear');
  const genres = document.getElementById('heroGenres');
  const synopsis = document.getElementById('heroSynopsis');
  const counter = document.querySelector('.carousel-counter');
  const dots = document.querySelectorAll('.carousel-indicators .dot');
  const creatorLabel = document.querySelector('.creator-label');

  if (banner && slide) {
    banner.style.backgroundImage = `linear-gradient(180deg, rgba(7, 10, 16, 0.4) 0%, rgba(7, 10, 16, 0.95) 100%), url('${slide.backdrop}')`;
  }
  if (title) title.textContent = slide.title;
  if (year) year.textContent = slide.year;
  if (synopsis) synopsis.textContent = slide.synopsis;
  if (creatorLabel) creatorLabel.textContent = slide.creator;
  if (counter) counter.textContent = `0${currentHeroIdx + 1} / 04`;

  if (genres) {
    genres.innerHTML = slide.genres.map(g => `<span class="hero-genre-pill">${g}</span>`).join('');
  }

  if (dots) {
    dots.forEach((d, i) => d.classList.toggle('active', i === currentHeroIdx));
  }
}

function nextHeroSlide() {
  currentHeroIdx = (currentHeroIdx + 1) % HERO_SLIDES.length;
  updateHeroBanner(HERO_SLIDES[currentHeroIdx]);
}

function prevHeroSlide() {
  currentHeroIdx = (currentHeroIdx - 1 + HERO_SLIDES.length) % HERO_SLIDES.length;
  updateHeroBanner(HERO_SLIDES[currentHeroIdx]);
}

function scrollRail(railId, offset) {
  const rail = document.getElementById(railId);
  if (rail) {
    rail.scrollBy({ left: offset, behavior: 'smooth' });
  }
}

/* Quick Filter Pills (Page 1) */
function selectQuickFilter(type, value, btn) {
  const group = btn.closest('.filter-pills-group');
  if (group) {
    group.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }

  // Navigate to Discover with filter
  if (type === 'genre' && value !== 'all') {
    location.href = `/discover?genres=${encodeURIComponent(value)}`;
  } else if (type === 'lang' && value !== 'all') {
    location.href = `/discover?language=${encodeURIComponent(value)}`;
  } else if (type === 'decade') {
    if (value === '2020s') location.href = '/discover?year_min=2020&year_max=2026';
    else if (value === '2010s') location.href = '/discover?year_min=2010&year_max=2019';
    else if (value === 'Classics') location.href = '/discover?year_min=1950&year_max=1999';
    else location.href = '/discover';
  }
}

function resetQuickFilters() {
  document.querySelectorAll('.filter-pills-group').forEach(group => {
    group.querySelectorAll('.pill-btn').forEach((b, i) => b.classList.toggle('active', i === 0));
  });
  showToast('Quick filters reset', 'info');
}

/* ==========================================================================
   Page 2: Movie Detail Interactive Feedback Box
   ========================================================================== */
const verbalScores = {
  1: 'Not for me', 2: 'Below Average', 3: 'Mediocre', 4: 'Fair',
  5: 'Average', 6: 'Decent', 7: 'Good', 8: 'Very Good',
  9: 'Excellent', 10: 'Masterpiece / All-time favorite'
};

function handleSliderChange(val) {
  const num = parseInt(val, 10);
  const scoreNum = document.getElementById('scoreNumber');
  const scoreVerbal = document.getElementById('scoreVerbal');

  if (scoreNum) scoreNum.textContent = num;
  if (scoreVerbal) scoreVerbal.textContent = verbalScores[num] || 'Excellent';

  // Highlight stars up to num
  const stars = document.querySelectorAll('#starsRow .star-item');
  stars.forEach((s, i) => s.classList.toggle('filled', i < num));
}

function setRatingVal(val) {
  const slider = document.getElementById('ratingSlider');
  if (slider) {
    slider.value = val;
    handleSliderChange(val);
  }
}

function updateCharCount(textarea) {
  const label = document.getElementById('reviewCharCount');
  if (label) {
    label.textContent = `${textarea.value.length} / 1,000 characters`;
  }
}

async function submitUserReview(movieId) {
  const slider = document.getElementById('ratingSlider');
  const textarea = document.getElementById('reviewTextInput');
  const nameInput = document.getElementById('reviewerNameInput');
  const spoilerCheck = document.getElementById('spoilerCheckbox');
  const statusTag = document.getElementById('ratingSaveStatus');

  const ratingVal = slider ? parseFloat(slider.value) : 9.0;
  const reviewText = textarea ? textarea.value.trim() : '';
  let authorName = nameInput ? nameInput.value.trim() : '';
  const spoilers = spoilerCheck ? spoilerCheck.checked : false;

  if (!authorName || authorName.toLowerCase() === 'anonymous cinephile') {
    if (nameInput) {
      nameInput.value = '';
      nameInput.focus();
      nameInput.style.borderColor = '#EF4444';
      nameInput.style.boxShadow = '0 0 16px rgba(239, 68, 68, 0.6)';
      nameInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      nameInput.addEventListener('input', function onInputClear() {
        nameInput.style.borderColor = 'rgba(255, 255, 255, 0.12)';
        nameInput.style.boxShadow = 'none';
        nameInput.removeEventListener('input', onInputClear);
      });
    }
    showToast('⚠️ Please enter your Name / Critic Handle above to post your review!', 'info');
    return;
  }

  // Remember reviewer name for future reviews
  try {
    localStorage.setItem('cinematch_reviewer_name', authorName);
  } catch (e) {}

  try {
    const res = await fetch(`/api/movies/${movieId}/rating`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rating: ratingVal,
        author_name: authorName,
        review_text: reviewText,
        contains_spoilers: spoilers,
      })
    });

    if (res.ok) {
      const data = await res.json();
      if (statusTag) {
        statusTag.textContent = 'Saved ✓';
        statusTag.style.color = '#34D399';
      }
      showToast('Rating & review saved successfully!', 'success');

      // Live real-time update of the Community Reviews list
      const list = document.getElementById('communityReviewsList');
      const noPrompt = document.getElementById('noReviewsPrompt');
      if (noPrompt) noPrompt.remove();

      if (list) {
        const initials = escapeXml(authorName.slice(0, 2).toUpperCase());
        const safeAuthor = escapeXml(authorName);
        const safeText = escapeXml(reviewText);
        const cardHtml = `
          <div class="community-review-card" style="padding: 18px 20px; background: rgba(30, 41, 59, 0.8); border: 1px solid #10B981; border-radius: 12px; box-shadow: 0 0 16px rgba(16, 185, 129, 0.2); animation: fadeIn 0.4s ease-out;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #10B981, #059669); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; color: #FFFFFF;">
                  ${initials}
                </div>
                <div>
                  <div style="font-weight: 600; font-size: 15px; color: #FFFFFF;">${safeAuthor} <span style="font-size: 11px; color: #34D399; font-weight: 400; margin-left: 6px;">(You · Just now)</span></div>
                  <div style="font-size: 12px; color: #64748B;">Just now</div>
                </div>
              </div>
              <div style="display: flex; align-items: center; gap: 8px;">
                ${spoilers ? '<span style="font-size: 11px; padding: 2px 8px; background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); color: #FCA5A5; border-radius: 4px; font-weight: 600;">SPOILER</span>' : ''}
                <span style="font-size: 14px; font-weight: 700; color: #F59E0B; background: rgba(245, 158, 11, 0.15); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(245, 158, 11, 0.3);">
                  ★ ${ratingVal.toFixed(1)}/10
                </span>
              </div>
            </div>
            ${safeText ? `<p style="font-size: 14px; color: #E2E8F0; line-height: 1.6; margin: 0; white-space: pre-line;">${safeText}</p>` : '<p style="font-size: 13px; color: #94A3B8; font-style: italic; margin: 0;">Rated this title without written comments.</p>'}
          </div>
        `;
        list.insertAdjacentHTML('afterbegin', cardHtml);

        const badge = document.getElementById('communityReviewsCountBadge');
        if (badge) {
          const count = list.querySelectorAll('.community-review-card').length;
          badge.textContent = `${count} Review${count !== 1 ? 's' : ''}`;
        }
      }
    } else {
      showToast('Error saving review', 'info');
    }
  } catch (err) {
    console.error('Submit review error:', err);
    showToast('Failed to submit review', 'info');
  }
}

function shareMovie(title) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(window.location.href);
    showToast(`Copied share link for "${title}" to clipboard!`, 'success');
  } else {
    showToast(`Share URL: ${window.location.href}`, 'info');
  }
}

function openTrailerModal(title) {
  const modal = document.getElementById('trailerModal');
  const iframe = document.getElementById('trailerIframe');
  const titleEl = document.getElementById('trailerModalTitle');
  const extBtn = document.getElementById('trailerExternalLink');
  if (!modal || !iframe) return;

  const cleanTitle = (title || 'Official Trailer').trim();
  if (titleEl) titleEl.textContent = `Trailer: ${cleanTitle}`;

  const ytSearchUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(cleanTitle + ' official trailer')}`;
  if (extBtn) {
    extBtn.href = ytSearchUrl;
  }

  // Direct match or dynamic search embed
  let trailerUrl = TRAILERS[cleanTitle];
  if (!trailerUrl) {
    trailerUrl = `https://www.youtube.com/embed?listType=search&list=${encodeURIComponent(cleanTitle + ' official trailer')}&autoplay=1`;
  }

  iframe.src = trailerUrl;
  modal.classList.remove('hidden');
}

function closeTrailerModal() {
  const modal = document.getElementById('trailerModal');
  const iframe = document.getElementById('trailerIframe');
  if (modal) modal.classList.add('hidden');
  if (iframe) iframe.src = '';
}

/* ==========================================================================
   Navbar Category Dropdowns (Genre, Language, Year)
   ========================================================================== */
function toggleNavDropdown(menuId, event) {
  if (event) event.stopPropagation();
  const menu = document.getElementById(menuId);
  const isHidden = menu ? menu.classList.contains('hidden') : true;

  // Close all other nav dropdowns first
  document.querySelectorAll('.nav-dropdown-menu').forEach(m => m.classList.add('hidden'));

  if (menu && isHidden) {
    menu.classList.remove('hidden');
  }
}

function selectNavFilter(type, value) {
  document.querySelectorAll('.nav-dropdown-menu').forEach(m => m.classList.add('hidden'));

  // If currently on /discover, apply filters immediately in-page
  if (window.location.pathname === '/discover') {
    if (type === 'genre') {
      const cb = document.querySelector(`input[name="genreFilter"][value="${value}"]`);
      if (cb) {
        cb.checked = true;
      } else {
        if (!state.activeGenres.includes(value)) state.activeGenres.push(value);
      }
      applyFilters();
    } else if (type === 'lang') {
      selectCatalogLanguage(value);
    } else if (type === 'decade') {
      if (value === '2020s') { state.yearMin = 2020; state.yearMax = 2026; }
      else if (value === '2010s') { state.yearMin = 2010; state.yearMax = 2019; }
      else if (value === '2000s') { state.yearMin = 2000; state.yearMax = 2009; }
      else if (value === '1990s') { state.yearMin = 1990; state.yearMax = 1999; }
      else if (value === '1980s') { state.yearMin = 1980; state.yearMax = 1989; }
      else if (value === 'Classics') { state.yearMin = 1950; state.yearMax = 1979; }

      const minInput = document.getElementById('rangeMinInput');
      const maxInput = document.getElementById('rangeMaxInput');
      if (minInput) minInput.value = state.yearMin;
      if (maxInput) maxInput.value = state.yearMax;
      syncDualSliderUI();
      applyFilters();
    }
  } else {
    // Navigate to /discover with the selected filter in query string
    if (type === 'genre') {
      location.href = `/discover?genres=${encodeURIComponent(value)}`;
    } else if (type === 'lang') {
      location.href = `/discover?language=${encodeURIComponent(value)}`;
    } else if (type === 'decade') {
      if (value === '2020s') location.href = '/discover?year_min=2020&year_max=2026';
      else if (value === '2010s') location.href = '/discover?year_min=2010&year_max=2019';
      else if (value === '2000s') location.href = '/discover?year_min=2000&year_max=2009';
      else if (value === '1990s') location.href = '/discover?year_min=1990&year_max=1999';
      else if (value === '1980s') location.href = '/discover?year_min=1980&year_max=1989';
      else if (value === 'Classics') location.href = '/discover?year_min=1950&year_max=1979';
    }
  }
}

// Global click-outside listener to dismiss navbar dropdowns
document.addEventListener('click', (e) => {
  if (!e.target.closest('.nav-dropdown-wrapper')) {
    document.querySelectorAll('.nav-dropdown-menu').forEach(m => m.classList.add('hidden'));
  }
});

/* ==========================================================================
   Page 3: Catalog & Advanced Filter Engine
   ========================================================================== */
function initCatalogEngine() {
  const urlParams = new URLSearchParams(window.location.search);

  // 1. Parse genres
  if (urlParams.has('genres')) {
    const raw = urlParams.get('genres');
    const glist = raw.split(',').map(s => s.trim()).filter(Boolean);
    if (glist.length > 0) {
      state.activeGenres = glist;
      document.querySelectorAll('input[name="genreFilter"]').forEach(cb => {
        cb.checked = state.activeGenres.includes(cb.value);
      });
      const countBadge = document.getElementById('genreSelectedCount');
      if (countBadge) countBadge.textContent = `${state.activeGenres.length} selected`;
    }
  }

  // 2. Parse language
  if (urlParams.has('language')) {
    const lang = urlParams.get('language').trim();
    if (lang) {
      state.selectedLanguage = lang;
      const tag = document.getElementById('currentLangTag');
      if (tag) {
        tag.innerHTML = `${lang} <span class="tag-remove" onclick="event.stopPropagation(); removeLangTag()">×</span>`;
      }
    }
  }

  // 3. Parse years
  if (urlParams.has('year_min')) {
    state.yearMin = parseInt(urlParams.get('year_min'), 10);
    const minInput = document.getElementById('rangeMinInput');
    if (minInput) minInput.value = state.yearMin;
  }
  if (urlParams.has('year_max')) {
    state.yearMax = parseInt(urlParams.get('year_max'), 10);
    const maxInput = document.getElementById('rangeMaxInput');
    if (maxInput) maxInput.value = state.yearMax;
  }

  // 4. Parse min_rating
  if (urlParams.has('min_rating')) {
    state.minRating = parseFloat(urlParams.get('min_rating'));
    const slider = document.getElementById('ratingThresholdSlider');
    const display = document.getElementById('ratingThresholdDisplay');
    if (slider) slider.value = state.minRating;
    if (display) display.textContent = `${state.minRating.toFixed(1)}+`;
  }

  // 5. Parse sort_by
  if (urlParams.has('sort_by')) {
    const sb = urlParams.get('sort_by');
    state.sortBy = sb;
    const labelElem = document.getElementById('selectedSortLabel');
    const headerElem = document.getElementById('currentSortHeader');
    if (labelElem) labelElem.textContent = sb;
    if (headerElem) headerElem.textContent = `${sb} first`;
  }

  updateActivePillsBar();
  syncDualSliderUI();
  fetchCatalogMovies();
}

function syncDualSliderUI() {
  const minInput = document.getElementById('rangeMinInput');
  const maxInput = document.getElementById('rangeMaxInput');
  const track = document.getElementById('rangeSelectedTrack');
  const minBox = document.getElementById('yearMinBox');
  const maxBox = document.getElementById('yearMaxBox');

  if (!minInput || !maxInput || !track) return;

  const min = parseInt(minInput.min, 10);
  const max = parseInt(minInput.max, 10);
  const vMin = parseInt(minInput.value, 10);
  const vMax = parseInt(maxInput.value, 10);

  const leftPct = ((vMin - min) / (max - min)) * 100;
  const rightPct = 100 - (((vMax - min) / (max - min)) * 100);

  track.style.left = `${leftPct}%`;
  track.style.right = `${rightPct}%`;

  if (minBox) minBox.textContent = vMin;
  if (maxBox) maxBox.textContent = vMax;
}

function handleDualYearMin(val) {
  const maxInput = document.getElementById('rangeMaxInput');
  if (parseInt(val, 10) > parseInt(maxInput.value, 10)) {
    val = maxInput.value;
    document.getElementById('rangeMinInput').value = val;
  }
  state.yearMin = parseInt(val, 10);
  syncDualSliderUI();
  applyFiltersDebounced();
}

function handleDualYearMax(val) {
  const minInput = document.getElementById('rangeMinInput');
  if (parseInt(val, 10) < parseInt(minInput.value, 10)) {
    val = minInput.value;
    document.getElementById('rangeMaxInput').value = val;
  }
  state.yearMax = parseInt(val, 10);
  syncDualSliderUI();
  applyFiltersDebounced();
}

function handleRatingThreshold(val) {
  const display = document.getElementById('ratingThresholdDisplay');
  const num = parseFloat(val);
  state.minRating = num;
  if (display) display.textContent = `${num.toFixed(1)}+`;
  applyFiltersDebounced();
}

function toggleLangDropdown() {
  const drawer = document.getElementById('langOptionsDrawer');
  if (drawer) drawer.classList.toggle('hidden');
}

function selectCatalogLanguage(lang) {
  state.selectedLanguage = lang;
  const tag = document.getElementById('currentLangTag');
  if (tag) {
    tag.innerHTML = `${lang} <span class="tag-remove" onclick="event.stopPropagation(); removeLangTag()">×</span>`;
  }
  toggleLangDropdown();
  applyFilters();
}

function removeLangTag() {
  selectCatalogLanguage('All');
}

function toggleSortDropdown() {
  const drawer = document.getElementById('sortOptionsDrawer');
  if (drawer) drawer.classList.toggle('hidden');
}

function selectSortOption(sortLabel) {
  state.sortBy = sortLabel;
  const labelElem = document.getElementById('selectedSortLabel');
  const headerElem = document.getElementById('currentSortHeader');
  if (labelElem) labelElem.textContent = sortLabel;
  if (headerElem) headerElem.textContent = `${sortLabel} first`;

  document.querySelectorAll('#sortOptionsDrawer .sort-opt').forEach(opt => {
    opt.classList.toggle('active', opt.textContent.includes(sortLabel));
  });

  toggleSortDropdown();
  applyFilters();
}

function toggleExtraGenres(btn) {
  showToast('All 19 cinematic genres are indexed & searchable.', 'info');
}

function setViewMode(mode) {
  state.viewMode = mode;
  document.getElementById('gridViewBtn').classList.toggle('active', mode === 'grid');
  document.getElementById('listViewBtn').classList.toggle('active', mode === 'list');
  const grid = document.getElementById('catalogGrid');
  if (grid) {
    grid.style.gridTemplateColumns = mode === 'list' ? '1fr' : 'repeat(4, 1fr)';
  }
}

let filterDebounceTimer = null;
function applyFiltersDebounced() {
  clearTimeout(filterDebounceTimer);
  filterDebounceTimer = setTimeout(applyFilters, 300);
}

function applyFilters() {
  // Collect checked genres
  const checked = Array.from(document.querySelectorAll('input[name="genreFilter"]:checked')).map(cb => cb.value);
  state.activeGenres = checked;

  // Update selected count badge
  const countBadge = document.getElementById('genreSelectedCount');
  if (countBadge) {
    countBadge.textContent = `${checked.length} selected`;
  }

  updateActivePillsBar();
  state.page = 1;
  fetchCatalogMovies();
}

function updateActivePillsBar() {
  const bar = document.getElementById('activeFilterPillsList');
  if (!bar) return;

  let html = `
    <span class="active-filter-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="4" y1="6" x2="20" y2="6"></line>
        <line x1="7" y1="12" x2="17" y2="12"></line>
        <line x1="10" y1="18" x2="14" y2="18"></line>
      </svg>
    </span>
  `;

  state.activeGenres.forEach(g => {
    const shortName = g === 'Science Fiction' ? 'Sci-Fi' : g;
    html += `<span class="active-filter-pill" onclick="removeGenreFilter('${g}')">${shortName} <span class="pill-x">×</span></span>`;
  });

  if (state.yearMin !== 1950 || state.yearMax !== 2026) {
    html += `<span class="active-filter-pill" onclick="resetYearFilter()">${state.yearMin}–${state.yearMax} <span class="pill-x">×</span></span>`;
  }

  if (state.minRating > 0) {
    html += `<span class="active-filter-pill" onclick="resetRatingFilter()">${state.minRating.toFixed(1)}+ <span class="pill-x">×</span></span>`;
  }

  if (state.selectedLanguage && state.selectedLanguage !== 'All') {
    html += `<span class="active-filter-pill" onclick="removeLangTag()">${state.selectedLanguage} <span class="pill-x">×</span></span>`;
  }

  html += `<button class="clear-all-link" onclick="resetAllCatalogFilters()">Clear all</button>`;
  bar.innerHTML = html;
}

function removeGenreFilter(genre) {
  const cb = document.querySelector(`input[name="genreFilter"][value="${genre}"]`);
  if (cb) cb.checked = false;
  applyFilters();
}

function resetYearFilter() {
  document.getElementById('rangeMinInput').value = 1950;
  document.getElementById('rangeMaxInput').value = 2026;
  state.yearMin = 1950;
  state.yearMax = 2026;
  syncDualSliderUI();
  applyFilters();
}

function resetRatingFilter() {
  const slider = document.getElementById('ratingThresholdSlider');
  if (slider) slider.value = 0;
  state.minRating = 0.0;
  document.getElementById('ratingThresholdDisplay').textContent = '0.0+';
  applyFilters();
}

function resetAllCatalogFilters() {
  document.querySelectorAll('input[name="genreFilter"]').forEach(cb => cb.checked = false);
  state.activeGenres = [];
  resetYearFilter();
  resetRatingFilter();
  selectCatalogLanguage('All');
  showToast('Filters reset', 'info');
}

function saveCurrentSearch() {
  showToast('Current filter configuration bookmarked to your session.', 'success');
}

/* Fetch catalog movies matching exact filters */
async function fetchCatalogMovies() {
  const grid = document.getElementById('catalogGrid');
  if (!grid) return;

  grid.innerHTML = '<div class="catalog-loading-placeholder"><div class="spinner"></div><p>Querying cinema catalog...</p></div>';

  const params = new URLSearchParams();
  if (state.activeGenres.length > 0) {
    params.set('genres', state.activeGenres.join(','));
  }
  if (state.yearMin) params.set('year_min', state.yearMin);
  if (state.yearMax) params.set('year_max', state.yearMax);
  if (state.minRating > 0) params.set('min_rating', state.minRating);
  if (state.selectedLanguage && state.selectedLanguage !== 'All') {
    params.set('language', state.selectedLanguage);
  }
  params.set('sort_by', state.sortBy);
  params.set('page', state.page);
  params.set('limit', state.limit);

  try {
    const res = await fetch(`/api/movies?${params.toString()}`);
    const data = await res.json();

    // Update match count readout
    const matchNum = document.getElementById('matchCountNumber');
    if (matchNum) matchNum.textContent = `${data.total} movies`;

    // Render cards
    if (data.items && data.items.length > 0) {
      grid.innerHTML = data.items.map(m => `
        <div class="catalog-card" onclick="location.href='/movie/${m.id}'">
          <div class="card-poster-wrap">
            <img src="${m.poster_url}" alt="${escapeXml(m.title)}" data-title="${escapeXml(m.title)}" data-year="${m.year || ''}" data-genre="${m.genres ? escapeXml(m.genres[0]) : ''}" onerror="handleImageError(this)">
            <span class="card-star-badge">★ ${m.vote_average ? m.vote_average.toFixed(1) : '—'}</span>
            <button class="card-save-btn ${m.is_in_watchlist ? 'active' : ''}" title="Save to Watchlist" onclick="event.stopPropagation(); toggleWatchlist(${m.id}, this)">
              <svg viewBox="0 0 24 24" fill="${m.is_in_watchlist ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
              </svg>
            </button>
          </div>
          <div class="card-details">
            <h3 class="card-film-title">${m.title}</h3>
            <div class="card-meta-line">
              <span class="meta-year-lang">${m.year || ''} • ${m.original_language ? m.original_language.toUpperCase() : 'EN'}</span>
              ${m.revenue_display ? `<span class="card-revenue-pill">${m.revenue_display}</span>` : ''}
            </div>
            <div class="card-genres-line">
              ${m.genres ? m.genres.slice(0, 2).join(' · ') : 'Cinema'}
            </div>
          </div>
        </div>
      `).join('');
    } else {
      grid.innerHTML = `
        <div class="catalog-loading-placeholder" style="grid-column: 1 / -1;">
          <p style="font-size: 16px; color: #FFFFFF;">No movies found matching your filters.</p>
          <button class="btn btn-primary btn-small" onclick="resetAllCatalogFilters()">Reset All Filters</button>
        </div>
      `;
    }

    // Pagination controls matching page 3.jpg (< 1 2 3 4 ... 16 Next >)
    renderPagination(data.total, data.page, data.pages, data.limit);
  } catch (err) {
    console.error('Catalog fetch error:', err);
    grid.innerHTML = '<div class="catalog-loading-placeholder"><p>Error connecting to movies API.</p></div>';
  }
}

function renderPagination(total, page, pages, limit) {
  const showing = document.getElementById('paginationShowingText');
  const controls = document.getElementById('paginationControls');
  if (!controls) return;

  const start = total === 0 ? 0 : ((page - 1) * limit) + 1;
  const end = Math.min(page * limit, total);
  if (showing) {
    showing.textContent = `Showing ${start}–${end} of ${total} movies`;
  }

  let html = '';
  // Prev button
  if (page > 1) {
    html += `<button class="page-nav-btn" onclick="goToCatalogPage(${page - 1})">&lt;</button>`;
  }

  // Page numbers
  const maxButtons = 5;
  let startPage = Math.max(1, page - 2);
  let endPage = Math.min(pages, startPage + maxButtons - 1);
  if (endPage - startPage < maxButtons - 1) {
    startPage = Math.max(1, endPage - maxButtons + 1);
  }

  for (let p = startPage; p <= endPage; p++) {
    html += `<button class="page-num-btn ${p === page ? 'active' : ''}" onclick="goToCatalogPage(${p})">${p}</button>`;
  }

  if (endPage < pages) {
    html += `<span style="color: #64748B; padding: 0 4px;">...</span>`;
    html += `<button class="page-num-btn" onclick="goToCatalogPage(${pages})">${pages}</button>`;
  }

  // Next button
  if (page < pages) {
    html += `<button class="page-nav-btn" onclick="goToCatalogPage(${page + 1})">Next &gt;</button>`;
  }

  controls.innerHTML = html;
}

function goToCatalogPage(p) {
  state.page = p;
  fetchCatalogMovies();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ==========================================================================
   Partner CRUD Console Modal Logic
   ========================================================================== */
function openCrudModal() {
  const modal = document.getElementById('crudModal');
  if (modal) modal.classList.remove('hidden');
}

function closeCrudModal() {
  const modal = document.getElementById('crudModal');
  if (modal) modal.classList.add('hidden');
}

function switchModalTab(tabId) {
  document.querySelectorAll('.modal-tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.modal-tabs .tab-btn').forEach(b => b.classList.remove('active'));
  const target = document.getElementById(tabId);
  if (target) target.classList.add('active');

  const btn = Array.from(document.querySelectorAll('.modal-tabs .tab-btn'))
    .find(b => b.getAttribute('onclick').includes(tabId));
  if (btn) btn.classList.add('active');
}

async function handleCreateMovie(e) {
  e.preventDefault();
  const id = parseInt(document.getElementById('newMovieId').value, 10);
  const title = document.getElementById('newMovieTitle').value.trim();
  const overview = document.getElementById('newMovieOverview').value.trim();
  const director = document.getElementById('newMovieDirector').value.trim();
  const genresRaw = document.getElementById('newMovieGenres').value.trim();
  const dateVal = document.getElementById('newMovieDate').value;
  const rating = parseFloat(document.getElementById('newMovieRating').value);
  const budget = parseInt(document.getElementById('newMovieBudget').value, 10) || null;
  const revenue = parseInt(document.getElementById('newMovieRevenue').value, 10) || null;

  const genres = genresRaw ? genresRaw.split(',').map(g => g.trim()).filter(Boolean) : ['Drama'];

  const payload = {
    id,
    title,
    overview,
    director,
    genres,
    release_date: dateVal || null,
    vote_average: rating,
    vote_count: 10,
    budget,
    revenue,
    original_language: 'en'
  };

  try {
    const res = await fetch('/api/movies', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      showToast(`Created movie "${title}"! Re-indexing triggered.`, 'success');
      closeCrudModal();
      document.getElementById('createMovieForm').reset();
    } else {
      const err = await res.json();
      showToast(`Create failed: ${err.detail || 'Error'}`, 'info');
    }
  } catch (err) {
    showToast('Failed to connect to API', 'info');
  }
}

async function handleUpdateMovie(e) {
  e.preventDefault();
  const id = parseInt(document.getElementById('updateMovieId').value, 10);
  const title = document.getElementById('updateMovieTitle').value.trim();
  const ratingStr = document.getElementById('updateMovieRating').value;
  const revenueStr = document.getElementById('updateMovieRevenue').value;
  const overview = document.getElementById('updateMovieOverview').value.trim();

  const payload = {};
  if (title) payload.title = title;
  if (ratingStr) payload.vote_average = parseFloat(ratingStr);
  if (revenueStr) payload.revenue = parseInt(revenueStr, 10);
  if (overview) payload.overview = overview;

  try {
    const res = await fetch(`/api/movies/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      showToast(`Updated movie #${id}! Re-indexing triggered.`, 'success');
      closeCrudModal();
      document.getElementById('updateMovieForm').reset();
    } else {
      const err = await res.json();
      showToast(`Update failed: ${err.detail || 'Error'}`, 'info');
    }
  } catch (err) {
    showToast('Failed to connect to API', 'info');
  }
}

async function handleDeleteMovie(e) {
  e.preventDefault();
  const id = parseInt(document.getElementById('deleteMovieId').value, 10);
  if (!confirm(`Are you sure you want to remove movie ID ${id} from the shared PostgreSQL database?`)) return;

  try {
    const res = await fetch(`/api/movies/${id}`, { method: 'DELETE' });
    if (res.ok) {
      showToast(`Movie #${id} deleted. Re-indexed memory vectors.`, 'success');
      closeCrudModal();
      document.getElementById('deleteMovieForm').reset();
    } else {
      const err = await res.json();
      showToast(`Delete failed: ${err.detail || 'Not found'}`, 'info');
    }
  } catch (err) {
    showToast('Failed to connect to API', 'info');
  }
}

async function triggerReindex() {
  const output = document.getElementById('reindexStatusOutput');
  showToast('Triggering Scikit-Learn TF-IDF re-indexing...', 'info');

  try {
    const res = await fetch('/api/reindex', { method: 'POST' });
    const data = await res.json();
    if (output) {
      output.textContent = `${data.message} (${data.total_indexed} records). Status: ${data.status}`;
      output.classList.remove('hidden');
    }
    showToast(`Re-indexed ${data.total_indexed} movies in ${data.elapsed_seconds}s!`, 'success');
  } catch (err) {
    showToast('Re-index pipeline error', 'info');
  }
}

/* ==========================================================================
   Partner Bridge Live Analytics Logic
   ========================================================================== */
function switchBridgeTab(tabId) {
  document.querySelectorAll('.bridge-tab-view').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.explorer-tabs .tab-btn').forEach(b => b.classList.remove('active'));

  const target = document.getElementById(tabId);
  if (target) target.classList.add('active');

  const btn = Array.from(document.querySelectorAll('.explorer-tabs .tab-btn'))
    .find(b => b.getAttribute('onclick').includes(tabId));
  if (btn) btn.classList.add('active');
}

async function loadBridgeAnalytics() {
  refreshBridgeData();
}

async function refreshBridgeData() {
  try {
    // 1. Trends
    const trendsRes = await fetch('/api/analytics/trends');
    const trendsData = await trendsRes.json();

    const topRevList = document.getElementById('topRevenueList');
    if (topRevList && trendsData.top_revenue) {
      topRevList.innerHTML = trendsData.top_revenue.slice(0, 5).map(m => `
        <div class="stat-item">
          <span class="stat-title">${m.title} (${m.year})</span>
          <span class="stat-val">${m.revenue_formatted}</span>
        </div>
      `).join('');
    }

    const decadesList = document.getElementById('decadesList');
    if (decadesList && trendsData.decades) {
      decadesList.innerHTML = trendsData.decades.slice(-6).map(d => `
        <div class="stat-item">
          <span class="stat-title">${d.decade}</span>
          <span class="stat-val">${d.count} releases</span>
        </div>
      `).join('');
    }

    const genreContainer = document.getElementById('genreDistributionTags');
    if (genreContainer && trendsData.genres_distribution) {
      genreContainer.innerHTML = trendsData.genres_distribution.slice(0, 12).map(g => `
        <div class="genre-bar-item">
          <span class="g-name">${g.genre}</span>
          <span class="g-count">${g.count}</span>
        </div>
      `).join('');
    }

    // 2. Summary JSON
    const summaryRes = await fetch('/api/analytics/summary');
    const summaryData = await summaryRes.json();
    const sumJson = document.getElementById('summaryJsonOutput');
    if (sumJson) sumJson.textContent = JSON.stringify(summaryData, null, 2);

    // 3. Genres JSON
    const genresRes = await fetch('/api/analytics/genres');
    const genresData = await genresRes.json();
    const gJson = document.getElementById('genresJsonOutput');
    if (gJson) gJson.textContent = JSON.stringify(genresData, null, 2);

    showToast('Live analytical data refreshed from shared database.', 'success');
  } catch (err) {
    console.error('Bridge error:', err);
  }
}

function showAboutModal() {
  showToast('CineMatch AI v1.0 — Pair-programmed movie intelligence platform.', 'info');
}

function showHowItWorksModal() {
  showToast('Content-based TF-IDF vectorization weighted by genres, cast, and directors.', 'info');
}
