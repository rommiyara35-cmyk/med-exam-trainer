import re
with open('data/generate_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """                    else:
                        print(f"❌ שגיאה בנושא {subtopic['title']} עם {model_name}: {e}", flush=True)
                        time.sleep(5)
                        break"""

new_block = """                    else:
                        print(f"❌ שגיאה בנושא {subtopic['title']} עם {model_name}: {e}. מנסה מודל הבא...", flush=True)
                        current_model_idx += 1
                        time.sleep(2)"""

content = content.replace(old_block, new_block)
with open('data/generate_data.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched errors.")
