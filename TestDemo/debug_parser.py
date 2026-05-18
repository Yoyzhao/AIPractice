import re

def test_parse():
    with open(r'd:\Workspace\AIPractice\理论\AI+人工智能训练师-答案.md', 'r', encoding='utf-8') as f:
        content = f.read()

    sections = {}
    current_section = None
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if re.match(r'^#\s*（[一二三]）(.*)', line):
            current_section = re.match(r'^#\s*（[一二三]）(.*)', line).group(1)
            sections[current_section] = []
        elif current_section is not None:
            if "三、理论竞赛题库公开说明" in line:
                break
            sections[current_section].append(line)
            
    sec_lines = sections.get('单选题', [])
    sec_content = '\n'.join(sec_lines)
    
    # Ensure that `\d+、` has a newline before it if preceded by text.
    sec_content = re.sub(r'([^#\n\s])\s+(\d+、)', r'\1\n\2', sec_content)
    
    pattern = r'(?:^|\n)\s*(\d+)、(.*?)(?=(?:\n\s*\d+、|\Z))'
    matches = list(re.finditer(pattern, sec_content, re.DOTALL))
    
    expected = 1
    for m in matches:
        num = int(m.group(1))
        if num != expected:
            print(f"[{num}] {m.group(2)[:50]}")
        else:
            expected += 1
            
test_parse()
