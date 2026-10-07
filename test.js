
// ============================================================
// DATA
// ============================================================
let SYLLABUS = null;
let QUESTIONS = [];
let LESSONS = [];
let OFFICIAL_RAW = null;

async function loadData() {
  try {
    const [syl, qs, ls, raw] = await Promise.all([
      fetch('data/syllabus.json').then(r => r.json()),
      fetch('data/questions.json').then(r => r.json()).catch(() => []),
      fetch('data/lessons.json').then(r => r.json()).catch(() => []),
      fetch('data/official-syllabus.json').then(r => r.json()).catch(() => null),
    ]);
    SYLLABUS = syl;
    QUESTIONS = Array.isArray(qs) ? qs : [];
    LESSONS = Array.isArray(ls) ? ls : [];
    OFFICIAL_RAW = raw;
  } catch(e) {
    console.error('Data load error', e);
    showToast('שגיאה בטעינת נתונים');
  }
}

// ============================================================
// PERSISTENCE
// ============================================================
const NS = 'medexam2_';
const DB = {
  get(k, d = null) { try { return JSON.parse(localStorage.getItem(NS+k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(NS+k, JSON.stringify(v)); } catch {} }
};

function getState() {
  const defState = {
    streak: 0, lastDate: null, xpToday: 0, xpTotal: 0,
    totalAnswered: 0, totalCorrect: 0,
    missionsCompleted: [],
    mastery: {},
    settings: { sounds: true, haptics: true }
  };
  const saved = DB.get('state');
  if (!saved) return defState;
  return { ...defState, ...saved, settings: { ...defState.settings, ...(saved.settings || {}) } };
}
function saveState(s) { DB.set('state', s); }

// ============================================================
// STREAK
// ============================================================
function todayStr() { return new Date().toISOString().split('T')[0]; }
function yesterdayStr() { return new Date(Date.now()-86400000).toISOString().split('T')[0]; }

function touchStreak(state) {
  const t = todayStr();
  if (state.lastDate === t) return state;
  if (state.lastDate === yesterdayStr()) state.streak++;
  else state.streak = 1;
  state.lastDate = t;
  state.xpToday = 0;
  state.missionsCompleted = [];
  return state;
}

// ============================================================
// XP
// ============================================================
const XP_CORRECT = 10, XP_CARD = 5, XP_GOAL = 100;
function addXP(state, n) {
  state.xpToday = Math.min(state.xpToday + n, XP_GOAL * 3);
  state.xpTotal += n;
  return state;
}

// ============================================================
// MASTERY / SPACED REPETITION
// ============================================================
const MASTERY_CLS = ['unseen','learning','familiar','mastered'];

function getMastery(state, subId) {
  return state.mastery[subId] || { level: 0, correct: 0, total: 0, nextReview: null };
}

function updateMastery(state, subId, correct) {
  const m = getMastery(state, subId);
  m.total++;
  if (correct) m.correct++;
  const acc = m.total > 0 ? m.correct / m.total : 0;
  if (m.total >= 5 && acc >= 0.90) m.level = 3;
  else if (m.total >= 3 && acc >= 0.70) m.level = 2;
  else m.level = Math.max(1, m.level);
  const days = [1,1,3,7][Math.min(m.level, 3)];
  m.nextReview = new Date(Date.now() + (correct ? days : 1) * 86400000).toISOString().split('T')[0];
  state.mastery[subId] = m;
  return state;
}

function getAllSubtopics() {
  if (!SYLLABUS) return [];
  const out = [];
  for (const area of SYLLABUS.areas)
    for (const ch of area.chapters)
      for (const sub of ch.subtopics)
        out.push({ ...sub, chapterId: ch.id, areaId: area.id });
  return out;
}

function getWeakSubtopics(state, limit = 6) {
  const t = todayStr();
  return getAllSubtopics()
    .map(s => ({ ...s, m: getMastery(state, s.id) }))
    .filter(s => s.m.level < 3)
    .sort((a, b) => {
      if (a.m.level !== b.m.level) return a.m.level - b.m.level;
      const ad = !a.m.nextReview || a.m.nextReview <= t;
      const bd = !b.m.nextReview || b.m.nextReview <= t;
      if (ad && !bd) return -1;
      if (!ad && bd) return 1;
      return (a.m.correct / Math.max(a.m.total, 1)) - (b.m.correct / Math.max(b.m.total, 1));
    })
    .slice(0, limit);
}

// ============================================================
// MISSIONS
// ============================================================
function buildMissions(state) {
  const missions = [];

  // 1. New lesson
  const newLesson = LESSONS.find(l => {
    const chSubs = getAllSubtopics().filter(s => s.chapterId === l.chapterId);
    return chSubs.some(s => getMastery(state, s.id).level === 0);
  }) || LESSONS[0];
  missions.push({
    id: 'learn_new', type: 'learn', icon: '📚',
    title: 'שיעור חדש',
    meta: newLesson ? `${newLesson.title} • ~${newLesson.estimatedMinutes} דק'` : 'כל השיעורים הושלמו!',
    lessonId: newLesson?.id, xp: 30,
  });

  // 2. Weak review
  const weakQs = QUESTIONS.filter(q => getMastery(state, q.subtopicId).level < 2)
    .sort(() => Math.random() - .5).slice(0, 5);
  missions.push({
    id: 'review_weak', type: 'review', icon: '🎯',
    title: 'חיזוק נקודות חולשה',
    meta: `${weakQs.length} שאלות · נושאים חלשים`,
    questionIds: weakQs.map(q => q.id), xp: 25,
  });

  // 3. Area-of-day
  if (SYLLABUS) {
    const areaIdx = new Date().getDay() % SYLLABUS.areas.length;
    const area = SYLLABUS.areas[areaIdx];
    const aQs = QUESTIONS.filter(q => q.areaId === area.id).sort(() => Math.random() - .5).slice(0, 5);
    missions.push({
      id: 'area_daily', type: 'practice', icon: area.icon,
      title: `תרגול: ${area.title}`,
      meta: `${aQs.length} שאלות · ${area.titleEn}`,
      questionIds: aQs.map(q => q.id), xp: 20,
    });
  }
  return missions;
}

// ============================================================
// NAVIGATION
// ============================================================
function switchTab(name, el) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
  document.getElementById('screen-' + name).classList.add('active');
  el.classList.add('active');
  if (name === 'progress') renderProgress();
  if (name === 'explore') renderExplore();
  if (name === 'profile') renderProfile();
  if (name === 'flashcards') renderFlashcards();
}

// ============================================================
// HOME
// ============================================================
function renderHome() {
  let state = getState();
  state = touchStreak(state);
  saveState(state);

  const h = new Date().getHours();
  document.getElementById('greeting').textContent = h<12?'בוקר טוב ☀️':h<18?'צהריים טובים 🌤️':'ערב טוב 🌙';
  const DAYS=['ראשון','שני','שלישי','רביעי','חמישי','שישי','שבת'];
  const MONTHS=['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];
  const d = new Date();
  document.getElementById('greeting-date').textContent = `יום ${DAYS[d.getDay()]}, ${d.getDate()} ${MONTHS[d.getMonth()]}`;
  document.getElementById('streak-num').textContent = state.streak;

  const pct = Math.min((state.xpToday / XP_GOAL) * 100, 100);
  document.getElementById('xp-display').textContent = `${state.xpToday} / ${XP_GOAL} XP`;
  document.getElementById('xp-fill').style.width = pct + '%';

  // Missions
  const missions = buildMissions(state);
  document.getElementById('missions').innerHTML = missions.map(m => {
    const done = state.missionsCompleted.includes(m.id);
    return `<button class="mission-item ${done?'done':''}" onclick='startMission(${JSON.stringify(m).replace(/"/g, "&quot;")})' style="border:none; text-align:inherit; font-family:inherit; width:100%">
      <div class="m-icon ${m.type}">${m.icon}</div>
      <div class="m-info"><div class="m-title">${m.title}</div><div class="m-meta">${m.meta}</div></div>
      ${done ? '<div class="m-badge">✓</div>' : `<div class="m-xp">⭐${m.xp}</div>`}
    </button>`;
  }).join('');

  // Areas
  if (!SYLLABUS) return;
  document.getElementById('areas-grid').innerHTML = SYLLABUS.areas.map(area => {
    const subs = area.chapters.flatMap(c => c.subtopics);
    const mastered = subs.filter(s => getMastery(state, s.id).level >= 3).length;
    const pctA = subs.length > 0 ? Math.round((mastered / subs.length) * 100) : 0;
    return `<div class="area-card" style="background:linear-gradient(135deg,${area.color}CC,${area.color})" onclick="startAreaPractice('${area.id}')">
      <div class="a-icon">${area.icon}</div>
      <div class="a-title">${area.title}</div>
      <div class="a-sub">${area.titleEn}</div>
      <div class="a-track"><div class="a-fill" style="width:${pctA}%"></div></div>
      <div class="a-pct">${pctA}% שולטים · ${subs.length} נושאים</div>
    </div>`;
  }).join('');
}

// ============================================================
// EXPLORE
// ============================================================
let exploreQ = '';
function renderExplore() {
  if (!SYLLABUS) return;
  const state = getState();
  const q = exploreQ.toLowerCase().trim();
  let html = '';
  for (const area of SYLLABUS.areas) {
    const filteredChs = area.chapters.filter(ch => {
      if (!q) return true;
      if (ch.title.includes(q) || ch.titleEn.toLowerCase().includes(q)) return true;
      return ch.subtopics.some(s => s.title.includes(q) || s.titleEn.toLowerCase().includes(q));
    });
    if (!filteredChs.length) continue;
    html += `<div class="explore-area">
      <div class="ea-hdr">
        <div class="area-dot" style="background:${area.color}"></div>
        <div class="area-name-txt">${area.icon} ${area.title}</div>
      </div>`;
    for (const ch of filteredChs) {
      const total = ch.subtopics.length;
      const mastered = ch.subtopics.filter(s => getMastery(state, s.id).level >= 2).length;
      const pct = Math.round((mastered / total) * 100);
      html += `<div class="chapter-card">
        <div class="ch-hdr" onclick="toggleChapter('${ch.id}')">
          <div class="ch-info">
            <div class="ch-name">${ch.title}</div>
            <div class="ch-meta">${ch.titleEn} · ${total} נושאי משנה</div>
          </div>
          ${ringHTML(pct, area.color)}
          <span class="ch-chev" id="chev-${ch.id}">▼</span>
        </div>
        <div class="ch-subs" id="csubs-${ch.id}">
          ${ch.subtopics.map(s => {
            const m = getMastery(state, s.id);
            const cls = MASTERY_CLS[m.level];
            return `<span class="sub-pill ${cls}" onclick="practiceSubtopic('${s.id}','${ch.id}','${area.id}')">
              <span class="sub-dot"></span>${s.title}
            </span>`;
          }).join('')}
          <div><span class="practice-btn" onclick="event.stopPropagation();startChapterPractice('${ch.id}','${area.id}')">📝 תרגל פרק זה</span></div>
          <div><span class="practice-btn" style="background:rgba(52,199,89,.1);color:var(--success)" onclick="event.stopPropagation();startChapterLesson('${ch.id}')">📖 שיעור לפרק זה</span></div>
        </div>
      </div>`;
    }
    html += '</div>';
  }
  document.getElementById('explore-content').innerHTML = html || '<div class="empty"><div class="empty-e">🔍</div><div class="empty-t">לא נמצאו תוצאות</div></div>';
}

function filterExplore(v) { exploreQ = v; renderExplore(); }
function toggleChapter(id) {
  document.getElementById('csubs-'+id)?.classList.toggle('open');
  document.getElementById('chev-'+id)?.classList.toggle('open');
}

function ringHTML(pct, color) {
  const r = 14, circ = 2 * Math.PI * r, dash = (pct / 100) * circ;
  return `<svg class="ch-ring" viewBox="0 0 36 36">
    <circle cx="18" cy="18" r="${r}" fill="none" stroke="#E5E5EA" stroke-width="3"/>
    <circle cx="18" cy="18" r="${r}" fill="none" stroke="${color}" stroke-width="3"
      stroke-dasharray="${dash} ${circ}" stroke-linecap="round" transform="rotate(-90 18 18)"/>
    <text x="18" y="22" text-anchor="middle" font-size="9" font-weight="700" fill="${color}">${pct}%</text>
  </svg>`;
}

// ============================================================
// PROGRESS
// ============================================================
function renderProgress() {
  if (!SYLLABUS) return;
  const state = getState();
  let mastered = 0, learning = 0, unseen = 0;
  for (const area of SYLLABUS.areas)
    for (const ch of area.chapters)
      for (const sub of ch.subtopics) {
        const l = getMastery(state, sub.id).level;
        if (l >= 3) mastered++;
        else if (l >= 1) learning++;
        else unseen++;
      }
  document.getElementById('s-mastered').textContent = mastered;
  document.getElementById('s-learning').textContent = learning;
  document.getElementById('s-unseen').textContent = unseen;

  let html = '';
  for (const area of SYLLABUS.areas) {
    const subs = area.chapters.flatMap(c => c.subtopics);
    const m = subs.filter(s => getMastery(state, s.id).level >= 3).length;
    const pct = Math.round((m / subs.length) * 100);
    html += `<div class="mastery-area">
      <div class="ma-hdr" id="mahdr-${area.id}" onclick="toggleMasteryArea('${area.id}')">
        <span class="ma-icon">${area.icon}</span>
        <span class="ma-name">${area.title}</span>
        <span class="ma-pct" style="color:${area.color}">${pct}%</span>
        <span class="ma-ch" id="mach-${area.id}">▼</span>
      </div>
      <div class="ma-body" id="mabody-${area.id}">`;
    for (const ch of area.chapters) {
      html += `<div class="ch-row">
        <div class="ch-row-name">${ch.title}</div>
        <div class="pills-wrap">`;
      for (const sub of ch.subtopics) {
        const l = getMastery(state, sub.id).level;
        html += `<span class="sub-pill ${MASTERY_CLS[l]}" onclick="practiceSubtopic('${sub.id}','${ch.id}','${area.id}')">
          <span class="sub-dot"></span>${sub.title}
        </span>`;
      }
      html += '</div></div>';
    }
    html += '</div></div>';
  }
  document.getElementById('mastery-map').innerHTML = html;
}

function toggleMasteryArea(id) {
  const hdr = document.getElementById('mahdr-'+id);
  const body = document.getElementById('mabody-'+id);
  const ch = document.getElementById('mach-'+id);
  const isOpen = body.classList.toggle('open');
  ch.classList.toggle('open', isOpen);
  hdr.classList.toggle('open-hdr', isOpen);
}

// ============================================================
// PROFILE
// ============================================================
function renderProfile() {
  const state = getState();
  document.getElementById('p-streak').textContent = state.streak + ' ימים';
  document.getElementById('p-xp').textContent = state.xpTotal.toLocaleString() + ' XP';
  document.getElementById('p-ans').textContent = state.totalAnswered;
  const acc = state.totalAnswered > 0 ? Math.round((state.totalCorrect/state.totalAnswered)*100) + '%' : '—';
  document.getElementById('p-acc').textContent = acc;
  const seen = Object.keys(state.mastery).length;
  document.getElementById('p-seen').textContent = `${seen} / 175`;
  ['sounds','haptics'].forEach(k => {
    const el = document.getElementById('tog-'+k);
    if (el) el.classList.toggle('on', !!state.settings?.[k]);
  });
  if (OFFICIAL_RAW?.books) {
    document.getElementById('books-list').innerHTML = OFFICIAL_RAW.books.map(b =>
      `<div style="font-size:14px;color:var(--label2);padding:4px 0;border-bottom:.5px solid var(--sep);line-height:1.4">
        <strong>${b.title}</strong><br>
        <span style="color:var(--label4)">${b.edition} · ${b.year_in_official_syllabus}</span>
      </div>`
    ).join('');
  }
}

function toggleSetting(k) {
  const state = getState();
  if (!state.settings) state.settings = {};
  state.settings[k] = !state.settings[k];
  saveState(state);
  renderProfile();
  haptic();
}

// ============================================================
// MISSION DISPATCH
// ============================================================
function startMission(mission) {
  haptic();
  if (mission.lessonId) {
    // Try exact ID first, then fallback to chapterId match
    let l = LESSONS.find(x => x.id === mission.lessonId);
    if (!l) {
      // lessonId may be like "learn_new" – find first unstarted lesson
      l = LESSONS.find(lesson => {
        const chSubs = getAllSubtopics().filter(s => s.chapterId === lesson.chapterId);
        return chSubs.some(s => getMastery(getState(), s.id).level === 0);
      }) || LESSONS[0];
    }
    if (l) { startLesson(l, mission); return; }
  }
  if (mission.questionIds?.length) {
    const qs = mission.questionIds.map(id => QUESTIONS.find(q => q.id === id)).filter(Boolean);
    if (qs.length) { startQuizSession(qs, mission); return; }
  }
  // Fallback: if this is a "learn_new" mission and we have lessons, just start the first one
  // If nothing worked, just open the first available lesson
  if (LESSONS.length > 0) { startLesson(LESSONS[0], mission); return; }
  showToast('תוכן בהכנה — הוסף שאלות ל-questions.json');
}

function startAreaPractice(areaId) {
  haptic();
  const qs = QUESTIONS.filter(q => q.areaId === areaId).sort(() => Math.random() - .5).slice(0, 6);
  if (!qs.length) { showToast('אין שאלות לתחום זה עדיין'); return; }
  const area = SYLLABUS?.areas.find(a => a.id === areaId);
  startQuizSession(qs, { id: 'area_'+areaId, title: `תרגול: ${area?.title||areaId}`, xp: 20 });
}

function startChapterPractice(chId, areaId) {
  haptic();
  const qs = QUESTIONS.filter(q => q.chapterId === chId).sort(() => Math.random() - .5).slice(0, 5);
  if (!qs.length) { showToast('אין שאלות לפרק זה עדיין'); return; }
  startQuizSession(qs, { id: 'ch_'+chId, title: 'תרגול פרק', xp: 15 });
}

function startChapterLesson(chId) {
  haptic();
  const lesson = LESSONS.find(l => l.chapterId === chId);
  if (!lesson) { showToast('אין שיעור לפרק זה עדיין'); return; }
  startLesson(lesson, { id: 'lesson_'+chId, title: lesson.title, xp: 20 });
}

function practiceSubtopic(subId, chId, areaId) {
  haptic();
  const qs = QUESTIONS.filter(q => q.subtopicId === subId);
  if (!qs.length) {
    const lesson = LESSONS.find(l => l.chapterId === chId);
    if (lesson) { startLesson(lesson, { id: 'sub_'+subId, title: 'למידה', xp: 10 }); return; }
    showToast('תוכן בהכנה לנושא זה');
    return;
  }
  startQuizSession(qs, { id: 'sub_'+subId, title: 'תרגול נושא', xp: 15 });
}

// ============================================================
// LESSON FLOW
// ============================================================

// ============================================================
// FLASHCARDS
// ============================================================
function sm2(card, grade) {
  const quality = [1, 2, 4, 5][grade];
  let { interval, repetitions, easeFactor } = card;
  if (quality < 3) {
    repetitions = 0;
    interval = 1;
  } else {
    if (repetitions === 0) interval = 1;
    else if (repetitions === 1) interval = 6;
    else interval = Math.round(interval * easeFactor);
    repetitions++;
  }
  easeFactor = Math.max(1.3, easeFactor + 0.1 - (5-quality)*(0.08 + (5-quality)*0.02));
  const dueDate = Date.now() + interval * 24 * 60 * 60 * 1000;
  return { ...card, interval, repetitions, easeFactor, dueDate };
}

function initFlashcards() {
  let data = DB.get('flashcards');
  if (!data) {
    data = { decks: [] };
    if (SYLLABUS && SYLLABUS.areas) {
      for (const area of SYLLABUS.areas) {
        for (const ch of area.chapters) {
          const deckId = 'deck_' + ch.id;
          const cards = [];
          for (const sub of ch.subtopics) {
            let back = sub.titleEn;
            // Try to find a lesson card
            const lesson = LESSONS.find(l => l.chapterId === ch.id);
            if (lesson && lesson.cards) {
              const matchingCard = lesson.cards.find(c => c.title && c.title.includes(sub.title));
              if (matchingCard && matchingCard.keyPoints && matchingCard.keyPoints.length > 0) {
                back = matchingCard.keyPoints[0];
              } else {
                 const genericCard = lesson.cards.find(c => c.keyPoints && c.keyPoints.length > 0);
                 if (genericCard) back = genericCard.keyPoints[0];
              }
            }
            cards.push({
              id: 'c_' + Math.random().toString(36).substr(2,9),
              front: sub.title,
              back: back,
              deckId, interval: 1, repetitions: 0, easeFactor: 2.5, dueDate: Date.now(), createdAt: Date.now()
            });
          }
          data.decks.push({
            id: deckId, name: ch.title, subtopicId: null, chapterId: ch.id, areaId: area.id, cards
          });
        }
      }
      // Add questions-based deck for terms/enzymes
      const termQs = QUESTIONS.filter(q => q.tags && (q.tags.includes('Enzyme') || q.tags.includes('Term') || q.question.includes('אנזים')));
      if (termQs.length > 0) {
        const tcards = termQs.map(q => ({
          id: 'c_' + Math.random().toString(36).substr(2,9),
          front: q.question.substring(0, 50) + '...',
          back: (q.explanation || q.options[q.correctIndex] || '').substring(0, 100),
          deckId: 'deck_terms', interval: 1, repetitions: 0, easeFactor: 2.5, dueDate: Date.now(), createdAt: Date.now()
        }));
        data.decks.push({ id: 'deck_terms', name: 'מונחים ואנזימים', subtopicId: null, chapterId: null, areaId: null, cards: tcards });
      }
    }
    DB.set('flashcards', data);
  }
}

function renderFlashcards() {
  const data = DB.get('flashcards', { decks: [] });
  const now = Date.now();
  let totalDue = 0;
  
  let html = `<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
    <h2 style="font-size:20px;font-weight:700;">חפיסות</h2>
    <button class="btn btn-ghost" style="width:auto;padding:8px 16px" onclick="createDeckPrompt()">+ חדש</button>
  </div>`;
  
  const decksHtml = data.decks.map(deck => {
    const dueCount = deck.cards.filter(c => c.dueDate <= now).length;
    totalDue += dueCount;
    return `
      <div class="deck-row" onclick="viewDeck('${deck.id}')">
        <div>
          <div style="font-weight:600;font-size:16px">${deck.name}</div>
          <div style="font-size:13px;color:var(--label4)">${deck.cards.length} כרטיסיות</div>
        </div>
        ${dueCount > 0 ? `<div class="deck-due-badge">${dueCount} להיום</div>` : '<div style="color:var(--label4);font-size:12px">הכל תורגל</div>'}
      </div>
    `;
  }).join('');

  let hero = `
    <div style="background:var(--surface);border-radius:var(--r-xl);padding:24px;text-align:center;margin-bottom:24px;box-shadow:var(--shadow)">
      <div style="font-size:40px;margin-bottom:8px">🃏</div>
      <div style="font-size:18px;font-weight:700;margin-bottom:4px">כרטיסיות להיום</div>
      <div style="font-size:14px;color:var(--label3);margin-bottom:16px">${totalDue} כרטיסיות ממתינות לחזרה</div>
      <button class="btn btn-accent" ${totalDue===0?'disabled':''} onclick="startDueSession()">התחל חזרה</button>
    </div>
  `;

  document.getElementById('flashcards-content').innerHTML = hero + html + decksHtml;
}

function createDeckPrompt() {
  const name = prompt('שם החפיסה:');
  if (name) {
    const data = DB.get('flashcards');
    data.decks.push({ id: 'deck_'+Date.now(), name, cards: [] });
    DB.set('flashcards', data);
    renderFlashcards();
  }
}

function viewDeck(deckId) {
  const data = DB.get('flashcards');
  const deck = data.decks.find(d => d.id === deckId);
  if (!deck) return;
  const now = Date.now();
  const dueCards = deck.cards.filter(c => c.dueDate <= now);
  
  let cardsList = deck.cards.map(c => `
    <div style="padding:12px;border-bottom:1px solid var(--sep);display:flex;justify-content:space-between;align-items:center">
      <div style="flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:14px;margin-left:10px">${c.front}</div>
      <div style="display:flex;gap:8px">
        <button onclick="editCard('${deckId}', '${c.id}')" style="background:none;border:none;font-size:16px">✏️</button>
        <button onclick="deleteCard('${deckId}', '${c.id}')" style="background:none;border:none;font-size:16px">🗑️</button>
      </div>
    </div>
  `).join('');
  
  openOverlay(`
    <div class="ov-hdr">
      <button class="close-btn" onclick="closeOverlay(); renderFlashcards()">✕</button>
      <div style="flex:1;text-align:center;font-weight:600">${deck.name}</div>
      <button class="btn btn-ghost" style="width:auto;padding:4px 8px;font-size:20px" onclick="createCard('${deckId}')">+</button>
    </div>
    <div class="ov-body">
      <button class="btn btn-accent" style="margin-bottom:16px" ${dueCards.length===0?'disabled':''} onclick="playFlashcardSession('${deckId}')">
        תרגל ${dueCards.length} כרטיסיות
      </button>
      <div style="background:var(--surface);border-radius:var(--r-md)">
        ${cardsList}
      </div>
      <button class="btn btn-ghost" style="margin-top:16px;color:var(--danger)" onclick="deleteDeck('${deckId}')">מחק חפיסה</button>
    </div>
  `);
}

function createCard(deckId) {
  const front = prompt('צד קדמי (שאלה/מונח):');
  if (!front) return;
  const back = prompt('צד אחורי (תשובה/הסבר):');
  if (!back) return;
  const data = DB.get('flashcards');
  const deck = data.decks.find(d => d.id === deckId);
  deck.cards.push({
    id: 'c_'+Date.now(), front, back, deckId,
    interval: 1, repetitions: 0, easeFactor: 2.5, dueDate: Date.now(), createdAt: Date.now()
  });
  DB.set('flashcards', data);
  viewDeck(deckId);
}

function editCard(deckId, cardId) {
  const data = DB.get('flashcards');
  const deck = data.decks.find(d => d.id === deckId);
  const card = deck.cards.find(c => c.id === cardId);
  const front = prompt('צד קדמי:', card.front);
  if (front!==null) card.front = front;
  const back = prompt('צד אחורי:', card.back);
  if (back!==null) card.back = back;
  DB.set('flashcards', data);
  viewDeck(deckId);
}

function deleteCard(deckId, cardId) {
  if (!confirm('למחוק כרטיסיה זו?')) return;
  const data = DB.get('flashcards');
  const deck = data.decks.find(d => d.id === deckId);
  deck.cards = deck.cards.filter(c => c.id !== cardId);
  DB.set('flashcards', data);
  viewDeck(deckId);
}

function deleteDeck(deckId) {
  if (!confirm('למחוק את כל החפיסה?')) return;
  const data = DB.get('flashcards');
  data.decks = data.decks.filter(d => d.id !== deckId);
  DB.set('flashcards', data);
  closeOverlay();
  renderFlashcards();
}

let FC_SESSION = [];
let FC_IDX = 0;

function startDueSession() {
  const data = DB.get('flashcards', { decks: [] });
  const now = Date.now();
  let due = [];
  data.decks.forEach(d => {
    d.cards.forEach(c => {
      if (c.dueDate <= now) due.push({...c, _deckId: d.id});
    });
  });
  if (due.length === 0) { showToast('אין כרטיסיות לתרגול'); return; }
  due.sort(() => Math.random() - 0.5);
  FC_SESSION = due;
  FC_IDX = 0;
  playFlashcard();
}

function playFlashcardSession(deckId) {
  const data = DB.get('flashcards');
  const deck = data.decks.find(d => d.id === deckId);
  const now = Date.now();
  let due = deck.cards.filter(c => c.dueDate <= now).map(c => ({...c, _deckId: deckId}));
  if (due.length === 0) return;
  due.sort(() => Math.random() - 0.5);
  FC_SESSION = due;
  FC_IDX = 0;
  playFlashcard();
}

function playFlashcard() {
  if (FC_IDX >= FC_SESSION.length) {
    closeOverlay();
    renderFlashcards();
    showToast('התרגול הושלם! 🎉');
    return;
  }
  const c = FC_SESSION[FC_IDX];
  const pct = Math.round((FC_IDX / FC_SESSION.length) * 100);
  
  openOverlay(`
    <div class="ov-hdr">
      <button class="close-btn" onclick="closeOverlay(); renderFlashcards()">✕</button>
      <div class="prog-track"><div class="prog-fill" style="width:${pct}%"></div></div>
      <div style="font-size:14px;font-weight:600;margin-right:12px">${FC_IDX+1}/${FC_SESSION.length}</div>
    </div>
    <div class="ov-body" style="display:flex;flex-direction:column;justify-content:center">
      <div class="fc-scene" onclick="document.getElementById('fc-inner').classList.toggle('flipped'); document.getElementById('fc-grades').style.display='grid'">
        <div class="fc-card" id="fc-inner">
          <div class="fc-face fc-front">${c.front}</div>
          <div class="fc-face fc-back">${c.back}</div>
        </div>
      </div>
      <div class="grade-btns" id="fc-grades" style="display:none">
        <button class="grade-btn grade-again" onclick="gradeCard(0)">שוב 🔁</button>
        <button class="grade-btn grade-hard" onclick="gradeCard(1)">קשה 😬</button>
        <button class="grade-btn grade-good" onclick="gradeCard(2)">טוב 👍</button>
        <button class="grade-btn grade-easy" onclick="gradeCard(3)">קל ⭐</button>
      </div>
    </div>
  `);
}

function gradeCard(grade) {
  const c = FC_SESSION[FC_IDX];
  const updated = sm2(c, grade);
  
  // Save
  const data = DB.get('flashcards');
  const deck = data.decks.find(d => d.id === c._deckId);
  if (deck) {
    const idx = deck.cards.findIndex(x => x.id === c.id);
    if (idx !== -1) {
      deck.cards[idx] = { ...deck.cards[idx], ...updated };
      delete deck.cards[idx]._deckId;
    }
  }
  DB.set('flashcards', data);
  
  FC_IDX++;
  playFlashcard();
}

let CUR_LESSON = null, CUR_LESSON_IDX = 0, CUR_MISSION = null;


let GAME_CHALLENGES = [];
let GAME_IDX = 0;
let GAME_COMBO = 0;
let GAME_MISSION = null;

function buildGameChallenges(lesson) {
  const challenges = [];
  const cards = lesson.cards || [];
  
  for (const card of cards) {
    if (card.type !== 'concept') continue;
    const kps = card.keyPoints || [];
    
    // TRUE_FALSE
    if (kps.length > 0) {
      challenges.push({ type: 'TRUE_FALSE', text: kps[0], answer: true });
      if (kps.length > 1 && Math.random() > 0.5) {
        // Create a fake false by reversing the sentence roughly, or just push true
        challenges.push({ type: 'TRUE_FALSE', text: kps[1], answer: true });
      }
    }
    
    // FILL_BLANK
    if (card.content) {
      const boldMatch = card.content.match(/\*\*(.*?)\*\*/);
      if (boldMatch) {
         let term = boldMatch[1];
         let sentence = card.content.split('. ').find(s => s.includes(`**${term}**`));
         if (sentence) {
             sentence = sentence.replace(`**${term}**`, '___');
             let options = [term, 'מולקולה אחרת', 'תא חי'].sort(() => Math.random() - 0.5);
             challenges.push({ type: 'FILL_BLANK', text: sentence, options, answer: term, reteach: card.content.substring(0, 150) });
         }
      }
    }
    
    // SORT_ORDER
    if (kps.length >= 3) {
      let shuffled = [...kps].sort(() => Math.random() - 0.5);
      challenges.push({ type: 'SORT_ORDER', text: 'סדר את השלבים:', items: kps, shuffledItems: shuffled });
    }
  }

  const ids = lesson.followUpQuestionIds || [];
  ids.forEach(id => {
    const q = QUESTIONS.find(x => x.id === id);
    if (q) {
      challenges.push({ type: 'TAP_CORRECT', text: q.question, options: q.options, answerIndex: q.correctIndex, reteach: q.explanation });
    }
  });

  return challenges.sort(() => Math.random() - 0.5); // shuffle some
}

function startLesson(lesson, mission) {
  CUR_LESSON = lesson;
  GAME_MISSION = mission;
  GAME_CHALLENGES = buildGameChallenges(lesson);
  GAME_IDX = 0;
  GAME_COMBO = 0;
  
  console.log("Generated challenges: ", GAME_CHALLENGES.length);
  if (GAME_CHALLENGES.length === 0) {
      showToast('אין תוכן לשיעור זה');
      return;
  }
  renderGameChallenge();
}

function renderGameChallenge() {
  if (GAME_IDX >= GAME_CHALLENGES.length) {
    completeSession(GAME_CHALLENGES.length, GAME_CHALLENGES.length, GAME_MISSION);
    return;
  }
  
  const ch = GAME_CHALLENGES[GAME_IDX];
  const pct = Math.round((GAME_IDX / GAME_CHALLENGES.length) * 100);
  
  let contentHtml = '';
  
  if (ch.type === 'TRUE_FALSE') {
    contentHtml = `
      <div style="font-size:18px;font-weight:600;text-align:center;margin:30px 0">${ch.text}</div>
      <div class="game-chips">
        <button class="game-chip" onclick="checkGameAnswer(true, ${ch.answer})">✓ נכון</button>
        <button class="game-chip" onclick="checkGameAnswer(false, ${ch.answer})">✗ שקר</button>
      </div>
    `;
  } else if (ch.type === 'TAP_CORRECT') {
    contentHtml = `
      <div style="font-size:18px;font-weight:600;margin-bottom:20px">${ch.text}</div>
      <div style="display:flex;flex-direction:column;gap:10px">
        ${ch.options.map((o,i) => `<button class="game-chip" onclick="checkGameAnswer(${i}, ${ch.answerIndex})">${o}</button>`).join('')}
      </div>
    `;
  } else if (ch.type === 'FILL_BLANK') {
    contentHtml = `
      <div style="font-size:18px;font-weight:600;text-align:center;margin:30px 0;line-height:1.5">${ch.text.replace('___', '<span style="display:inline-block;width:60px;border-bottom:2px solid var(--accent)"></span>')}</div>
      <div class="game-chips">
        ${ch.options.map(o => `<button class="game-chip" onclick="checkGameAnswer('${o}', '${ch.answer}')">${o}</button>`).join('')}
      </div>
    `;
  } else if (ch.type === 'SORT_ORDER') {
    // For simplicity, just render a modified tap correct or skip real sort and just display text
    // A true sort order requires drag-drop or click-to-slot. Let's do click-to-slot.
    contentHtml = `
      <div style="font-size:18px;font-weight:600;margin-bottom:20px">${ch.text}</div>
      <div id="sort-slots" style="display:flex;flex-direction:column;gap:8px;margin-bottom:20px;min-height:120px;background:var(--surface2);border-radius:12px;padding:10px">
      </div>
      <div class="game-chips" id="sort-chips">
        ${ch.shuffledItems.map((item, i) => `<button class="game-chip" onclick="handleSortClick(this, ${i})">${item}</button>`).join('')}
      </div>
      <button class="btn btn-accent" style="margin-top:20px;display:none" id="sort-submit" onclick="checkSortOrder()">בדוק תשובה</button>
      
        window.currentSortItems = ${JSON.stringify(ch.shuffledItems)};
        window.correctSortOrder = ${JSON.stringify(ch.items)};
        window.selectedSort = [];
        function handleSortClick(btn, i) {
          if (btn.classList.contains('locked')) return;
          btn.classList.add('locked');
          btn.style.opacity = '0.5';
          window.selectedSort.push(window.currentSortItems[i]);
          const slots = document.getElementById('sort-slots');
          slots.innerHTML += '<div style="padding:10px;background:var(--surface);border-radius:8px;font-size:14px">' + window.currentSortItems[i] + '</div>';
          if (window.selectedSort.length === window.currentSortItems.length) {
            document.getElementById('sort-submit').style.display = 'block';
          }
        }
        function checkSortOrder() {
          const isCorrect = window.selectedSort.join('|') === window.correctSortOrder.join('|');
          checkGameAnswer(isCorrect, true);
        }
      
