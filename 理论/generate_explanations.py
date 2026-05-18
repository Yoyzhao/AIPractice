import os
import re
import json
import urllib.request
from urllib.error import URLError, HTTPError

# =========================================================
# 【请在此处填入您的大模型 API 密钥】
# 推荐使用 DeepSeek、通义千问（DashScope）、智谱等兼容 OpenAI 格式的 API
API_KEY = "sk-bfsvzxyhrelqtkjohxhifexrbpvgcgoxbrjszjlyhyvotqsl"
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL_NAME = "Qwen/Qwen3-30B-A3B-Instruct-2507"  # 换用指定的 Qwen3 模型
# =========================================================

INPUT_FILE = "AI+人工智能训练师-答案.md"
OUTPUT_FILE = "AI+训练师理论题库及解析_V3.md"

def generate_explanation(question_text, options_text, answer):
    """调用大模型 API 生成解析"""
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        return "（请配置 API_KEY 后自动生成解析，或手动补充）"

    prompt = f"""
请你作为人工智能领域的专家、并了解人员培训、项目管理、劳动法等相关法律，为以下理论考试题目提供简明扼要的解析（控制在 50-80 字以内）。
直接输出解析内容，不要输出多余的引导语。

题目：{question_text}
选项：{options_text}
正确答案：{answer}
"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 150
    }
    
    req = urllib.request.Request(API_URL, data=json.dumps(data).encode('utf-8'), headers=headers)
    
    import time
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"API 请求失败 (第 {attempt + 1} 次尝试): {e}")
            time.sleep(2)
            
    return "（解析生成失败，请检查网络或 API 配置）"

def process_file():
    if not os.path.exists(INPUT_FILE):
        print(f"未找到输入文件: {INPUT_FILE}，请确保脚本在 '理论' 目录下运行。")
        return
        
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = content.replace('\r\n', '\n')
    # 【新增预处理】：修复因为 PDF 复制导致多道题合并在同一行的问题
    content = re.sub(r'([^#\n\s])\s+(\d+、)', r'\1\n\2', content)
    
    lines = content.split('\n')
    
    parsed_items = []
    
    q_num = ""
    q_stem = ""
    q_options = ""
    q_answer = ""
    
    def collect_current_question():
        nonlocal q_num, q_stem, q_options, q_answer
        if not q_num:
            return
            
        ans_match = re.search(r'[（\(]\s*([A-F对错√×TF]+)\s*[）\)]\s*[。.]*\s*$', q_stem)
        if ans_match:
            q_answer = ans_match.group(1)
            clean_stem = re.sub(r'[（\(]\s*[A-F对错√×TF]+\s*[）\)]\s*([。.]*)\s*$', r'（）\1', q_stem).strip()
        else:
            clean_stem = q_stem.strip()
            
        clean_opts = q_options.strip()
        if clean_opts:
            clean_opts = re.sub(r'[（\(]([A-F])[）\)]', r'\n\1. ', clean_opts).strip()
            
        parsed_items.append({
            'type': 'question',
            'q_num': q_num,
            'clean_stem': clean_stem,
            'clean_opts': clean_opts,
            'q_answer': q_answer
        })
        
        q_num = ""
        q_stem = ""
        q_options = ""
        q_answer = ""

    state = "search"
    for line in lines:
        line_s = line.strip()
        
        if line_s.startswith('# '):
            collect_current_question()
            parsed_items.append({'type': 'title', 'content': line_s})
            continue
            
        if "三、理论竞赛题库公开说明" in line_s:
            collect_current_question()
            break
            
        if not line_s:
            continue
            
        num_match = re.match(r'^(\d+)、(.*)', line_s)
        if num_match:
            collect_current_question()
            q_num = num_match.group(1)
            q_stem = num_match.group(2)
            state = "stem"
        elif state == "stem":
            if re.match(r'^[（\(][A-F][）\)]', line_s):
                q_options += line_s + " "
                state = "options"
            else:
                q_stem += "\n" + line_s
        elif state == "options":
            q_options += line_s + " "

    collect_current_question()
    
    # 开始并发处理
    print(f"解析到 {len([i for i in parsed_items if i['type'] == 'question'])} 道题目，准备使用并发调用大模型...")
    import concurrent.futures
    
    def process_item(item):
        if item['type'] == 'title':
            return f"{item['content']}\n\n"
        
        # 题目类型
        q_num = item['q_num']
        print(f"正在请求第 {q_num} 题...", flush=True)
        exp = generate_explanation(item['clean_stem'], item['clean_opts'], item['q_answer'])
        
        res = f"**{q_num}**\n**【题干】** {item['clean_stem']}\n"
        if item['clean_opts']:
            res += f"**【备选项】**\n{item['clean_opts']}\n"
        res += f"**【答案】** {item['q_answer']}\n"
        res += f"**【解析】** {exp}\n\n"
        return res

    out_f = open(OUTPUT_FILE, 'w', encoding='utf-8')
    
    # 调整 max_workers 控制并发数，数值越大越快，但容易触发 API 频率限制
    # 硅基流动 Qwen 并发通常可设置在 5-10
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # executor.map 保证返回结果的顺序与输入顺序完全一致
        for result_text in executor.map(process_item, parsed_items):
            out_f.write(result_text)
            out_f.flush()
            
    out_f.close()
    print("处理完成！极速结果已保存至", OUTPUT_FILE)

if __name__ == "__main__":
    process_file()
