// Configuration - now points to local API server instead of Notion directly
const API_BASE_URL = 'http://localhost:5000/api';

// State
let articles = [];
let currentArticleIndex = 0;
let currentSectionIndex = 0;
let sections = [];
let isPlaying = false;
let speechSynthesis = window.speechSynthesis;
let currentUtterance = null;
let playbackSpeed = 1;

// DOM Elements
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const player = document.getElementById('player');
const articleTitle = document.getElementById('articleTitle');
const articleMeta = document.getElementById('articleMeta');
const playPauseBtn = document.getElementById('playPause');
const prevArticleBtn = document.getElementById('prevArticle');
const nextArticleBtn = document.getElementById('nextArticle');
const rewindBtn = document.getElementById('rewind');
const forwardBtn = document.getElementById('forward');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');
const currentTime = document.getElementById('currentTime');
const totalTime = document.getElementById('totalTime');
const playlistItems = document.getElementById('playlistItems');
const playlistCount = document.getElementById('playlistCount');

// Initialize
async function init() {
    try {
        await loadArticles();
        setupEventListeners();
        if (articles.length > 0) {
            loadArticle(0);
            player.style.display = 'block';
        }
        loading.style.display = 'none';
    } catch (err) {
        showError('Failed to load articles: ' + err.message);
        loading.style.display = 'none';
    }
}

// Load articles from backend API
async function loadArticles() {
    const response = await fetch(`${API_BASE_URL}/articles`);

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    if (data.error) {
        throw new Error(data.error);
    }

    articles = data.articles;

    // Load content for each article
    for (let article of articles) {
        article.content = await loadArticleContent(article.id);
    }

    renderPlaylist();
}

// Load article content blocks
async function loadArticleContent(pageId) {
    const response = await fetch(`${API_BASE_URL}/article/${pageId}`);

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    if (data.error) {
        throw new Error(data.error);
    }

    return data.content;
}

// Load an article
function loadArticle(index) {
    if (index < 0 || index >= articles.length) return;

    stop();
    currentArticleIndex = index;
    const article = articles[index];

    // Update UI
    articleTitle.textContent = article.title;

    // Show tags
    articleMeta.innerHTML = article.tags.map(tag =>
        `<span class="tag ${tag === 'Product Release' ? 'release' : ''}">${tag}</span>`
    ).join('');

    // Prepare sections for reading
    sections = [];

    // Add title
    sections.push(`Article ${index + 1} of ${articles.length}. ${article.title}. From ${article.source}.`);

    // Add content sections
    for (let block of article.content) {
        if (block.type === 'heading') {
            sections.push(block.text);
        } else if (block.type === 'text' || block.type === 'callout') {
            sections.push(block.text);
        }
    }

    currentSectionIndex = 0;
    updatePlaylistHighlight();
    updateButtonStates();
}

// Play/Pause
function togglePlayPause() {
    if (isPlaying) {
        pause();
    } else {
        play();
    }
}

function play() {
    if (currentSectionIndex >= sections.length) {
        nextArticle();
        return;
    }

    isPlaying = true;
    playPauseBtn.textContent = '⏸';

    speak(sections[currentSectionIndex]);
}

function pause() {
    isPlaying = false;
    playPauseBtn.textContent = '▶';
    speechSynthesis.cancel();
}

function stop() {
    isPlaying = false;
    playPauseBtn.textContent = '▶';
    speechSynthesis.cancel();
    currentSectionIndex = 0;
    updateProgress();
}

// Speech
function speak(text) {
    speechSynthesis.cancel();

    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.rate = playbackSpeed;
    currentUtterance.pitch = 1;
    currentUtterance.volume = 1;

    // Try to use a good English voice
    const voices = speechSynthesis.getVoices();
    const goodVoice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Enhanced'))
                   || voices.find(v => v.lang.startsWith('en-US'))
                   || voices.find(v => v.lang.startsWith('en'));
    if (goodVoice) currentUtterance.voice = goodVoice;

    currentUtterance.onend = () => {
        currentSectionIndex++;
        updateProgress();

        if (currentSectionIndex < sections.length && isPlaying) {
            speak(sections[currentSectionIndex]);
        } else if (currentSectionIndex >= sections.length) {
            // Article finished
            nextArticle();
        }
    };

    currentUtterance.onerror = (event) => {
        console.error('Speech error:', event);
        pause();
    };

    speechSynthesis.speak(currentUtterance);
    updateProgress();
}

