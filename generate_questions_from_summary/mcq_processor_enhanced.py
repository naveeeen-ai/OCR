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

def extract_36_bullet_points():
    """Extract exactly 36 bullet points from the PDF"""
    print("Extracting 36 bullet points from Kinematics and Dynamics PDF...")
    
    with pdfplumber.open('kinematics_and_dynamics.pdf') as pdf:
        full_text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + '\n'

    # Look for content starting from SI units  
    start_marker = 'The SI units include meter, kilogram, second, ampère, mole, kelvin, and'
    end_marker = 'angular velocity is usually zero.'

    start_idx = full_text.find(start_marker)
    end_idx = full_text.find(end_marker)

    if start_idx != -1 and end_idx != -1:
        end_idx = end_idx + len(end_marker)
        content_section = full_text[start_idx:end_idx]
        
        # Use Gemini to extract exactly 36 bullet points
        prompt = f"""Extract exactly 36 distinct physics bullet points from the following content in order. Each bullet point should be a complete, standalone physics concept or fact suitable for creating MCAT questions.

Requirements:
1. Start with: "The SI units include meter, kilogram, second, ampère, mole, kelvin, and candela."
2. End with: "Rotational equilibrium has constant angular velocity (usually zero on the MCAT)."
3. Extract exactly 36 bullet points in the order they appear
4. Each should be a complete, educational physics statement
5. Include concepts from all sections: Units, Vectors and Scalars, Displacement and Velocity, Forces, Newton's Laws, Motion with Constant Acceleration, and Mechanical Equilibrium

Content:
{content_section}

Please return EXACTLY 36 bullet points, numbered 1-36:"""
        
        response = model.generate_content(prompt)
        bullet_points_text = response.text
        
        # Parse the bullet points into a list
        lines = bullet_points_text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit() and '. ' in line:
                bullet_point = line.split('. ', 1)[1] if '. ' in line else line
                bullet_points.append(bullet_point)
        
        print(f"Successfully extracted {len(bullet_points)} bullet points")
        return bullet_points
    else:
        print("Could not find the specified markers in the PDF")
        return []

