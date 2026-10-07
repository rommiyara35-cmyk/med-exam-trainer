import re
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_func = """function getState() {
  const defState = {
    streak: 0, lastDate: null, xpToday: 0, xpTotal: 0,
    totalAnswered: 0, totalCorrect: 0,
    missionsCompleted: [],
    mastery: {},
    settings: { sounds: true, haptics: true }
  };
  const saved = DB.get('state');
  if (!saved) return defState;
  return { ...defState, ...saved, settings: { ...defState.settings, ...(saved.settings || {}) } };
}"""

content = re.sub(r'function getState\(\) \{.*?\}\);?\n?\}', new_func, content, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done.")
