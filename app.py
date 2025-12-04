# -*- coding: utf-8 -*-
"""
香料美食猜灯谜系统 · 公网部署版
"""

from flask import Flask, render_template, request
import pandas as pd
import random
import os

app = Flask(__name__)

def load_questions():
    try:
        df = pd.read_excel('questions.xlsx')
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 错误：无法读取 questions.xlsx\n{e}")
        return []

questions = load_questions()

@app.route('/')
def index():
    if not questions:
        return "⚠️ 题库未加载，请检查 questions.xlsx 是否存在。"
    q = random.choice(questions)
    return render_template('index.html', question=q)

@app.route('/check', methods=['POST'])
def check():
    try:
        q_id = request.form['id']
        user_answer = request.form['answer'].strip()
        
        # 以字符串比较，避免 Excel 导出的数字/字符串类型不一致
        q = next((q for q in questions if str(q["id"]) == str(q_id)), None)
        if not q:
            return "题目不存在！"

        # 统一转成字符串，避免 None 或数字导致 strip 失败
        correct = str(q.get('answer', '')).strip().lower()
        user = user_answer.lower()

        # 空答案直接判错，避免空字符串触发 startswith True
        if not user:
            is_correct = False
        else:
            is_correct = (
                correct in user or
                user in correct or
                user.startswith(correct[:2]) or
                correct.startswith(user[:2])
            )

        return render_template('result.html',
                               question=q,
                               user_answer=user_answer,
                               is_correct=is_correct)
    except Exception as e:
        return f"系统错误：{e}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
