import os
import re
import pdfplumber
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Configure OpenAI API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_openai_model():
    """Return the configured OpenAI model, defaulting to a top-tier paid model."""
    # You can override via OPENAI_MODEL in .env, e.g., gpt-4.1, gpt-4o
    return os.getenv("OPENAI_MODEL", "gpt-4.1")

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
        # Resolve path relative to this script so it works regardless of CWD
        if not os.path.isabs(pdf_path):
            pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), pdf_path)
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
    return text

def save_questions(filename, questions):
    """Save questions to a file in the same folder as this script unless an absolute path is provided."""
    target_path = filename
    if not os.path.isabs(target_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        target_path = os.path.join(base_dir, target_path)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(questions)

def extract_numbered_points(text):
    """Extract list points from text into a list of strings.
    Supports numeric markers (1., 2), (3)), bullet glyphs (•, -, –, —), and PDF private-use glyph clusters like '' or ''.
    Assumes each point starts at a new line and content may wrap to the next line until the next item marker.
    """
    # Normalize line endings and collapse multiple blank lines
    normalized = re.sub(r"\r\n?|\u2028", "\n", text)
    lines = normalized.split("\n")
    points = []
    current = []

    numbered_pat = re.compile(r"^\s*(\d+\.|\d+\)|\(\d+\))\s+")
    pua_bullet_pat = re.compile(r"^\s*[\uE000-\uF8FF]{1,10}\s+")  # Private Use Area cluster
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
            # continuation of previous point (if any)
            if current:
                if line.strip():
                    current.append(line.strip())
    if current:
        points.append(" ".join(current).strip())

    # Filter out empties and duplicates while preserving order
    seen = set()
    unique_points = []
    for p in points:
        if p and p not in seen:
            seen.add(p)
            unique_points.append(p)
    return unique_points

def generate_mcat_mcq_for_point(point_text):
    """Generate one MCAT-style MCQ (question + 4 choices + answer + explanation) for a single point."""
    prompt = f"""You are creating MCAT physics MCQs. Convert the following point into ONE conceptual MCAT-style multiple-choice question (no calculations, theoretical/conceptual focus), with exactly four distinct answer choices where only one is correct. Then provide the correct answer and a concise teaching explanation.

Point:
{point_text}

STRICT OUTPUT FORMAT (no numbering, no extra blank lines, no markdown):
Question text
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
Answer: [Letter]. [Full correct answer text]
Explanation: [1-3 sentences focusing on MCAT-relevant concept]

Constraints:
- Keep the question theoretical and concept-focused.
- Ensure exactly four options A-D; only one is indisputably correct.
- Use precise physics terminology suitable for MCAT.
"""
    response = client.chat.completions.create(
        model=get_openai_model(),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

def task1_generate_mcqs_from_summary():
    """Generate one MCAT MCQ per numbered point in the PDF and save to summary_questions.txt."""
    print("Task 1: Generating one MCQ per numbered point from PDF...")

    pdf_text = extract_text_from_pdf('kinematics_and_dynamics.pdf')
    if not pdf_text:
        print("Error: Could not extract text from PDF")
        return

    points = extract_numbered_points(pdf_text)
    if not points:
        print("No numbered points were found in the PDF text.")
        return

    print(f"Found {len(points)} numbered points. Generating MCQs...")

    outputs = []
    mapping_rows = []  # (question_number, point_text)
    for idx, point in enumerate(points, start=1):
        try:
            mcq = generate_mcat_mcq_for_point(point)
            # Add numbering to the first non-empty line (question line)
            lines = mcq.splitlines()
            # find first non-empty line index
            q_idx = None
            for i, ln in enumerate(lines):
                if ln.strip():
                    q_idx = i
                    break
            if q_idx is not None:
                lines[q_idx] = f"{idx}. {lines[q_idx].lstrip()}"
            numbered_mcq = "\n".join(lines).strip()
            outputs.append(numbered_mcq)
            mapping_rows.append((idx, point))
        except Exception as e:
            print(f"Error generating MCQ for point {idx}: {e}")
            continue

    # Join MCQs with a single blank line between items to keep readability
    final_output = "\n\n".join(outputs)
    save_questions('summary_questions.txt', final_output)
    
    # Save mapping table (Markdown) for validation
    md_lines = [
        "| Question # | Source Point |",
        "|---:|---|",
    ]
    for qnum, pt in mapping_rows:
        safe_point = pt.replace("|", "\\|")
        md_lines.append(f"| {qnum} | {safe_point} |")
    mapping_md = "\n".join(md_lines)
    save_questions('points_to_questions.md', mapping_md)

    print(f"Task 1 completed: {len(outputs)} MCQs saved to summary_questions.txt")
    print("Mapping saved to points_to_questions.md\n")
    return final_output

def task2_refine_questions(original_mcqs):
    """Task 2: Refine questions with same meaning and choices"""
    print("Task 2: Refining questions...")
    
    prompt = f"""Refine the following MCAT preparation MCQs to improve clarity and wording while maintaining:
- EXACT same meaning for each question
- EXACT same answer choices (A, B, C, D) - do not change any option text
- Same level of difficulty appropriate for MCAT exam
- Better grammar and more professional language
- MCAT-style question format and terminology

Focus only on improving the question wording for MCAT preparation, not the choices.

Original MCQs:
{original_mcqs}

Provide the refined questions in the same format:
Question text
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text  
D. Answer choice 4 text

"""
    
    # Get refined questions from OpenAI
    response = client.chat.completions.create(
        model=get_openai_model(),
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=0.7
    )
    refined_mcqs = response.choices[0].message.content
    
    # Save to file
    save_questions('refined_summary_questions.txt', refined_mcqs)
    print("Task 2 completed: Refined questions saved to refined_summary_questions.txt\n")
    
    return refined_mcqs

def task3_add_answers_and_explanations(original_mcqs, refined_mcqs):
    """Task 3: Add answers and explanations to both sets of questions"""
    print("Task 3: Adding answers and explanations...")
    
    # Process original questions
    prompt_original = f"""For each of the following MCAT preparation MCQs, add the correct answer and detailed explanation.

Format should be:
Question text
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
Correct Answer text with option letter
Explanation

Example format:
What is the formula for acceleration?
A. v = u + at
B. a = (v - u) / t
C. s = ut + (1/2)at²
D. F = ma
B. a = (v - u) / t
Acceleration is defined as the rate of change of velocity with respect to time. The formula a = (v - u) / t represents this relationship where 'v' is final velocity, 'u' is initial velocity, and 't' is time. This concept is fundamental for MCAT physics problems involving motion analysis.

MCQs to process:
{original_mcqs}

Add correct answers and explanations for each question:"""
    
    response_original = client.chat.completions.create(
        model=get_openai_model(),
        messages=[
            {"role": "user", "content": prompt_original}
        ],
        max_tokens=4000,
        temperature=0.7
    )
    original_with_answers = response_original.choices[0].message.content
    
    # Process refined questions  
    prompt_refined = f"""For each of the following refined MCAT preparation MCQs, add the correct answer and detailed explanation.

Format should be:
Question text
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
Correct Answer text with option letter
Explanation

Provide explanations that help MCAT test-takers understand the underlying physics concepts and problem-solving strategies.

MCQs to process:
{refined_mcqs}

Add correct answers and explanations for each question:"""
    
    response_refined = client.chat.completions.create(
        model=get_openai_model(),
        messages=[
            {"role": "user", "content": prompt_refined}
        ],
        max_tokens=4000,
        temperature=0.7
    )
    refined_with_answers = response_refined.choices[0].message.content
    
    # Save updated files
    save_questions('summary_questions.txt', original_with_answers)
    save_questions('refined_summary_questions.txt', refined_with_answers)
    
    print("Task 3 completed: Answers and explanations added to both files\n")
    
    return original_with_answers, refined_with_answers

def main():
    """Main entrypoint: generate one MCQ per numbered point and write to summary_questions.txt."""
    print("Starting MCQ generation from numbered points...\n")

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Please set your OpenAI API key in the .env file")
        print("\nTo get an OpenAI API key:")
        print("1. Go to: https://platform.openai.com/api-keys")
        print("2. Click 'Create new secret key'")
        print("3. Copy the key and add it to your .env file as: OPENAI_API_KEY=your_key_here")
        return

    try:
        task1_generate_mcqs_from_summary()
        print("Done. Output: summary_questions.txt")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nPlease check:")
        print("1. Your OpenAI API key is correctly set in the .env file")
        print("2. You have an active internet connection")
        print("3. The PDF file exists and is readable")

if __name__ == "__main__":
    main()
