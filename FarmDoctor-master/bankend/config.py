"""Configuration parameters for RAG pipeline - centralized management"""

# ============= INGESTION CONFIGURATION =============
INGESTION_CONFIG = {
    "chunk_size": 1000,      # Increased from 500 for better context retention
    "chunk_overlap": 200,    # Increased from 100 for better continuity
    "separator_strategy": "agricultural",  # New strategy
    "separators": [
        "\n\n",  # Paragraph break (highest priority)
        "\n",    # Line break
        ". ",    # Sentence with space
        "! ",
        "? ",
        ": ",    # NEW: Capture section headers
        "; ",    # NEW: Capture compound statements
        ", ",    # LOW priority
        " ",
        ""
    ]
}

# ============= RETRIEVAL CONFIGURATION =============
RETRIEVAL_CONFIG = {
    "default_k": 5,
    "similarity_threshold": 0.3,  # LOWERED: More lenient for small KB
    "min_relevance_score": 0.4,   # LOWERED: Allow lower quality matches
    "max_tokens_context": 4000,   # NEW: Limit context window
    "rerank_enabled": True,       # NEW: Optional re-ranking
}

# ============= VALIDATION CONFIGURATION =============
VALIDATION_CONFIG = {
    "max_retries": 3,
    "confidence_threshold": 0.7,  # NEW: Min confidence for answer
    "require_sources": True,      # NEW: Must cite sources
    "check_response_structure": True,  # NEW: Validate response format
}

# ============= MODEL CONFIGURATION =============
MODEL_CONFIG = {
    "primary_model": "llama-3.3-70b-versatile",
    "fallback_model": "mixtral-8x7b-32768",
    "temperature": 0.3,           # NEW: Lower for consistency
    "top_p": 0.9,                 # NEW: Nucleus sampling
    "max_tokens": 2000,
}

# ============= KNOWLEDGE BASE REQUIREMENTS =============
KNOWLEDGE_BASE_REQUIREMENTS = {
    "min_documents": 1,           # TEMPORARILY LOWERED for testing
    "min_total_chars": 10000,     # TEMPORARILY LOWERED for testing
    "required_categories": [      # NEW: Ensure coverage
        "Crop Diseases",
        "Pest Management",
        "Soil Management",
        "Irrigation",
        "Fertilizers",
        "Seasonal Guides",
        "Regional Guides"
    ]
}