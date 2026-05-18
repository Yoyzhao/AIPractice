from md_parser import MDParser
import os

p = MDParser()
file_path = '../理论/AI+人工智能训练师-答案.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    
# Duplicate the logic to see what's dropped
import re
content = content.replace('\r\n', '\n')
sections = {}
current_section = None
lines = content.split('\n')
for line in lines:
    line = line.strip()
    sec_match = re.match(r'^#\s*（[一二三]）(.*)', line)
    if sec_match:
        current_section = sec_match.group(1).strip()
        sections[current_section] = []
    elif current_section is not None:
        if "三、理论竞赛题库公开说明" in line:
            break
        sections[current_section].append(line)
        
sec_name = '单选题'
sec_lines = sections[sec_name]
sec_content = '\n'.join(sec_lines)
sec_content = re.sub(r'([^#\n\s])\s+(\d+、)', r'\1\n\2', sec_content)
pattern = r'(?:^|\n)\s*(\d+)、(.*?)(?=(?:\n\s*\d+、|\Z))'
matches = list(re.finditer(pattern, sec_content, re.DOTALL))

parsed_count = 0
dropped = []
for m in matches:
    q_num = m.group(1)
    q_text = m.group(2)
    q_obj = p._parse_block(q_num, q_text, 'single')
    if q_obj:
        parsed_count += 1
    else:
        dropped.append((q_num, q_text))
        
print(f"Total regex matches: {len(matches)}")
print(f"Parsed: {parsed_count}")
print(f"Dropped: {len(dropped)}")
for num, txt in dropped:
    print(f"Dropped Q{num}: {txt[:60]}")
    
