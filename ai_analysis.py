import os
from dotenv import load_dotenv
import openai

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    raise RuntimeError("OPENAI_API_KEY is not set. Copy .env.example to .env and set your key.")

openai.api_key = OPENAI_API_KEY


def analyze_content(prompt_text: str, model: str = "gpt-4o-mini") -> str:
    """Send prompt_text to OpenAI and return the assistant response as text."""
    # Keep prompts concise and slice long input if needed
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=1500,
            temperature=0.2,
        )
        return resp.choices[0].message["content"].strip()
    except Exception as e:
        return f"AI call failed: {e}"


def accessibility_ai_check(html_snippet: str) -> str:
    prompt = (
        "You are an accessibility QA engineer. Analyze the following HTML for accessibility issues: "
        "missing alt attributes, missing form labels, aria attributes, color contrast problems, tab order issues, and common WCAG failures. "
        "Return a bullet list with severity (high/medium/low) and suggested fixes.\n\nHTML:\n" + html_snippet
    )
    return analyze_content(prompt)


def content_quality_check(text_snippet: str) -> str:
    prompt = (
        "You are a UX writer and QA reviewer. For the text below, provide: \n"
        "1) Summary of issues (clarity, grammar, tone)\n"
        "2) Suggested rewrites for problematic sentences\n"
        "3) A short readability score assessment.\n\nText:\n" + text_snippet
    )
    return analyze_content(prompt)
