import re
with open('data/generate_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        print(f"⚠️ מודל {model_name} סיים מכסה, עובר למודל הבא...", flush=True)
                        current_model_idx += 1
                        time.sleep(2)
                    else:
                        print(f"❌ שגיאה בנושא {subtopic['title']} עם {model_name}: {e}", flush=True)
                        time.sleep(5)
                        break # Skip this subtopic if it's not a quota error"""

new_block = """                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        print(f"⚠️ מודל {model_name} סיים מכסה, עובר למודל הבא...", flush=True)
                        current_model_idx += 1
                        time.sleep(2)
                    elif "503" in err_str or "UNAVAILABLE" in err_str:
                        print(f"⚠️ עומס שרת ב-{model_name}, ממתין 20 שניות ומנסה שוב...", flush=True)
                        time.sleep(20)
                    else:
                        print(f"❌ שגיאה בנושא {subtopic['title']} עם {model_name}: {e}", flush=True)
                        time.sleep(5)
                        break"""

content = content.replace(old_block, new_block)
with open('data/generate_data.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched.")
