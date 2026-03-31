import streamlit as st
from groq import Groq
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
api_key= "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"
client= Groq(api_key=api_key)
# Set page configuration
st.set_page_config(page_title="Badshah-GPT", page_icon="crown", layout="centered")

# Custom CSS for premium look and typing animation
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatInputContainer {
        padding-bottom: 2rem;
    }
    h1 {
        color: #00ffcc;
        text-align: center;
        font-family: 'Outfit', sans-serif;
    }
    /* Typing indicator animation */
    .typing-dots {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #00ffcc;
        margin-right: 5px;
        animation: typing 1.5s infinite;
    }
    .typing-dots:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typing {
        0%, 100% { transform: translateY(0); opacity: 0.2; }
        50% { transform: translateY(-5px); opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("PeakSolution-GPT")

# Sidebar for model selection
with st.sidebar:
    st.title("Settings")
    model_option = st.selectbox(
        "Choose a model:",
        ("llama-3.3-70b-versatile", "gemma2-9b-it", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "deepseek-r1-distill-llama-70b"),
        index=0
    )
    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response from Groq
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Show a "thinking" typing indicator first
        message_placeholder.markdown("""
            <div class="typing-dots"></div>
            <div class="typing-dots"></div>
            <div class="typing-dots"></div>
        """, unsafe_allow_html=True)
        
        full_response = ""
        
        try:
            # Call Groq API
            completion = client.chat.completions.create(
                model=model_option,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # Stream the response with a slight delay for smoother animation
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01) # Very slight delay to make typing visible
            
            message_placeholder.markdown(full_response)
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error generating response: {e}")
