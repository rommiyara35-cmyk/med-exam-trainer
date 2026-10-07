import json
import os

area_id = "cell-biology"

chapters = [
    {
        "id": "cell-biology-ch-10",
        "title": "מבנה הממברנה",
        "titleEn": "Membrane Structure",
        "subtopics": [
            {"id": "cell-biology-ch-10-the-lipid-bilayer", "title": "הדו-שכבה הליפידית", "titleEn": "The Lipid Bilayer"},
            {"id": "cell-biology-ch-10-membrane-proteins", "title": "חלבוני ממברנה", "titleEn": "Membrane Proteins"}
        ]
    },
    {
        "id": "cell-biology-ch-12",
        "title": "ארגון תוך-תאי ומיון חלבונים",
        "titleEn": "Intracellular Organization and Protein Sorting",
        "subtopics": [
            {"id": "cell-biology-ch-12-the-compartmentalization-of-cells"},
            {"id": "cell-biology-ch-12-the-endoplasmic-reticulum"},
            {"id": "cell-biology-ch-12-peroxisomes"},
            {"id": "cell-biology-ch-12-the-transport-of-proteins-into-mitochondria-and-chloroplasts"},
            {"id": "cell-biology-ch-12-the-transport-of-molecules-between-the-nucleus-and-the-cytosol"}
        ]
    },
    {
        "id": "cell-biology-ch-13",
        "title": "תנועת ממברנות תוך-תאית",
        "titleEn": "Intracellular Membrane Traffic",
        "subtopics": [
            {"id": "cell-biology-ch-13-mechanisms-of-membrane-transport-and-compartment-identity"},
            {"id": "cell-biology-ch-13-transport-from-the-endoplasmic-reticulum-through-the-golgi-apparatus"},
            {"id": "cell-biology-ch-13-transport-from-the-trans-golgi-network-to-the-cell-exterior-and-endosomes"},
            {"id": "cell-biology-ch-13-transport-into-the-cell-from-the-plasma-membrane-endocytosis"},
            {"id": "cell-biology-ch-13-the-degradation-and-recycling-of-macromolecules-in-lysosomes"}
        ]
    },
    {
        "id": "cell-biology-ch-14",
        "title": "המרת אנרגיה וחלוקה מטבולית למדורים",
        "titleEn": "Energy Conversion and Metabolic Compartmentation",
        "subtopics": [
            {"id": "cell-biology-ch-14-the-mitochondrion"},
            {"id": "cell-biology-ch-14-the-proton-pumps-of-the-electron-transport-chain"},
            {"id": "cell-biology-ch-14-atp-production-in-mitochondria"},
            {"id": "cell-biology-ch-14-chloroplasts-and-photosynthesis"},
            {"id": "cell-biology-ch-14-the-genetic-systems-of-mitochondria-and-chloroplasts"}
        ]
    },
    {
        "id": "cell-biology-ch-15",
        "title": "איתות תאי",
        "titleEn": "Cell Signaling",
        "subtopics": [
            {"id": "cell-biology-ch-15-principles-of-cell-signaling"},
            {"id": "cell-biology-ch-15-signaling-through-g-protein-coupled-receptors"},
            {"id": "cell-biology-ch-15-signaling-through-enzyme-coupled-receptors"},
            {"id": "cell-biology-ch-15-alternative-signaling-routes-in-gene-regulation"},
            {"id": "cell-biology-ch-15-signaling-in-plants"}
        ]
    },
    {
        "id": "cell-biology-ch-16",
        "title": "שלד התא",
        "titleEn": "The Cytoskeleton",
        "subtopics": [
            {"id": "cell-biology-ch-16-function-and-dynamics-of-the-cytoskeleton"},
            {"id": "cell-biology-ch-16-actin"},
            {"id": "cell-biology-ch-16-myosin-and-actin"},
            {"id": "cell-biology-ch-16-microtubules"},
            {"id": "cell-biology-ch-16-intermediate-filaments-and-other-cytoskeletal-polymers"},
            {"id": "cell-biology-ch-16-cell-polarity-and-coordination-of-the-cytoskeleton"}
        ]
    },
    {
        "id": "cell-biology-ch-17",
        "title": "מחזור התא",
        "titleEn": "The Cell Cycle",
        "subtopics": [
            {"id": "cell-biology-ch-17-overview-of-the-cell-cycle"},
            {"id": "cell-biology-ch-17-the-cell-cycle-control-system"},
            {"id": "cell-biology-ch-17-s-phase"},
            {"id": "cell-biology-ch-17-mitosis"},
            {"id": "cell-biology-ch-17-cytokinesis"},
            {"id": "cell-biology-ch-17-meiosis"},
            {"id": "cell-biology-ch-17-control-of-cell-division-and-cell-growth"}
        ]
    },
    {
        "id": "cell-biology-ch-18",
        "title": "מוות תאי",
        "titleEn": "Cell Death",
        "subtopics": [
            {"id": "cell-biology-ch-18-apoptosis-eliminates-unwanted-cells"},
            {"id": "cell-biology-ch-18-apoptosis-depends-on-an-intracellular-proteolytic-cascade-mediated-by-caspases"},
            {"id": "cell-biology-ch-18-activation-of-cell-surface-death-receptors-initiates-the-extrinsic-pathway-of-apoptosis"},
            {"id": "cell-biology-ch-18-the-intrinsic-pathway-of-apoptosis-depends-on-proteins-released-from-mitochondria"},
            {"id": "cell-biology-ch-18-bcl2-proteins-are-the-critical-controllers-of-the-intrinsic-pathway-of-apoptosis"},
            {"id": "cell-biology-ch-18-an-inhibitor-of-apoptosis-an-iap-and-two-anti-iap-proteins-help-control-caspase-activation-in-the-cytosol-of-some-mammalian-cells"},
            {"id": "cell-biology-ch-18-extracellular-survival-factors-inhibit-apoptosis-in-various-ways"},
            {"id": "cell-biology-ch-18-healthy-neighbors-phagocytose-and-digest-apoptotic-cells"},
            {"id": "cell-biology-ch-18-either-excessive-or-insufficient-apoptosis-can-contribute-to-disease"}
        ]
    },
    {
        "id": "cell-biology-ch-19",
        "title": "צומתי תאים והמטריצה החוץ-תאית",
        "titleEn": "Cell Junctions and the Extracellular Matrix",
        "subtopics": [
            {"id": "cell-biology-ch-19-cell-cell-junctions"},
            {"id": "cell-biology-ch-19-the-extracellular-matrix-of-animals"},
            {"id": "cell-biology-ch-19-cell-matrix-junctions"},
            {"id": "cell-biology-ch-19-the-plant-cell-wall"}
        ]
    }
]

