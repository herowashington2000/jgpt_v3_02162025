import streamlit as st
import openai
import tiktoken
from datetime import datetime
import chardet

# 环境变量
OPENAI_API_KEY = ''
MAX_TOKENS = 16000

# 语言支持
def get_text(key):
    texts = {
        "English": {
            "log_out": "Log Out",
            "footer": "<a href='#'>Privacy Policy</a> | <a href='#'>Terms & Conditions</a> | Copyright © 2025 Pony Inc. All rights reserved.",
            "question_placeholder": "Example Questions for Reference",
            "question_input_box": "Question Input Box",
            "upload_file": "Upload a file",
            "uploaded_file": "Uploaded file: {}",
            "uploaded_files": "Uploaded Files",  # Added
            "type": "Type",  # Added
            "delete_file": "Delete File",  # Added
            "admin_panel": "Admin Panel",
            "user_panel": "User Panel",
            "contact_host": "Please contact the host.",
            "answer": "### Answer",
            "data_file_not_found": "Data file 'data.txt' not found. Please ensure it exists.",
            "view_user_log": "Viewing user logs",
            "add_api_key": "Please add your API key to continue.",
            "file_not_found": "Data file 'data.txt' not found. Please ensure it exists.",
            "see_user_log": "See User Log",
            "viewing_user_logs": "Viewing user logs",
            "settings": "Settings",
            "sign_in": "Sign In",
            "username": "Username",
            "password": "Password",
            "hint": "Hint",
            "next": "Next"
        },
        "中文": {
            "log_out": "登出",
            "footer": "<a href='#'>隐私政策</a> | <a href='#'>条款和条件</a> | 版权所有 © 2025 Pony Inc.",
            "question_placeholder": "参考问题示例",
            "question_input_box": "问题输入框",
            "upload_file": "上传文件",
            "uploaded_file": "已上传文件: {}",
            "uploaded_files": "已上传文件",  # Added
            "type": "类型",  # Added
            "delete_file": "删除文件",  # Added
            "admin_panel": "管理员面板",
            "user_panel": "用户面板",
            "contact_host": "请联系管理员。",
            "answer": "### 答案",
            "data_file_not_found": "数据文件 'data.txt' 未找到，请确保其存在。",
            "view_user_log": "查看用户日志",
            "add_api_key": "请添加您的 API 密钥以继续。",
            "file_not_found": "数据文件 'data.txt' 未找到，请确保其存在。",
            "see_user_log": "查看用户日志",
            "viewing_user_logs": "正在查看用户日志",
            "settings": "设置",
            "sign_in": "登录",
            "username": "用户名",
            "password": "密码",
            "hint": "提示",
            "next": "下一步"
        },
        "日本語": {
            "log_out": "ログアウト",
            "footer": "<a href='#'>プライバシーポリシー</a> | <a href='#'>利用規約</a> | 著作権 © 2025 Pony Inc.",
            "question_placeholder": "参考のための質問例",
            "question_input_box": "質問入力ボックス",
            "upload_file": "ファイルをアップロード",
            "uploaded_file": "アップロードされたファイル: {}",
            "uploaded_files": "アップロードされたファイル",  # Added
            "type": "タイプ",  # Added
            "delete_file": "ファイルを削除",  # Added
            "admin_panel": "管理パネル",
            "user_panel": "ユーザーパネル",
            "contact_host": "管理者に連絡してください。",
            "answer": "### 回答",
            "data_file_not_found": "データファイル 'data.txt' が見つかりません。ファイルが存在することを確認してください。",
            "view_user_log": "ユーザーログを表示",
            "add_api_key": "APIキーを追加してください。",
            "file_not_found": "データファイル 'data.txt' が見つかりません。ファイルが存在することを確認してください。",
            "see_user_log": "ユーザーログを見る",
            "viewing_user_logs": "ユーザーログを表示中",
            "settings": "設定",
            "sign_in": "サインイン",
            "username": "ユーザー名",
            "password": "パスワード",
            "hint": "ヒント",
            "next": "次へ"
        }
    }
    return texts[st.session_state.get("language", "English")].get(key, key)


# process text
def truncate_text(text, max_tokens=6000):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = enc.encode(text)
    truncated_text = enc.decode(tokens[:max_tokens])
    return truncated_text

def count_tokens(messages):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return sum(len(enc.encode(m["content"])) for m in messages)


# 侧边栏设置
with st.sidebar:
    st.title(get_text("settings"))
    st.session_state["language"] = st.radio(get_text("select_language"), ["English", "中文", "日本語"], index=0)
    openai_api_key = st.text_input(get_text("api_key"), key="file_qa_api_key", type="password")
    openai.api_key = openai_api_key
    "[[About](support@pony.com)](© 2025 Pony. All rights reserved.)"

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None

# 登录页面
def show_login_page():
    st.image("icon/icon_no_word_bg.png", width=700)
    st.write(f"<div style='text-align: center; font-size: 32px; font-weight: bold;'>{get_text('sign_in')}</div>", unsafe_allow_html=True)

    username = st.text_input(get_text("username"))
    password = st.text_input(get_text("password"), type="password")

    if "show_hint" not in st.session_state:
        st.session_state["show_hint"] = False

    if st.button(get_text("hint")):
        st.session_state["show_hint"] = not st.session_state["show_hint"]

    if st.session_state["show_hint"]:
        st.info("First-time login: Admin -> Username: admin, Password: Password | User -> Username: user, Password: password")

    if st.button(get_text("next")) or st.session_state.get("submit_login"):
        if username == "admin" and password == "Password":
            st.session_state["logged_in"] = True
            st.session_state["user_role"] = "admin"
        elif username == "user" and password == "password":
            st.session_state["logged_in"] = True
            st.session_state["user_role"] = "user"
        else:
            st.error(get_text("invalid_credentials"))

