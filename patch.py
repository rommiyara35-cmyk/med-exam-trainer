import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add CSS
css_to_add = """
    /* GAME CHIPS */
    .game-chips { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; margin-top:20px; }
    .game-chip { padding:12px 20px; border-radius:14px; border:2px solid var(--sep); background:var(--card); font-size:15px; cursor:pointer; transition:all .15s; }
    .game-chip.correct { background:#34c759; color:#fff; border-color:#34c759; }
    .game-chip.wrong { background:#ff3b30; color:#fff; border-color:#ff3b30; }
    .game-chip.selected { border-color:var(--accent); }
    .xp-pop { position:fixed; top:40%; left:50%; transform:translate(-50%,-50%); font-size:28px; font-weight:800; color:#34c759; pointer-events:none; animation:popUp .8s ease forwards; z-index:999; }
    @keyframes popUp { 0%{opacity:1;transform:translate(-50%,-50%)} 100%{opacity:0;transform:translate(-50%,-120%)} }
    .combo-pop { position:fixed; top:35%; left:50%; transform:translateX(-50%); font-size:22px; font-weight:800; color:#ff9500; pointer-events:none; animation:popUp .9s ease forwards; z-index:999; }
    .reteach { background:var(--surface); border-radius:12px; padding:12px 16px; margin:12px 0; border-right:4px solid #ff9500; font-size:14px; color:var(--text-secondary); }

    /* FLASHCARDS */
    .fc-scene { perspective: 1000px; width: 100%; max-width: 340px; margin: 0 auto; height: 220px; }
    .fc-card { width:100%; height:100%; position:relative; transform-style:preserve-3d; transition:transform .5s; border-radius:18px; }
    .fc-card.flipped { transform: rotateY(180deg); }
    .fc-face { position:absolute; width:100%; height:100%; backface-visibility:hidden; border-radius:18px; display:flex; align-items:center; justify-content:center; padding:20px; text-align:center; }
    .fc-front { background: var(--surface); border: 1.5px solid var(--sep); font-size:18px; font-weight:600; }
    .fc-back { background: var(--accent); color: #fff; font-size:16px; transform: rotateY(180deg); }
    .grade-btns { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:24px; }
    .grade-btn { padding:14px; border-radius:14px; border:none; font-size:14px; font-weight:600; cursor:pointer; }
    .grade-again { background:#ff3b30; color:#fff; }
    .grade-hard { background:#ff9500; color:#fff; }
    .grade-good { background:#34c759; color:#fff; }
    .grade-easy { background:#007aff; color:#fff; }
    .deck-row { display:flex; align-items:center; justify-content:space-between; padding:14px 16px; background:var(--surface); border-radius:14px; margin-bottom:10px; }
    .deck-due-badge { background:var(--accent); color:#fff; border-radius:20px; padding:3px 10px; font-size:12px; font-weight:700; }
"""
html = html.replace("</style>", css_to_add + "\n  </style>")

# 2. Add Screen
fc_screen = """
  <!-- ====== FLASHCARDS ====== -->
  <div class="screen" id="screen-flashcards">
    <div class="large-title">כרטיסיות 🃏</div>
    <div id="flashcards-content" style="padding: 16px"></div>
  </div>
"""
html = html.replace("<!-- ====== PROFILE ====== -->", fc_screen + "\n  <!-- ====== PROFILE ====== -->")

# 3. Add Tab
fc_tab = """    <div class="tab-item" onclick="switchTab('flashcards',this)" data-tab="flashcards"><div class="tab-icon">🃏</div><div class="tab-label">כרטיסיות</div></div>"""
html = html.replace("""<div class="tab-item" onclick="switchTab('profile',this)" data-tab="profile"><div class="tab-icon">👤</div><div class="tab-label">פרופיל</div></div>""", fc_tab + """\n    <div class="tab-item" onclick="switchTab('profile',this)" data-tab="profile"><div class="tab-icon">👤</div><div class="tab-label">פרופיל</div></div>""")

# 4. Fix buildMissions onclick and tag
html = html.replace("""<div class="mission-item ${done?'done':''}" onclick='startMission(${JSON.stringify(m)})'>""", """<button class="mission-item ${done?'done':''}" onclick='startMission(${JSON.stringify(m).replace(/"/g, "&quot;")})' style="border:none; text-align:inherit; font-family:inherit; width:100%">""")
html = html.replace("""${done ? '<div class="m-badge">✓</div>' : `<div class="m-xp">⭐${m.xp}</div>`}
    </div>`;""", """${done ? '<div class="m-badge">✓</div>' : `<div class="m-xp">⭐${m.xp}</div>`}
    </button>`;""")

