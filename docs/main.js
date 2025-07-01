// Load transcripts from JSON and store in localStorage
async function ingestTranscripts() {
  const response = await fetch('transcripts.json');
  const data = await response.json();
  const content = data.map(item => ({
    title: item.title,
    transcript: item.transcript,
    grade_level: fkGrade(item.transcript)
  }));
  localStorage.setItem('content', JSON.stringify(content));
  displayKnownWords();
  document.getElementById('rec-output').innerHTML = '';
}

function loadContent() {
  const stored = localStorage.getItem('content');
  return stored ? JSON.parse(stored) : [];
}

function loadKnownWords() {
  const stored = localStorage.getItem('known_words');
  return stored ? JSON.parse(stored) : [];
}

function saveKnownWords(words) {
  localStorage.setItem('known_words', JSON.stringify(words));
}

function countSyllables(word) {
  word = word.toLowerCase();
  const vowels = 'aeiouy';
  let count = 0;
  let prev = false;
  for (const ch of word) {
    if (vowels.includes(ch)) {
      if (!prev) count++;
      prev = true;
    } else {
      prev = false;
    }
  }
  if (word.endsWith('e') && count > 1) count--;
  return count || 1;
}

function fkGrade(text) {
  const sentences = text.split(/[.!?]+/).filter(s => s.trim());
  const words = text.toLowerCase().match(/\b\w+\b/g) || [];
  const syllables = words.reduce((sum, w) => sum + countSyllables(w), 0);
  const numWords = words.length;
  const numSentences = sentences.length || 1;
  return 0.39 * numWords / numSentences + 11.8 * syllables / numWords - 15.59;
}

function recommendByLevel() {
  const level = parseFloat(document.getElementById('level').value) || 0;
  const content = loadContent();
  if (!content.length) {
    alert('No transcripts ingested yet');
    return;
  }
  const target = level + 1;
  let best = null;
  let bestDiff = Infinity;
  for (const item of content) {
    const diff = Math.abs(item.grade_level - target);
    if (diff < bestDiff) {
      bestDiff = diff;
      best = item;
    }
  }
  displayRecommendation(best, true);
}

function coverageScore(transcript, knownWords) {
  const words = transcript.toLowerCase().match(/\b\w+\b/g) || [];
  if (!words.length) return 0;
  const known = words.filter(w => knownWords.includes(w)).length;
  return known / words.length;
}

function recommendByKnown() {
  const content = loadContent();
  const knownWords = loadKnownWords();
  if (!content.length) {
    alert('No transcripts ingested yet');
    return;
  }
  if (!knownWords.length) {
    alert('No known words stored');
    return;
  }
  let best = null;
  let bestScore = -1;
  for (const item of content) {
    const score = coverageScore(item.transcript, knownWords);
    if (score > bestScore) {
      bestScore = score;
      best = {...item, score};
    }
  }
  displayRecommendation(best, false);
}

function displayRecommendation(item, showGrade) {
  const container = document.getElementById('rec-output');
  if (!item) {
    container.innerHTML = '<p>No recommendation available.</p>';
    return;
  }
  let html = `<div class="card mb-4"><div class="card-body">`;
  html += `<h5 class="card-title">${item.title}</h5>`;
  if (showGrade && item.grade_level !== undefined) {
    html += `<p class="card-text"><strong>Grade level:</strong> ${item.grade_level.toFixed(2)}</p>`;
  }
  if (item.score !== undefined) {
    html += `<p class="card-text"><strong>Known word coverage:</strong> ${(item.score*100).toFixed(1)}%</p>`;
  }
  html += `<pre>${item.transcript}</pre>`;
  html += `</div></div>`;
  container.innerHTML = html;
}

function addWords() {
  const input = document.getElementById('words');
  const words = input.value.split(/\s+/).map(w => w.trim().toLowerCase()).filter(Boolean);
  if (!words.length) return;
  const known = loadKnownWords();
  for (const w of words) if (!known.includes(w)) known.push(w);
  saveKnownWords(known);
  input.value = '';
  displayKnownWords();
}

function displayKnownWords() {
  const list = document.getElementById('known-list');
  const words = loadKnownWords();
  if (!list) return;
  if (!words.length) {
    list.innerHTML = '<p>No known words stored.</p>';
    return;
  }
  let html = '<ul>';
  for (const w of words) {
    html += `<li>${w}</li>`;
  }
  html += '</ul>';
  list.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', () => {
  displayKnownWords();
});
