"""Log and track query-answer pairs for accuracy monitoring"""
import json
import os
import csv
from datetime import datetime
from typing import Dict, Any

class AccuracyLogger:
    """Log Q&A pairs and metrics for accuracy analysis"""
    
    def __init__(self, log_file="qa_accuracy_log.csv"):
        self.log_file = log_file
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'query', 'demo_mode', 'docs_retrieved',
                    'retrieval_score', 'confidence_score', 'mode',
                    'language', 'solution_type', 'response_length',
                    'has_sources', 'user_feedback', 'notes'
                ])
    
    def log_query_response(self, entry: Dict[str, Any]):
        """Log a query-response pair with metrics"""
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'timestamp', 'query', 'demo_mode', 'docs_retrieved',
                'retrieval_score', 'confidence_score', 'mode',
                'language', 'solution_type', 'response_length',
                'has_sources', 'user_feedback', 'notes'
            ])
            
            entry['timestamp'] = entry.get('timestamp', datetime.now().isoformat())
            writer.writerow(entry)
    
    def get_accuracy_summary(self, sample_size=100) -> Dict[str, float]:
        """Calculate accuracy metrics from logged data"""
        if not os.path.exists(self.log_file):
            return {}
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        
        if not rows:
            return {}
        
        recent = rows[-sample_size:]
        
        # Calculate aggregate metrics
        avg_confidence = sum(float(r.get('confidence_score', 0)) for r in recent) / len(recent) if recent else 0
        high_conf_count = sum(1 for r in recent if float(r.get('confidence_score', 0)) >= 0.7)
        positive_feedback = sum(1 for r in recent if r.get('user_feedback') == 'positive')
        
        return {
            "sample_size": len(recent),
            "avg_confidence_score": avg_confidence,
            "high_confidence_pct": (high_conf_count / len(recent) * 100) if recent else 0,
            "positive_feedback_pct": (positive_feedback / len(recent) * 100) if recent else 0,
            "total_queries": len(rows)
        }

accuracy_logger = AccuracyLogger()