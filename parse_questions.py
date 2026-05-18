import re
import json

def parse_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Clean up the text
    content = content.replace('\r\n', '\n')
    
    # Use a more robust regex to find questions
    # A question starts with a number followed by '、'
    # We can find all occurrences of number、
    matches = list(re.finditer(r'(\d+)、(.*?)(?=(\d+、)|$)', content, re.DOTALL))
    
    questions = []
    for m in matches:
        q_num = m.group(1)
        q_text = m.group(2).strip()
        
        # We need to extract the answer and options
        ans_match = re.search(r'（([A-Z]+)）|（([A-Z，,]+)）|（(正确|错误|对|错|√|×|T|F|TRUE|FALSE)）', q_text)
        answer = ""
        if ans_match:
            answer = ans_match.group(1) or ans_match.group(2) or ans_match.group(3)
            
        # Extract options: look for （A） or A.
        # Options usually start with （A）
        opt_match = re.search(r'（A）[\s\S]*', q_text)
        options_str = ""
        question_body = q_text
        if opt_match:
            options_str = opt_match.group(0).strip()
            question_body = q_text[:opt_match.start()].strip()
            
        # Clean up question body (remove trailing answer if it's at the end)
        question_body = re.sub(r'（[A-Z]+）$', '（）', question_body).strip()
        
        questions.append({
            "num": q_num,
            "body": question_body,
            "options": options_str,
            "answer": answer
        })

    with open('parsed_100.json', 'w', encoding='utf-8') as f:
        json.dump(questions[:100], f, ensure_ascii=False, indent=2)
        
    print(f"Total questions found: {len(questions)}")

parse_md('d:/Workspace/AIPractice/理论/AI+人工智能训练师-答案.md')
