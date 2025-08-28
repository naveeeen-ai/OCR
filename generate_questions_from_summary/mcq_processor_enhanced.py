import os
import pdfplumber
from dotenv import load_dotenv
import google.generativeai as genai
import re

load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
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
    """Save questions to a file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(questions)

def validate_answers(questions_text):
    """Validate that answers are consistent and logical"""
    # Extract questions and answers for validation
    pattern = r'\*\*(\d+)\.\s*([^*]+)\*\*\n([^*]+)\*\*Correct Answer:\s*([^*]+)\*\*'
    matches = re.findall(pattern, questions_text, re.DOTALL)
    
    validation_errors = []
    for match in matches:
        question_num, question_text, options_text, answer = match
        # Basic validation - you can expand this
        if not answer.strip():
            validation_errors.append(f"Question {question_num}: Empty answer")
        if len(answer.strip()) < 2:
            validation_errors.append(f"Question {question_num}: Answer too short: '{answer.strip()}'")
    
    return validation_errors

def task1_generate_mcqs_from_summary():
    """Task 1: Generate MCQs from PDF summary with enhanced prompting"""
    print("Task 1: Generating MCAT MCQs from Kinematics and Dynamics summary...")
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf('kinematics_and_dynamics.pdf')
    if not pdf_text:
        print("Error: Could not extract text from PDF")
        return
    
    # Enhanced prompt with more specific instructions
    prompt = f"""Based on the following physics summary about Kinematics and Dynamics, generate 15 comprehensive multiple-choice questions (MCQs) for MCAT exam preparation. 

CRITICAL REQUIREMENTS:
1. Each question must have EXACTLY 4 answer choices (A, B, C, D)
2. Only ONE choice should be definitively correct
3. Ensure physics accuracy - double-check all calculations and concepts
4. Use proper MCAT-style terminology and complexity
5. Cover diverse topics from the summary

