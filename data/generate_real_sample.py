import json

questions = [
    {
        "id": "q_bc_amino_1",
        "subtopicId": "biochemistry-ch-03-amino-acids",
        "chapterId": "biochemistry-ch-03",
        "areaId": "biochemistry",
        "difficulty": 2,
        "question": "איזו חומצת אמינו מבין הבאות אינה כיראלית (Achiral)?",
        "options": ["Glycine", "Alanine", "Valine", "Leucine"],
        "correctIndex": 0,
        "explanation": "Glycine היא חומצת האמינו היחידה שאינה כיראלית משום שקבוצת הצד (R group) שלה היא אטום מימן, מה שאומר שיש לה שני מתמירים זהים (אטומי מימן) על פחמן האלפא.",
        "tags": ["Amino Acids", "Chirality"]
    },
    {
        "id": "q_bc_amino_2",
        "subtopicId": "biochemistry-ch-03-amino-acids",
        "chapterId": "biochemistry-ch-03",
        "areaId": "biochemistry",
        "difficulty": 2,
        "question": "באיזה pH חומצת אמינו עם שייר לא נטען תימצא בעיקר בצורת Zwitterion?",
        "options": ["ב-pH השווה ל-pK1", "ב-pH השווה ל-pK2", "ב-pH השווה ל-pI (הנקודה האיזואלקטרית)", "ב-pH פיזיולוגי (7.4) תמיד"],
        "correctIndex": 2,
        "explanation": "הנקודה האיזואלקטרית (pI) היא ערך ה-pH בו המטען החשמלי נטו של המולקולה הוא אפס, והיא נמצאת כ-Zwitterion. זהו הממוצע של pK1 ו-pK2 עבור חומצות אמינו ללא שייר נטען.",
        "tags": ["pI", "Zwitterion"]
    }
]

lessons = [
    {
        "id": "lesson_biochemistry-ch-03",
        "chapterId": "biochemistry-ch-03",
        "areaId": "biochemistry",
        "title": "חומצות אמינו ופפטידים",
        "titleEn": "Amino Acids, Peptides, and Proteins",
        "estimatedMinutes": 5,
        "cards": [
            {
                "type": "concept",
                "title": "מבנה חומצות אמינו",
                "content": "כל חומצות האמינו (מלבד Proline) מורכבות מפחמן אלפא אליו קשורים קבוצת אמינו, קבוצת קרבוקסיל, אטום מימן וקבוצת צד (R group) המייחדת אותן. ה**כיראליות** של פחמן האלפא קיימת בכולן מלבד Glycine.",
                "keyPoints": ["L-amino acids הן הנפוצות בטבע", "Glycine אינה כיראלית"]
            },
            {
                "type": "quiz_prompt",
                "content": "כעת נתרגל את מה שלמדנו על חומצות אמינו."
            }
        ],
        "followUpQuestionIds": ["q_bc_amino_1", "q_bc_amino_2"]
    }
]

with open('data/questions.json', 'w') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

with open('data/lessons.json', 'w') as f:
    json.dump(lessons, f, ensure_ascii=False, indent=2)

print("Sample created.")
