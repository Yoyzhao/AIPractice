import re

def parse_block(question_num, text, q_type):
    # print(f"\n--- Question {question_num} ---")
    # print(f"Raw: {text}")
    
    # 1. Extract Answer from text
    answer = None
    if q_type == 'judge':
        # Find (对) or (错) etc.
        ans_match = re.search(r'[（\(]\s*(对|错|√|×|T|F|TRUE|FALSE)\s*[）\)]', text)
        if ans_match:
            ans_str = ans_match.group(1)
            if ans_str in ['对', '√', 'T', 'TRUE']:
                answer = 'A'
            else:
                answer = 'B'
            # Replace answer with empty parentheses
            text = text[:ans_match.start()] + '（）' + text[ans_match.end():]
    else:
        # Find (A) or (AB) etc.
        ans_matches = list(re.finditer(r'[（\(]\s*([A-Ea-e]{1,5})\s*[）\)]', text))
        if ans_matches:
            # Usually the last one is the answer, or there is only one
            ans_match = ans_matches[-1]
            answer = ans_match.group(1).upper()
            # Replace answer with empty parentheses
            text = text[:ans_match.start()] + '（）' + text[ans_match.end():]

    # 2. Extract Options (for single/multi)
    options = {}
    if q_type in ['single', 'multi']:
        # Options usually start with （A） or (A) or A. or A、
        # We can split the text by finding the first option.
        # But wait, what if the text contains A. in the question?
        # Let's search for the first occurrence of `(?:[（\(][A-E][）\)]|[A-E][.、])`
        # However, to be safe, let's just find all options.
        opt_pattern = r'(?:[（\(]([A-E])[）\)]|([A-E])[.、])\s*(.*?)(?=(?:[（\(][A-E][）\)]|[A-E][.、]|$))'
        
        # We need to find where the options block starts. It starts at the first match of option A.
        # Let's find option A.
        opt_a_match = re.search(r'(?:[（\(]A[）\)]|A[.、])', text)
        if opt_a_match:
            q_content = text[:opt_a_match.start()].strip()
            opt_content = text[opt_a_match.start():].strip()
            
            # Now extract all options from opt_content
            for m in re.finditer(opt_pattern, opt_content, re.DOTALL):
                opt_key = m.group(1) or m.group(2)
                opt_val = m.group(3).strip()
                options[opt_key.upper()] = opt_val
            text = q_content
        else:
            q_content = text.strip()
    else:
        q_content = text.strip()
        options = {'A': '正确', 'B': '错误'}
        
    # print(f"Content: {q_content}")
    # print(f"Options: {options}")
    # print(f"Answer: {answer}")
    return q_content, options, answer

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
            
    type_map = {'单选题': 'single', '多选题': 'multi', '判断题': 'judge'}
            
    for sec_name, sec_lines in sections.items():
        q_type = type_map.get(sec_name)
        if not q_type: continue
            
        sec_content = '\n'.join(sec_lines)
        sec_content = re.sub(r'([^#\n\s])\s+(\d+、)', r'\1\n\2', sec_content)
        pattern = r'(?:^|\n)\s*(\d+)、(.*?)(?=(?:\n\s*\d+、|\Z))'
        matches = list(re.finditer(pattern, sec_content, re.DOTALL))
        
        missing_answers = 0
        missing_options = 0
        
        for m in matches:
            q_num = m.group(1)
            q_text = m.group(2)
            content, options, answer = parse_block(q_num, q_text, q_type)
            
            if not answer:
                missing_answers += 1
                # print(f"[{sec_name}] Missing answer for Q{q_num}: {q_text[:50]}")
            if q_type in ['single', 'multi'] and not options:
                missing_options += 1
                print(f"[{sec_name}] Missing options for Q{q_num}: {q_text}")
                
        print(f"Section {sec_name}: {len(matches)} questions, {missing_answers} missing answers, {missing_options} missing options.")
        
test_parse()
