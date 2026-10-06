import os
import sys
import json
import time
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)

with open('data/syllabus.json', 'r', encoding='utf-8') as f:
    syllabus = json.load(f)

def load_json(filepath, default_val):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return default_val

questions = load_json('data/questions.json', [])
lessons = load_json('data/lessons.json', [])

existing_q_subs = {q.get('subtopicId') for q in questions if 'subtopicId' in q}
existing_l_chs = {l.get('chapterId') for l in lessons if 'chapterId' in l}

SYSTEM_INSTRUCTION = """אתה מומחה תוכן רפואי שמכין חומרי לימוד איכותיים לבחינת הידע הארבע-שנתית ברפואה (ישראל).
עליך לייצר תוכן עבור נושא-משנה ספציפי מהסילבוס. 

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

print("🔬 מתחיל לייצר תוכן רפואי... (לחץ Ctrl+C כדי לעצור בכל שלב)", flush=True)

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

            try:
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.4,
                        response_mime_type="application/json"
                    )
                )
                
                res_json = json.loads(response.text)
                
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
                
                time.sleep(4)
                
            except Exception as e:
                print(f"❌ שגיאה בנושא {subtopic['title']}: {e}", flush=True)
                time.sleep(10)

print("✅ כל הסילבוס הושלם!", flush=True)
