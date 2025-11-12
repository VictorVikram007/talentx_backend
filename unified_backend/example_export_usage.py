#!/usr/bin/env python3
"""
Example: Using the Resume Export Service
Demonstrates how to export resumes to PDF, DOCX, and text formats
"""

import sys
from pathlib import Path
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.export_service import (
    export_resume_to_pdf,
    export_resume_to_docx,
    export_resume_to_text,
    export_resume,
    create_export_dir,
    generate_filename
)


# ============================================================================
# SAMPLE RESUME DATA
# ============================================================================

SAMPLE_RESUME = {
    "name": "Jane Smith",
    "email": "jane.smith@email.com",
    "phone": "+1-555-0123",
    "location": "San Francisco, CA",
    "summary": """Senior Software Engineer with 7+ years of experience building scalable 
    distributed systems and leading cross-functional teams. Expertise in cloud architecture, 
    microservices, and DevOps. Passionate about writing clean code and mentoring junior engineers.""",
    
    "skills": [
        "Python", "FastAPI", "Django", "Go", "Rust",
        "AWS", "GCP", "Kubernetes", "Docker", "Terraform",
        "PostgreSQL", "Redis", "MongoDB",
        "System Design", "Microservices", "DevOps",
        "Leadership", "Agile", "Git"
    ],
    
    "experience": [
        {
            "title": "Senior Software Engineer",
            "company": "TechCorp AI",
            "duration": "March 2021 - Present",
            "description": [
                "Led architecture and development of real-time data pipeline serving 10M+ events/day",
                "Designed and implemented microservices architecture using FastAPI and Kubernetes",
                "Mentored team of 3 junior engineers; improved code review process reducing bugs by 35%",
                "Optimized database queries and caching strategies, reducing API latency by 60%",
                "Managed infrastructure on AWS using Terraform and CloudFormation"
            ]
        },
        {
            "title": "Software Engineer II",
            "company": "DataSystems Inc",
            "duration": "July 2019 - February 2021",
            "description": [
                "Built and maintained REST API serving 5M requests/day with 99.9% uptime",
                "Implemented comprehensive monitoring and alerting using Prometheus and Grafana",
                "Reduced infrastructure costs by 40% through resource optimization",
                "Developed CI/CD pipelines using GitHub Actions and Jenkins"
            ]
        },
        {
            "title": "Software Engineer",
            "company": "StartupXYZ",
            "duration": "June 2017 - June 2019",
            "description": [
                "Developed full-stack features for Django-based web application",
                "Implemented real-time notifications using WebSockets and Redis",
                "Participated in code reviews and contributed to architectural decisions"
            ]
        }
    ],
    
    "education": [
        {
            "degree": "B.S.",
            "field": "Computer Science",
            "school": "UC Berkeley",
            "year": 2017
        },
        {
            "degree": "Certification",
            "field": "AWS Certified Solutions Architect",
            "school": "Amazon Web Services",
            "year": 2022
        }
    ],
    
    "achievements": [
        "Improved application performance by 60% through optimization and caching",
        "Led team that reduced technical debt by 45%",
        "Published 3 technical articles on system design",
        "Open source contributor to FastAPI and SQLAlchemy projects",
        "Speaker at 2 tech conferences"
    ],
    
    "ats_score": 92,
    "match_percentage": 88
}


# ============================================================================
# EXAMPLE 1: Export to PDF
# ============================================================================

