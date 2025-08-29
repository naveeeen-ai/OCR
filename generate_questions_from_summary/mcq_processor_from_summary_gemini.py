import os
import re
import pdfplumber
from dotenv import load_dotenv

load_dotenv()

# Gemini SDK
try:
    import google.generativeai as genai
except Exception as e:
    genai = None

def get_gemini_model():
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in environment")
    if genai is None:
        raise RuntimeError("google-generativeai package not installed. Install with: pip install google-generativeai")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(get_gemini_model())

def extract_text_from_pdf(pdf_path):
    text = ""
    # Resolve path relative to this script so it works regardless of CWD
    if not os.path.isabs(pdf_path):
        pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), pdf_path)
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def save_file(filename, content):
    target_path = filename
    if not os.path.isabs(target_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        target_path = os.path.join(base_dir, target_path)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)

def extract_numbered_points(text):
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

def generate_three_mcqs_with_gemini(model, point_text):
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
    resp = model.generate_content(prompt)
    raw = resp.text.strip() if hasattr(resp, 'text') and resp.text else str(resp)

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

def task_generate_mcqs_from_summary():
    print("Task: Generating 3 MCQs per point with Gemini...")
    model = configure_gemini()

    pdf_text = extract_text_from_pdf('kinematics_and_dynamics.pdf')
    if not pdf_text:
        print("Error: Could not extract text from PDF")
        return

    points = extract_numbered_points(pdf_text)
    if not points:
        print("No numbered points were found in the PDF text.")
        return

    print(f"Found {len(points)} points. Generating MCQs...")

    outputs = []
    mapping_rows = []  # (point_text, [ids])
    for p_idx, point in enumerate(points, start=1):
        try:
            mcqs = generate_three_mcqs_with_gemini(model, point)
            letters = ['a', 'b', 'c']
            assigned = []
            for j, mcq in enumerate(mcqs):
                if not mcq.strip():
                    continue
                lines = mcq.splitlines()
                q_idx = None
                for i, ln in enumerate(lines):
                    if ln.strip():
                        q_idx = i
                        break
                if q_idx is not None:
                    label = f"{p_idx}{letters[j]}"
                    lines[q_idx] = f"{label}. {lines[q_idx].lstrip()}"
                outputs.append("\n".join(lines).strip())
                assigned.append(f"{p_idx}{letters[j]}")
            if assigned:
                mapping_rows.append((point, assigned))
        except Exception as e:
            print(f"Error generating MCQs for a point: {e}")
            continue

    final_output = "\n\n".join(outputs)
    save_file('summary_questions_gemini.txt', final_output)

    md_lines = ["| Source Point | Question ID(s) |", "|---|---|"]
    for pt, ids in mapping_rows:
        safe_point = pt.replace("|", "\\|")
        md_lines.append(f"| {safe_point} | {', '.join(ids)} |")
    save_file('points_to_questions_gemini.md', "\n".join(md_lines))

    print(f"Completed: {len(outputs)} MCQs -> summary_questions_gemini.txt")
    print("Mapping saved to points_to_questions_gemini.md\n")

def main():
    print("Starting MCQ generation with Gemini...\n")
    try:
        task_generate_mcqs_from_summary()
        print("Done. Output: summary_questions_gemini.txt")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nPlease check:")
        print("1. GEMINI_API_KEY is set; package google-generativeai is installed")
        print("2. You have an active internet connection")
        print("3. The PDF file exists and is readable")

if __name__ == "__main__":
    main()