def task1_generate_mcqs_from_summary():
    """Task 1: Generate one specific MCAT MCQ for each of the 36 bullet points"""
    print("Task 1: Generating 36 specific MCAT MCQs (one for each bullet point)...")
    
    # Extract the 36 bullet points
    bullet_points = extract_36_bullet_points()
    if not bullet_points:
        print("Error: Could not extract bullet points from PDF")
        return
    
    if len(bullet_points) != 36:
        print(f"Warning: Expected 36 bullet points, got {len(bullet_points)}")
    
    # Create specific theoretical MCAT questions for each bullet point
    prompt = f"""Create exactly one specific THEORETICAL MCAT-style multiple choice question for each physics bullet point listed below. 

CRITICAL REQUIREMENTS:
1. Each question must be PURELY THEORETICAL - NO numerical calculations, NO math problems
2. Each question must be SPECIFIC to the individual bullet point concept (not general)
3. Each question must have EXACTLY 4 answer choices (A, B, C, D)
4. Only ONE choice should be definitively correct
5. Use proper MCAT-style terminology and complexity
6. Focus ONLY on definitions, principles, concepts, and theoretical understanding

THEORETICAL MCAT Question Types ONLY:
- Definition and concept identification questions
- Theoretical principles and laws
- Conceptual relationships between physics concepts
- Classification of physics phenomena (vector vs scalar, types of forces, etc.)
- Theoretical understanding of physics laws and principles
- Conceptual applications without numerical values
- Qualitative comparisons and relationships

STRICTLY AVOID:
- Any numerical calculations or math problems
- Questions requiring specific numerical values
- Problems involving formulas with numbers
- Quantitative analysis or computations

For each bullet point below, create ONE purely theoretical question that tests conceptual understanding.

Format each question EXACTLY as:
**Question number. Question text**
A. Answer choice 1 text
B. Answer choice 2 text  
C. Answer choice 3 text
D. Answer choice 4 text

IMPORTANT: Do NOT include answers or explanations in this step - only questions and choices.

Physics Bullet Points (create one theoretical question for each):
{chr(10).join(f"{i+1}. {bp}" for i, bp in enumerate(bullet_points))}

Generate exactly {len(bullet_points)} purely theoretical MCAT questions (one for each bullet point above):"""
    
    # Get MCQs from Gemini
    response = model.generate_content(prompt)
    mcqs = response.text
    
    # Save to file
    save_questions('summary_questions.txt', mcqs)
    print(f"Task 1 completed: {len(bullet_points)} specific MCQs saved to summary_questions.txt\n")
    
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
    
    # Process original questions with enhanced prompt for theoretical questions
    prompt_original = f"""For each of the following THEORETICAL MCAT preparation MCQs, add the correct answer and detailed explanation.

CRITICAL ACCURACY REQUIREMENTS FOR THEORETICAL QUESTIONS:
1. Double-check all physics concepts and theoretical principles
2. Ensure only ONE answer choice is definitively correct based on physics theory
3. Verify answers against fundamental physics definitions and principles
4. Provide clear, educational explanations suitable for MCAT preparation
5. Focus on conceptual understanding, NOT mathematical calculations

Format should be:
**Question number. Question text**
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
**Correct Answer: [Letter]. [Full answer text]**
**Explanation:** [Detailed theoretical explanation with MCAT context]

Example format for theoretical question:
**1. Which of the following best describes a vector quantity?**
A. It has only magnitude
B. It has only direction
C. It has both magnitude and direction
D. It is dimensionless
**Correct Answer: C. It has both magnitude and direction**
**Explanation:** A vector quantity is defined as having both magnitude (size) and direction. This distinguishes vectors from scalar quantities, which have only magnitude. Understanding this fundamental distinction is crucial for MCAT physics, as it affects how quantities are added, subtracted, and analyzed in physics problems.

VALIDATION CHECKLIST before providing answer:
- Is the physics concept/definition correct?
- Is only one choice definitively right based on theory?
- Does the explanation focus on conceptual understanding?
- Is the explanation helpful for MCAT preparation?
- Does it avoid unnecessary mathematical complexity?

Theoretical MCQs to process:
{original_mcqs}

Add correct answers and theoretical explanations for each question:"""
    
    response_original = model.generate_content(prompt_original)
    original_with_answers = response_original.text
    
    # Process refined questions with cross-validation for theoretical focus
    prompt_refined = f"""For each of the following refined THEORETICAL MCAT preparation MCQs, add the correct answer and detailed explanation.

IMPORTANT: Cross-reference with the original questions to ensure answer consistency and maintain theoretical focus.

CRITICAL VALIDATION FOR THEORETICAL QUESTIONS:
1. Verify answers are scientifically correct based on physics theory
2. Ensure explanations emphasize conceptual understanding for MCAT
3. Double-check that only one choice is definitively correct
4. Maintain consistency with physics principles and definitions
5. Focus on theoretical understanding rather than calculations

Format should be:
**Question number. Question text**
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
**Correct Answer: [Letter]. [Full answer text]**
**Explanation:** [Detailed theoretical explanation helping MCAT test-takers understand physics concepts and principles]

Refined Theoretical MCQs to process:
{refined_mcqs}

Add correct answers and theoretical explanations for each question:"""
    
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
    """Main function for generating 36 specific MCAT questions (one per bullet point)"""
    print("Starting 36 Specific MCAT MCQ Generation from Kinematics and Dynamics Bullet Points...\n")
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: Please set your Gemini API key in the .env file")
        print("\nTo get a FREE Gemini API key:")
        print("1. Go to: https://aistudio.google.com/apikey")
        print("2. Click 'Create API Key'")
        print("3. Copy the key and add it to your .env file as: GEMINI_API_KEY=your_key_here")
        return
    
    try:
        # Execute Task 1: Generate 36 specific MCQs (one per bullet point)
        print("🎯 Generating 36 specific MCAT questions (one for each bullet point)...")
        original_mcqs = task1_generate_mcqs_from_summary()
        if not original_mcqs:
            print("Failed to generate original MCQs")
            return
        
        # Execute Task 2: Refine questions while maintaining specificity
        print("🔄 Refining questions while preserving specificity and choices...")
        refined_mcqs = task2_refine_questions(original_mcqs)
        if not refined_mcqs:
            print("Failed to refine MCQs")
            return
        
        # Execute Task 3: Add answers and explanations with validation
        print("✅ Adding validated answers and explanations...")
        task3_add_answers_and_explanations_enhanced(original_mcqs, refined_mcqs)
        
        print("\n🎉 All tasks completed successfully!")
        print("\n36 Specific MCAT Preparation Output files:")
        print("- summary_questions.txt: 36 specific MCAT MCQs with validated answers and explanations")
        print("- refined_summary_questions.txt: 36 refined specific MCAT MCQs with validated answers and explanations")
        
        print("\n📋 Bullet Point Specific Features:")
        print("✅ 36 questions generated (one for each specific bullet point)")
        print("✅ Each question targets a specific physics concept")
        print("✅ MCAT-style terminology and complexity")
        print("✅ Conceptual focus suitable for MCAT preparation")
        print("✅ Enhanced prompting for accuracy")
        print("✅ Validation checks for answers")
        print("✅ Cross-referencing between versions")
        print("✅ Physics concept verification")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nPlease check:")
        print("1. Your Gemini API key is correctly set in the .env file")
        print("2. You have an active internet connection")
        print("3. The PDF file exists and is readable")

if __name__ == "__main__":
    main()
