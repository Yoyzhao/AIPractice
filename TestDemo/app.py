#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在线刷题系统 - Flask主应用
功能：提供刷题、错题本、统计等API接口
"""

import os
import random
from flask import Flask, render_template, jsonify, request
from models import get_db
from md_parser import MDParser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'exam-practice-secret-key-2026'
app.config['JSON_AS_ASCII'] = False

# 刷题会话数据（内存存储）
session_data = {
    'current_question': None,
    'answered_ids': [],
    'current_type': 'single',
    'type_counts': {'single': 0, 'multi': 0, 'judge': 0},
    'type_targets': {'single': 0, 'multi': 0, 'judge': 0}
}

# 题型比例
TYPE_RATIOS = {
    'single': 0.6,   # 单选题 60%
    'multi': 0.1,    # 多选题 10%
    'judge': 0.3     # 判断题 30%
}


def calculate_type_targets():
    """
    根据设置或导入题目的实际数量计算各题型目标数量
    """
    db = get_db()
    settings = db.get_settings()
    
    # 获取各题型实际题目数量
    single_count = db.get_question_count_by_type('single')
    multi_count = db.get_question_count_by_type('multi')
    judge_count = db.get_question_count_by_type('judge')

    total_available = single_count + multi_count + judge_count

    if total_available == 0:
        return {'single': 0, 'multi': 0, 'judge': 0, 'total': 0}

    # 如果数据库题目数量少于设置的目标，则以数据库数量为准
    # 否则以设置的目标为准，实现“练习一轮”的概念
    single_target = min(settings.get('single_count', 120), single_count)
    multi_target = min(settings.get('multi_count', 10), multi_count)
    judge_target = min(settings.get('judge_count', 30), judge_count)

    return {
        'single': single_target,
        'multi': multi_target,
        'judge': judge_target,
        'total': single_target + multi_target + judge_target
    }


def get_next_question():
    """
    获取下一道题目
    选题优先级（在目标题型内）：
    1. 错题本中的题目 (Priority 1)
    2. 从未做过的题目 (Priority 2)
    3. 已答对的题目 (Priority 3)

    出题比例由 calculate_type_targets 动态计算
    """
    db = get_db()

    # 1. 计算各题型目标数量
    session_data['type_targets'] = calculate_type_targets()

    # 2. 获取本次会话已答题目的各题型数量
    answered_by_type = {'single': 0, 'multi': 0, 'judge': 0}
    for qid in session_data['answered_ids']:
        q = db.get_question_by_id(qid)
        if q:
            answered_by_type[q['type']] += 1

    # 3. 找出还未达到目标的题型（按优先级）
    type_priority = ['single', 'multi', 'judge']
    target_type = None

    for qtype in type_priority:
        if answered_by_type[qtype] < session_data['type_targets'][qtype]:
            target_type = qtype
            break

    # 如果所有题型都答完了，说明当前会话目标已达成
    if target_type is None:
        return None

    # 4. 在该题型内，按“错题 > 未做题 > 已对题”的优先级获取
    for pool in ['wrong', 'unseen', 'all']:
        question = db.get_random_question(
            question_type=target_type,
            exclude_ids=session_data['answered_ids'],
            pool=pool
        )
        if question:
            return question

    return None


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/wrongbook')
def wrongbook():
    """错题本页面"""
    return render_template('wrongbook.html')


@app.route('/api/init', methods=['POST'])
def init_session():
    """初始化刷题会话"""
    global session_data

    # 重置会话
    session_data = {
        'current_question': None,
        'answered_ids': [],
        'current_type': 'single',
        'type_counts': {'single': 0, 'multi': 0, 'judge': 0},
        'type_targets': {'single': 0, 'multi': 0, 'judge': 0, 'total': 0}
    }

    db = get_db()
    stats = db.get_statistics()
    type_targets = calculate_type_targets()
    question_count = db.get_question_count()

    return jsonify({
        'success': True,
        'stats': stats,
        'type_targets': type_targets,
        'question_count': question_count
    })


@app.route('/api/question/next', methods=['GET'])
def get_next():
    """获取下一道题目"""
    global session_data

    # 获取查询参数
    wrong_only = request.args.get('wrong_only', 'false').lower() == 'true'
    target_type = request.args.get('type')  # single, multi, judge
    
    if wrong_only:
        db = get_db()
        wrongbook = db.get_wrongbook()
        if not wrongbook:
            return jsonify({'success': False, 'message': '错题本已清空！'})
        
        # 如果指定了题型，则在错题本中过滤
        if target_type:
            wrongbook = [q for q in wrongbook if q['type'] == target_type]
            if not wrongbook:
                return jsonify({'success': False, 'message': f'错题本中没有该类型的题目！'})
        
        question = random.choice(wrongbook)
    elif target_type:
        # 指定了题型，按优先级获取题目
        db = get_db()
        for pool in ['wrong', 'unseen', 'all']:
            question = db.get_random_question(
                question_type=target_type,
                exclude_ids=session_data['answered_ids'],
                pool=pool
            )
            if question:
                break
    else:
        # 默认混合模式
        question = get_next_question()

    if question is None:
        return jsonify({
            'success': False,
            'message': '该类型题目已答完！' if target_type else '题目已答完！'
        })

    # 更新当前题目
    session_data['current_question'] = question

    return jsonify({
        'success': True,
        'question': {
            'id': question['id'],
            'type': question['type'],
            'type_name': {'single': '单选题', 'multi': '多选题', 'judge': '判断题'}[question['type']],
            'content': question['content'],
            'options': question['options']
        }
    })


@app.route('/api/question/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """获取指定题目"""
    db = get_db()
    question = db.get_question_by_id(question_id)

    if question is None:
        return jsonify({'success': False, 'message': '题目不存在'})

    return jsonify({
        'success': True,
        'question': {
            'id': question['id'],
            'type': question['type'],
            'type_name': {'single': '单选题', 'multi': '多选题', 'judge': '判断题'}[question['type']],
            'content': question['content'],
            'options': question['options'],
            'answer': question['answer'],
            'explanation': question['explanation']
        }
    })


@app.route('/api/answer', methods=['POST'])
def submit_answer():
    """提交答案"""
    global session_data

    data = request.get_json()
    question_id = data.get('question_id')
    user_answer = data.get('answer', '').upper()

    if not question_id or not user_answer:
        return jsonify({'success': False, 'message': '参数不完整'})

    db = get_db()

    # 获取题目信息
    question = db.get_question_by_id(question_id)
    if question is None:
        return jsonify({'success': False, 'message': '题目不存在'})

    # 标准化答案（去除空格，排序多选题答案）
    correct_answer = question['answer'].upper().replace(' ', '')
    user_answer_normalized = user_answer.upper().replace(' ', '')

    # 多选题排序答案以便比较
    if question['type'] == 'multi':
        correct_answer = ''.join(sorted(correct_answer))
        user_answer_normalized = ''.join(sorted(user_answer_normalized))

    # 判断是否正确
    is_correct = (correct_answer == user_answer_normalized)

    # 记录答题
    db.add_answer_record(question_id, user_answer, is_correct)

    # 更新已答题ID列表
    if question_id not in session_data['answered_ids']:
        session_data['answered_ids'].append(question_id)
        session_data['type_counts'][question['type']] += 1

    # 如果答错，记录到错题本
    if not is_correct:
        db.add_to_wrongbook(
            question_id=question_id,
            user_answer=user_answer
        )
    # 取消自动移除逻辑，改为用户手动在错题本页面移除

    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'correct_answer': question['answer'],
        'user_answer': user_answer,
        'explanation': question.get('explanation', ''),
        'question_type': question['type']
    })


@app.route('/api/wrongbook', methods=['GET'])
def get_wrongbook():
    """获取错题本"""
    db = get_db()
    wrongbook = db.get_wrongbook()

    questions = []
    for item in wrongbook:
        questions.append({
            'id': item['id'],
            'question_id': item['question_id'],
            'type': item['type'],
            'type_name': {'single': '单选题', 'multi': '多选题', 'judge': '判断题'}[item['type']],
            'content': item['content'],
            'options': item['options'],
            'user_answer': item['user_answer'],
            'correct_answer': item['correct_answer'],
            'explanation': item['explanation'],
            'wrong_count': item['wrong_count']
        })

    return jsonify({
        'success': True,
        'count': len(questions),
        'questions': questions
    })


@app.route('/api/wrongbook/<int:question_id>', methods=['DELETE'])
def remove_from_wrongbook(question_id):
    """从错题本移除（答对后移除）"""
    db = get_db()
    db.remove_from_wrongbook(question_id)
    return jsonify({'success': True})


@app.route('/api/wrongbook/clean', methods=['POST'])
def clean_wrongbook():
    """清空错题本"""
    db = get_db()
    wrongbook = db.get_wrongbook()
    for item in wrongbook:
        db.remove_from_wrongbook(item['question_id'])
    return jsonify({'success': True})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    db = get_db()
    stats = db.get_statistics()

    # 获取各题型实际数量
    single_count = db.get_question_count_by_type('single')
    multi_count = db.get_question_count_by_type('multi')
    judge_count = db.get_question_count_by_type('judge')

    # 动态计算题型目标（用于刷题进度）
    type_targets = calculate_type_targets()

    return jsonify({
        'success': True,
        'stats': stats,
        'type_targets': type_targets,
        'actual_counts': {
            'single': single_count,
            'multi': multi_count,
            'judge': judge_count,
            'total': single_count + multi_count + judge_count
        },
        'session_progress': {
            'answered': len(session_data['answered_ids']),
            'by_type': session_data['type_counts']
        }
    })


@app.route('/api/import', methods=['POST'])
def import_questions():
    """导入题库（从上传的文件）"""
    if 'files' not in request.files:
        return jsonify({
            'success': False,
            'message': '没有检测到上传的文件'
        })

    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({
            'success': False,
            'message': '未选择文件'
        })

    parser = MDParser()
    all_questions = []
    
    type_mapping = {
        '单选题': 'single',
        '多选题': 'multi',
        '判断题': 'judge'
    }

    for file in files:
        filename = file.filename
        if not filename.endswith('.md'):
            continue

        question_type = None
        for key, value in type_mapping.items():
            if key in filename:
                question_type = value
                break

        if question_type is None:
            # 如果文件名不含关键字，默认尝试解析为单选题或根据内容判断（这里简化处理）
            question_type = 'single'

        try:
            content = file.read().decode('utf-8')
            file_questions = parser.parse_content(content, question_type)
            all_questions.extend(file_questions)
        except Exception as e:
            print(f"解析文件 {filename} 出错: {str(e)}")

    if not all_questions:
        return jsonify({
            'success': False,
            'message': '未能从所选文件中解析出任何题目，请确保文件名包含“单选题”、“多选题”或“判断题”关键字。'
        })

    db = get_db()
    # 导入新题目（不清空旧题库，由用户决定是否清空）
    count = db.import_questions(all_questions)

    # 更新 parser 中的题目列表以获取统计
    parser.questions = all_questions

    return jsonify({
        'success': True,
        'message': f'成功导入 {count} 道题目',
        'statistics': parser.get_statistics()
    })


@app.route('/api/import/check', methods=['GET'])
def check_import():
    """检查是否已导入题库"""
    db = get_db()
    count = db.get_question_count()

    if count > 0:
        stats = db.get_statistics()
        return jsonify({
            'success': True,
            'imported': True,
            'count': count,
            'stats': stats
        })
    else:
        return jsonify({
            'success': True,
            'imported': False,
            'message': '题库未导入'
        })


@app.route('/api/reset', methods=['POST'])
def reset_progress():
    """重置刷题进度"""
    global session_data

    session_data = {
        'current_question': None,
        'answered_ids': [],
        'current_type': 'single',
        'type_counts': {'single': 0, 'multi': 0, 'judge': 0}
    }

    return jsonify({'success': True, 'message': '进度已重置'})


@app.route('/api/clear', methods=['POST'])
def clear_database():
    """清空题库和所有数据"""
    global session_data

    try:
        db = get_db()
        db.clear_questions()
        db.clear_wrong_answers()
        db.clear_answer_records()

        session_data = {
            'current_question': None,
            'answered_ids': [],
            'current_type': 'single',
            'type_counts': {'single': 0, 'multi': 0, 'judge': 0},
            'type_targets': {'single': 0, 'multi': 0, 'judge': 0, 'total': 0}
        }

        return jsonify({'success': True, 'message': '已清空所有数据'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)

    # 启动应用
    print("=" * 50)
    print("在线刷题系统启动中...")
    print("访问地址: http://127.0.0.1:5001")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)
