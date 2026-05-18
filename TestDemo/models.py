#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型
功能：定义SQLite数据库表结构和操作方法
"""

import sqlite3
import json
import os
from datetime import datetime


class Database:
    """数据库操作类"""

    def __init__(self, db_path='data/exam.db'):
        """
        初始化数据库

        参数:
            db_path - 数据库文件路径
        """
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                options TEXT NOT NULL,
                answer VARCHAR(50) NOT NULL,
                explanation TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answer_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                user_answer VARCHAR(50) NOT NULL,
                is_correct BOOLEAN NOT NULL,
                answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wrong_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                user_answer VARCHAR(50) NOT NULL,
                correct_answer VARCHAR(50) NOT NULL,
                explanation TEXT,
                wrong_count INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_reviewed DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions(id),
                UNIQUE(question_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                single_count INTEGER DEFAULT 120,
                multi_count INTEGER DEFAULT 10,
                judge_count INTEGER DEFAULT 30,
                total_count INTEGER DEFAULT 160
            )
        ''')

        cursor.execute('SELECT COUNT(*) FROM settings')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO settings (id, single_count, multi_count, judge_count, total_count)
                VALUES (1, 120, 10, 30, 160)
            ''')

        conn.commit()
        conn.close()

    def import_questions(self, questions):
        """批量导入题目"""
        conn = self._get_connection()
        cursor = conn.cursor()

        count = 0
        for q in questions:
            cursor.execute('''
                INSERT INTO questions (type, content, options, answer, explanation)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                q['type'],
                q['content'],
                json.dumps(q['options'], ensure_ascii=False),
                q['answer'],
                q.get('explanation', '')
            ))
            count += 1

        conn.commit()
        conn.close()
        return count

    def clear_questions(self):
        """清空题目表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM questions')
        conn.commit()
        conn.close()

    def clear_wrong_answers(self):
        """清空错题表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM wrong_questions')
        conn.commit()
        conn.close()

    def get_question_by_id(self, question_id):
        """根据ID获取题目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questions WHERE id = ?', (question_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return self._row_to_dict(row)
        return None

    def get_random_question(self, question_type=None, exclude_ids=None):
        """获取随机题目"""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM questions WHERE 1=1'
        params = []

        if question_type:
            query += ' AND type = ?'
            params.append(question_type)

        if exclude_ids:
            placeholders = ','.join(['?'] * len(exclude_ids))
            query += f' AND id NOT IN ({placeholders})'
            params.extend(exclude_ids)

        query += ' ORDER BY RANDOM() LIMIT 1'

        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_dict(row)
        return None

    def get_questions_by_type(self, question_type, limit=None):
        """获取指定题型的题目"""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM questions WHERE type = ?'
        params = [question_type]

        if limit:
            query += ' LIMIT ?'
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(row) for row in rows]

    def get_all_questions(self):
        """获取所有题目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questions')
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_dict(row) for row in rows]

    def get_question_count(self):
        """获取题目总数"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM questions')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_question_count_by_type(self, question_type):
        """获取指定题型数量"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM questions WHERE type = ?', (question_type,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def _row_to_dict(self, row):
        """将数据库行转换为字典"""
        d = dict(row)
        if 'options' in d and isinstance(d['options'], str):
            d['options'] = json.loads(d['options'])
        return d

    def add_answer_record(self, question_id, user_answer, is_correct):
        """添加答题记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO answer_records (question_id, user_answer, is_correct)
            VALUES (?, ?, ?)
        ''', (question_id, user_answer, is_correct))
        conn.commit()
        conn.close()

    def get_answer_records(self, question_id=None):
        """获取答题记录"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if question_id:
            cursor.execute('''
                SELECT * FROM answer_records
                WHERE question_id = ?
                ORDER BY answered_at DESC
            ''', (question_id,))
        else:
            cursor.execute('SELECT * FROM answer_records ORDER BY answered_at DESC')

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_to_wrongbook(self, question_id, user_answer, correct_answer, explanation):
        """添加错题到错题本"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, wrong_count FROM wrong_questions
            WHERE question_id = ?
        ''', (question_id,))

        row = cursor.fetchone()
        if row:
            cursor.execute('''
                UPDATE wrong_questions
                SET user_answer = ?,
                    wrong_count = wrong_count + 1,
                    last_reviewed = CURRENT_TIMESTAMP
                WHERE question_id = ?
            ''', (user_answer, question_id))
        else:
            cursor.execute('''
                INSERT INTO wrong_questions
                (question_id, user_answer, correct_answer, explanation)
                VALUES (?, ?, ?, ?)
            ''', (question_id, user_answer, correct_answer, explanation))

        conn.commit()
        conn.close()

    def remove_from_wrongbook(self, question_id):
        """从错题本移除"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM wrong_questions WHERE question_id = ?', (question_id,))
        conn.commit()
        conn.close()

    def get_wrongbook(self):
        """获取错题本"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT w.*, q.content, q.type, q.options, q.answer as correct_answer
            FROM wrong_questions w
            JOIN questions q ON w.question_id = q.id
            ORDER BY w.last_reviewed DESC
        ''')

        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            d = dict(row)
            if 'options' in d and isinstance(d['options'], str):
                d['options'] = json.loads(d['options'])
            result.append(d)

        return result

    def get_wrongbook_count(self):
        """获取错题数量"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM wrong_questions')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_statistics(self):
        """获取刷题统计"""
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {
            'total_questions': self.get_question_count(),
            'wrong_count': self.get_wrongbook_count(),
            'answered_count': 0,
            'correct_count': 0,
            'accuracy': 0
        }

        cursor.execute('SELECT COUNT(*) FROM answer_records')
        stats['answered_count'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM answer_records WHERE is_correct = 1')
        stats['correct_count'] = cursor.fetchone()[0]

        conn.close()

        if stats['answered_count'] > 0:
            stats['accuracy'] = round(
                stats['correct_count'] / stats['answered_count'] * 100, 1
            )

        return stats

    def get_settings(self):
        """获取刷题设置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM settings WHERE id = 1')
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_settings(self, single_count, multi_count, judge_count):
        """更新刷题设置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE settings
            SET single_count = ?,
                multi_count = ?,
                judge_count = ?,
                total_count = ?
            WHERE id = 1
        ''', (single_count, multi_count, judge_count, single_count + multi_count + judge_count))
        conn.commit()
        conn.close()


db = None


def get_db(db_path='data/exam.db'):
    """获取数据库实例"""
    global db
    if db is None:
        db = Database(db_path)
    return db
