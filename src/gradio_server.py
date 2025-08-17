import os

import gradio as gr

from chatbot import ChatBot
from input_parser import parse_input_text
from ppt_generator import generate_presentation
from layout_manager import LayoutManager
from template_manager import load_template, get_layout_mapping

system_prompt_file = os.path.join(os.path.dirname(__file__), '../prompts/formatter.txt')
slide_template_file = os.path.join(os.path.dirname(__file__), '../templates/MasterTemplate.pptx')
outputs_path = os.path.join(os.path.dirname(__file__), '../outputs')

chatbot = ChatBot(system_prompt_file)
ppt_template = load_template(slide_template_file)

# 初始化 LayoutManager, 使用配置文件中的 layout_mapping
layout_manager = LayoutManager(get_layout_mapping(ppt_template))

def generate_slides_content(message, history):
    slides_content = chatbot.chat_with_history(message["text"])
    return slides_content

def generate_slides(history):
    slides_content = history[-1]["content"]
    slides_data, presentation_title = parse_input_text(slides_content, layout_manager)
    output_slides_file = f"{outputs_path}/{presentation_title}.pptx"
    generate_presentation(slides_data, slide_template_file, output_slides_file)

    return output_slides_file

placeholder = """
<strong>AI 一键生成 PPT</strong>
<div>请输入你的主题，AI 将自动为您进行合理扩展，并形成完整的具有逻辑性的内容。</div>
<ul>
<li>如果您认为内容符合您的预期，请点击“Generate Slides”按钮，将自动为您生成 PPT 文件。</li>
<li>如果不符合您的预期，您可以继续与 ChatBot 深入沟通，直到内容符合您的预期。</li>
</ul>
"""

with gr.Blocks(title="ChatPPT Demo") as demo:
    gr.Markdown("# ChatPPT Demo")

    contents_chatbot = gr.Chatbot(
        placeholder=placeholder,
        height=600,
        type="messages"
    )

    gr.ChatInterface(
        fn=generate_slides_content,
        chatbot=contents_chatbot,
        type="messages",
        multimodal=True
    )

    slides_generate_button = gr.Button("Generate Slides")
    slides_generate_button.click(
        fn=generate_slides,
        inputs=contents_chatbot,
        outputs=gr.File(label="Generated Slides")
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", allowed_paths=[outputs_path])
