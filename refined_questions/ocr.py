from pdf2image import convert_from_path
import pytesseract
import os

# Convert PDF to images (using system PATH)
pdf_path = "test.pdf"
images = convert_from_path(pdf_path)

extracted_text = ""
for image in images:
    text = pytesseract.image_to_string(image)
    extracted_text += text + "\n"

with open("output.txt", "w", encoding="utf-8") as text_file:
    text_file.write(extracted_text)
print(extracted_text)