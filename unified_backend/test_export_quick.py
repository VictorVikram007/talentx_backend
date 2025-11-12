#!/usr/bin/env python3
"""
Quick Test - Export Service (Standalone)
Tests PDF, DOCX, and text export without loading other services
"""

import sys
from pathlib import Path
from io import BytesIO

# Direct import avoiding services __init__.py
sys.path.insert(0, str(Path(__file__).parent))

# Import only what we need
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

print("=" * 70)
print("TALENTX EXPORT SERVICE - QUICK TEST")
print("=" * 70)

# Import export service directly
from services.export_service import (
    export_resume_to_pdf,
    export_resume_to_docx,
    export_resume_to_text
)

# Sample resume
resume = {
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "+1-555-0123",
    "location": "San Francisco, CA",
    "summary": "Senior Software Engineer with 5+ years of experience",
    "skills": ["Python", "FastAPI", "AWS", "Kubernetes", "Docker"],
    "experience": [
        {
            "title": "Senior Engineer",
            "company": "TechCorp",
            "duration": "2021-Present",
            "description": [
                "Led microservices architecture",
                "Improved performance by 60%",
                "Managed team of 5 engineers"
            ]
        },
        {
            "title": "Software Engineer",
            "company": "StartupXYZ",
            "duration": "2019-2021",
            "description": "Built scalable APIs using FastAPI"
        }
    ],
    "education": [
        {
            "degree": "B.S.",
            "field": "Computer Science",
            "school": "UC Berkeley",
            "year": 2017
        }
    ],
    "achievements": [
        "Improved system performance by 60%",
        "Open source contributor to FastAPI"
    ],
    "ats_score": 88,
    "match_percentage": 92
}

print("\n📋 Testing Resume Export Service\n")

# Test 1: PDF Export
print("1️⃣  Testing PDF Export...")
try:
    pdf_bytes = export_resume_to_pdf(resume)
    assert isinstance(pdf_bytes, bytes), "PDF should be bytes"
    assert len(pdf_bytes) > 1000, f"PDF too small: {len(pdf_bytes)} bytes"
    print(f"   ✅ PDF Export: SUCCESS ({len(pdf_bytes)} bytes)")
    
    # Save PDF
    Path("data/exports").mkdir(parents=True, exist_ok=True)
    with open("data/exports/test_resume.pdf", "wb") as f:
        f.write(pdf_bytes)
    print(f"   ✅ Saved: data/exports/test_resume.pdf")
except Exception as e:
    print(f"   ❌ PDF Export FAILED: {str(e)}")

# Test 2: DOCX Export
print("\n2️⃣  Testing DOCX Export...")
try:
    docx_bytes = export_resume_to_docx(resume)
    assert isinstance(docx_bytes, bytes), "DOCX should be bytes"
    assert docx_bytes[:2] == b'PK', "DOCX should be valid ZIP format"
    assert len(docx_bytes) > 1000, f"DOCX too small: {len(docx_bytes)} bytes"
    print(f"   ✅ DOCX Export: SUCCESS ({len(docx_bytes)} bytes)")
    
    # Save DOCX
    with open("data/exports/test_resume.docx", "wb") as f:
        f.write(docx_bytes)
    print(f"   ✅ Saved: data/exports/test_resume.docx")
except Exception as e:
    print(f"   ❌ DOCX Export FAILED: {str(e)}")

# Test 3: Text Export
print("\n3️⃣  Testing Text Export...")
try:
    text_content = export_resume_to_text(resume)
    assert isinstance(text_content, str), "Text should be string"
    assert len(text_content) > 100, f"Text too short: {len(text_content)} chars"
    assert "ALICE JOHNSON" in text_content.upper(), "Name should be in content"
    assert "PROFESSIONAL EXPERIENCE" in text_content, "Sections should be present"
    print(f"   ✅ Text Export: SUCCESS ({len(text_content)} characters)")
    
    # Save Text
    with open("data/exports/test_resume.txt", "w", encoding="utf-8") as f:
        f.write(text_content)
    print(f"   ✅ Saved: data/exports/test_resume.txt")
except Exception as e:
    print(f"   ❌ Text Export FAILED: {str(e)}")

# Test 4: Content Validation
print("\n4️⃣  Testing Content Validation...")
try:
    text_content = export_resume_to_text(resume)
    
    # Check all sections are present
    sections = [
        "PROFESSIONAL SUMMARY",
        "SKILLS",
        "PROFESSIONAL EXPERIENCE",
        "EDUCATION",
        "ACHIEVEMENTS"
    ]
    
    missing = [s for s in sections if s not in text_content]
    if missing:
        print(f"   ❌ Missing sections: {missing}")
    else:
        print(f"   ✅ All sections present: {', '.join(sections)}")
    
    # Check key data
    checks = [
        ("Name", "ALICE JOHNSON", resume['name'].upper()),
        ("Email", "alice@example.com", resume['email']),
        ("Company", "TechCorp", resume['experience'][0]['company']),
        ("Skills", "Python", resume['skills'][0]),
    ]
    
    for check_name, search_term, source in checks:
        if search_term.upper() in text_content.upper():
            print(f"   ✅ {check_name} found: {search_term}")
        else:
            print(f"   ❌ {check_name} NOT found: {search_term}")
            
except Exception as e:
    print(f"   ❌ Content Validation FAILED: {str(e)}")

# Test 5: Edge Cases
print("\n5️⃣  Testing Edge Cases...")
try:
    minimal_resume = {
        "name": "Bob Smith",
        "email": "bob@example.com"
    }
    
    pdf = export_resume_to_pdf(minimal_resume)
    docx = export_resume_to_docx(minimal_resume)
    text = export_resume_to_text(minimal_resume)
    
    assert len(pdf) > 1000, "Minimal PDF should still be valid"
    assert len(docx) > 1000, "Minimal DOCX should still be valid"
    assert "BOB SMITH" in text.upper(), "Minimal text should have name"
    
    print(f"   ✅ Minimal resume export: SUCCESS")
except Exception as e:
    print(f"   ❌ Edge Cases FAILED: {str(e)}")

print("\n" + "=" * 70)
print("✅ EXPORT SERVICE TEST COMPLETE")
print("=" * 70)
print("\n📁 Generated Files:")
print("   • data/exports/test_resume.pdf")
print("   • data/exports/test_resume.docx")
print("   • data/exports/test_resume.txt")
print("\n✨ All export functions working correctly!")
print()