# 5. Fix startMission fallback
start_mission_find = """  if (mission.id === 'learn_new' && LESSONS.length > 0) {
    const l = LESSONS[0];
    startLesson(l, mission);
    return;
  }
  showToast('תוכן בהכנה — הוסף שאלות ל-questions.json');"""

start_mission_repl = """  // If nothing worked, just open the first available lesson
  if (LESSONS.length > 0) { startLesson(LESSONS[0], mission); return; }
  showToast('תוכן בהכנה — הוסף שאלות ל-questions.json');"""
html = html.replace(start_mission_find, start_mission_repl)

# 6. Flashcards switchTab logic
tab_switch_find = """  if (name === 'profile') renderProfile();"""
tab_switch_repl = """  if (name === 'profile') renderProfile();\n  if (name === 'flashcards') renderFlashcards();"""
html = html.replace(tab_switch_find, tab_switch_repl)

# 7. Add Flashcard Logic & Init
fc_logic = """
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
"""
init_call_find = """  await loadData();"""
init_call_repl = """  await loadData();\n  initFlashcards();"""
html = html.replace(init_call_find, init_call_repl)
html = html.replace("let CUR_LESSON = null, CUR_LESSON_IDX = 0, CUR_MISSION = null;", fc_logic + "\nlet CUR_LESSON = null, CUR_LESSON_IDX = 0, CUR_MISSION = null;")

# 8. Game Logic
game_logic = """
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
      const boldMatch = card.content.match(/\\*\\*(.*?)\\*\\*/);
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
      <script>
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
      </script>
    `;
  }
  
  openOverlay(`
    <div class="ov-hdr">
      <button class="close-btn" onclick="closeOverlay()">✕</button>
      <div class="prog-track"><div class="prog-fill" style="width:${pct}%"></div></div>
      <div class="xp-badge" style="color:var(--label4)">🔥 ${GAME_COMBO}</div>
    </div>
    <div class="ov-body">
      <div style="font-size:13px;font-weight:600;color:var(--label3);margin-bottom:10px;text-transform:uppercase">
        ${ch.type === 'TRUE_FALSE' ? 'נכון או שקר?' : ch.type === 'FILL_BLANK' ? 'השלם את החסר' : ch.type === 'SORT_ORDER' ? 'סדר את השלבים' : 'בחר את התשובה הנכונה'}
      </div>
      ${contentHtml}
      <div id="reteach-area"></div>
    </div>
  `);
}

function checkGameAnswer(given, correct) {
  const isCorrect = given === correct;
  const ch = GAME_CHALLENGES[GAME_IDX];
  
  if (isCorrect) {
    GAME_COMBO++;
    let state = getState(); state = addXP(state, 5); saveState(state);
    
    // Show correct UI
    const xpPop = document.createElement('div');
    xpPop.className = 'xp-pop';
    xpPop.textContent = '+5 XP';
    document.body.appendChild(xpPop);
    setTimeout(() => xpPop.remove(), 1000);
    
    if (GAME_COMBO >= 3) {
      const comboPop = document.createElement('div');
      comboPop.className = 'combo-pop';
      comboPop.textContent = '🔥 Combo!';
      document.body.appendChild(comboPop);
      setTimeout(() => comboPop.remove(), 1000);
    }
    
    haptic();
    setTimeout(() => {
      GAME_IDX++;
      renderGameChallenge();
    }, 600);
  } else {
    GAME_COMBO = 0;
    haptic();
    const reteach = document.getElementById('reteach-area');
    reteach.innerHTML = `
      <div class="reteach">
        <strong>לא מדויק.</strong><br>
        ${ch.reteach || 'נסה לזכור את העובדות מהשיעור ולהתרכז בפרטים הקטנים.'}
      </div>
      <button class="btn btn-accent" style="margin-top:10px" onclick="GAME_IDX++; renderGameChallenge()">המשך</button>
    `;
    // Push the question to the end to try again
    GAME_CHALLENGES.push({...ch});
  }
}
"""

html = re.sub(r"function startLesson[\s\S]*?(?=// Follow-up questions)", game_logic, html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
