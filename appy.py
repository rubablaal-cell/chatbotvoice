import streamlit as st
from groq import Groq
import os
import time
import io
from dotenv import load_dotenv

# Initialize Groq client
# SECURITY WARNING: This key is hardcoded as requested. It will be public on GitHub.
api_key = "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"
client = Groq(api_key=api_key)

# Set page configuration
st.set_page_config(page_title="PeakSolution-GPT", page_icon="🤖", layout="centered")

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

# Sidebar for model selection and features
with st.sidebar:
    st.title("Settings")
    model_option = st.selectbox(
        "Choose a model:",
        ("llama-3.3-70b-versatile", "gemma2-9b-it", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "deepseek-r1-distill-llama-70b"),
        index=0
    )
    
    st.markdown("---")
    st.subheader("🔊 Audio Settings")
    tts_enabled = st.toggle("Enable Text-to-Speech", value=False)
    voice_option = st.selectbox(
        "Choose a voice:",
        ("troy", "anna", "josh", "lisa"),
        index=0,
        disabled=not tts_enabled
    )
    
    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        if "last_audio" in st.session_state:
            del st.session_state.last_audio
        st.rerun()

st.markdown("---")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If there's audio associated with this message (optional, but for now we only play latest)
        
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
        
        try:
            # 1. Get the full response first (non-streamed for sync)
            chat_completion = client.chat.completions.create(
                model=model_option,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=False, # Use non-streamed for faster sync
            )
            full_response = chat_completion.choices[0].message.content
            
            # 2. Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # 3. Handle TTS if enabled
            if tts_enabled:
                # Orpheus 200 character limit
                tts_input = full_response[:200]
                
                audio_response = client.audio.speech.create(
                    model="canopylabs/orpheus-v1-english",
                    voice=voice_option,
                    input=tts_input,
                    response_format="wav"
                )
                
                # Convert to bytes
                audio_data = io.BytesIO()
                for chunk in audio_response.iter_bytes():
                    audio_data.write(chunk)
                
                # Start Audio and Text together
                st.audio(audio_data, format="audio/wav", autoplay=True)
                
            # 4. Stream ("Type") the response
            # Since we have the full text, we simulate typing to make it look smooth
            displayed_text = ""
            for char in full_response:
                displayed_text += char
                message_placeholder.markdown(displayed_text + "▌")
                # Speed control: very small delay for natural look
                time.sleep(0.01) 
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Error: {e}")
