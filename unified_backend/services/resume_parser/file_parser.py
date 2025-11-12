"""
File Parser Module for Extracting Text from Resumes

Supports:
- PDF files (using PyMuPDF/fitz)
- DOCX files (using docx2txt)
- TXT files (using built-in open())

The extract_text_from_file() function detects file type by extension
and returns clean, combined text content.
"""

import fitz  # PyMuPDF
import docx2txt
from pathlib import Path


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text content from a file based on its extension.
    
    Args:
        file_path (str): Path to the file to extract text from
        
    Returns:
        str: Extracted text content from the file
        
    Raises:
        ValueError: If file type is not supported
        FileNotFoundError: If file does not exist
    """
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get file extension
    file_extension = file_path.suffix.lower()
    
    try:
        if file_extension == ".pdf":
            return _extract_from_pdf(str(file_path))
        elif file_extension == ".docx":
            return _extract_from_docx(str(file_path))
        elif file_extension == ".txt":
            return _extract_from_txt(str(file_path))
        else:
            raise ValueError(
                f"Unsupported file type: {file_extension}. "
                f"Supported types: .pdf, .docx, .txt"
            )
    except Exception as e:
        raise Exception(f"Error extracting text from {file_extension} file: {str(e)}")


def _extract_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF (fitz).
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    text = ""
    try:
        pdf_document = fitz.open(file_path)
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text()
        
        pdf_document.close()
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def _extract_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file using docx2txt.
    
    Args:
        file_path (str): Path to the DOCX file
        
    Returns:
        str: Extracted text from the DOCX
    """
    try:
        text = docx2txt.process(file_path)
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")


def _extract_from_txt(file_path: str) -> str:
    """
    Extract text from a TXT file using built-in open().
    
    Args:
        file_path (str): Path to the TXT file
        
    Returns:
        str: Text content from the TXT file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text.strip()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to read TXT file with different encodings: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to extract text from TXT: {str(e)}")


def get_text_preview(text: str, max_length: int = 300) -> str:
    """
    Get a preview of the extracted text (first N characters).
    
    Args:
        text (str): Full text content
        max_length (int): Maximum length of preview (default: 300)
        
    Returns:
        str: Preview of the text (truncated if necessary)
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def get_text_summary(text: str) -> dict:
    """
    Get summary statistics about extracted text.
    
    Args:
        text (str): Extracted text content
        
    Returns:
        dict: Summary with word count, character count, and line count
    """
    lines = text.split('\n')
    words = text.split()
    
    return {
        "character_count": len(text),
        "word_count": len(words),
        "line_count": len(lines),
        "avg_line_length": len(text) // len(lines) if lines else 0
    }
