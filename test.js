const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// evaluate the scripts in index.html to see if it works.
// We'll just run a node script that replicates the logic to see counts.

const questions = JSON.parse(fs.readFileSync('data/questions.json', 'utf8'));
const lessons = JSON.parse(fs.readFileSync('data/lessons.json', 'utf8'));
const syllabus = JSON.parse(fs.readFileSync('data/syllabus.json', 'utf8'));

const QUESTIONS = questions;
const LESSONS = lessons;
const SYLLABUS = syllabus;

// mock DB
const DB = {
  data: {},
  get(k, d) { return this.data[k] || d; },
  set(k, v) { this.data[k] = v; }
};

// Copy logic from HTML
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

const lesson1 = LESSONS[0];
const chal1 = buildGameChallenges(lesson1);
console.log('Challenges for lesson 1:', chal1.length);

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

initFlashcards();
console.log('Flashcard decks generated:', DB.data.flashcards.decks.length);

