import os
import re
import io
import pdfplumber
import streamlit as st
from dotenv import load_dotenv

# Optional SDKs
try:
    from openai import OpenAI as OpenAIClient
except Exception:
    OpenAIClient = None

try:
    import google.generativeai as genai
except Exception:
    genai = None

import requests

load_dotenv()


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_numbered_points(text: str):
    normalized = re.sub(r"\r\n?|\u2028", "\n", text)
    lines = normalized.split("\n")
    points = []
    current = []

    numbered_pat = re.compile(r"^\s*(\d+\.|\d+\)|\(\d+\))\s+")
    pua_bullet_pat = re.compile(r"^\s*[\uE000-\uF8FF]{1,10}\s+")
    std_bullet_pat = re.compile(r"^\s*[•◦▪‣\-–—]\s+")

    def is_item_start(s):
        return (
            numbered_pat.match(s)
            or pua_bullet_pat.match(s)
            or std_bullet_pat.match(s)
        ) is not None

    def strip_marker(s):
        s = numbered_pat.sub("", s)
        s = pua_bullet_pat.sub("", s)
        s = std_bullet_pat.sub("", s)
        return s.strip()

    for line in lines:
        if is_item_start(line):
            if current:
                points.append(" ".join(current).strip())
                current = []
            content = strip_marker(line)
            if content:
                current.append(content)
        else:
            if current and line.strip():
                current.append(line.strip())
    if current:
        points.append(" ".join(current).strip())

    seen = set()
    unique_points = []
    for p in points:
        if p and p not in seen:
            seen.add(p)
            unique_points.append(p)

    # Drop header/footer artifacts like "Numbered list"
    artifact_pat = re.compile(r"\bnumbered\s+list\b", re.IGNORECASE)
    unique_points = [p for p in unique_points if not artifact_pat.search(p)]

    return unique_points


def generate_three_mcqs_openai(point_text: str, model: str) -> list[str]:
    if OpenAIClient is None:
        raise RuntimeError("openai package not installed. pip install openai")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAIClient(api_key=api_key)
    prompt = f"""You will write THREE distinct MCAT physics multiple-choice questions based on ONE point.
Each question must be conceptual/theoretical (no calculations) and must test a DIFFERENT facet or ask from a UNIQUE angle. Do NOT paraphrase the same question.

Point:
{point_text}

STRICT OUTPUT FORMAT FOR EACH MCQ (no extra blank lines, no markdown):
Question text
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
Answer: [Letter]. [Full correct answer text]
Explanation: [1-3 sentences focusing on MCAT-relevant concept]

CRITICAL CONSTRAINTS:
- Produce EXACTLY THREE MCQs.
- Each MCQ must assess a different perspective (definition vs. application vs. discrimination, etc.).
- Ensure exactly four options A–D; only one option is indisputably correct.
- Use precise MCAT-appropriate physics terminology.

SEPARATION:
- Separate the three MCQs with a single line containing only: ---
"""
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1400,
        temperature=0.45,
    )
    return split_three_blocks(resp.choices[0].message.content or "")


def configure_gemini(model: str):
    if genai is None:
        raise RuntimeError("google-generativeai not installed. pip install google-generativeai")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model)


def generate_three_mcqs_gemini(point_text: str, model: str) -> list[str]:
    m = configure_gemini(model)
    prompt = f"""You will write THREE distinct MCAT physics multiple-choice questions based on ONE point.
Each question must be conceptual/theoretical (no calculations) and must test a DIFFERENT facet or ask from a UNIQUE angle. Do NOT paraphrase the same question.

Point:
{point_text}

STRICT OUTPUT FORMAT FOR EACH MCQ (no extra blank lines, no markdown):
Question text
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
Answer: [Letter]. [Full correct answer text]
Explanation: [1-3 sentences focusing on MCAT-relevant concept]

CRITICAL CONSTRAINTS:
- Produce EXACTLY THREE MCQs.
- Each MCQ must assess a different perspective (definition vs. application vs. discrimination, etc.).
- Ensure exactly four options A–D; only one option is indisputably correct.
- Use precise MCAT-appropriate physics terminology.

SEPARATION:
- Separate the three MCQs with a single line containing only: ---
"""
    resp = m.generate_content(prompt)
    raw = getattr(resp, 'text', None) or str(resp)
    return split_three_blocks(raw)


def generate_three_mcqs_mistral(point_text: str, model: str, api_url: str) -> list[str]:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY not set")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = f"""You will write THREE distinct MCAT physics multiple-choice questions based on ONE point.
Each question must be conceptual/theoretical (no calculations) and must test a DIFFERENT facet or ask from a UNIQUE angle. Do NOT paraphrase the same question.

