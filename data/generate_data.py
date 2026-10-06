import os
import sys
import json
import time
import google.generativeai as genai

API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=API_KEY)

# Load existing data
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

# Create sets for fast lookup
existing_q_subs = {q['subtopicId'] for q in questions}
existing_l_chs = {l['chapterId'] for l in lessons}

generation_config = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

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
      "difficulty": 2, // 1 to 3
      "question": "טקסט השאלה...",
      "options": ["אופציה 1", "אופציה 2", "אופציה 3", "אופציה 4"],
      "correctIndex": 0, // 0-3
      "explanation": "הסבר מפורט למה התשובה נכונה ולמה המסיחים שגויים.",
      "tags": ["מושג1", "מושג2"]
    }
  ]
}
"""

model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    generation_config=generation_config,
    system_instruction=SYSTEM_INSTRUCTION
)

print("🔬 מתחיל לייצר תוכן רפואי... (לחץ Ctrl+C כדי לעצור בכל שלב)")

for area in syllabus['areas']:
    for chapter in area['chapters']:
        
        chapter_lesson_generated = (chapter['id'] in existing_l_chs)
        
        for idx, subtopic in enumerate(chapter['subtopics']):
            if subtopic['id'] in existing_q_subs:
                print(f"✅ נושא {subtopic['id']} כבר קיים, מדלג.")
                continue
                
            print(f"⏳ מייצר תוכן עבור: {subtopic['title']} ({subtopic['id']})...")
            
            # אם כבר יש שיעור לפרק הזה מהנושא הראשון, נבקש רק שאלות
            prompt = f"""
Area: {area['title']}
Chapter: {chapter['title']}
Subtopic to teach and test: {subtopic['titleEn']} ({subtopic['title']})

"""
            if chapter_lesson_generated:
                prompt += "הערה: כבר נוצר שיעור לפרק זה, לכן תוכל להשאיר את ה-lesson ריק או קצר, אך חובה לייצר 4 שאלות קשות ומקיפות על תת-נושא זה."
            else:
                prompt += "אנא צור שיעור מקיף שמכסה את עקרונות הפרק כולו (התמקד בתת-נושא זה), וייצר 4 שאלות קשות."

            try:
                response = model.generate_content(prompt)
                res_json = json.loads(response.text)
                
                # עבד את השאלות
                for q_idx, q in enumerate(res_json.get('questions', [])):
                    q['id'] = f"q_{subtopic['id']}_{q_idx+1}"
                    q['subtopicId'] = subtopic['id']
                    q['chapterId'] = chapter['id']
                    q['areaId'] = area['id']
                    questions.append(q)
                
                # עבד את השיעור (אם טרם נוצר לפרק זה)
                if not chapter_lesson_generated and res_json.get('lesson') and len(res_json['lesson'].get('cards', [])) > 0:
                    l = res_json['lesson']
                    l['id'] = f"lesson_{chapter['id']}"
                    l['chapterId'] = chapter['id']
                    l['areaId'] = area['id']
                    l['followUpQuestionIds'] = [q['id'] for q in questions if q['subtopicId'] == subtopic['id']]
                    lessons.append(l)
                    chapter_lesson_generated = True
                    existing_l_chs.add(chapter['id'])
                elif chapter_lesson_generated and res_json.get('lesson'):
                    # Update followUpQuestionIds of the existing lesson
                    existing_lesson = next((l for l in lessons if l['chapterId'] == chapter['id']), None)
                    if existing_lesson:
                        new_ids = [q['id'] for q in questions if q['subtopicId'] == subtopic['id']]
                        existing_lesson.setdefault('followUpQuestionIds', []).extend(new_ids)
                
                # שמירה מיידית לקבצים
                with open('data/questions.json', 'w', encoding='utf-8') as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
                with open('data/lessons.json', 'w', encoding='utf-8') as f:
                    json.dump(lessons, f, ensure_ascii=False, indent=2)
                    
                existing_q_subs.add(subtopic['id'])
                print(f"🎉 הושלם: {subtopic['title']} (הוספו שאלות, הקבצים עודכנו)")
                
                # המתנה קצרה כדי לא לחרוג ממגבלות ה-API
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ שגיאה בנושא {subtopic['title']}: {e}")
                time.sleep(10) # במקרה של שגיאת Quota נחכה יותר

print("✅ כל הסילבוס הושלם!")
