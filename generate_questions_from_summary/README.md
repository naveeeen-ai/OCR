# MCAT MCQ Generation from Summary

This module generates Multiple Choice Questions (MCQs) specifically designed for MCAT exam preparation from physics PDF summaries using AI.

## Files Description

### 📄 Source Materials
- **`kinematics_and_dynamics.pdf`** - Physics summary PDF containing bullet points on kinematics and dynamics concepts

### 🤖 Processing Script
- **`mcq_processor_from_summary.py`** - Python script that uses OpenAI GPT to:
  - Extract text from the PDF
  - Parse numbered/bulleted points
  - Generate exactly one MCAT-style MCQ per point
  - Number each question (1., 2., 3., ...)
  - Save a mapping table of Point → Question # for validation

### 📋 Generated Files
- **`summary_questions.txt`** - Numbered MCAT-style MCQs (one per source point)
- **`points_to_questions.md`** - Markdown table mapping each source point to its question number

## MCQ Format

Each question follows this structure:
```
N. Question text
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
Answer: [Letter]. [Full correct answer text]
Explanation: [1–3 sentences]
```

## Topics Covered

The generated MCQs cover various aspects of:

### 🎯 Kinematics
- Displacement, velocity, and acceleration concepts
- Motion equations and mathematical relationships
- Vector vs. scalar quantities
- Projectile motion

### ⚡ Dynamics
- Newton's laws of motion
- Forces and equilibrium
- Momentum and impulse
- Work, energy, and power
- Collisions and conservation laws

## Usage

1. **Prerequisites:**
   ```bash
   pip install openai python-dotenv pdfplumber
   ```

2. **Setup:**
   - Create a `.env` file with your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

3. **Optional – choose a model (paid accounts):**
   - Default model: `gpt-4.1`. To override, set in `.env` (e.g., `gpt-4o`, `gpt-4.1-mini`):
     ```
     OPENAI_MODEL=gpt-4o
     ```

4. **Run the processor:**
   ```bash
   cd generate_questions_from_summary
   python mcq_processor_from_summary.py
   ```

## Features

✅ Parse numbered/bulleted points from the PDF  
✅ Generate one conceptual MCAT-style MCQ per point  
✅ Number questions for easier reference  
✅ Save point → question mapping to validate coverage  

## Quality Assurance

- **MCAT-Focused:** Questions designed specifically for MCAT physics preparation
- **Comprehensive Coverage:** Questions span different difficulty levels and topic areas relevant to MCAT
- **Accurate Content:** AI-generated answers verified against physics principles tested on MCAT
- **Clear Explanations:** Detailed explanations help understand the reasoning behind correct answers and MCAT problem-solving strategies
- **Consistent Format:** Standardized format for easy reading and MCAT study preparation

- **OpenAI GPT-4.1 (default, configurable via `OPENAI_MODEL`)**: Used for MCQ generation
- **Smart PDF Processing:** Extracts and processes text from complex academic PDFs
- **Context-Aware Generation:** Creates questions based on specific topic understanding
