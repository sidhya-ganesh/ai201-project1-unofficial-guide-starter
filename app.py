"""
app.py — Gradio web interface for the Unofficial Penn Guide.
Run: python app.py
Then open: http://localhost:7860
"""

import gradio as gr
from query import ask


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources_text = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources_text


with gr.Blocks(title="The Unofficial Penn Guide") as demo:
    gr.Markdown("""
    # 📚 The Unofficial Penn Guide
    ### Student-powered knowledge about UPenn courses and professors
    Ask anything about professors, exams, grading curves, registration tips, and more.
    *All answers are grounded in real student reviews — with sources cited.*
    """)

    with gr.Row():
        with gr.Column(scale=3):
            question_input = gr.Textbox(
                label="Your question",
                placeholder='e.g. "Is there a curve in CIS 1200?" or "What is Angela Duckworth\'s class like?"',
                lines=2
            )
            ask_btn = gr.Button("Ask the Guide", variant="primary")

    with gr.Row():
        with gr.Column(scale=3):
            answer_output = gr.Textbox(
                label="Answer (grounded in student reviews)",
                lines=10,
                interactive=False
            )
        with gr.Column(scale=1):
            sources_output = gr.Textbox(
                label="Retrieved from",
                lines=6,
                interactive=False
            )

    gr.Markdown("""
    ---
    **Sample questions to try:**
    - What do students say about Professor Ghrist's exams?
    - How do I get off the waitlist for a course at Penn?
    - What is it like taking CIS 1210 with Callison-Burch?
    - Are Penn writing seminars graded harshly?
    - What resources does Penn have for academic support?
    """)

    ask_btn.click(
        handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output]
    )
    question_input.submit(
        handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output]
    )

if __name__ == "__main__":
    demo.launch()