"""Knowledge base validation and audit tool"""
import os
import glob
import logging
from typing import Dict, List
from config import KNOWLEDGE_BASE_REQUIREMENTS

logger = logging.getLogger(__name__)

def audit_knowledge_base() -> Dict:
    """Audit KB coverage and completeness"""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_path = os.path.normpath(os.path.join(base_dir, "docs"))
    
    audit_report = {
        "status": "READY",
        "documents": [],
        "total_size_mb": 0,
        "coverage": {}
    }
    
    # Collect all files
    for ext in ["*.txt", "*.pdf"]:
        for file in glob.glob(os.path.join(docs_path, ext)):
            size_mb = os.path.getsize(file) / (1024 * 1024)
            audit_report["documents"].append({
                "path": file,
                "size_mb": size_mb,
                "type": ext.replace("*.", "")
            })
            audit_report["total_size_mb"] += size_mb
    
    # Check categories
    for category in KNOWLEDGE_BASE_REQUIREMENTS["required_categories"]:
        category_lower = category.lower().replace(" ", "")
        found = any(category_lower in str(d).lower() for d in audit_report["documents"])
        audit_report["coverage"][category] = "✓" if found else "✗ (ADD)"
    
    # Validation
    min_docs = KNOWLEDGE_BASE_REQUIREMENTS["min_documents"]
    min_size_mb = KNOWLEDGE_BASE_REQUIREMENTS["min_total_chars"] / (1024 * 1024)
    
    if len(audit_report["documents"]) < min_docs:
        audit_report["status"] = "INSUFFICIENT"
        logger.error(f"Need {min_docs} docs, have {len(audit_report['documents'])}")
    
    if audit_report["total_size_mb"] < min_size_mb:
        audit_report["status"] = "INSUFFICIENT"
        logger.error(f"Need {min_size_mb:.1f}MB, have {audit_report['total_size_mb']:.1f}MB")
    
    return audit_report

if __name__ == "__main__":
    report = audit_knowledge_base()
    print(f"\n=== KNOWLEDGE BASE AUDIT ===")
    print(f"Status: {report['status']}")
    print(f"Documents: {len(report['documents'])}")
    print(f"Total Size: {report['total_size_mb']:.1f} MB")
    print(f"\nCoverage:")
    for cat, status in report['coverage'].items():
        print(f"  {cat}: {status}")