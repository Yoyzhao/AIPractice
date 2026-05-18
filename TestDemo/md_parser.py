#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MD文件解析器
功能：解析最新统一格式的Markdown题库文件（AI+人工智能训练师-答案.md）
支持从单个文件中自动按章节区分单选、多选、判断题。
"""

import re
import json
import os


class MDParser:
    """MD题库文件解析器"""

    def __init__(self):
        self.questions = []

    def parse_content(self, content, default_type=None):
        """
        解析MD内容字符串
        自动识别 `# （一）单选题` 等章节标题，忽略传入的 default_type
        """
        content = content.replace('\r\n', '\n')
        
        type_map = {
            '单选': 'single',
            '多选': 'multi',
            '判断': 'judge'
        }
        
        sections = re.split(r'(#\s*（[一二三]）.*)', content)
        questions = []
        
        for i in range(1, len(sections), 2):
            header = sections[i]
            sec_content = sections[i+1]
            
            q_type = default_type or 'single'
            for key, val in type_map.items():
                if key in header:
                    q_type = val
                    break
                    
            # 匹配题目块，使用非贪婪匹配并在遇到下一个 **数字** 块时停止
            blocks = re.findall(r'\*\*(\d+)\*\*\s*\n(.*?)(?=\n\*\*\d+\*\*\s*\n|\Z)', sec_content, re.DOTALL)
            
            # 使用字典去重，保留相同题号的最后一次解析（因为后面生成的带完整选项）
            unique_blocks = {}
            for q_num, q_text in blocks:
                unique_blocks[q_num] = q_text
                
            for q_num, q_text in unique_blocks.items():
                q_obj = self._parse_block(q_num, q_text, q_type)
                if q_obj:
                    questions.append(q_obj)

        return questions

    def parse_file(self, file_path, default_type=None):
        """解析单个MD文件"""
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.parse_content(content, default_type)

    def _parse_block(self, question_num, text, q_type):
        """解析单个题目块（提取题目、答案、选项、解析）"""
        stem_match = re.search(r'\*\*【题干】\*\*\s*(.*?)(?=\n\*\*|$)', text, re.DOTALL)
        options_match = re.search(r'\*\*【备选项】\*\*\s*(.*?)(?=\n\*\*|$)', text, re.DOTALL)
        ans_match = re.search(r'\*\*【答案】\*\*\s*(.*?)(?=\n\*\*|$)', text, re.DOTALL)
        exp_match = re.search(r'\*\*【解析】\*\*\s*(.*?)(?=\n\*\*|$)', text, re.DOTALL)
        
        if not stem_match or not ans_match:
            return None
            
        q_content = stem_match.group(1).strip()
        ans_str = ans_match.group(1).strip()
        explanation = exp_match.group(1).strip() if exp_match else ''
        
        # 尝试提取选项
        options = {}
        if q_type in ['single', 'multi']:
            # 如果存在【备选项】，从中提取；否则尝试从题干中提取（容错）
            opts_text = ""
            if options_match:
                opts_text = options_match.group(1).strip()
            else:
                # 尝试从题干提取 A. B. C. D.
                opt_start = re.search(r'([A-Ea-e])[.、]\s*', q_content)
                if opt_start:
                    opts_text = q_content[opt_start.start():].strip()
                    q_content = q_content[:opt_start.start()].strip()
            
            if opts_text:
                # 处理由于大模型可能输出重复选项块的问题（如A...D A...D）
                # 提取第一个完整的选项集
                found_keys = set()
                for m in re.finditer(r'([A-Ea-e])[.、]\s*(.*?)(?=\n[A-Ea-e][.、]|$)', opts_text, re.DOTALL):
                    opt_key = m.group(1).upper()
                    opt_val = m.group(2).strip()
                    if opt_key not in found_keys:
                        options[opt_key] = opt_val
                        found_keys.add(opt_key)
            
            # 多选题答案排序
            answer = ''.join(sorted(re.sub(r'[^A-Ea-e]', '', ans_str).upper()))
        else:
            options = {'A': '正确', 'B': '错误'}
            if ans_str in ['对', '√', 'T', 'TRUE', 'A', '正确']:
                answer = 'A'
            else:
                answer = 'B'

        # 验证题目完整性
        if not q_content or not answer:
            return None
        if q_type in ['single', 'multi'] and len(options) < 2:
            return None

        return {
            'original_index': int(question_num),
            'type': q_type,
            'content': q_content,
            'options': options,
            'answer': answer,
            'explanation': explanation
        }

    def parse_all(self, md_dir):
        """解析目录下所有MD文件（兼容旧版调用逻辑）"""
        questions = []
        for filename in os.listdir(md_dir):
            if not filename.endswith('.md'):
                continue
            
            file_path = os.path.join(md_dir, filename)
            print(f"正在解析: {filename}")
            file_questions = self.parse_file(file_path)
            questions.extend(file_questions)
            print(f"  解析完成，共 {len(file_questions)} 道题目")

        self.questions = questions
        return questions

    def get_questions_by_type(self, question_type):
        """按题型获取题目"""
        return [q for q in self.questions if q['type'] == question_type]

    def get_statistics(self):
        """获取题目统计"""
        stats = {
            'total': len(self.questions),
            'single': len(self.get_questions_by_type('single')),
            'multi': len(self.get_questions_by_type('multi')),
            'judge': len(self.get_questions_by_type('judge'))
        }
        return stats


def main():
    """测试解析器"""
    parser = MDParser()
    md_file = '../理论/AI+训练师理论题库及解析_V3.md'

    if os.path.exists(md_file):
        questions = parser.parse_file(md_file)
        parser.questions = questions
        stats = parser.get_statistics()

        print("\n" + "=" * 50)
        print("解析完成！题目统计：")
        print(f"  总题目数: {stats['total']}")
        print(f"  单选题: {stats['single']}")
        print(f"  多选题: {stats['multi']}")
        print(f"  判断题: {stats['judge']}")

        if questions:
            print("\n第一道题示例：")
            print(f"类型: {questions[0]['type']}")
            print(f"内容: {questions[0]['content']}")
            print(f"选项: {questions[0]['options']}")
            print(f"答案: {questions[0]['answer']}")

        os.makedirs('data', exist_ok=True)
        output_file = 'data/questions.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"\n已保存到: {output_file}")
    else:
        print(f"文件不存在: {md_file}")


if __name__ == '__main__':
    main()
