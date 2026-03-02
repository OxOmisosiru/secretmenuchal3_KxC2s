import streamlit as st
import google.generativeai as genai
import time

# セッションごとに最後に発言した時間を記録
if "last_chat_time" not in st.session_state:
    st.session_state.last_chat_time = -5

# 5秒以内の連投をブロック
current_time = time.time()
if current_time - st.session_state.last_chat_time < 5:
    st.warning("連投は控えてください（5秒待機が必要です）。リロードしてやり直してください。")
    st.stop()

st.session_state.last_chat_time = current_time

# 重要情報はすべて Secrets から読み込む
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    SYSTEM_PROMPT = st.secrets["SYSTEM_PROMPT"]
    CORRECT_ANSWER = st.secrets["CORRECT_ANSWER"]
    STAGE_TITLE = st.secrets["STAGE_TITLE"]
except Exception:
    st.error("Secrets の設定が読み込めません。")
    st.stop()

st.set_page_config(page_title=STAGE_TITLE, layout="wide")
st.title(f"{STAGE_TITLE}")

# 画面分割（左：チャット、右：回答入力）
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Recipe App AI Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # チャット履歴表示
    chat_box = st.container(height=450)
    for msg in st.session_state.messages:
        chat_box.chat_message(msg["role"]).write(msg["content"])

    # 入力処理
    if prompt := st.chat_input("AIに話しかける..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        chat_box.chat_message("user").write(prompt)

        # Gemini 呼び出し（モデルは 1.5 Flash または 2.0 Flash-Lite 等）
        model = genai.GenerativeModel("gemini-2.5-flash-lite", system_instruction=SYSTEM_PROMPT)
        response = model.generate_content(prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        chat_box.chat_message("assistant").write(response.text)

with col2:
    st.subheader("Answer")
    with st.form("answer_form"):
        answer = st.text_input("秘密のメニューをカタカナで入力してください")
        if st.form_submit_button("送信"):
            if answer.strip().upper() == CORRECT_ANSWER.strip().upper():
                st.balloons()
                st.success("正解です！Stage 3 クリア！そして、Secret Menu クリア！キーワードは「あくようげんきん（悪用厳禁）」です。タブレットに入力しよう！")
            else:
                st.error("❌ 不正解です。")
