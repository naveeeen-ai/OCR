import os
import pdfplumber
from dotenv import load_dotenv
import google.generativeai as genai

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

def task1_generate_mcqs_from_summary():
    """Task 1: Generate MCQs from PDF summary"""
    print("Task 1: Generating MCQs from Kinematics and Dynamics summary...")
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf('kinematics_and_dynamics.pdf')
    if not pdf_text:
        print("Error: Could not extract text from PDF")
        return
    
    # Create prompt for generating MCQs
    prompt = f"""Based on the following physics summary about Kinematics and Dynamics, generate 15 comprehensive multiple-choice questions (MCQs) for MCAT exam preparation. 

Make sure to cover various topics from the summary including:
- Kinematics concepts (displacement, velocity, acceleration, motion equations)
- Dynamics concepts (forces, Newton's laws, momentum, energy)
- Mathematical relationships and formulas
- Real-world applications and examples
- MCAT-style problem-solving scenarios

For each question, provide:
1. A clear, educational question suitable for MCAT preparation
2. Four answer choices (A, B, C, D)
3. Make sure only one choice is clearly correct
4. Include both conceptual and calculation-based questions typical of MCAT physics
5. Focus on critical thinking and application skills required for MCAT

Format each question as:
Question text
A. Answer choice 1 text
B. Answer choice 2 text  
C. Answer choice 3 text
D. Answer choice 4 text


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
    
    # Get refined questions from Gemini
    response = model.generate_content(prompt)
    refined_mcqs = response.text
    
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
    
    response_original = model.generate_content(prompt_original)
    original_with_answers = response_original.text
    
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
    
    response_refined = model.generate_content(prompt_refined)
    refined_with_answers = response_refined.text
    
    # Save updated files
    save_questions('summary_questions.txt', original_with_answers)
    save_questions('refined_summary_questions.txt', refined_with_answers)
    
    print("Task 3 completed: Answers and explanations added to both files\n")
    
    return original_with_answers, refined_with_answers

def main():
    """Main function to execute all tasks"""
    print("Starting MCAT MCQ Generation from Kinematics and Dynamics Summary...\n")
    
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
        original_mcqs = task1_generate_mcqs_from_summary()
        if not original_mcqs:
            print("Failed to generate original MCQs")
            return
        
        # Execute Task 2: Refine questions
        refined_mcqs = task2_refine_questions(original_mcqs)
        if not refined_mcqs:
            print("Failed to refine MCQs")
            return
        
        # Execute Task 3: Add answers and explanations
        task3_add_answers_and_explanations(original_mcqs, refined_mcqs)
        
        print("All tasks completed successfully!")
        print("\nMCAT Preparation Output files:")
        print("- summary_questions.txt: Original MCAT MCQs with answers and explanations")
        print("- refined_summary_questions.txt: Refined MCAT MCQs with answers and explanations")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nPlease check:")
        print("1. Your Gemini API key is correctly set in the .env file")
        print("2. You have an active internet connection")
        print("3. The PDF file exists and is readable")

if __name__ == "__main__":
    main()
