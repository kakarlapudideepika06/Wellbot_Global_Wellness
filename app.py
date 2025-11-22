import streamlit as st
from utils.auth import init_db, register_user, login_user, get_user_language, get_user_id
from utils.response_generator import get_response
from utils.db_ops import start_conversation, log_message, store_feedback
from deep_translator import GoogleTranslator

# Initialize database
init_db()

# Initialize translator
translator = GoogleTranslator(source='auto', target='hi')

def translate_text(text, target_lang):
    """Unified translation function"""
    if target_lang == "Hindi" and text.strip():
        try:
            translated = translator.translate(text)
            return translated
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    return text

# Initialize session state
if 'current_language' not in st.session_state: st.session_state.current_language = "English"
if 'messages' not in st.session_state: st.session_state.messages = []
if 'show_chat' not in st.session_state: st.session_state.show_chat = False
if 'show_auth' not in st.session_state: st.session_state.show_auth = False
if 'user_language_set' not in st.session_state: st.session_state.user_language_set = False
if 'last_message_feedback' not in st.session_state: st.session_state.last_message_feedback = {}
if 'show_feedback_comment' not in st.session_state: st.session_state.show_feedback_comment = False
if 'show_admin' not in st.session_state: st.session_state.show_admin = False
if 'admin_authenticated' not in st.session_state: st.session_state.admin_authenticated = False
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'conversation_id' not in st.session_state: st.session_state.conversation_id = None
if 'email' not in st.session_state: st.session_state.email = None

# ---------- NAVIGATION ----------
def go_to_welcome():
    st.session_state.show_chat = False
    st.session_state.show_auth = False
    st.session_state.show_admin = False
    st.session_state.admin_authenticated = False
    st.rerun()

def go_to_auth():
    st.session_state.show_auth = True
    st.session_state.show_admin = False
    st.session_state.admin_authenticated = False
    st.rerun()

def go_to_admin():
    st.session_state.show_admin = True
    st.session_state.show_auth = False
    st.session_state.show_chat = False
    st.session_state.admin_authenticated = False
    st.rerun()