# 退出登录
def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None

# 主要逻辑
def main():
    if not st.session_state["logged_in"]:
        show_login_page()
    else:
        with st.sidebar:
            st.button(get_text("log_out"), on_click=logout)
        
        if st.session_state["user_role"] == "admin":
            handle_admin_features()
        else:
            handle_user_features()
    st.markdown(
        f"""
        <style>
            .footer {{
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background-color: white;
                text-align: center;
                padding: 10px;
            }}
        </style>
        <div class='footer'>
            {get_text("footer")}
        </div>
        """,
        unsafe_allow_html=True
    )

def prepare():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []  # 初始化对话历史

    #question_placeholder = "Example Questions for Reference" if language != "日本語" else "参考のための質問例"
    question = st.text_input(get_text("question_input_box"), placeholder=get_text("question_placeholder"))
    question = truncate_text(question, 500)
    return question

def process(question, file_content):
    
        
    article = truncate_text(file_content, 6000)
    
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Here's an article:\n\n{article}\n\n{question}"},
    ]
    
    while count_tokens(messages) > MAX_TOKENS:
        article = truncate_text(article, len(article) - 500)
        messages[1]["content"] = f"Here's an article:\n\n{article}\n\n{question}"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
        )
        st.write(get_text("answer"))
        answer = response.choices[0].message.content.strip()
        st.write(answer)

        # 更新对话历史
        st.session_state["chat_history"].append(("User", question))
        st.session_state["chat_history"].append(("Assistant", answer))

        # 实时显示对话历史
        st.write("### Chat History")
        for role, text in st.session_state["chat_history"]:
            st.write(f"**{role}:** {text}")

    except openai.OpenAIError as e:
        st.error(f"An error occurred: {e}")


def handle_admin_features():
    st.title(get_text("admin_panel"))
    st.markdown("""<style> .icon { font-size: 50px; text-align: center; } </style>""", unsafe_allow_html=True)

    # Initialize session state for stored files if not exists
    if "stored_files" not in st.session_state:
        st.session_state["stored_files"] = []

    uploaded_files = st.file_uploader(
        get_text("upload_file"), 
        type=["pdf", "doc", "docx", "txt"], 
        accept_multiple_files=True
    )

    file_content = ""
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Check for duplicate files
            if not any(stored_file["name"] == uploaded_file.name for stored_file in st.session_state["stored_files"]):
                try:
                    # Using read() instead of getvalue().decode()
                    file_text = read_file_content(uploaded_file)
                    if file_text is None:
                        continue

                    # Store file information
                    st.session_state["stored_files"].append({
                        "name": uploaded_file.name,
                        "type": uploaded_file.type,
                        "content": file_text,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success(f"{get_text('uploaded_file')}: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"{get_text('file_read_error')}: {uploaded_file.name} - {str(e)}")

    # # Display stored files
    # if st.session_state["stored_files"]:
    #     st.write("### " + get_text("uploaded_files"))
    #     for idx, file_info in enumerate(st.session_state["stored_files"]):
    #         with st.expander(f"{file_info['name']} ({file_info['timestamp']})"):
    #             st.write(f"{get_text('type')}: {file_info['type']}")
    #             if st.button(get_text("delete_file"), key=f"delete_{idx}"):
    #                 st.session_state["stored_files"].pop(idx)
    #                 st.rerun()

    question = prepare()

    if question and not openai_api_key:
        st.info(get_text("add_api_key"))
        return

    if question and openai_api_key:
        # Combine content from all stored files
        combined_content = "\n".join(
            file_info["content"] for file_info in st.session_state["stored_files"]
        )
        
        # Fallback to data.txt if no files are uploaded
        if not combined_content:
            try:
                with open("data.txt", "r", encoding="utf-8") as file:
                    combined_content = file.read()
            except FileNotFoundError:
                st.error(get_text("file_not_found"))
                return

        process(question, combined_content)

    if st.button(get_text("see_user_log")):
        st.info(get_text("viewing_user_logs"))

def read_file_content(uploaded_file):
        """Read file content with automatic encoding detection."""
        try:
            file_content = uploaded_file.read()
            encoding = detect_encoding(file_content)
            return file_content.decode(encoding)
        except Exception as e:
            st.error(f"{get_text('file_read_error')}: {uploaded_file.name} - {str(e)}")
            return None

def detect_encoding(file_content: bytes) -> str:
        """Detect the encoding of file content."""
        result = chardet.detect(file_content)
        return result['encoding'] or 'utf-8'

def handle_user_features():
    st.title(get_text("user_panel"))

    # question_placeholder = "Example Questions for Reference" if language != "日本語" else "参考のための質問例"
    # question = st.text_input("Question Input Box", placeholder="Example Questions for Reference")
    # question = truncate_text(question, 500)
    question = prepare()
    
    #q&a
    if question and not openai_api_key:
       st.info(get_text("contact_host"))
    
    if question and openai_api_key:
        data_file_path = "data.txt"
        if "admin_uploaded_file" in st.session_state:
            uploaded_file = st.session_state["admin_uploaded_file"]
            data_file_path = uploaded_file.name
            file_content = uploaded_file.getvalue().decode("utf-8")
        else:
            try:
                with open(data_file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
            except FileNotFoundError:
                st.error(get_text("file_not_found"))
                return
        
        process(question, file_content)

# 启动应用
if __name__ == "__main__":
    main()
