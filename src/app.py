import os
from dotenv import load_dotenv
import gradio as gr

from agent.ProFileAi import ProFileAi
from tools.tools_combo import tools
from tools.pushover import push

load_dotenv(override=True)

if __name__ == "__main__":
    name="Giuseppe Sirigu"
    
    me = ProFileAi(
        name=name,
        path_to_resume="data/Resume_Giuseppe_Sirigu.pdf",
        path_to_linkedin="data/linkedin.pdf",
        path_to_summary="data/summary.txt",
        tools=tools
    )

    # Set the initial message
    initial_messages = [{"role": "assistant", "content": f"Hello! I can answer questions about my career, background, skills and experience. How can I help you today?"}]

    chatbot = gr.Chatbot(value=initial_messages, type='messages')
    gr.ChatInterface(me.chat, type="messages", chatbot=chatbot).launch()
