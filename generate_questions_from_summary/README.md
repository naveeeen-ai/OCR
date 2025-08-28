# MCAT MCQ Generation from Summary

This module generates Multiple Choice Questions (MCQs) specifically designed for MCAT exam preparation from physics PDF summaries using AI.

## Files Description

### 📄 Source Materials
- **`kinematics_and_dynamics.pdf`** - Physics summary PDF containing bullet points on kinematics and dynamics concepts

### 🤖 Processing Scripts
- **`mcq_processor_from_summary_openai.py`** – Uses OpenAI to:
  - Extract text from the PDF
  - Parse numbered/bulleted points
  - Generate exactly THREE MCAT-style MCQs per point
  - Number questions per point as `1a., 1b., 1c.`; then `2a., 2b., 2c.`, etc.
  - Save a mapping table of Point → Question IDs for validation
- **`mcq_processor_from_summary_gemini.py`** – Same behavior using Google Gemini
- **`mcq_processor_from_summary_mistral.py`** – Same behavior using Mistral

### 📋 Generated Files
- **`summary_questions_openai.txt` / `summary_questions_gemini.txt` / `summary_questions_mistral.txt`** – Numbered MCQs (3 per source point)
- **`points_to_questions.md`** (OpenAI) and provider-specific: `points_to_questions_gemini.md`, `points_to_questions_mistral.md`

## MCQ Format

Each question follows this structure:
```
Na. Question text   (e.g., 1a., 1b., 1c.)
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
   pip install openai google-generativeai requests python-dotenv pdfplumber
   ```

2. **Setup:**
   - Create a `.env` file with your API keys (set what you need):
     ```
     OPENAI_API_KEY=your_openai_key_here
     GEMINI_API_KEY=your_gemini_key_here
     MISTRAL_API_KEY=your_mistral_key_here
     ```

3. **Optional – choose a model (paid accounts):**
   - OpenAI default: `gpt-4.1`
   - Gemini default: `gemini-2.0-flash`
   - Mistral default: `mistral-large-latest` (overrideable and API URL configurable)
   - Override via `.env`:
     ```
     OPENAI_MODEL=gpt-4o
     GEMINI_MODEL=gemini-2.0-flash
     MISTRAL_MODEL=mistral-large-latest
     MISTRAL_API_URL=https://api.mistral.ai/v1/chat/completions
     ```

4. **Run the processors:**
   ```bash
   cd generate_questions_from_summary
   # OpenAI
   python mcq_processor_from_summary_openai.py
   # Gemini
   python mcq_processor_from_summary_gemini.py
   # Mistral
   python mcq_processor_from_summary_mistral.py
   ```

5. **Optional – Streamlit app:**
   ```bash
   streamlit run generate_questions_from_summary/streamlit_app.py
   ```

## Features

✅ Parse numbered/bulleted points from the PDF  
✅ Generate three conceptual MCAT-style MCQs per point  
✅ Number per point as 1a./1b./1c. for easy reference  
✅ Save point → question mapping to validate coverage  

## Quality Assurance & AI Technology

- **MCAT-Focused:** Questions designed specifically for MCAT physics preparation
- **Comprehensive Coverage:** Questions span different difficulty levels and topic areas relevant to MCAT
- **Accurate Content:** AI-generated answers verified against physics principles tested on MCAT
- **Clear Explanations:** Detailed explanations help understand reasoning
- **Consistent Format:** Standardized format for study preparation

- **Models:** OpenAI (default `gpt-4.1`), Gemini (default `gemini-1.5-pro`), Mistral (default `mistral-large-latest`)
- **Smart PDF Processing:** Extracts and processes text from complex academic PDFs
- **Context-Aware Generation:** Creates questions based on specific topic understanding
