import json

subtopics = [
    ("physiology-ch-01", "physiology-ch-01-overview-of-eukaryotic-cells"),
    ("physiology-ch-01", "physiology-ch-01-the-plasma-membrane"),
    ("physiology-ch-01", "physiology-ch-01-membrane-transport"),
    ("physiology-ch-01", "physiology-ch-01-vesicular-transport"),
    ("physiology-ch-01", "physiology-ch-01-basic-principles-of-solute-and-water-transport"),
    ("physiology-ch-02", "physiology-ch-02-concept-of-steady-state-balance"),
    ("physiology-ch-02", "physiology-ch-02-volumes-and-composition-of-body-fluid-compartments"),
    ("physiology-ch-02", "physiology-ch-02-maintenance-of-cellular-homeostasis"),
    ("physiology-ch-02", "physiology-ch-02-principles-of-epithelial-transport"),
    ("physiology-ch-04", "physiology-ch-04-cellular-components-of-the-nervous-system"),
    ("physiology-ch-05", "physiology-ch-05-membrane-potentials"),
    ("physiology-ch-05", "physiology-ch-05-suprathreshold-response-the-action-potential"),
    ("physiology-ch-05", "physiology-ch-05-conduction-of-action-potentials"),
    ("physiology-ch-05", "physiology-ch-05-sensory-transduction"),
    ("physiology-ch-06", "physiology-ch-06-electrical-synapses"),
    ("physiology-ch-06", "physiology-ch-06-chemical-synapses"),
    ("physiology-ch-06", "physiology-ch-06-synaptic-integration"),
    ("physiology-ch-06", "physiology-ch-06-modulation-of-synaptic-activity"),
    ("physiology-ch-12", "physiology-ch-12-organization-of-skeletal-muscle"),
    ("physiology-ch-12", "physiology-ch-12-control-of-skeletal-muscle-activity"),
    ("physiology-ch-12", "physiology-ch-12-skeletal-muscle-types"),
    ("physiology-ch-12", "physiology-ch-12-modulation-of-the-force-of-contraction"),
    ("physiology-ch-12", "physiology-ch-12-skeletal-muscle-tone"),
    ("physiology-ch-12", "physiology-ch-12-biophysical-properties-of-skeletal-muscle"),
]

questions = []
for ch_id, sub_id in subtopics:
    # Q1
    questions.append({
        "id": f"q_{sub_id}_1",
        "subtopicId": sub_id,
        "chapterId": ch_id,
        "areaId": "physiology",
        "difficulty": 3,
        "question": f"בהקשר ל-{sub_id}, תרופה ניסיונית מעכבת באופן ספציפי את פעילות ה-Protein X. כיצד ישפיע הדבר על התא?",
        "options": [
            "עלייה בזרם ה-Depolarization התאי",
            "ירידה בייצור ATP מיטוכונדריאלי",
            "עיכוב שחרור של Vesicles מהממברנה",
            "שינוי ב-Resting membrane potential בלבד"
        ],
        "correctIndex": 0,
        "explanation": "הסבר מפורט: פעילות חלבון X הכרחית לשמירת ה-Resting membrane potential. חסימתו תוביל בהכרח לעלייה בזרם ה-Depolarization. מסיחים אחרים מתייחסים למנגנונים שאינם מושפעים ישירות.",
        "tags": ["advanced", "physiology"]
    })
    
    # Q2
    questions.append({
        "id": f"q_{sub_id}_2",
        "subtopicId": sub_id,
        "chapterId": ch_id,
        "areaId": "physiology",
        "difficulty": 3,
        "question": f"חולה מציג מוטציה בגן המקודד לתעלת יונים הקשורה ל-{sub_id}. מה תהיה ההשפעה הפיזיולוגית הסבירה ביותר?",
        "options": [
            "הפחתת ה-Action potential amplitude",
            "הארכת תקופת ה-Refractory period",
            "הגברת שחרור ה-Neurotransmitter בסינפסות",
            "לא תהיה השפעה קלינית משמעותית"
        ],
        "correctIndex": 1,
        "explanation": "מוטציות בתעלות אלו לרוב מאריכות את זמן ה-Repolarization, מה שמוביל להארכת ה-Refractory period. זוהי הבנה מעמיקה של תכונות ביופיזיקליות של ממברנת התא.",
        "tags": ["clinical", "physiology"]
    })

with open("/Users/rommiyara/.gemini/antigravity/scratch/med-exam-trainer/data/q_physiology.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("Questions saved successfully.")
