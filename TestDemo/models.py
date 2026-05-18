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
        """获取数据库连接，增加超时时间以减少 database is locked 错误"""
        conn = sqlite3.connect(self.db_path, timeout=20)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化数据库表"""
        conn = self._get_connection()
        try:
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

            # 检查并初始化 wrong_questions 表（包含架构迁移逻辑）
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wrong_questions'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                # 检查列是否存在，如果包含旧的冗余列，则重新创建
                cursor.execute("PRAGMA table_info(wrong_questions)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'correct_answer' in columns or 'explanation' in columns:
                    # 发现旧架构，备份并删除（由于是错题本，直接删除重建最稳妥，或者您可以选择迁移数据）
                    cursor.execute("DROP TABLE wrong_questions")
                    table_exists = False

            if not table_exists:
                cursor.execute('''
                    CREATE TABLE wrong_questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question_id INTEGER NOT NULL,
                        user_answer VARCHAR(50) NOT NULL,
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
        finally:
            conn.close()

    def import_questions(self, questions):
        """批量导入题目"""
        conn = self._get_connection()
        try:
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
            return count
        finally:
            conn.close()

    def clear_questions(self):
        """清空题目表"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM questions')
            conn.commit()
        finally:
            conn.close()

    def clear_wrong_answers(self):
        """清空错题表"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM wrong_questions')
            conn.commit()
        finally:
            conn.close()

    def clear_answer_records(self):
        """清空所有答题记录"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM answer_records')
            conn.commit()
        finally:
            conn.close()

    def get_question_by_id(self, question_id):
        """根据ID获取题目"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM questions WHERE id = ?', (question_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        finally:
            conn.close()

    def get_random_question(self, question_type=None, exclude_ids=None, pool='all'):
        """
        获取随机题目
        
        参数:
            question_type - 题型
            exclude_ids - 排除的ID列表
            pool - 题目池范围: 'all' (全部), 'wrong' (错题本中), 'unseen' (从未做过)
        """
        conn = self._get_connection()
        try:
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

            if pool == 'wrong':
                query += ' AND id IN (SELECT question_id FROM wrong_questions)'
            elif pool == 'unseen':
                query += ' AND id NOT IN (SELECT DISTINCT question_id FROM answer_records)'

            query += ' ORDER BY RANDOM() LIMIT 1'

            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        finally:
            conn.close()

    def get_questions_by_type(self, question_type, limit=None):
        """获取指定题型的题目"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            query = 'SELECT * FROM questions WHERE type = ?'
            params = [question_type]

            if limit:
                query += ' LIMIT ?'
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        finally:
            conn.close()

    def get_all_questions(self):
        """获取所有题目"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM questions')
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        finally:
            conn.close()

    def get_question_count(self):
        """获取题目总数"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM questions')
            count = cursor.fetchone()[0]
            return count
        finally:
            conn.close()

    def get_question_count_by_type(self, question_type):
        """获取指定题型数量"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM questions WHERE type = ?', (question_type,))
            count = cursor.fetchone()[0]
            return count
        finally:
            conn.close()

    def _row_to_dict(self, row):
        """将数据库行转换为字典"""
        d = dict(row)
        if 'options' in d and isinstance(d['options'], str):
            d['options'] = json.loads(d['options'])
        return d

    def add_answer_record(self, question_id, user_answer, is_correct):
        """添加答题记录"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO answer_records (question_id, user_answer, is_correct)
                VALUES (?, ?, ?)
            ''', (question_id, user_answer, is_correct))
            conn.commit()
        finally:
            conn.close()

    def get_answer_records(self, question_id=None):
        """获取答题记录"""
        conn = self._get_connection()
        try:
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
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def add_to_wrongbook(self, question_id, user_answer):
        """添加错题到错题本"""
        conn = self._get_connection()
        try:
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
                    (question_id, user_answer)
                    VALUES (?, ?)
                ''', (question_id, user_answer))
            conn.commit()
        finally:
            conn.close()

    def remove_from_wrongbook(self, question_id):
        """从错题本移除"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM wrong_questions WHERE question_id = ?', (question_id,))
            conn.commit()
        finally:
            conn.close()

    def get_wrongbook(self):
        """获取错题本"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # 始终从 questions 表获取最新的题目内容、答案和解析，保证一致性
            # 将 q.id 命名为 id，确保前端拿到的 ID 始终是题目表的 ID
            cursor.execute('''
                SELECT q.id, w.question_id, w.user_answer, w.wrong_count, w.last_reviewed,
                       q.content, q.type, q.options, q.answer as correct_answer, q.explanation
                FROM wrong_questions w
                JOIN questions q ON w.question_id = q.id
                ORDER BY w.last_reviewed DESC
            ''')

            rows = cursor.fetchall()
            result = []
            for row in rows:
                d = dict(row)
                if 'options' in d and isinstance(d['options'], str):
                    d['options'] = json.loads(d['options'])
                result.append(d)
            return result
        finally:
            conn.close()

    def get_wrongbook_count(self):
        """获取错题数量"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM wrong_questions')
            count = cursor.fetchone()[0]
            return count
        finally:
            conn.close()

    def get_statistics(self):
        """获取刷题统计"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            stats = {
                'total_questions': 0,
                'wrong_count': 0,
                'answered_count': 0,
                'correct_count': 0,
                'accuracy': 0
            }

            cursor.execute('SELECT COUNT(*) FROM questions')
            stats['total_questions'] = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM wrong_questions')
            stats['wrong_count'] = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM answer_records')
            stats['answered_count'] = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM answer_records WHERE is_correct = 1')
            stats['correct_count'] = cursor.fetchone()[0]

            if stats['answered_count'] > 0:
                stats['accuracy'] = round(
                    stats['correct_count'] / stats['answered_count'] * 100, 1
                )
            return stats
        finally:
            conn.close()

    def get_settings(self):
        """获取刷题设置"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM settings WHERE id = 1')
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def update_settings(self, single_count, multi_count, judge_count):
        """更新刷题设置"""
        conn = self._get_connection()
        try:
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
        finally:
            conn.close()


db = None


def get_db(db_path='data/exam.db'):
    """获取数据库实例"""
    global db
    if db is None:
        db = Database(db_path)
    return db
