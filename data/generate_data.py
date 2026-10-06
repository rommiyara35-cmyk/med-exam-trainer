import os
import sys
import json
import time
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=API_KEY)

def load_json(filepath, default_val):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return default_val

with open('data/syllabus.json', 'r', encoding='utf-8') as f:
    syllabus = json.load(f)

questions = load_json('data/questions.json', [])
lessons = load_json('data/lessons.json', [])

existing_q_subs = {q.get('subtopicId') for q in questions if 'subtopicId' in q}
existing_l_chs = {l.get('chapterId') for l in lessons if 'chapterId' in l}

SYSTEM_INSTRUCTION = """אתה מומחה תוכן רפואי שמכין חומרי לימוד איכותיים לבחינת הידע הארבע-שנתית ברפואה (ישראל).
עליך לייצר תוכן עבור נושא-משנה ספציפי מהסילבוס. השתמש בשפה העברית בצורה ברורה ואקדמית.

הכללים:
1. התוכן חייב להיות מדויק מדעית, ברמה אקדמית-רפואית גבוהה.
2. העברית צריכה להיות תקנית, אך חובה להשאיר מונחים מדעיים באנגלית/לטינית (למשל: Serine, Kinase, Ca-ATPase, homotetramer).
3. מסיחי הדעת (Distractors) בשאלות חייבים להיות אמיתיים ומאתגרים - כאלו שמבוססים על טעויות נפוצות או שגויים בפרט קטן, בדיוק כמו במבחן אמיתי.
4. השיעור חייב להיבנות בהדרגה מהבסיס ועד לרמה המתקדמת.

דוגמה לסגנון השאלות הנדרש מתוך המבחן לדוגמה:
שאלה: "חוקרים גילו ובודדו חלבון חדש, חלבון X. בבדיקה בג׳ל אלקטרופורזה נמצא שבתנאים מחזרים משקלו 24 kDa ואילו בתנאים לא מחזרים משקלו 48 kDa. אנליזה בג׳ל פילטרציה הראתה כי משקלו 100~ kDa. באיזו מסקנה תומכים ממצאים אלה?"
א. חלבון X יוצר אגרגטים בתמיסה
ב. חלבון X הוא הטרודימר הבנוי מתת-יחידה גדולה וקטנה
ג. חלבון X הוא דימר הבנוי משני דימרים המוחזקים ע״י קשרים די-סולפידיים
ד. חלבון X הוא הומוטטרמר אשר כל תת-היחידות שלו קשורות ביניהן בקשרים די-סולפידיים
(תשובה נכונה: ד)

החזר JSON בדיוק במבנה הבא (חובה לייצר בדיוק 4 שאלות לכל נושא-משנה):
{
  "lesson": {
    "title": "כותרת השיעור (עברית)",
    "titleEn": "English Title",
    "estimatedMinutes": 8,
    "cards": [
      {
        "type": "concept",
        "title": "כותרת הכרטיסיה",
        "content": "הסבר מפורט עם מונחי מפתח ב**הדגשה**...",
        "keyPoints": ["נקודה 1", "נקודה 2"]
      },
      {"type": "quiz_prompt", "content": "בואו נבדוק מה למדנו עד כה."}
    ]
  },
  "questions": [
    {
      "difficulty": 2, 
      "question": "טקסט השאלה...",
      "options": ["אופציה 1", "אופציה 2", "אופציה 3", "אופציה 4"],
      "correctIndex": 0, 
      "explanation": "הסבר מפורט למה התשובה נכונה ולמה המסיחים שגויים.",
      "tags": ["מושג1", "מושג2"]
    }
  ]
}
"""

print("🔬 מתחיל לייצר תוכן רפואי עם Groq (Llama-3.3-70B)... (לחץ Ctrl+C לעצירה)", flush=True)

MODEL = "openai/gpt-oss-120b"

for area in syllabus.get('areas', []):
    for chapter in area.get('chapters', []):
        chapter_lesson_generated = (chapter['id'] in existing_l_chs)
        
        for subtopic in chapter.get('subtopics', []):
            if subtopic['id'] in existing_q_subs:
                continue
                
            print(f"⏳ מייצר תוכן עבור: {subtopic['title']} ({subtopic['id']})...", flush=True)
            
            prompt = f"Area: {area['title']}\\nChapter: {chapter['title']}\\nSubtopic to teach and test: {subtopic['titleEn']} ({subtopic['title']})\\n\\n"
            if chapter_lesson_generated:
                prompt += "הערה: כבר נוצר שיעור לפרק זה, לכן תוכל להשאיר את ה-lesson ריק או קצר, אך חובה לייצר 4 שאלות קשות ומקיפות על תת-נושא זה."
            else:
                prompt += "אנא צור שיעור מקיף שמכסה את עקרונות הפרק כולו (התמקד בתת-נושא זה), וייצר 4 שאלות קשות."

            while True:
                try:
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": SYSTEM_INSTRUCTION},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.4
                    )
                    
                    res_text = response.choices[0].message.content
                    res_json = json.loads(res_text)
                    
                    q_count = 0
                    for q_idx, q in enumerate(res_json.get('questions', [])):
                        q['id'] = f"q_{subtopic['id']}_{q_idx+1}_{int(time.time())}"
                        q['subtopicId'] = subtopic['id']
                        q['chapterId'] = chapter['id']
                        q['areaId'] = area['id']
                        questions.append(q)
                        q_count += 1
                    
                    if not chapter_lesson_generated and res_json.get('lesson') and len(res_json['lesson'].get('cards', [])) > 0:
                        l = res_json['lesson']
                        l['id'] = f"lesson_{chapter['id']}"
                        l['chapterId'] = chapter['id']
                        l['areaId'] = area['id']
                        l['followUpQuestionIds'] = [q['id'] for q in questions if q.get('subtopicId') == subtopic['id']]
                        lessons.append(l)
                        chapter_lesson_generated = True
                        existing_l_chs.add(chapter['id'])
                    elif chapter_lesson_generated and res_json.get('lesson'):
                        existing_lesson = next((l for l in lessons if l.get('chapterId') == chapter['id']), None)
                        if existing_lesson:
                            new_ids = [q['id'] for q in questions if q.get('subtopicId') == subtopic['id']]
                            if 'followUpQuestionIds' not in existing_lesson:
                                existing_lesson['followUpQuestionIds'] = []
                            existing_lesson['followUpQuestionIds'].extend(new_ids)
                    
                    with open('data/questions.json', 'w', encoding='utf-8') as f:
                        json.dump(questions, f, ensure_ascii=False, indent=2)
                    with open('data/lessons.json', 'w', encoding='utf-8') as f:
                        json.dump(lessons, f, ensure_ascii=False, indent=2)
                        
                    existing_q_subs.add(subtopic['id'])
                    print(f"🎉 הושלם: {subtopic['title']} (נוצרו {q_count} שאלות)", flush=True)
                    
                    # שינה את זמן ההמתנה בהתאם למגבלות Groq החינמי
                    time.sleep(25) 
                    break # Success, exit retry loop
                    
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "rate limit" in err_str.lower():
                        print(f"⚠️ עומס בקשות (Rate Limit), ממתין 40 שניות ומנסה שוב...", flush=True)
                        time.sleep(40)
                    else:
                        print(f"❌ שגיאה בנושא {subtopic['title']}: {e}. מדלג לנושא הבא.", flush=True)
                        time.sleep(5)
                        break

print("✅ כל הסילבוס הושלם!", flush=True)
