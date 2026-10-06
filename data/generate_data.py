import json

def generate():
    with open('/Users/rommiyara/.gemini/antigravity/scratch/med-exam-trainer/data/syllabus.json', 'r', encoding='utf-8') as f:
        syllabus = json.load(f)

    questions = []
    lessons = []

    for area in syllabus['areas']:
        area_id = area['id']
        for chapter in area['chapters']:
            chapter_id = chapter['id']
            lesson_q_ids = []
            
            for subtopic in chapter['subtopics']:
                subtopic_id = subtopic['id']
                sub_short = subtopic_id.replace('biochemistry-ch-', 'bc').replace('molecular-biology-ch-', 'mb').replace('cell-biology-ch-', 'cb').replace('physiology-ch-', 'ph')
                
                for n in range(1, 5):
                    q_id = f"q_{sub_short}_{n}"
                    lesson_q_ids.append(q_id)
                    questions.append({
                        "id": q_id,
                        "subtopicId": subtopic_id,
                        "chapterId": chapter_id,
                        "areaId": area_id,
                        "difficulty": (n % 3) + 1,
                        "question": f"מהי המשמעות של {subtopic['title']}?",
                        "options": [
                            "תשובה נכונה המשקפת הבנה עמוקה של הנושא.",
                            "מסיח דעת סביר אך שגוי בפרט קטן.",
                            "מסיח דעת הקשור לנושא אחר בפרק.",
                            "מסיח דעת המבוסס על תפיסה שגויה נפוצה."
                        ],
                        "correctIndex": 0,
                        "explanation": f"ההסבר בעברית עבור {subtopic['titleEn']}, תוך שמירה על מונחים באנגלית כמו Enzyme.",
                        "tags": ["generated", area_id]
                    })
            
            lessons.append({
                "id": f"lesson_{chapter_id}",
                "chapterId": chapter_id,
                "areaId": area_id,
                "title": chapter['title'],
                "titleEn": chapter['titleEn'],
                "estimatedMinutes": 7,
                "cards": [
                    {
                        "type": "concept",
                        "title": chapter['title'],
                        "content": f"הסבר בעברית על {chapter['titleEn']} עם **מושגי מפתח** מודגשים.",
                        "keyPoints": ["נקודה חשובה ראשונה", "נקודה חשובה שנייה"]
                    },
                    {"type": "quiz_prompt", "content": "בואו נבדוק מה למדנו עד כה."}
                ],
                "followUpQuestionIds": lesson_q_ids[:3]  # Taking first 3 for example
            })

    with open('/Users/rommiyara/.gemini/antigravity/scratch/med-exam-trainer/data/questions.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    with open('/Users/rommiyara/.gemini/antigravity/scratch/med-exam-trainer/data/lessons.json', 'w', encoding='utf-8') as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generate()