Point:
{point_text}

STRICT OUTPUT FORMAT FOR EACH MCQ (no extra blank lines, no markdown):
Question text
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
Answer: [Letter]. [Full correct answer text]
Explanation: [1-3 sentences focusing on MCAT-relevant concept]

CRITICAL CONSTRAINTS:
- Produce EXACTLY THREE MCQs.
- Each MCQ must assess a different perspective (definition vs. application vs. discrimination, etc.).
- Ensure exactly four options A–D; only one option is indisputably correct.
- Use precise MCAT-appropriate physics terminology.

SEPARATION:
- Separate the three MCQs with a single line containing only: ---
"""
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.45,
        "max_tokens": 1400,
    }
    resp = requests.post(api_url, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return split_three_blocks(content)


def split_three_blocks(raw: str) -> list[str]:
    raw = (raw or "").strip()
    parts = []
    buf = []
    for line in raw.splitlines():
        if line.strip() == '---':
            if buf:
                parts.append("\n".join(buf).strip())
                buf = []
        else:
            buf.append(line)
    if buf:
        parts.append("\n".join(buf).strip())
    if len(parts) != 3:
        candidates = [blk.strip() for blk in raw.split("\n\n\n") if blk.strip()]
        if len(candidates) == 3:
            parts = candidates
    return [p.strip() for p in parts[:3]]


st.set_page_config(page_title="MCAT MCQ Generator", layout="wide")
st.title("MCAT MCQ Generator (OpenAI / Gemini / Mistral)")

with st.sidebar:
    provider = st.selectbox("Provider", ["OpenAI", "Gemini", "Mistral"], index=0)
    if provider == "OpenAI":
        model = st.text_input("OpenAI Model", value=os.getenv("OPENAI_MODEL", "gpt-4.1"))
    elif provider == "Gemini":
        model = st.text_input("Gemini Model", value=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"))
    else:
        model = st.text_input("Mistral Model", value=os.getenv("MISTRAL_MODEL", "mistral-large-latest"))

uploaded = st.file_uploader("Upload a PDF", type=["pdf"]) 

if uploaded is not None:
    try:
        text = extract_text_from_pdf_bytes(uploaded.read())
        st.success("PDF text extracted.")
        points = extract_numbered_points(text)
        st.write(f"Detected {len(points)} bullet points.")
        if points:
            st.subheader("Preview of first 5 points")
            for i, pt in enumerate(points[:5], start=1):
                st.write(f"{i}. {pt}")

        if st.button("Generate 3 MCQs per point"):
            target_points = points

            with st.spinner("Generating MCQs for all points... This may take a while"):
                outputs = []
                mapping = []
                for p_idx, pt in enumerate(target_points, start=1):
                    try:
                        if provider == "OpenAI":
                            mcqs = generate_three_mcqs_openai(pt, model)
                        elif provider == "Gemini":
                            mcqs = generate_three_mcqs_gemini(pt, model)
                        else:
                            api_url = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")
                            mcqs = generate_three_mcqs_mistral(pt, model, api_url)

                        letters = ['a', 'b', 'c']
                        assigned = []
                        for j, mcq in enumerate(mcqs):
                            if not mcq.strip():
                                continue
                            lines = mcq.splitlines()
                            q_idx = None
                            for k, ln in enumerate(lines):
                                if ln.strip():
                                    q_idx = k
                                    break
                            label = f"{p_idx}{letters[j]}"
                            if q_idx is not None:
                                lines[q_idx] = f"{label}. {lines[q_idx].lstrip()}"
                            outputs.append("\n".join(lines).strip())
                            assigned.append(label)
                        if assigned:
                            mapping.append((pt, assigned))
                    except Exception as e:
                        st.error(f"Error generating for point {p_idx}: {e}")

            st.success(f"Generated {len(outputs)} MCQs.")

            provider_tag = provider.lower()
            txt = "\n\n".join(outputs)
            md_lines = ["| Source Point | Question ID(s) |", "|---|---|"]
            for pt, ids in mapping:
                safe = pt.replace("|", "\\|")
                md_lines.append(f"| {safe} | {', '.join(ids)} |")
            md = "\n".join(md_lines)

            st.download_button("Download MCQs (.txt)", data=txt.encode("utf-8"), file_name=f"summary_questions_{provider_tag}.txt", mime="text/plain")
            st.download_button("Download Mapping (.md)", data=md.encode("utf-8"), file_name=f"points_to_questions_{provider_tag}.md", mime="text/markdown")

    except Exception as e:
        st.error(f"Failed to process PDF: {e}")