def example_export_to_pdf():
    """Export resume to PDF format"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Export Resume to PDF")
    print("="*70)
    
    try:
        pdf_bytes = export_resume_to_pdf(SAMPLE_RESUME)
        print(f"✅ PDF generated successfully!")
        print(f"   File size: {len(pdf_bytes)} bytes ({len(pdf_bytes)/1024:.2f} KB)")
        
        # Save to file
        output_path = Path("data/exports") / "jane_smith_resume.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f"   Saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


# ============================================================================
# EXAMPLE 2: Export to DOCX
# ============================================================================

def example_export_to_docx():
    """Export resume to DOCX format"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Export Resume to DOCX")
    print("="*70)
    
    try:
        docx_bytes = export_resume_to_docx(SAMPLE_RESUME)
        print(f"✅ DOCX generated successfully!")
        print(f"   File size: {len(docx_bytes)} bytes ({len(docx_bytes)/1024:.2f} KB)")
        
        # Save to file
        output_path = Path("data/exports") / "jane_smith_resume.docx"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(docx_bytes)
        print(f"   Saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


# ============================================================================
# EXAMPLE 3: Export to Plain Text
# ============================================================================

def example_export_to_text():
    """Export resume to plain text format (ATS-friendly)"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Export Resume to Plain Text (ATS-Friendly)")
    print("="*70)
    
    try:
        text_content = export_resume_to_text(SAMPLE_RESUME)
        print(f"✅ Text version generated successfully!")
        print(f"   Content size: {len(text_content)} characters")
        print(f"   First 300 characters preview:")
        print("-" * 70)
        print(text_content[:300] + "...")
        print("-" * 70)
        
        # Save to file
        output_path = Path("data/exports") / "jane_smith_resume.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        print(f"   Saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


# ============================================================================
# EXAMPLE 4: Export All Formats at Once
# ============================================================================

def example_export_all():
    """Export resume in all formats"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Export Resume in ALL Formats")
    print("="*70)
    
    try:
        result = export_resume(SAMPLE_RESUME, export_format="all", output_dir="data/exports")
        
        print(f"✅ All formats exported successfully!")
        print(f"   Timestamp: {result['timestamp']}")
        print(f"\n   Generated formats:")
        
        for format_name, format_info in result['formats'].items():
            status = "✅" if format_info.get('generated') else "❌"
            size = format_info.get('size_bytes', 'N/A')
            print(f"   {status} {format_name.upper()}")
            if isinstance(size, int):
                print(f"      Size: {size} bytes ({size/1024:.2f} KB)")
            if 'filepath' in format_info:
                print(f"      Path: {format_info['filepath']}")
            if 'error' in format_info:
                print(f"      Error: {format_info['error']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


# ============================================================================
# EXAMPLE 5: Working with Minimal Resume Data
# ============================================================================

def example_minimal_resume():
    """Example with minimal resume data"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Export Minimal Resume Data")
    print("="*70)
    
    minimal_resume = {
        "name": "Bob Johnson",
        "email": "bob@example.com",
        "phone": "+1-555-0456",
        "summary": "Software Developer with 3 years of experience",
        "skills": ["Python", "JavaScript", "React", "FastAPI"],
        "experience": [
            {
                "title": "Python Developer",
                "company": "WebDev Co",
                "duration": "2021-Present",
                "description": "Build web applications using FastAPI and React"
            }
        ],
        "education": [
            {
                "degree": "B.S.",
                "field": "Information Technology",
                "school": "Tech University",
                "year": 2021
            }
        ]
    }
    
    try:
        result = export_resume(minimal_resume, export_format="all", output_dir="data/exports")
        print(f"✅ Minimal resume exported successfully!")
        print(f"   Total formats generated: {len([f for f in result['formats'].values() if f.get('generated')])}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


# ============================================================================
# EXAMPLE 6: Using Export Service with API Response
# ============================================================================

def example_with_ats_scoring():
    """Example showing export with ATS scoring"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Export Resume with ATS Scoring")
    print("="*70)
    
    resume_with_score = {
        **SAMPLE_RESUME,
        "ats_score": 87,
        "match_percentage": 92
    }
    
    try:
        # Export all formats
        result = export_resume(resume_with_score, export_format="all", output_dir="data/exports")
        
        print(f"✅ Resume with ATS scoring exported!")
        print(f"   ATS Score: {resume_with_score['ats_score']}/100")
        print(f"   Job Match: {resume_with_score['match_percentage']}%")
        print(f"   Formats: {', '.join([k for k, v in result['formats'].items() if v.get('generated')])}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all examples"""
    print("\n" + "█"*70)
    print("  TALENTX RESUME EXPORT SERVICE - EXAMPLES")
    print("█"*70)
    
    # Create exports directory
    export_dir = create_export_dir("data/exports")
    print(f"\n📁 Export directory: {export_dir}")
    
    # Run all examples
    example_export_to_pdf()
    example_export_to_docx()
    example_export_to_text()
    example_export_all()
    example_minimal_resume()
    example_with_ats_scoring()
    
    print("\n" + "█"*70)
    print("  ALL EXAMPLES COMPLETED ✅")
    print("█"*70)
    print("\n📌 Summary:")
    print("   • PDF Export: Professional formatted resume")
    print("   • DOCX Export: Editable in Microsoft Word")
    print("   • Text Export: ATS-friendly plain text version")
    print("   • All Formats: Generate all 3 at once")
    print("\n💡 Use Cases:")
    print("   • Download for job applications")
    print("   • Submit to ATS systems")
    print("   • Share with recruiters")
    print("   • Print to physical copy")
    print("\n📂 Check 'data/exports' folder for generated files")
    print()


if __name__ == "__main__":
    main()
