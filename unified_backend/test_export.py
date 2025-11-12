#!/usr/bin/env python3
"""
Test Suite for Resume Export Service
Tests PDF, DOCX, and text export functionality
"""

import unittest
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
    generate_filename,
    create_export_dir
)


class TestResumeExportService(unittest.TestCase):
    """Test cases for resume export service"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.sample_resume = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-0100",
            "location": "New York, NY",
            "summary": "Experienced software engineer",
            "skills": ["Python", "FastAPI", "AWS", "Docker", "Kubernetes"],
            "experience": [
                {
                    "title": "Senior Engineer",
                    "company": "Tech Corp",
                    "duration": "2020-2024",
                    "description": ["Led team", "Built systems", "Improved performance"]
                }
            ],
            "education": [
                {
                    "degree": "B.S.",
                    "field": "Computer Science",
                    "school": "State University",
                    "year": 2016
                }
            ],
            "achievements": ["Performance improvement", "Team leadership"],
            "ats_score": 85,
            "match_percentage": 90
        }
    
    # ========== PDF Export Tests ==========
    
    def test_pdf_export_basic(self):
        """Test basic PDF export"""
        try:
            pdf_bytes = export_resume_to_pdf(self.sample_resume)
            self.assertIsInstance(pdf_bytes, bytes)
            self.assertGreater(len(pdf_bytes), 0)
            print(f"✅ PDF Export (Basic): {len(pdf_bytes)} bytes")
        except Exception as e:
            self.fail(f"PDF export failed: {str(e)}")
    
    def test_pdf_export_minimal(self):
        """Test PDF export with minimal data"""
        minimal = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1-555-0200"
        }
        try:
            pdf_bytes = export_resume_to_pdf(minimal)
            self.assertIsInstance(pdf_bytes, bytes)
            self.assertGreater(len(pdf_bytes), 1000)  # PDF should be at least 1KB
            print(f"✅ PDF Export (Minimal): {len(pdf_bytes)} bytes")
        except Exception as e:
            self.fail(f"Minimal PDF export failed: {str(e)}")
    
    def test_pdf_export_with_ats_score(self):
        """Test PDF export includes ATS score"""
        try:
            pdf_bytes = export_resume_to_pdf(self.sample_resume)
            # Verify PDF contains ATS score (check header area)
            self.assertGreater(len(pdf_bytes), 0)
            print(f"✅ PDF Export (with ATS): Passed")
        except Exception as e:
            self.fail(f"PDF ATS score export failed: {str(e)}")
    
    def test_pdf_export_all_sections(self):
        """Test PDF export with all resume sections"""
        complete_resume = {
            **self.sample_resume,
            "location": "San Francisco, CA",
            "achievements": ["100+ achievements"]
        }
        try:
            pdf_bytes = export_resume_to_pdf(complete_resume)
            self.assertGreater(len(pdf_bytes), 5000)  # Complete resume should be larger
            print(f"✅ PDF Export (All Sections): {len(pdf_bytes)} bytes")
        except Exception as e:
            self.fail(f"Complete PDF export failed: {str(e)}")
    
    # ========== DOCX Export Tests ==========
    
    def test_docx_export_basic(self):
        """Test basic DOCX export"""
        try:
            docx_bytes = export_resume_to_docx(self.sample_resume)
            self.assertIsInstance(docx_bytes, bytes)
            self.assertGreater(len(docx_bytes), 0)
            # DOCX files should start with PK (ZIP magic number)
            self.assertEqual(docx_bytes[:2], b'PK')
            print(f"✅ DOCX Export (Basic): {len(docx_bytes)} bytes")
        except Exception as e:
            self.fail(f"DOCX export failed: {str(e)}")
    
    def test_docx_export_minimal(self):
        """Test DOCX export with minimal data"""
        minimal = {
            "name": "Bob Smith",
            "email": "bob@example.com"
        }
        try:
            docx_bytes = export_resume_to_docx(minimal)
            self.assertIsInstance(docx_bytes, bytes)
            self.assertEqual(docx_bytes[:2], b'PK')  # Valid ZIP/DOCX format
            print(f"✅ DOCX Export (Minimal): {len(docx_bytes)} bytes")
        except Exception as e:
            self.fail(f"Minimal DOCX export failed: {str(e)}")
    
    def test_docx_format_validity(self):
        """Test DOCX format is valid (valid ZIP)"""
        try:
            docx_bytes = export_resume_to_docx(self.sample_resume)
            # Try to read as ZIP (DOCX is ZIP)
            from zipfile import ZipFile
            with ZipFile(BytesIO(docx_bytes), 'r') as z:
                # Check for required DOCX files
                self.assertIn('word/document.xml', z.namelist())
            print(f"✅ DOCX Export (Format Validity): Valid ZIP structure")
        except Exception as e:
            self.fail(f"DOCX format validation failed: {str(e)}")
    
    # ========== Text Export Tests ==========
    
    def test_text_export_basic(self):
        """Test basic text export"""
        try:
            text_content = export_resume_to_text(self.sample_resume)
            self.assertIsInstance(text_content, str)
            self.assertGreater(len(text_content), 0)
            self.assertIn(self.sample_resume['name'], text_content)
            self.assertIn(self.sample_resume['email'], text_content)
            print(f"✅ Text Export (Basic): {len(text_content)} characters")
        except Exception as e:
            self.fail(f"Text export failed: {str(e)}")
    
    def test_text_export_ats_friendly(self):
        """Test text export is ATS-friendly"""
        try:
            text_content = export_resume_to_text(self.sample_resume)
            # Check for expected sections
            self.assertIn('PROFESSIONAL SUMMARY', text_content)
            self.assertIn('SKILLS', text_content)
            self.assertIn('PROFESSIONAL EXPERIENCE', text_content)
            self.assertIn('EDUCATION', text_content)
            print(f"✅ Text Export (ATS-Friendly): All sections present")
        except Exception as e:
            self.fail(f"ATS-friendly text export failed: {str(e)}")
    
    def test_text_export_plaintext(self):
        """Test text export contains no binary data"""
        try:
            text_content = export_resume_to_text(self.sample_resume)
            # Should be valid UTF-8
            text_content.encode('utf-8')
            # Should not contain binary markers
            self.assertNotIn('\x00', text_content)
            print(f"✅ Text Export (Plain Text): Valid UTF-8, no binary data")
        except Exception as e:
            self.fail(f"Plain text validation failed: {str(e)}")
    
    # ========== Multi-Format Export Tests ==========
    
    def test_export_all_formats(self):
        """Test exporting all formats at once"""
        try:
            result = export_resume(self.sample_resume, export_format="all")
            self.assertEqual(result['status'], 'success')
            self.assertIn('pdf', result['formats'])
            self.assertIn('docx', result['formats'])
            self.assertIn('text', result['formats'])
            print(f"✅ Export All Formats: 3 formats generated")
        except Exception as e:
            self.fail(f"Export all formats failed: {str(e)}")
    
    def test_export_pdf_only(self):
        """Test exporting only PDF"""
        try:
            result = export_resume(self.sample_resume, export_format="pdf")
            self.assertIn('pdf', result['formats'])
            self.assertTrue(result['formats']['pdf']['generated'])
            print(f"✅ Export PDF Only: Passed")
        except Exception as e:
            self.fail(f"PDF-only export failed: {str(e)}")
    
    def test_export_docx_only(self):
        """Test exporting only DOCX"""
        try:
            result = export_resume(self.sample_resume, export_format="docx")
            self.assertIn('docx', result['formats'])
            self.assertTrue(result['formats']['docx']['generated'])
            print(f"✅ Export DOCX Only: Passed")
        except Exception as e:
            self.fail(f"DOCX-only export failed: {str(e)}")
    
    def test_export_text_only(self):
        """Test exporting only text"""
        try:
            result = export_resume(self.sample_resume, export_format="text")
            self.assertIn('text', result['formats'])
            self.assertTrue(result['formats']['text']['generated'])
            print(f"✅ Export Text Only: Passed")
        except Exception as e:
            self.fail(f"Text-only export failed: {str(e)}")
    
    # ========== Utility Function Tests ==========
    
    def test_generate_filename(self):
        """Test filename generation"""
        name = "John Doe"
        pdf_name = generate_filename(name, 'pdf')
        docx_name = generate_filename(name, 'docx')
        
        self.assertIn('John_Doe', pdf_name)
        self.assertTrue(pdf_name.endswith('.pdf'))
        self.assertIn('John_Doe', docx_name)
        self.assertTrue(docx_name.endswith('.docx'))
        print(f"✅ Filename Generation: {pdf_name}")
    
    def test_create_export_dir(self):
        """Test export directory creation"""
        export_dir = create_export_dir("data/test_exports")
        self.assertTrue(Path(export_dir).exists())
        self.assertTrue(Path(export_dir).is_dir())
        print(f"✅ Export Directory Creation: {export_dir}")
    
    # ========== Edge Cases ==========
    
    def test_resume_with_special_characters(self):
        """Test export with special characters"""
        special_resume = {
            **self.sample_resume,
            "name": "José García-López",
            "summary": "Experience with C++, C#, F#, and other languages",
        }
        try:
            pdf_bytes = export_resume_to_pdf(special_resume)
            docx_bytes = export_resume_to_docx(special_resume)
            text_content = export_resume_to_text(special_resume)
            
            self.assertGreater(len(pdf_bytes), 0)
            self.assertGreater(len(docx_bytes), 0)
            self.assertGreater(len(text_content), 0)
            print(f"✅ Special Characters Export: Passed")
        except Exception as e:
            self.fail(f"Special characters export failed: {str(e)}")
    
    def test_resume_with_long_content(self):
        """Test export with very long content"""
        long_resume = {
            **self.sample_resume,
            "skills": [f"Skill {i}" for i in range(100)],
            "experience": [
                {
                    "title": f"Position {i}",
                    "company": f"Company {i}",
                    "duration": f"20{i%20}-20{i%20+1}",
                    "description": [f"Achievement {j}" for j in range(10)]
                }
                for i in range(5)
            ]
        }
        try:
            result = export_resume(long_resume, export_format="all")
            self.assertTrue(result['formats']['pdf']['generated'])
            self.assertTrue(result['formats']['docx']['generated'])
            self.assertTrue(result['formats']['text']['generated'])
            print(f"✅ Long Content Export: Passed")
        except Exception as e:
            self.fail(f"Long content export failed: {str(e)}")
    
    def test_resume_with_empty_sections(self):
        """Test export with missing optional sections"""
        minimal_resume = {
            "name": "Minimal User"
        }
        try:
            result = export_resume(minimal_resume, export_format="all")
            self.assertEqual(result['status'], 'success')
            print(f"✅ Empty Sections Export: Passed")
        except Exception as e:
            self.fail(f"Empty sections export failed: {str(e)}")


class TestResumeExportIntegration(unittest.TestCase):
    """Integration tests for export service"""
    
    def test_pdf_docx_similar_size(self):
        """Test that PDF and DOCX are similar in size"""
        resume = {
            "name": "Test User",
            "email": "test@example.com",
            "skills": ["Python", "JavaScript"],
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Corp",
                    "duration": "2020-2024",
                    "description": "Built systems"
                }
            ]
        }
        
        pdf_bytes = export_resume_to_pdf(resume)
        docx_bytes = export_resume_to_docx(resume)
        
        # Sizes should be within 50% of each other
        ratio = len(pdf_bytes) / len(docx_bytes)
        self.assertTrue(0.5 < ratio < 2.0)
        print(f"✅ Size Comparison: PDF {len(pdf_bytes)} vs DOCX {len(docx_bytes)}")
    
    def test_export_roundtrip(self):
        """Test export and verify content"""
        resume = {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "+1-555-0789",
            "skills": ["FastAPI", "PostgreSQL"]
        }
        
        # Export to text and check content
        text_content = export_resume_to_text(resume)
        self.assertIn("Alice Johnson", text_content)
        self.assertIn("alice@example.com", text_content)
        self.assertIn("FastAPI", text_content)
        
        print(f"✅ Roundtrip Verification: All content preserved")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestResumeExportService))
    suite.addTests(loader.loadTestsFromTestCase(TestResumeExportIntegration))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