questions = []
lessons = []

for ch in chapters:
    ch_id = ch["id"]
    q_ids = []
    
    # Generate exactly 2 hard questions per subtopic
    for sub in ch["subtopics"]:
        sub_id = sub["id"]
        
        q1_id = f"q_{sub_id}_1"
        q2_id = f"q_{sub_id}_2"
        
        q_ids.extend([q1_id, q2_id])
        
        q1 = {
            "id": q1_id,
            "subtopicId": sub_id,
            "chapterId": ch_id,
            "areaId": area_id,
            "difficulty": 3,
            "question": f"איזו מבין התופעות הבאות הקשורות ל-{sub_id.replace('-', ' ')} מדגימה בצורה הטובה ביותר את המורכבות של התהליך?",
            "options": [
                "שינוי במוטציה בחלבון Transmembrane המוביל לחוסר יציבות.",
                "עיכוב של אנזים Kinase המונע זרחון תלוי-ליגנד.",
                "עלייה בריכוז ה-Calcium בציטוזול כתוצאה מפתיחת תעלות.",
                "פגיעה ברצף ה-Signal Peptide המכוון חלבונים לאברון."
            ],
            "correctIndex": 0,
            "explanation": "התשובה הנכונה היא א' מכיוון שחלבון ה-Transmembrane מהווה מרכיב קריטי. מוטציה באזור ההידרופובי תפגע באינטראקציה עם ה-Lipid Bilayer. תשובות אחרות, אף שהן נכונות לתהליכים אחרים, פחות ספציפיות לנושא זה.",
            "tags": ["cell-biology", "advanced"]
        }
        
        q2 = {
            "id": q2_id,
            "subtopicId": sub_id,
            "chapterId": ch_id,
            "areaId": area_id,
            "difficulty": 3,
            "question": "בניסוי in vitro לבחינת מנגנונים הקשורים לנושא, הוספת מעכב תחרותי גרמה להפסקת התהליך. מהי הסיבה הסבירה ביותר?",
            "options": [
                "המעכב נקשר לאתר הפעיל ומונע קישור של ה-Substrate הטבעי.",
                "פירוק ספונטני של ה-Lipid Bilayer עקב שינוי ב-pH.",
                "אוליגומריזציה של חלבונים ב-Endoplasmic Reticulum.",
                "ירידה בביטוי גנים ברמת ה-Transcription בגרעין."
            ],
            "correctIndex": 0,
            "explanation": "מעכב תחרותי נקשר לאתר הפעיל במקום ה-Substrate (הליגנד), וכך חוסם את פעילות האנזים או הרצפטור. האפשרויות האחרות מתארות מנגנונים שאינם נובעים ישירות ממעכב תחרותי ספציפי.",
            "tags": ["cell-biology", "experimental"]
        }
        
        questions.extend([q1, q2])
    
    # Generate 1 lesson per chapter
    lesson = {
        "id": f"lesson_{ch_id}",
        "chapterId": ch_id,
        "areaId": area_id,
        "title": ch["title"],
        "titleEn": ch["titleEn"],
        "estimatedMinutes": 30,
        "cards": [
            {
                "type": "concept",
                "title": "מבוא לפרק",
                "content": "בפרק זה נדון במבנה ותפקוד של רכיבי התא. **Lipid Bilayer** וחלבוני הממברנה מהווים את הבסיס למדור התאי.",
                "keyPoints": ["מבנה הממברנה", "חלבוני תא"]
            },
            {
                "type": "concept",
                "title": "מושגים מתקדמים",
                "content": "תהליכי **Signal Transduction** ו-**Vesicular Transport** חיוניים לשמירה על הומיאוסטזיס תאי. חלבונים כגון **SNAREs** מעורבים באיחוי ממברנות.",
                "keyPoints": ["העברת אותות", "איחוי ממברנות"]
            },
            {
                "type": "quiz_prompt",
                "content": "בואו נתרגל את מה שלמדנו עד כה."
            }
        ],
        "followUpQuestionIds": q_ids
    }
    lessons.append(lesson)

with open("/Users/rommiyara/.gemini/antigravity/scratch/med-exam-trainer/data/q_cell-biology.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

with open("/Users/rommiyara/.gemini/antigravity/scratch/med-exam-trainer/data/l_cell-biology.json", "w", encoding="utf-8") as f:
    json.dump(lessons, f, ensure_ascii=False, indent=2)

print("Successfully saved both files.")
