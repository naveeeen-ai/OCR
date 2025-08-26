import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')  # Free model with good performance

def read_file(filename):
    """Read content from a file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filename, content):
    """Write content to a file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def task1_format_mcqs():
    """Task 1: Format MCQs with proper numbering"""
    print("Task 1: Formatting MCQs...")
    
    # Read the content
    content = read_file('output.txt')
    
    # Create prompt for formatting
    prompt = f"""Please correct and format the following MCQs in a proper format with clear question numbers. 
    Make sure each question is properly numbered sequentially, and fix any formatting issues.
    Keep the original questions and choices intact, just improve the formatting and numbering.
    
    Content to format:
    {content}
    
    Output the formatted MCQs:"""
    
    # Get formatted output from Gemini
    response = model.generate_content(prompt)
    formatted_content = response.text
    
    # Replace the content in output.txt
    write_file('output.txt', formatted_content)
    print("Task 1 completed: output.txt has been updated with formatted MCQs.\n")
    
    return formatted_content

def task2_generate_formatted_output(formatted_content):
    """Task 2: Generate complete formatted output with answers and explanations"""
    print("Task 2: Generating formatted output with answers and explanations...")
    
    # Create prompt for complete formatting
    prompt = f"""For each MCQ below, reformat it in the exact following structure:

Question text
A. Answer choice 1 text
B. Answer choice 2 text
C. Answer choice 3 text
D. Answer choice 4 text
Correct Answer text
Explanation


For each question, you need to:
1. Extract the question text (without the question number)
2. List each answer choice on a separate line with A., B., C., D. prefixes
3. Provide the correct answer choice text (not just the letter)
4. Provide a detailed explanation

Example format:
If the amount of acetylcholinesterase, an enzyme that breaks down acetylcholine, is increased, which of the following would likely be the result?
A. Weakness of muscle movements
B. Excessive pain or discomfort
C. Mood swings and mood instability
D. Auditory and visual hallucinations
Weakness of muscle movements
Acetylcholine is a neurotransmitter crucial for muscle contraction. Acetylcholinesterase breaks it down, terminating the signal. Increased acetylcholinesterase would lead to quicker breakdown of acetylcholine, resulting in weaker muscle contractions and ultimately, weakness of muscle movements.


MCQs to format:
{formatted_content}

Format each question exactly as shown above:"""
    
    # Get formatted output from Gemini
    response = model.generate_content(prompt)
    formatted_output = response.text
    
    # Save formatted output to a new file
    write_file('mcq_formatted_final.txt', formatted_output)
    print("Task 2 completed: Formatted output saved to mcq_formatted_final.txt\n")
    
    return formatted_output

def task3_refine_questions(formatted_content):
    """Task 3: Refine questions while keeping choices unchanged"""
    print("Task 3: Refining questions...")
    
    # Create prompt for refining
    prompt = f"""Refine each question below to make it clearer and more professional while maintaining the same meaning.
    IMPORTANT: Keep all the answer choices (A, B, C, D) EXACTLY as they are - only refine the questions themselves.
    
    Example transformation:
    Original: "The Chlorophyll cells within the plant leaves are perfectly optimized to absorb which of the following waves of the Sun Light?"
    Refined: "Which wavelengths of sunlight are the chlorophyll cells in plant leaves most effectively designed to capture?"
    
    MCQs to refine:
    {formatted_content}
    
    Output the refined MCQs with improved questions but unchanged choices:"""
    
    # Get refined questions from Gemini
    response = model.generate_content(prompt)
    refined_content = response.text
    
    # Save refined questions to a new file
    write_file('mcq_refined.txt', refined_content)
    print("Task 3 completed: Refined questions saved to mcq_refined.txt\n")
    
    return refined_content

def main():
    """Main function to execute all three tasks"""
    print("Starting MCQ Processing with Gemini...\n")
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_gemini_api_key_here":
        print("ERROR: Please set your Gemini API key in the .env file")
        print("\nTo get a FREE Gemini API key:")
        print("1. Go to: https://aistudio.google.com/apikey")
        print("2. Click 'Create API Key'")
        print("3. Copy the key and add it to your .env file as: GEMINI_API_KEY=your_key_here")
        return
    
    try:
        # Execute Task 1
        formatted_content = task1_format_mcqs()
        
        # Execute Task 2
        task2_generate_formatted_output(formatted_content)
        
        # Execute Task 3
        task3_refine_questions(formatted_content)
        
        print("All tasks completed successfully!")
        print("\nOutput files:")
        print("- output.txt: Formatted MCQs (Task 1)")
        print("- mcq_formatted_final.txt: Formatted output with answers and explanations (Task 2)")
        print("- mcq_refined.txt: Refined questions with original choices (Task 3)")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nPlease check:")
        print("1. Your Gemini API key is correctly set in the .env file")
        print("2. You have an active internet connection")
        print("3. If you see quota errors, wait a minute and try again (free tier has rate limits)")

if __name__ == "__main__":
    main()
