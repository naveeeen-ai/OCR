# Refined Questions

This folder contains all MCQ (Multiple Choice Questions) related files that have been processed and refined using AI.

## Files Description

### 📄 Source Files
- **`output.txt`** - Original formatted MCQs extracted from PDF
- **`mcq_refined.txt`** - Refined questions with improved clarity (questions only)

### 📋 Complete MCQ Files (with Answers & Explanations)
- **`mcq_formatted_final.txt`** - Original MCQs with answers and detailed explanations
- **`mcq_refined_with_answers.txt`** - Refined MCQs with answers and detailed explanations

### 🤖 Processing Script
- **`mcq_processor_openai.py`** - Python script using OpenAI GPT to:
  - Format MCQs with proper numbering
  - Generate answers and explanations
  - Refine questions for better clarity
  - Create complete answer sheets

## File Formats

All MCQ files follow this structure:
```
**Question [number]**

Question text
A. Answer choice 1
B. Answer choice 2
C. Answer choice 3
D. Answer choice 4
[Letter]. Correct Answer text
Detailed explanation
```

## Usage

To process new MCQs:
1. Make sure you have a `.env` file with your `OPENAI_API_KEY`
2. Run: `python mcq_processor_openai.py`
3. Follow the prompts to select which task to perform

## Chapter Coverage

Current MCQs cover:
- **Chapter 1: Biology and Behavior** (7 questions)
  - Neurotransmitters and enzymes
  - Endocrine system
  - Reflexes and motor skills
  - Twin studies and genetics