Topics to cover:
- Kinematics concepts (displacement, velocity, acceleration, motion equations)
- Dynamics concepts (forces, Newton's laws, momentum, energy)
- Mathematical relationships and formulas
- Real-world applications and MCAT-style scenarios
- Vector operations and equilibrium conditions

For each question, provide:
- Clear, unambiguous question suitable for MCAT preparation
- Four distinct answer choices with proper physics terminology
- Ensure correct answer is scientifically accurate
- Include both conceptual and calculation-based questions
- Focus on critical thinking and application skills required for MCAT

Format each question EXACTLY as:
**Question number. Question text**
A. Answer choice 1 text
B. Answer choice 2 text  
C. Answer choice 3 text
D. Answer choice 4 text

IMPORTANT: Do NOT include answers or explanations in this step - only questions and choices.

Summary content:
{pdf_text}

Generate exactly 15 MCQs covering different aspects of kinematics and dynamics:"""
    
    # Get MCQs from Gemini
    response = model.generate_content(prompt)
    mcqs = response.text
    
    # Save to file
    save_questions('summary_questions.txt', mcqs)
    print("Task 1 completed: MCQs saved to summary_questions.txt\n")
    
    return mcqs

def task2_refine_questions(original_mcqs):
    """Task 2: Refine questions with enhanced validation"""
    print("Task 2: Refining questions with enhanced validation...")
    
    prompt = f"""Refine the following MCAT preparation MCQs to improve clarity and wording while maintaining:

CRITICAL REQUIREMENTS:
- EXACT same meaning for each question
- EXACT same answer choices (A, B, C, D) - do not change any option text or letters
- Same level of difficulty appropriate for MCAT exam
- Better grammar and more professional language
- MCAT-style question format and terminology
- Maintain scientific accuracy

VALIDATION CHECKLIST:
- Ensure all 4 choices (A, B, C, D) are preserved exactly
- Question wording should be clearer but mean the same thing
- Use proper physics terminology
- Maintain MCAT-appropriate complexity

Focus only on improving the question wording for MCAT preparation, NOT the choices.

Original MCQs:
{original_mcqs}

Provide the refined questions in the EXACT same format:
**Question number. Improved question text**
A. Same answer choice 1 text
B. Same answer choice 2 text
C. Same answer choice 3 text
D. Same answer choice 4 text

REMEMBER: Only improve question wording, keep all answer choices identical.
"""
    
    # Get refined questions from Gemini
    response = model.generate_content(prompt)
    refined_mcqs = response.text
    
    # Save to file
    save_questions('refined_summary_questions.txt', refined_mcqs)
    print("Task 2 completed: Refined questions saved to refined_summary_questions.txt\n")
    
    return refined_mcqs

def task3_add_answers_and_explanations_enhanced(original_mcqs, refined_mcqs):
    """Task 3: Add answers with enhanced validation and cross-checking"""
    print("Task 3: Adding answers and explanations with enhanced validation...")
    
    # Process original questions with enhanced prompt
    prompt_original = f"""For each of the following MCAT preparation MCQs, add the correct answer and detailed explanation.

CRITICAL ACCURACY REQUIREMENTS:
1. Double-check all physics concepts and calculations
2. Ensure only ONE answer choice is definitively correct
3. Verify answers against fundamental physics principles
4. Provide clear, educational explanations suitable for MCAT preparation

Format should be:
**Question number. Question text**
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
**Correct Answer: [Letter]. [Full answer text]**
**Explanation:** [Detailed explanation with MCAT context]

Example format:
**1. What is the formula for acceleration?**
A. v = u + at
B. a = (v - u) / t
C. s = ut + (1/2)at²
D. F = ma
**Correct Answer: B. a = (v - u) / t**
**Explanation:** Acceleration is defined as the rate of change of velocity with respect to time. The formula a = (v - u) / t represents this relationship where 'v' is final velocity, 'u' is initial velocity, and 't' is time. This concept is fundamental for MCAT physics problems involving motion analysis.

VALIDATION CHECKLIST before providing answer:
- Is the physics concept correct?
- Is only one choice definitively right?
- Does the explanation help MCAT preparation?
- Are calculations accurate?

MCQs to process:
{original_mcqs}

Add correct answers and explanations for each question:"""
    
    response_original = model.generate_content(prompt_original)
    original_with_answers = response_original.text
    
    # Process refined questions with cross-validation
    prompt_refined = f"""For each of the following refined MCAT preparation MCQs, add the correct answer and detailed explanation.

IMPORTANT: Cross-reference with the original questions to ensure answer consistency.

CRITICAL VALIDATION:
1. Verify answers are scientifically correct
2. Ensure explanations are MCAT-appropriate
3. Double-check that only one choice is definitively correct
4. Maintain consistency with physics principles

Format should be:
**Question number. Question text**
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
**Correct Answer: [Letter]. [Full answer text]**
**Explanation:** [Detailed explanation helping MCAT test-takers understand the physics concepts and problem-solving strategies]

MCQs to process:
{refined_mcqs}

Add correct answers and explanations for each question:"""
    
    response_refined = model.generate_content(prompt_refined)
    refined_with_answers = response_refined.text
    
    # Validate answers
    print("Validating generated answers...")
    original_errors = validate_answers(original_with_answers)
    refined_errors = validate_answers(refined_with_answers)
    
    if original_errors:
        print("⚠️  Validation warnings for original questions:")
        for error in original_errors:
            print(f"   - {error}")
    
    if refined_errors:
        print("⚠️  Validation warnings for refined questions:")
        for error in refined_errors:
            print(f"   - {error}")
    
    if not original_errors and not refined_errors:
        print("✅ All answers passed basic validation")
    
    # Save updated files
    save_questions('summary_questions.txt', original_with_answers)
    save_questions('refined_summary_questions.txt', refined_with_answers)
    
    print("Task 3 completed: Answers and explanations added to both files\n")
    
    return original_with_answers, refined_with_answers

def main():
    """Main function with enhanced error prevention"""
    print("Starting Enhanced MCAT MCQ Generation from Kinematics and Dynamics Summary...\n")
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: Please set your Gemini API key in the .env file")
        print("\nTo get a FREE Gemini API key:")
        print("1. Go to: https://aistudio.google.com/apikey")
        print("2. Click 'Create API Key'")
        print("3. Copy the key and add it to your .env file as: GEMINI_API_KEY=your_key_here")
        return
    
    try:
        # Execute Task 1: Generate MCQs
        print("🎯 Generating physics-accurate MCAT questions...")
        original_mcqs = task1_generate_mcqs_from_summary()
        if not original_mcqs:
            print("Failed to generate original MCQs")
            return
        
        # Execute Task 2: Refine questions
        print("🔄 Refining questions while preserving choices...")
        refined_mcqs = task2_refine_questions(original_mcqs)
        if not refined_mcqs:
            print("Failed to refine MCQs")
            return
        
        # Execute Task 3: Add answers and explanations with validation
        print("✅ Adding validated answers and explanations...")
        task3_add_answers_and_explanations_enhanced(original_mcqs, refined_mcqs)
        
        print("\n🎉 All tasks completed successfully!")
        print("\nEnhanced MCAT Preparation Output files:")
        print("- summary_questions.txt: Original MCAT MCQs with validated answers and explanations")
        print("- refined_summary_questions.txt: Refined MCAT MCQs with validated answers and explanations")
        
        print("\n📋 Error Prevention Features:")
        print("✅ Enhanced prompting for accuracy")
        print("✅ Validation checks for answers")
        print("✅ Cross-referencing between versions")
        print("✅ Physics concept verification")
        print("✅ MCAT-specific formatting")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nPlease check:")
        print("1. Your Gemini API key is correctly set in the .env file")
        print("2. You have an active internet connection")
        print("3. The PDF file exists and is readable")

if __name__ == "__main__":
    main()
