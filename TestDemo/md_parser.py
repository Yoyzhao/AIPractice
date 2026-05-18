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

    def parse_content(self, content, question_type):
        """解析MD内容字符串"""
        # 统一换行符，避免不同平台的换行符导致切分失败
        content = content.replace('\r\n', '\n')
        
        # 增强的分隔符正则：
        # 1. 支持 3 个及以上的连字符 (-{3,})
        # 2. 支持分隔符前后有空格 (\s*)
        # 3. 允许分隔符出现在行首或行尾，不仅仅是 \n---\n
        # 4. 过滤掉切分后产生的空块
        blocks = re.split(r'\n\s*-{3,}\s*\n|^---+\s*\n|\n\s*---+$', content, flags=re.MULTILINE)
        
        questions = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            parsed = self._parse_block(block, question_type)
            if parsed:
                questions.extend(parsed)

        return questions

    def parse_file(self, file_path, question_type):
        """解析单个MD文件"""
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.parse_content(content, question_type)

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

            # 1. 强匹配识别：如果匹配到数字题号，则强制开启一个新题目
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
            # 2. 弱匹配识别：如果当前没有正在解析的题目，且本行不是答案/解析/选项，则将其作为新题目起始
            elif current_question is None:
                is_metadata = '**答案' in line or '**解析' in line or self._is_option_line(line)
                if not is_metadata:
                    current_question = {
                        'type': question_type,
                        'content': line,
                        'options': {},
                        'answer': '',
                        'explanation': ''
                    }
            # 3. 内容填充：已有题目，则将行内容交给 _parse_line 处理（识别选项、答案或追加内容）
            else:
                self._parse_line(line, current_question, question_type)

        if current_question and current_question['content']:
            q = self._finish_question(current_question, question_type)
            if q:
                questions.append(q)

        return questions

    def _is_option_line(self, line):
        """判断是否为疑似选项行"""
        line = line.strip()
        # 只要是以 (A), A., A、 或 A 后面跟空格开头的，都视为疑似选项
        return bool(re.match(r'^([（(][A-E][）)]|[A-E][\.、\s])', line))

    def _finish_question(self, question, question_type):
        """完成题目解析，验证并返回"""
        # 清理题目内容
        question['content'] = question['content'].strip()
        
        if question_type in ['single', 'multi']:
            question['options'] = question.get('options', {})
            if not question['options']:
                return None
            
            # 多选题答案排序
            if question_type == 'multi' and question['answer']:
                question['answer'] = ''.join(sorted(question['answer'].upper()))
                
        elif question_type == 'judge':
            question['options'] = {'A': '正确', 'B': '错误'}

        if not question['content'] or not question['answer']:
            return None

        if question_type in ['single', 'multi'] and len(question['options']) < 2:
            return None

        return question

    def _parse_line(self, line, question, question_type):
        """解析题目中的一行"""
        line = line.strip()
        if not line:
            return False

        # 1. 识别答案
        if '**答案' in line:
            if question_type == 'judge':
                # 增强判断题识别
                if any(x in line for x in ['正确', '对', '√', 'T', 'TRUE']):
                    question['answer'] = 'A'
                elif any(x in line for x in ['错误', '错', '×', 'F', 'FALSE']):
                    question['answer'] = 'B'
            else:
                answer_match = re.search(r'\*\*答案[:：]?\s*([A-Za-e]+)', line)
                if answer_match:
                    question['answer'] = answer_match.group(1).upper()
            return True

        # 2. 识别解析
        elif '**解析' in line:
            exp_match = re.search(r'\*\*解析[:：]?\s*(.+)', line)
            if exp_match:
                question['explanation'] = exp_match.group(1).strip()
            return True

        # 3. 识别选项 (仅限单选/多选)
        elif question_type in ['single', 'multi']:
            if self._parse_options_line(line, question['options']):
                return True
        
        # 4. 如果以上都不是，且题目已经开始，则累加到题目内容
        if question['content']:
            # 避免重复累加选项（如果选项格式非常特殊没被识别到，至少不要弄乱题目内容）
            # 只有当行不符合“疑似选项”特征时才累加
            if not self._is_option_line(line):
                question['content'] += " " + line
        else:
            question['content'] = line
            
        return True

    def _parse_options_line(self, line, options_dict):
        """解析选项行，支持单行多个选项或单行单个选项"""
        line = line.strip()
        if not line:
            return False

        # 尝试匹配多种格式的选项: (A) A. A、 A
        # 我们使用更通用的正则，优先匹配带括号或点的
        
        # 模式1: (A) 或 （A） 开头的选项
        pattern_with_paren = r'[（(]([A-E])[）)]\s*([^（(]+)'
        matches = re.findall(pattern_with_paren, line)
        
        if not matches:
            # 模式2: A. 或 A、 或 A 开头的选项 (单行单个)
            pattern_single = r'^([A-E])[\.、\s]\s*(.+)$'
            match = re.match(pattern_single, line)
            if match:
                matches = [(match.group(1), match.group(2))]

        if matches:
            for key, val in matches:
                key = key.upper()
                if key not in options_dict:
                    options_dict[key] = val.strip()
            return True
            
        return False

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