# ---------- SIMPLE ADMIN PANEL THAT WORKS ----------
def show_admin_panel():
    """Simple admin panel that integrates properly"""
    
    # If not authenticated, show login
    if not st.session_state.get('admin_authenticated', False):
        st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🛠️ Admin Dashboard</h1>", unsafe_allow_html=True)
        
        if st.button("← Back to Welcome", key="admin_back_welcome"):
            go_to_welcome()
        
        st.subheader("🔐 Admin Login")
        
        with st.form("admin_login_form"):
            username = st.text_input("Username", value="admin", key="admin_username")
            password = st.text_input("Password", type="password", value="admin123", key="admin_password")
            login_btn = st.form_submit_button("Login", key="admin_login_btn")
            
            if login_btn:
                if username == "admin" and password == "admin123":
                    st.session_state.admin_authenticated = True
                    st.success("✅ Admin login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        return
    
    # If authenticated, show the actual admin interface
    try:
        # Import the dashboard class
        from admin_dashboard import EnhancedAdminDashboard
        
        # Create dashboard instance
        dashboard = EnhancedAdminDashboard()
        
        # MANUALLY CREATE THE SIDEBAR
        with st.sidebar:
            st.title("🛠️ Admin Panel")
            
            if st.button("🚪 Logout", use_container_width=True, key="admin_logout_btn"):
                st.session_state.admin_authenticated = False
                st.rerun()
            
            st.markdown("---")
            
            # Navigation
            nav_options = ["📊 Dashboard", "📚 Knowledge Base", "👥 User Management", "⭐ Feedback Analysis"]
            selected_nav = st.radio("Navigation", nav_options, key="admin_nav_radio")
        
        # Show the selected page based on navigation
        if selected_nav == "📊 Dashboard":
            dashboard.show_dashboard_overview()
        elif selected_nav == "📚 Knowledge Base":
            dashboard.manage_knowledge_base()
        elif selected_nav == "👥 User Management":
            dashboard.user_management()
        elif selected_nav == "⭐ Feedback Analysis":
            dashboard.feedback_analysis()
            
    except Exception as e:
        st.error(f"Error loading admin dashboard: {e}")
        import traceback
        st.code(traceback.format_exc())

# ---------- MAIN APP ----------

# Set page config only once at the start
st.set_page_config(
    page_title="Digital Wellness Chatbot",
    page_icon="🤖",
    layout="wide",  # Changed to wide for admin panel
    initial_sidebar_state="auto"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%); min-height: 100vh; }
    .main-title { text-align: center; background: linear-gradient(135deg, #1976d2, #42a5f5);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem; font-weight: 800; }
    .welcome-title { text-align: center; background: linear-gradient(135deg, #1976d2, #42a5f5);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.2rem; font-weight: 800; }
    .subtitle { text-align: center; color: #546e7a; font-size: 1.1rem; margin-bottom: 2rem; }
    
    .stButton button {
        background: linear-gradient(135deg, #1976d2, #42a5f5); color: white;
        border: none; padding: 0.75rem 2rem; border-radius: 50px; font-weight: 600;
        transition: 0.3s; width: 100%;
    }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(33,150,243,0.3); }

    .user-message { background: linear-gradient(135deg,#1976D2,#42A5F5); color: white;
        padding: 0.75rem; border-radius: 18px 18px 5px 18px; margin: 10px 0; max-width: 70%;
        margin-left: auto; box-shadow: 0 4px 12px rgba(33,150,243,0.3); }
    .bot-message { background: white; color: #37474f; padding: 0.75rem; border-radius: 18px 18px 18px 5px;
        margin: 10px 0; max-width: 70%; border: 1px solid #e1f0ff; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

    .stTextInput input {
        border: 2px solid #e1f0ff; border-radius: 25px; padding: 0.75rem;
    }
    .stTextInput input:focus { border-color: #42a5f5; box-shadow: 0 0 0 2px rgba(66,165,245,0.2); }

    header, footer, [data-testid="stHeader"], [data-testid="stDecoration"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ---------- APP ROUTING ----------

# WELCOME SCREEN
if not st.session_state.show_auth and not st.session_state.show_chat and not st.session_state.show_admin:
    st.markdown("<h1 class='welcome-title'>🧘 Digital Wellness Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Your AI companion for personalized health & wellness support 🌿</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔐 Login / Register", use_container_width=True, key="welcome_login_btn"):
            go_to_auth()
    
    with col2:
        if st.button("🛠️ Admin Panel", use_container_width=True, key="welcome_admin_btn"):
            go_to_admin()

# ADMIN PANEL SCREEN
elif st.session_state.show_admin:
    show_admin_panel()

# AUTH SCREEN
elif st.session_state.show_auth and "token" not in st.session_state:
    st.markdown("<h1 class='main-title'>🧘 Digital Wellness</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Back to Welcome", use_container_width=True, key="auth_back_btn"):
            go_to_welcome()
    
    with col2:
        if st.button("🛠️ Admin Panel", use_container_width=True, key="auth_admin_btn"):
            go_to_admin()

    tabs = st.tabs(["🔐 Login", "🆕 Register"])

    # LOGIN TAB
    with tabs[0]:
        st.subheader("Welcome Back!")
        email_login = st.text_input("📧 Email", placeholder="Enter your email", key="login_email")
        password_login = st.text_input("🔑 Password", type="password", placeholder="Enter your password", key="login_password")

        if st.button("🔑 Login to Chat", use_container_width=True, key="login_submit_btn"):
            if email_login and password_login:
                token = login_user(email_login, password_login)
                if token:
                    st.session_state["token"] = token
                    st.session_state["email"] = email_login
                    st.session_state.show_chat = True
                    st.session_state.show_auth = False
                    st.session_state.messages = []

                    user_id = get_user_id(email_login)
                    st.session_state.user_id = user_id

                    try:
                        st.session_state.conversation_id = start_conversation(user_id)
                    except Exception as e:
                        st.error(f"Error starting conversation: {e}")
                        st.session_state.conversation_id = None

                    st.session_state.current_language = get_user_language(email_login)
                    st.session_state.user_language_set = True

                    st.success("🎉 Welcome! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
            else:
                st.warning("⚠️ Fill all fields")

    # REGISTER TAB
    with tabs[1]:
        st.subheader("Create Your Account")
        selected_language = st.radio("Select Language:", ["English", "Hindi"], horizontal=True, key="reg_lang_radio")
        st.session_state.current_language = selected_language

        name = st.text_input("👤 Full Name", placeholder="Enter your full name", key="reg_name")
        email = st.text_input("📧 Email", placeholder="Enter your email", key="reg_email")
        password = st.text_input("🔑 Password", type="password", placeholder="Create a password", key="reg_password")

        age_group = st.selectbox("🎂 Age Group", ["Under 18", "18-25 years", "26-35 years",
                                                  "36-45 years", "46-55 years", "56-65 years", "Over 65 years"], key="reg_age_select")

        if st.button("🚀 Create Account & Continue", use_container_width=True, key="reg_submit_btn"):
            if name and email and password:
                if register_user(email, password, name, selected_language, age_group):
                    token = login_user(email, password)
                    if token:
                        st.session_state.update({
                            "token": token,
                            "email": email,
                            "show_chat": True,
                            "show_auth": False,
                            "messages": [],
                            "current_language": selected_language,
                            "user_language_set": True
                        })
                        
                        user_id = get_user_id(email)
                        st.session_state.user_id = user_id
                        
                        try:
                            st.session_state.conversation_id = start_conversation(user_id)
                        except Exception as e:
                            st.error(f"Error starting conversation: {e}")
                            st.session_state.conversation_id = None
                        
                        st.success("🎉 Account created!")
                        st.rerun()
                    else:
                        st.error("❌ Login failed after registration")
                else:
                    st.error("❌ Email already exists")
            else:
                st.warning("⚠️ Fill all fields")

# CHATBOT SCREEN
elif "token" in st.session_state and st.session_state.show_chat:
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("🔙 Logout", key="chat_logout_btn"):
            for key in list(st.session_state.keys()): 
                if key not in ['current_language', 'show_chat', 'show_auth', 'user_language_set', 'show_admin', 'admin_authenticated']:
                    del st.session_state[key]
            st.session_state.show_chat = False
            st.session_state.show_auth = False
            st.rerun()
    with col2:
        st.markdown("<h1 class='main-title'>💬 Wellness Chat</h1>", unsafe_allow_html=True)
    with col3:
        switch_text = "🌐 Hindi" if st.session_state.current_language == "English" else "🌐 English"
        if st.button(switch_text, key="language_switch_btn"):
            switch_language()

    # Display messages
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)

    # FEEDBACK SECTION
    if (st.session_state.messages and 
        st.session_state.messages[-1]["role"] == "assistant"):
        
        current_message_index = len(st.session_state.messages) - 1
        
        feedback_given = (st.session_state.get('last_message_feedback', {}).get('message_index') == current_message_index and
                         st.session_state.last_message_feedback.get('feedback_given', False))
        
        if not feedback_given:
            st.markdown("---")
            
            feedback_text = "**Was this response helpful?**" if st.session_state.current_language == "English" else "**क्या यह प्रतिक्रिया मददगार थी?**"
            st.write(feedback_text)
            
            col1, col2 = st.columns(2)
            
            with col1:
                yes_text = "👍 Yes" if st.session_state.current_language == "English" else "👍 हाँ"
                if st.button(yes_text, use_container_width=True, key=f"feedback_yes_{current_message_index}"):
                    user_query = st.session_state.messages[-2]["content"] if len(st.session_state.messages) >= 2 else "Unknown"
                    bot_response = st.session_state.messages[-1]["content"]
                    
                    store_feedback(
                        st.session_state.user_id,
                        user_query,
                        bot_response,
                        "up",
                        "User found response helpful"
                    )
                    
                    st.session_state.last_message_feedback = {
                        'feedback_given': True,
                        'message_index': current_message_index
                    }
                    
                    success_text = "Thanks for your feedback! 👍" if st.session_state.current_language == "English" else "आपके फीडबैक के लिए धन्यवाद! 👍"
                    st.success(success_text)
                    st.rerun()
                
            with col2:
                no_text = "👎 No" if st.session_state.current_language == "English" else "👎 नहीं"
                if st.button(no_text, use_container_width=True, key=f"feedback_no_{current_message_index}"):
                    st.session_state.show_feedback_comment = True
                    st.rerun()
        
        if st.session_state.get('show_feedback_comment', False):
            st.markdown("---")
            
            comment_title = "💬 **How can we improve?**" if st.session_state.current_language == "English" else "💬 **हम कैसे सुधार कर सकते हैं?**"
            comment_placeholder = "Your feedback (optional):" if st.session_state.current_language == "English" else "आपका फीडबैक (वैकल्पिक):"
            
            st.write(comment_title)
            feedback_comment = st.text_area("", placeholder=comment_placeholder, key="feedback_comment_area")
            
            col1, col2 = st.columns(2)
            with col1:
                submit_text = "📤 Submit Feedback" if st.session_state.current_language == "English" else "📤 फीडबैक भेजें"
                if st.button(submit_text, use_container_width=True, key="feedback_submit_btn"):
                    user_query = st.session_state.messages[-2]["content"] if len(st.session_state.messages) >= 2 else "Unknown"
                    bot_response = st.session_state.messages[-1]["content"]
                    
                    store_feedback(
                        st.session_state.user_id,
                        user_query,
                        bot_response,
                        "down",
                        feedback_comment if feedback_comment else "User did not find response helpful"
                    )
                    
                    st.session_state.last_message_feedback = {
                        'feedback_given': True,
                        'message_index': current_message_index
                    }
                    st.session_state.show_feedback_comment = False
                    
                    success_text = "Thanks for your detailed feedback! We'll use it to improve. 💪" if st.session_state.current_language == "English" else "आपके विस्तृत फीडबैक के लिए धन्यवाद! हम इसे सुधारने के लिए उपयोग करेंगे। 💪"
                    st.success(success_text)
                    st.rerun()
            
            with col2:
                cancel_text = "❌ Cancel" if st.session_state.current_language == "English" else "❌ रद्द करें"
                if st.button(cancel_text, use_container_width=True, key="feedback_cancel_btn"):
                    st.session_state.show_feedback_comment = False
                    st.rerun()

    # Input area
    with st.form(key='chat_form', clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            placeholder_text = "Type your message..." if st.session_state.current_language == "English" else "अपना संदेश टाइप करें..."
            user_input = st.text_input(
                "",
                placeholder=placeholder_text, 
                label_visibility="collapsed",
                key="chat_input"
            )
        
        with col2:
            button_text = "🚀" if st.session_state.current_language == "English" else "🚀"
            send_clicked = st.form_submit_button(button_text, use_container_width=True, key="chat_send_btn")

    if send_clicked and user_input.strip():
        if 'last_message_feedback' in st.session_state:
            st.session_state.last_message_feedback = {}
        if 'show_feedback_comment' in st.session_state:
            st.session_state.show_feedback_comment = False
            
        original_input = user_input

        st.session_state.messages.append({"role": "user", "content": original_input})
        log_message(st.session_state.conversation_id, "user", original_input)

        if st.session_state.current_language == "Hindi":
            try: 
                user_input_en = translator.translate(original_input)
            except: 
                user_input_en = original_input
        else:
            user_input_en = original_input

        response = get_response(user_input_en, st.session_state.current_language)
        log_message(st.session_state.conversation_id, "bot", response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        st.rerun()

# Footer
st.markdown("<div style='text-align: center; margin-top: 2rem; color: #666;'><p>💙 Stay balanced — your wellness matters!</p></div>", unsafe_allow_html=True)