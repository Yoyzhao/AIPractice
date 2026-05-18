#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MD文件解析器
功能：解析Markdown格式的题库文件，提取题目、选项、答案、解析
"""

import re
import json
import os


class MDParser:
    """MD题库文件解析器"""

    def __init__(self):
        self.questions = []

    def parse_file(self, file_path, question_type):
        """解析单个MD文件"""
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks = re.split(r'\n---\n', content)
        questions = []

        for block in blocks:
            parsed = self._parse_block(block.strip(), question_type)
            if parsed:
                questions.extend(parsed)

        return questions

    def _parse_block(self, block, question_type):
        """解析单个题目块，可能包含标题和多个题目"""
        if not block:
            return []

        lines = [l for l in block.split('\n') if l.strip()]
        if not lines:
            return []

        questions = []
        current_question = None

        for line in lines:
            line = line.strip()

            if line.startswith('#'):
                continue

            if re.match(r'^\d+[、．.]', line):
                if current_question and current_question['content']:
                    q = self._finish_question(current_question, question_type)
                    if q:
                        questions.append(q)
                content_match = re.match(r'^\d+[．.、]\s*(.+)', line)
                current_question = {
                    'type': question_type,
                    'content': content_match.group(1) if content_match else line,
                    'options': {},
                    'answer': '',
                    'explanation': ''
                }
            elif current_question is not None:
                self._parse_line(line, current_question, question_type)

        if current_question and current_question['content']:
            q = self._finish_question(current_question, question_type)
            if q:
                questions.append(q)

        return questions

    def _finish_question(self, question, question_type):
        """完成题目解析，验证并返回"""
        if question_type in ['single', 'multi']:
            question['options'] = question.get('options', {})
            if not question['options']:
                return None
        elif question_type == 'judge':
            question['options'] = {'A': '正确', 'B': '错误'}

        if not question['content'] or not question['answer']:
            return None

        if question_type in ['single', 'multi'] and len(question['options']) < 2:
            return None

        return question

    def _parse_line(self, line, question, question_type):
        """解析题目中的一行"""
        if '**答案' in line:
            if question_type == 'judge':
                if '正确' in line:
                    question['answer'] = 'A'
                elif '错误' in line:
                    question['answer'] = 'B'
            else:
                answer_match = re.search(r'\*\*答案[:：]?\s*([A-Za-e]+)', line)
                if answer_match:
                    question['answer'] = answer_match.group(1).upper()

        elif '**解析' in line:
            exp_match = re.search(r'\*\*解析[:：]?\s*(.+)', line)
            if exp_match:
                question['explanation'] = exp_match.group(1).strip()

        elif question_type in ['single', 'multi']:
            self._parse_options_line(line, question['options'])

    def _parse_options_line(self, line, options_dict):
        """解析选项行"""
        line = line.strip()
        if not line:
            return

        pattern1 = r'[（(]([A-E])[）)]\s*(.+?)(?=[（(][A-E]|$)'
        matches = re.findall(pattern1, line, re.DOTALL)
        if matches:
            for match in matches:
                option_key = match[0].upper()
                option_value = match[1].strip()
                option_value = re.sub(r'[（(][A-E][）)]\s*.*$', '', option_value).strip()
                if option_value and option_key not in options_dict:
                    options_dict[option_key] = option_value
            return

        pattern2 = r'^[（(]([A-E])[）)]\s*(.+)$'
        match = re.match(pattern2, line)
        if match:
            option_key = match.group(1).upper()
            option_value = match.group(2).strip()
            if option_key not in options_dict:
                options_dict[option_key] = option_value

    def parse_all(self, md_dir):
        """解析目录下所有MD文件"""
        questions = []

        type_mapping = {
            '单选题': 'single',
            '多选题': 'multi',
            '判断题': 'judge'
        }

        for filename in os.listdir(md_dir):
            if not filename.endswith('.md'):
                continue

            question_type = None
            for key, value in type_mapping.items():
                if key in filename:
                    question_type = value
                    break

            if question_type is None:
                continue

            file_path = os.path.join(md_dir, filename)
            print(f"正在解析: {filename} ({question_type})")

            file_questions = self.parse_file(file_path, question_type)
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
    md_dir = '../理论'

    if os.path.exists(md_dir):
        questions = parser.parse_all(md_dir)
        stats = parser.get_statistics()

        print("\n" + "=" * 50)
        print("解析完成！题目统计：")
        print(f"  总题目数: {stats['total']}")
        print(f"  单选题: {stats['single']}")
        print(f"  多选题: {stats['multi']}")
        print(f"  判断题: {stats['judge']}")

        if questions:
            print("\n第一道题示例：")
            print(f"内容: {questions[0]['content']}")
            print(f"选项: {questions[0]['options']}")
            print(f"答案: {questions[0]['answer']}")

        os.makedirs('data', exist_ok=True)
        output_file = 'data/questions.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"\n已保存到: {output_file}")
    else:
        print(f"目录不存在: {md_dir}")


if __name__ == '__main__':
    main()
