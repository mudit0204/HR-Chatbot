import streamlit as st
import os
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="HR Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .chat-message {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 15px;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .bot-message {
        background: #f8f9fa;
        color: #333;
        border: 1px solid #e9ecef;
        margin-right: auto;
    }
    
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e9ecef;
        border-radius: 15px;
        background: #fafafa;
        margin-bottom: 1rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e9ecef;
        padding: 0.75rem 1rem;
    }
    
    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    
    .quick-btn {
        margin: 0.25rem;
        padding: 0.5rem 1rem;
        border: 1px solid #667eea;
        border-radius: 20px;
        background: white;
        color: #667eea;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quick-btn:hover {
        background: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ✅ Load Gemini API Key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class SimpleChatbot:
    def __init__(self):
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                self.model = None
                st.error(f"Error configuring Gemini: {e}")
        else:
            self.model = None

    def get_response(self, question: str) -> str:
        if not self.model:
            return "⚠️ Please set your GEMINI_API_KEY in the .env file."
        # HR-specific prompt
        prompt = f"""
You are a helpful HR assistant. Answer the following employee question using your knowledge of HR policies, benefits, workplace guidance, and best practices. Be professional, clear, and supportive. If the question requires company-specific information, advise the user to consult their HR department.

Employee Question: {question}
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Sorry, I'm having trouble right now. Please try again. ({e})"

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 HR Chatbot</h1>
        <p>Your personal HR assistant - Ask me anything about HR policies, benefits, or workplace questions!</p>
    </div>
    """, unsafe_allow_html=True)

    # Check API key
    if not GEMINI_API_KEY:
        st.error("⚠️ Please set your GEMINI_API_KEY in a .env file (GEMINI_API_KEY=your_key)")
        st.stop()

    # Chat history display
    if st.session_state.chat_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for chat in st.session_state.chat_history:
            # User message
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {chat['question']}
                <br><small>{chat['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Bot message
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>🤖 Bot:</strong> {chat['answer']}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <h3>👋 Welcome!</h3>
            <p>Start a conversation by typing a message below or try one of the quick questions.</p>
        </div>
        """, unsafe_allow_html=True)

    # Chat input
    st.markdown("### 💬 Chat with HR Assistant")
    
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Type your message...",
                placeholder="Ask me anything!",
                label_visibility="collapsed"
            )
        
        with col2:
            submitted = st.form_submit_button("Send 🚀")
        
        if submitted and user_input:
            # Add user message and get bot response
            chatbot = SimpleChatbot()
            response = chatbot.get_response(user_input)
            
            st.session_state.chat_history.append({
                "question": user_input,
                "answer": response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            st.rerun()

    # Quick questions
    st.markdown("### ⚡ Quick HR Questions")
    quick_questions = [
        "What are common HR policies?",
        "How do I request time off?",
        "What benefits are typically offered?",
        "How does performance review work?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(question, key=f"quick_{i}"):
                chatbot = SimpleChatbot()
                response = chatbot.get_response(question)
                
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": response,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                st.rerun()

    # Clear chat button (centered using columns)
    if st.session_state.chat_history:
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🗑️ Clear Chat", key="clear_chat_btn", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <small>HR Chatbot powered by Google Gemini Flash 1.5</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
