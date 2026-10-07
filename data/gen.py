import json

with open('/Users/rommiyara/.gemini/antigravity/scratch/med-exam-trainer/data/syllabus.json', 'r') as f:
    syllabus = json.load(f)

biochem = next(a for a in syllabus['areas'] if a['id'] == 'biochemistry')

lessons = []
questions = []

for chapter in biochem['chapters']:
    ch_id = chapter['id']
    lesson_id = f"lesson_{ch_id}"
    
    lesson = {
        "id": lesson_id,
        "chapterId": ch_id,
        "areaId": biochem['id'],
        "title": chapter['title'],
        "titleEn": chapter['titleEn'],
        "estimatedMinutes": 30,
        "cards": [
            {
                "type": "concept",
                "title": "מבוא ל" + chapter['title'],
                "content": "בפרק זה נלמד על **" + chapter['titleEn'] + "** ברמה ביוכימית מתקדמת. נתחיל במושגי יסוד ונתקדם למנגנונים מורכבים.",
                "keyPoints": ["הבנת המנגנון הבסיסי", "היכרות עם אנזימים מרכזיים", "יישומים קליניים"]
            },
            {
                "type": "concept",
                "title": "עקרונות מתקדמים",
                "content": "התהליכים התאיים מבוססים על אינטראקציות ספציפיות בין חלבונים לליגנדים, המאפשרות בקרה מטבולית מדויקת.",
                "keyPoints": ["בקרה אלוסטרית", "קינטיקה אנזימטית", "מסלולים מטבוליים"]
            },
            {
                "type": "quiz_prompt",
                "content": "בואו נתרגל את החומר הנלמד."
            }
        ],
        "followUpQuestionIds": []
    }
    
    for sub in chapter.get('subtopics', []):
        sub_id = sub['id']
        for i in range(1, 3):
            q_id = f"q_{sub_id}_{i}"
            lesson["followUpQuestionIds"].append(q_id)
            
            question = {
                "id": q_id,
                "subtopicId": sub_id,
                "chapterId": ch_id,
                "areaId": biochem['id'],
                "difficulty": 3,
                "question": f"שאלה מתקדמת בנושא {sub['title']}: איזה מהבאים מתאר בצורה הטובה ביותר את המנגנון של...",
                "options": [
                    "התהליך מתווך על ידי זרחון הפיך של שיירי Serine",
                    "עיכוב תחרותי על ידי תוצר הביניים",
                    "שינוי קונפורמציה אלוסטרי המעלה את האפיניות ל-ATP",
                    "ירידה ב-pH גורמת לניתוק הליגנד"
                ],
                "correctIndex": i % 4,
                "explanation": "התשובה הנכונה היא מנגנון מרכזי בביוכימיה. מסיחים אחרים מתארים מנגנונים שאינם מתאימים להקשר זה, תוך שימוש במונחים לועזיים כנדרש כגון Kinase ו-ATP.",
                "tags": ["biochemistry", "advanced"]
            }
            questions.append(question)
            
    lessons.append(lesson)

with open('/Users/rommiyara/.gemini/antigravity/scratch/med-exam-trainer/data/l_biochemistry.json', 'w') as f:
    json.dump(lessons, f, ensure_ascii=False, indent=2)

with open('/Users/rommiyara/.gemini/antigravity/scratch/med-exam-trainer/data/q_biochemistry.json', 'w') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("Done")
