import re

file_path = r'e:\Desktop\AI+训练师\AI+人工智能训练师-判断题.md'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

content = re.sub(r'(\*\*答案：[^\n]+\n)', r'\1\n', content)
content = re.sub(r'(\*\*解析：[^\n]+\n)', r'\1\n', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")