// Navigation
function prevArticle() {
    if (currentArticleIndex > 0) {
        loadArticle(currentArticleIndex - 1);
    }
}

function nextArticle() {
    if (currentArticleIndex < articles.length - 1) {
        loadArticle(currentArticleIndex + 1);
        if (isPlaying) play();
    } else {
        stop();
    }
}

function rewind() {
    if (currentSectionIndex > 0) {
        currentSectionIndex = Math.max(0, currentSectionIndex - 1);
        if (isPlaying) {
            play();
        }
    }
}

function forward() {
    if (currentSectionIndex < sections.length - 1) {
        currentSectionIndex++;
        if (isPlaying) {
            play();
        }
    }
}

// Progress
function updateProgress() {
    const progress = sections.length > 0 ? (currentSectionIndex / sections.length) * 100 : 0;
    progressFill.style.width = progress + '%';

    currentTime.textContent = formatTime(currentSectionIndex * 15); // Rough estimate
    totalTime.textContent = formatTime(sections.length * 15);
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Playlist
function renderPlaylist() {
    playlistCount.textContent = articles.length;

    playlistItems.innerHTML = articles.map((article, index) => `
        <div class="playlist-item ${index === currentArticleIndex ? 'active' : ''}"
             data-index="${index}">
            <span class="playlist-number">${index + 1}</span>
            <div style="flex: 1;">
                <div class="playlist-title">${article.title}</div>
                <div class="playlist-meta">${article.source}</div>
            </div>
        </div>
    `).join('');
}

function updatePlaylistHighlight() {
    document.querySelectorAll('.playlist-item').forEach((item, index) => {
        item.classList.toggle('active', index === currentArticleIndex);
    });
}

// Speed control
function setSpeed(speed) {
    playbackSpeed = speed;
    document.querySelectorAll('.speed-btn').forEach(btn => {
        btn.classList.toggle('active', parseFloat(btn.dataset.speed) === speed);
    });

    if (isPlaying) {
        const wasPlaying = isPlaying;
        pause();
        if (wasPlaying) play();
    }
}

// Button states
function updateButtonStates() {
    prevArticleBtn.disabled = currentArticleIndex === 0;
    nextArticleBtn.disabled = currentArticleIndex === articles.length - 1;
}

// Event Listeners
function setupEventListeners() {
    playPauseBtn.addEventListener('click', togglePlayPause);
    prevArticleBtn.addEventListener('click', prevArticle);
    nextArticleBtn.addEventListener('click', nextArticle);
    rewindBtn.addEventListener('click', rewind);
    forwardBtn.addEventListener('click', forward);

    progressBar.addEventListener('click', (e) => {
        const rect = progressBar.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        currentSectionIndex = Math.floor(sections.length * percent);
        updateProgress();
        if (isPlaying) play();
    });

    document.querySelectorAll('.speed-btn').forEach(btn => {
        btn.addEventListener('click', () => setSpeed(parseFloat(btn.dataset.speed)));
    });

    playlistItems.addEventListener('click', (e) => {
        const item = e.target.closest('.playlist-item');
        if (item) {
            const index = parseInt(item.dataset.index);
            loadArticle(index);
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space') {
            e.preventDefault();
            togglePlayPause();
        } else if (e.code === 'ArrowLeft') {
            rewind();
        } else if (e.code === 'ArrowRight') {
            forward();
        } else if (e.code === 'ArrowUp') {
            e.preventDefault();
            prevArticle();
        } else if (e.code === 'ArrowDown') {
            e.preventDefault();
            nextArticle();
        }
    });
}

function showError(message) {
    error.textContent = message;
    error.style.display = 'block';
}

// Load voices (needed for some browsers)
speechSynthesis.addEventListener('voiceschanged', () => {
    console.log('Voices loaded:', speechSynthesis.getVoices().length);
});

// Start
init();
