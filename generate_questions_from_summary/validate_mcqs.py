#!/usr/bin/env python3
"""
Quick MCQ Validation Script
Checks for common errors in generated MCQ files
"""

import re
import sys

def extract_questions_and_answers(file_path):
    """Extract questions and answers from MCQ file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []
    
    # Pattern to match questions with answers
    pattern = r'\*\*(\d+)\.\s*([^*]+?)\*\*\n(.*?)\*\*Correct Answer:\s*([^*]+?)\*\*'
    matches = re.findall(pattern, content, re.DOTALL)
    
    questions = []
    for match in matches:
        question_num, question_text, options_section, answer = match
        
        # Extract individual options
        option_pattern = r'([A-D])\.\s*([^\n]+)'
        options = re.findall(option_pattern, options_section)
        
        questions.append({
            'number': int(question_num),
            'question': question_text.strip(),
            'options': dict(options),
            'answer': answer.strip(),
            'options_section': options_section
        })
    
    return questions

def validate_mcq_file(file_path):
    """Validate MCQ file for common errors"""
    print(f"\n🔍 Validating: {file_path}")
    print("=" * 50)
    
    questions = extract_questions_and_answers(file_path)
    
    if not questions:
        print("❌ No questions found or parsing error")
        return False
    
    errors = []
    warnings = []
    
    for q in questions:
        question_num = q['number']
        options = q['options']
        answer = q['answer']
        
        # Check 1: Ensure all 4 options exist
        expected_options = {'A', 'B', 'C', 'D'}
        actual_options = set(options.keys())
        
        if actual_options != expected_options:
            missing = expected_options - actual_options
            extra = actual_options - expected_options
            if missing:
                errors.append(f"Q{question_num}: Missing options: {missing}")
            if extra:
                warnings.append(f"Q{question_num}: Extra options: {extra}")
        
        # Check 2: Answer format validation
        if not answer:
            errors.append(f"Q{question_num}: Empty answer")
        
        # Check 3: Answer letter validation
        answer_letter = answer[0].upper() if answer else ""
        if answer_letter not in ['A', 'B', 'C', 'D']:
            errors.append(f"Q{question_num}: Invalid answer letter '{answer_letter}'")
        
        # Check 4: Answer consistency (letter matches option)
        if answer_letter in options:
            answer_text = answer[2:].strip() if len(answer) > 2 else ""  # Remove "A. " part
            option_text = options[answer_letter].strip()
            
            # Basic similarity check (first 20 characters)
            if answer_text[:20].lower() != option_text[:20].lower() and answer_text and option_text:
                warnings.append(f"Q{question_num}: Answer text mismatch with option {answer_letter}")
    
    # Report results
    print(f"📊 Found {len(questions)} questions")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"   • {error}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   • {warning}")
    
    if not errors and not warnings:
        print("✅ All validations passed!")
    
    return len(errors) == 0

def compare_files(file1, file2):
    """Compare answers between two MCQ files"""
    print(f"\n🔄 Comparing answers between files:")
    print(f"   File 1: {file1}")
    print(f"   File 2: {file2}")
    print("=" * 50)
    
    questions1 = extract_questions_and_answers(file1)
    questions2 = extract_questions_and_answers(file2)
    
    if len(questions1) != len(questions2):
        print(f"❌ Different number of questions: {len(questions1)} vs {len(questions2)}")
        return False
    
    mismatches = []
    
    for q1, q2 in zip(questions1, questions2):
        if q1['number'] != q2['number']:
            print(f"❌ Question numbering mismatch: {q1['number']} vs {q2['number']}")
            continue
        
        # Extract answer letters
        answer1_letter = q1['answer'][0].upper() if q1['answer'] else ""
        answer2_letter = q2['answer'][0].upper() if q2['answer'] else ""
        
        if answer1_letter != answer2_letter:
            mismatches.append({
                'question': q1['number'],
                'file1_answer': answer1_letter,
                'file2_answer': answer2_letter,
                'file1_text': q1['answer'],
                'file2_text': q2['answer']
            })
    
    if mismatches:
        print(f"❌ ANSWER MISMATCHES ({len(mismatches)}):")
        for mismatch in mismatches:
            print(f"   • Q{mismatch['question']}: {mismatch['file1_answer']} vs {mismatch['file2_answer']}")
            print(f"     File 1: {mismatch['file1_text']}")
            print(f"     File 2: {mismatch['file2_text']}")
            print()
    else:
        print("✅ All answers match between files!")
    
    return len(mismatches) == 0

def main():
    """Main validation function"""
    print("🔍 MCQ Validation Tool")
    print("=" * 50)
    
    # Validate individual files
    file1_valid = validate_mcq_file('summary_questions.txt')
    file2_valid = validate_mcq_file('refined_summary_questions.txt')
    
    # Compare files
    files_match = compare_files('summary_questions.txt', 'refined_summary_questions.txt')
    
    # Final summary
    print("\n📋 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Original file valid: {'✅' if file1_valid else '❌'}")
    print(f"Refined file valid: {'✅' if file2_valid else '❌'}")
    print(f"Answers consistent: {'✅' if files_match else '❌'}")
    
    if file1_valid and file2_valid and files_match:
        print("\n🎉 All validations passed! MCQs are ready for use.")
        return 0
    else:
        print("\n⚠️  Some issues found. Please review and fix before using.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
