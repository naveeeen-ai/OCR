# MCQ Generation from Summary

This module generates Multiple Choice Questions (MCQs) from academic PDF summaries using AI.

## Files Description

### 📄 Source Materials
- **`kinematics_and_dynamics.pdf`** - Physics summary PDF containing bullet points on kinematics and dynamics concepts

### 🤖 Processing Script
- **`mcq_processor_from_summary.py`** - Python script that uses Google Gemini AI to:
  - Extract text from PDF summaries
  - Generate comprehensive MCQs covering various topics
  - Refine questions for better clarity
  - Add correct answers and detailed explanations

### 📋 Generated MCQ Files
- **`summary_questions.txt`** - Original MCQs with answers and explanations (15 questions)
- **`refined_summary_questions.txt`** - Refined MCQs with improved wording, same answers and explanations (15 questions)

## MCQ Format

Each question follows this structure:
```
Question text
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
Correct Answer text with option letter
Explanation
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
   pip install google-generativeai python-dotenv pdfplumber
   ```

2. **Setup:**
   - Create a `.env` file with your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

3. **Run the processor:**
   ```bash
   cd generate_questions_from_summary
   python mcq_processor_from_summary.py
   ```

## Features

✅ **Task 1:** Generate 15 comprehensive MCQs from PDF summary  
✅ **Task 2:** Refine questions for better clarity while maintaining same meaning and choices  
✅ **Task 3:** Add correct answers and detailed explanations to both sets of questions  

## Quality Assurance

- **Comprehensive Coverage:** Questions span different difficulty levels and topic areas
- **Accurate Content:** AI-generated answers verified against physics principles
- **Clear Explanations:** Detailed explanations help understand the reasoning behind correct answers
- **Consistent Format:** Standardized format for easy reading and study

## AI Technology

- **Google Gemini 1.5 Flash:** Used for text processing and question generation
- **Smart PDF Processing:** Extracts and processes text from complex academic PDFs
- **Context-Aware Generation:** Creates questions based on specific topic understanding
