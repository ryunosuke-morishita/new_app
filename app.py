import streamlit as st
import pandas as pd
import random
import os

# --- ページ設定 ---
st.set_page_config(page_title="教職教養 一問一答", page_icon="📚")

# --- 問題読み込み関数 ---
@st.cache_data
def load_questions():
    file_path = "questions.csv"
    
    # CSVファイルが存在しない場合のエラーハンドリング
    if not os.path.exists(file_path):
        st.error(f"エラー: '{file_path}' が見つかりません。同じフォルダにCSVファイルを作成してください。")
        return []

    try:
        # CSVを読み込む（文字化けする場合は encoding="shift_jis" に変更してください）
        df = pd.read_csv(file_path, encoding="utf-8")
        questions = []
        for _, row in df.iterrows():
            questions.append({
                "q": row["q"],
                "options": [row["opt1"], row["opt2"], row["opt3"], row["opt4"]],
                "answer_idx": int(row["ans"]),
                "explanation": row["exp"]
            })
        return questions
    except Exception as e:
        st.error(f"CSVファイルの読み込み中にエラーが発生しました: {e}")
        return []

# --- セッション状態（アプリの状態）の初期化 ---
if 'questions' not in st.session_state:
    all_questions = load_questions()
    if all_questions:
        # 問題をシャッフルしてセット
        st.session_state.questions = random.sample(all_questions, len(all_questions))
    else:
        st.session_state.questions = []
        
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False

# --- アプリのUIとロジック ---
st.title("📚 教職教養 4択一問一答")

# 問題データがない場合はここで処理を止める
if not st.session_state.questions:
    st.stop()

total_q = len(st.session_state.questions)

# 全問終了していない場合の表示
if st.session_state.current_q < total_q:
    q_data = st.session_state.questions[st.session_state.current_q]
    
    st.subheader(f"第 {st.session_state.current_q + 1} 問 / 全 {total_q} 問")
    st.write(f"**{q_data['q']}**")
    
    # 選択肢の表示（解答済みの場合は disabled=True で変更不可にする）
    selected_option = st.radio(
        "選択肢:", 
        options=range(4), 
        format_func=lambda x: q_data['options'][x],
        key=f"q_{st.session_state.current_q}",
        disabled=st.session_state.answered
    )
    
    # 解答ボタン
    if not st.session_state.answered:
        if st.button("解答する", type="primary"):
            st.session_state.answered = True
            if selected_option == q_data['answer_idx']:
                st.session_state.score += 1
            st.rerun()
            
    # 解答後の表示（正誤判定と解説）
    if st.session_state.answered:
        correct_idx = q_data['answer_idx']
        
        if selected_option == correct_idx:
            st.success("⭕ 正解！")
        else:
            st.error(f"❌ 不正解... (正解は「{q_data['options'][correct_idx]}」)")
            
        st.info(f"**【解説】**\n{q_data['explanation']}")
        
        # 次の問題へ進むボタン
        if st.button("次の問題へ"):
            st.session_state.current_q += 1
            st.session_state.answered = False
            st.rerun()

# 全問終了した場合の表示
else:
    st.balloons()
    st.header("🎉 テスト終了！お疲れ様でした。")
    st.subheader(f"あなたのスコア: {st.session_state.score} 点 / {total_q} 問")
    
    accuracy = (st.session_state.score / total_q) * 100
    st.write(f"正答率: {accuracy:.1f} %")
    
    # リトライボタン
    if st.button("最初からやり直す", type="primary"):
        st.session_state.questions = random.sample(st.session_state.questions, len(st.session_state.questions))
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.rerun()