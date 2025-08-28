import pdfplumber
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_36_bullet_points():
    print('Extracting PDF content to identify the 36 bullet points...')
    
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
        print(f'Found relevant section! Length: {len(content_section)} characters')
        
        # Use Gemini to extract exactly 36 bullet points
        prompt = f"""Extract exactly 36 distinct physics bullet points from the following content in order. Each bullet point should be a complete, standalone physics concept or fact suitable for creating MCAT questions.

Requirements:
1. Start with: "The SI units include meter, kilogram, second, ampère, mole, kelvin, and candela."
2. End with: "Rotational equilibrium occurs in the absence of any net torques acting on an object. Rotational motion may consider any pivot point, but the center of mass is most common. An object in rotational equilibrium has a constant angular velocity; on the MCAT, the angular velocity is usually zero."
3. Extract exactly 36 bullet points in the order they appear
4. Each should be a complete, educational physics statement
5. Include concepts from all sections: Units, Vectors and Scalars, Displacement and Velocity, Forces, Newton's Laws, Motion with Constant Acceleration, and Mechanical Equilibrium

Content:
{content_section}

Please return EXACTLY 36 bullet points, numbered 1-36:"""
        
        response = model.generate_content(prompt)
        bullet_points_text = response.text
        
        print('Generated bullet points:')
        print(bullet_points_text[:500] + '...')
        
        # Save the bullet points for review
        with open('extracted_bullet_points.txt', 'w', encoding='utf-8') as f:
            f.write(bullet_points_text)
        print('\nSaved bullet points to extracted_bullet_points.txt')
        
        # Parse the bullet points into a list
        lines = bullet_points_text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit() and '. ' in line:
                bullet_point = line.split('. ', 1)[1] if '. ' in line else line
                bullet_points.append(bullet_point)
        
        print(f'\nExtracted {len(bullet_points)} bullet points')
        return bullet_points
    else:
        print('Could not find the specified markers in the PDF')
        return []

if __name__ == "__main__":
    bullet_points = extract_36_bullet_points()
    if bullet_points:
        print(f'\nFirst 3 bullet points:')
        for i, bp in enumerate(bullet_points[:3], 1):
            print(f'{i}. {bp}')
        print(f'\nLast 3 bullet points:')
        for i, bp in enumerate(bullet_points[-3:], len(bullet_points)-2):
            print(f'{i}. {bp}')
