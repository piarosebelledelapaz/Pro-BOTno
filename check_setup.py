#!/usr/bin/env python3
"""
Setup checker for UNHCR Refugee Portal
Verifies that all dependencies and configuration are correct
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required = [
        "streamlit",
        "openai",
        "langchain_chroma",
        "langchain_huggingface",
        "langchain_openai",
        "sentence_transformers",
        "reportlab",
        "PyPDF2",
        "SPARQLWrapper"
    ]
    
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (MISSING)")
            missing.append(package)
    
    if missing:
        print(f"\n  Missing packages: {', '.join(missing)}")
        print(f"\n  Install with: pip install -r src/requirements.txt")
        return False
    
    return True

def check_api_key():
    """Check if OpenAI API key is set"""
    print("\nChecking OpenAI API key...")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        masked = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
        print(f"  ✓ OPENAI_API_KEY is set ({masked})")
        return True
    else:
        print(f"  ✗ OPENAI_API_KEY is not set")
        print(f"\n  Set with: export OPENAI_API_KEY='your-api-key'")
        return False

def check_vector_db():
    """Check if vector database exists"""
    print("\nChecking vector database...")
    
    db_path = Path(__file__).parent / "src" / "vector_db_data"
    
    if db_path.exists():
        files = list(db_path.iterdir())
        print(f"  ✓ Database found at {db_path}")
        print(f"  ✓ Contains {len(files)} files")
        return True
    else:
        print(f"  ✗ Database not found at {db_path}")
        return False

def check_directory_structure():
    """Check if required directories exist"""
    print("\nChecking directory structure...")
    
    base_path = Path(__file__).parent
    
    required_dirs = [
        "src",
        "src/modules",
        "src/prompts",
        "src/backend"
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ (MISSING)")
            all_ok = False
    
    return all_ok

def check_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    
    base_path = Path(__file__).parent
    
    required_files = [
        "src/portal.py",
        "src/pages/1_📝_New_Case_Intake.py",
        "src/pages/2_📊_Case_Reports.py",
        "src/backend/case_processor.py",
        "src/backend/pdf_generator.py",
        "src/modules/enhanced_rag.py",
        "src/modules/fedlex_client.py",
        "run_portal.sh"
    ]
    
    all_ok = True
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (MISSING)")
            all_ok = False
    
    return all_ok

def main():
    """Run all checks"""
    print("="*60)
    print("UNHCR Refugee Portal - Setup Checker")
    print("="*60)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_api_key(),
        check_vector_db(),
        check_directory_structure(),
        check_files()
    ]
    
    print("\n" + "="*60)
    
    if all(checks):
        print("✓ All checks passed! You're ready to run the portal.")
        print("\nTo start the portal:")
        print("  ./run_portal.sh")
        print("\nOr:")
        print("  cd src && streamlit run portal.py")
        print("="*60)
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

