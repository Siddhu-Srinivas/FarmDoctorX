from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
import os
import time
import random
import logging
from typing import List
from config import RETRIEVAL_CONFIG, VALIDATION_CONFIG, MODEL_CONFIG
from accuracy_logger import accuracy_logger

# Configure logging for better error tracking
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Configuration constants
DEFAULT_MODEL = "llama-3.1-8b-instant"  # Using 8B model to stay within your Groq daily token limits
FALLBACK_MODEL = "mixtral-8x7b-32768"  # Available fallback model
DEFAULT_EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
INDEX_NAME = "farmsdoctor-rag"
DEFAULT_K = 5
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2

# Demo mode flag - parse as FALSE for any string that's explicitly "false", "0", "no"
demo_mode_env = os.getenv("DEMO_MODE", "false").lower().strip()
DEMO_MODE = demo_mode_env in ["true", "1", "yes"]

logger.info(f"DEMO_MODE = {DEMO_MODE} (env value: '{demo_mode_env}')")
logger.info(f"Accuracy Mode: {'DEMO (templated, ~50-60%)' if DEMO_MODE else 'LIVE (AI-powered, target 90%+)'}")
if DEMO_MODE:
    logger.warning("⚠️ DEMO_MODE ENABLED - Responses will be templated, not AI-generated")
    logger.info("To disable demo mode, set DEMO_MODE=false in .env file")

# Validate required environment variables
required_env_vars = ["PINECONE_API_KEY", "GROK_API_KEY"]
for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"{var} not found in .env file")
        raise ValueError(f"{var} not found in .env")

def validate_api_configuration():
    """Validate that APIs are properly configured for live mode."""
    demo_mode = DEMO_MODE
    pinecone_key = os.getenv("PINECONE_API_KEY")
    grok_key = os.getenv("GROK_API_KEY")
    
    if not demo_mode:
        # Live mode requires all APIs
        if not grok_key:
            logger.error("GROK_API_KEY required for live mode")
            raise ValueError("GROK_API_KEY not configured. Set DEMO_MODE=true or provide API key")
        if not pinecone_key:
            logger.error("PINECONE_API_KEY required for live mode")
            raise ValueError("PINECONE_API_KEY not configured. Set DEMO_MODE=true or provide API key")
        logger.info("✓ Live mode: All API keys configured")
    else:
        logger.warning("⚠️ Demo mode enabled: Using templated responses (accuracy ~50-60%)")
        logger.info("To enable live AI (90%+ accuracy), set DEMO_MODE=false and provide API keys")

validate_api_configuration()

# Performance optimization: Cache embedding model (singleton pattern)
_embedding_model_cache = None

def get_embedding_model():
    """Get or create embedding model (cached for performance)."""
    global _embedding_model_cache
    if _embedding_model_cache is None:
        logger.debug("Initializing embedding model...")
        _embedding_model_cache = HuggingFaceEmbeddings(model_name=DEFAULT_EMBEDDING_MODEL)
    return _embedding_model_cache

# history of previous messages (HumanMessage, AIMessage)
chat_history = []

def is_farming_related_query(query: str) -> bool:
    """Detect if a query is related to farming/agriculture."""
    farming_keywords = {
        'crop', 'yield', 'pest', 'disease', 'soil', 'water', 'irrigation',
        'fertilizer', 'pesticide', 'harvest', 'season', 'plant', 'grow',
        'farm', 'agriculture', 'farming', 'wheat', 'rice', 'corn', 'maize',
        'tomato', 'potato', 'onion', 'cotton', 'sugarcane', 'insect',
        'fungal', 'bacterial', 'weed', 'germination', 'rainfall', 'humidity',
        'temperature', 'soil type', 'organic', 'inorganic', 'fertilization',
        'cultivation', 'pruning', 'grafting', 'NPK', 'pH', 'nutrient',
        'blight', 'rust', 'powdery', 'leaf', 'root', 'stem', 'fruit',
        'vegetable', 'grain', 'cereal', 'legume', 'orchard', 'vineyard',
        'livestock', 'cattle', 'buffalo', 'soil moisture', 'drainage',
        'mulching', 'composting', 'vermicompost', 'neem', 'monsoon', 'kharif',
        'rabi', 'summer', 'thrips', 'whitefly', 'aphid', 'armyworm', 'how many', 'list all'
    }
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in farming_keywords)

def detect_query_intent(query: str, model_instance) -> str:
    """Categorize the query into GLOBAL, DIRECT, ADVISORY, CROP_INFO, or GENERAL."""
    query_lower = query.lower()
    
    # 1. Broad Discovery (List all diseases for a crop)
    broad_keywords = ["disease", "pest", "problem", "list", "all", "everything", "how many", "total"]
    if any(k in query_lower for k in broad_keywords) and not any(k in query_lower for k in ["how to", "treat", "cure", "control", "step"]):
        return "GLOBAL"
        
    # 2. Crop Info (General profile)
    if len(query.split()) <= 2:
        return "CROP_INFO"
        
    heuristic_global = ["how many", "list all", "total", "database", "everything"]
    if any(k in query_lower for k in heuristic_global):
        return "GLOBAL"
        
    # Direct hints (what is X)
    if query_lower.startswith(("what is", "which is", "tell me the name of")):
        if not any(k in query_lower for k in ["how to", "treat", "solution", "manage", "control", "prevent"]):
            return "DIRECT"

    try:
        detection_prompt = f"""Categorize this agricultural query:
- GLOBAL: Counting or listing everything (e.g., "how many crops").
- DIRECT: Specific factual names/facts (e.g., "scientific name of wheat rust").
- ADVISORY: Treatment/management advice (e.g., "how to treat rust").
- CROP_INFO: General info about a crop (e.g., "wheat farming").
- GENERAL: Unrelated.

Query: "{query}"
Return only: GLOBAL, DIRECT, ADVISORY, CROP_INFO, or GENERAL."""
        
        response = invoke_with_retry(model_instance, [HumanMessage(content=detection_prompt)], max_retries=2)
        intent = response.content.strip().upper()
        for cat in ["GLOBAL", "DIRECT", "ADVISORY", "CROP_INFO", "GENERAL"]:
            if cat in intent: return cat
    except Exception as e:
        logger.warning(f"Intent detection retry failed: {e}")
    return "ADVISORY"

OOS_MESSAGES = {
    "English": "I'm sorry, I didn't quite understand that. Could you please ask a question related to farming?",
    "Hindi": "क्षमा करें, मुझे यह ठीक से समझ नहीं आया। क्या आप कृपया खेती से संबंधित कोई प्रश्न पूछ सकते हैं?",
    "Telugu": "క్షమించండి, అది నాకు సరిగ్గా అర్థం కాలేదు. దయచేసి వ్యవసాయానికి సంబంధించిన ప్రశ్న అడగగలరా?",
    "Marathi": "क्षमस्व, मला ते नीट समजले नाही. कृपया आपण शेतीशी संबंधित एखादा प्रश्न विचारू शकता का?",
    "Tamil": "மன்னிக்கவும், எனக்கு அது சரியாக புரியவில்லை. விவசாயம் தொடர்பான கேள்வியைக் கேட்க முடியுமா?",
    "Kannada": "ಕ್ಷಮಿಸಿ, ಅದು ನನಗೆ ಸರಿಯಾಗಿ ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದೇ?"
}

def generate_direct_response(query, docs, model_instance, language="English", solution_type="Both"):
    """Handle DIRECT queries with concise factual answers."""
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""Answer this agricultural question CONCISELY and CLEARLY for a farmer.
    Use {language}. 
    Response should be ONE sentence or a SHORT list only. No headers.
    
    Question: {query}
    Context: {context}
    Answer:"""
    try:
        response = invoke_with_retry(model_instance, [HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception:
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again in 1 minute."

def handle_global_query(query, model_instance, language="English"):
    """Handle GLOBAL queries by scanning many chunks."""
    logger.info("Handling GLOBAL query with discovery retrieval...")
    # Using 30 chunks (approx 30k tokens) to stay within most free-tier limits
    retrieval = retrieve_documents(query, k=30, validate_quality=False)
    docs = retrieval["documents"]
    if not docs: return "I don't have enough information in my records to answer that.", []
    
    context = "\n\n".join([f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}" for doc in docs])
    prompt = f"""You are analyzing the entire agricultural knowledge base.
    User asks: {query}
    
    Instructions:
    1. Scan all provided contexts.
    2. Count or list items as requested (be very specific).
    3. If counting crops, look for unique crop names.
    4. Give a clear, direct answer for a farmer.
    5. Language: {language}.
    
    Context:
    {context}
    
    Answer:"""
    try:
        response = invoke_with_retry(model_instance, [HumanMessage(content=prompt)], max_retries=2)
        return response.content.strip(), docs
    except Exception as e:
        logger.error(f"Global query LLM call failed: {e}. Using intelligent fallback.")
        # Fallback: Extract unique sources/names from metadata
        sources = sorted(list(set([doc.metadata.get('source', 'Unknown').split('/')[-1].split('\\')[-1] for doc in docs])))
        if sources:
            source_list = "\n".join([f"• {s.replace('.txt','').replace('.pdf','')}" for s in sources[:10]])
            msg = f"I found several records related to your search. Based on my quick scan, these items are in our database:\n\n{source_list}\n\nYou can ask about any of these specifically for a full guide!"
            return msg, docs
        return "I'm having trouble analyzing the full database right now. Please try asking about a specific disease like 'rice blast'.", docs

def generate_simple_statement(query: str, language: str = "English") -> str:
    """
    Generate a simple, direct statement for non-farming questions.
    """
    logger.info(f"Generating simple statement for non-farming query: {query[:50]}...")
    
    templates = {
        "English": {
            "heading": "Response:",
            "statement": "I'm specialized in farming and agriculture. Your question seems to be outside my expertise. I can help you with:",
            "examples": "• Crop diseases and pest management\n• Soil health and irrigation planning\n• Fertilizer recommendations\n• Farming best practices\n• Seasonal crop guidance",
            "offer": "If you have any farming-related questions, I'd be happy to help!"
        },
        "Hindi": {
            "heading": "उत्तर:",
            "statement": "मैं कृषि और खेती में विशेषज्ञ हूं। आपका प्रश्न मेरी विशेषज्ञता के बाहर लगता है। मैं आपकी मदद कर सकता हूं:",
            "examples": "• फसल रोग और कीट प्रबंधन\n• मिट्टी का स्वास्थ्य और सिंचाई योजना\n• खाद की सिफारिशें\n• खेती के सर्वोत्तम तरीके\n• मौसमी फसल मार्गदर्शन",
            "offer": "अगर आपके पास कृषि से संबंधित कोई प्रश्न है, तो मुझे खुशी होगी!"
        },
        "Telugu": {
            "heading": "సమాధానం:",
            "statement": "నేను వ్యవసాయ మరియు పైర్లలో నిపుణుడిని. మీ ప్రశ్న నా నిపుణతకు వెలుపల ఉంది. నేను మీకు సహాయం చేయగలను:",
            "examples": "• పంట వ్యాధులు మరియు కీటక నిర్వహణ\n• నేల ఆరోగ్యం మరియు నీటిపారపట్ల ప్రణాళిక\n• ఎరువు సిఫారసులు\n• కృషి ఉత్తమ పద్ధతులు\n• సీజనల్ పంట మార్గదర్శకత్వం",
            "offer": "మీకు వ్యవసాయ సంబంధిత ప్రశ్న ఉంటే, నేను సహాయం చేయడానికి ఆనందిస్తాను!"
        }
    }
    
    lang = language if language in templates else "English"
    t = templates[lang]
    
    response = f"""{t['heading']}

{t['statement']}
{t['examples']}

{t['offer']}"""
    
    return response

def calculate_doc_relevance_score(doc, query: str) -> dict:
    """Calculate multi-factor relevance score for a document"""
    embedding_model = get_embedding_model()
    query_terms = set(w for w in query.lower().split() if len(w) > 3)
    doc_text_lower = doc.page_content.lower()
    term_coverage = sum(1 for term in query_terms if term in doc_text_lower) / max(1, len(query_terms))
    doc_length = len(doc.page_content)
    length_score = 1.0 if 200 < doc_length < 8000 else 0.6
    source = doc.metadata.get('source', 'Unknown')
    source_score = 1.0
    
    composite_score = (
        (term_coverage * 0.3) +
        (length_score * 0.2) +
        (source_score * 0.2) +
        (0.3)
    )
    
    return {
        "composite_score": composite_score,
        "term_coverage": term_coverage,
        "quality_score": length_score,
        "source": source
    }

def retrieve_documents(query, k=None, validate_quality=True):
    """Retrieve relevant documents with quality validation"""
    if k is None:
        k = RETRIEVAL_CONFIG["default_k"]
    
    db = None
    warnings = []
    
    try:
        # Performance: Don't load embedding model if in DEMO_MODE and we don't have enough RAM
        if DEMO_MODE:
            logger.info("Demo mode: Skipping vector store initialization to save RAM.")
            return {"documents": [], "metrics": {"avg_score": 0}, "warnings": ["Demo mode active"]}

        db = PineconeVectorStore(
            index_name=INDEX_NAME,
            embedding=get_embedding_model()
        )
    except Exception as exc:
        logger.error(f"Failed to initialize vector store: {exc}")
        return {"documents": [], "metrics": {}, "warnings": [str(exc)]}
    
    try:
        raw_docs = db.similarity_search(query, k=k+5)
        if not raw_docs:
            return {"documents": [], "metrics": {}, "warnings": ["No documents found"]}
        
        scored_docs = [(doc, calculate_doc_relevance_score(doc, query)) for doc in raw_docs]
        threshold = RETRIEVAL_CONFIG["similarity_threshold"]
        min_relevance = RETRIEVAL_CONFIG["min_relevance_score"]
        
        if validate_quality:
            quality_docs = [(doc, rel) for doc, rel in scored_docs if rel['composite_score'] >= min_relevance * threshold]
        else:
            quality_docs = scored_docs[:k]
        
        if not quality_docs and len(scored_docs) > 0:
            quality_docs = scored_docs[:min(k, len(scored_docs))]
        
        final_docs = [doc for doc, _ in quality_docs[:k]]
        scores = [rel['composite_score'] for _, rel in quality_docs[:k]]
        
        metrics = {
            "retrieved_count": len(raw_docs),
            "quality_count": len(quality_docs),
            "returned_count": len(final_docs),
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "threshold": threshold
        }
        
        return {"documents": final_docs, "metrics": metrics, "warnings": warnings}
        
    except Exception as exc:
        logger.error(f"Document retrieval failed: {exc}")
        return {"documents": [], "metrics": {}, "warnings": [str(exc)]}

def score_answer_confidence(query: str, answer: str, docs: List, retrieval_metrics: dict) -> dict:
    """Calculate confidence score for the generated answer."""
    confidence_factors = {"retrieval_quality": 0.5, "answer_structure": 0.5, "source_citation": 0.5, "length_adequate": 0.5}
    if retrieval_metrics:
        doc_score = retrieval_metrics.get("avg_score", 0)
        confidence_factors["retrieval_quality"] = min(1.0, doc_score + 0.1)
    
    markers = ["Question", "Explanation", "Solution", "Step", "🌿", "⚙️"]
    sections_found = sum(1 for m in markers if m in answer)
    confidence_factors["answer_structure"] = min(1.0, (sections_found / len(markers)) + 0.2)
    
    if len(docs) > 0 and any(s in answer for s in ["Source", "Doc", "Knowledge"]):
        confidence_factors["source_citation"] = 1.0
    
    if len(answer) > 1000: confidence_factors["length_adequate"] = 1.0
    elif len(answer) > 300: confidence_factors["length_adequate"] = 0.7

    weights = {"retrieval_quality": 0.4, "answer_structure": 0.3, "source_citation": 0.2, "length_adequate": 0.1}
    composite = sum(confidence_factors[k] * weights[k] for k in weights)
    
    return {"confidence_score": composite, "factors": confidence_factors, "passed_threshold": composite >= 0.6}

def generate_demo_response(query, docs, solution_type="Both", language="English"):
    """Generate a demo response based on retrieved documents without API calls."""
    query_lower = query.lower()
    crop_names = ["wheat", "rice", "maize", "corn", "potato", "tomato", "onion", "cotton", "sugarcane"]
    crop = next((name for name in crop_names if name in query_lower), None)
    
    issue_kind = "crop problem"
    if any(keyword in query_lower for keyword in ["disease", "blast", "rust", "blight", "mildew", "spot", "yellow", "brown", "rot", "wilt", "mold", "pest", "aphid", "borer", "hopper", "whitefly"]):
        issue_kind = "disease or pest problem"
    elif any(keyword in query_lower for keyword in ["soil", "salty", "salinity", "ph", "water", "dry", "wet", "drainage", "nutrient", "fertilizer", "urea", "nitrogen", "potash", "kale"]):
        issue_kind = "soil or nutrient problem"
    
    issue_text = f"This looks like a {issue_kind} in your {crop if crop else 'farm'}."
    
    # Language-specific templates
    templates = {
        "English": {
            "question_header": "🔎 Question",
            "explanation_header": "📘 Simple Explanation",
            "organic_header": "🌿 Organic Solution",
            "inorganic_header": "⚙️ Inorganic Solution",
            "suggestion_header": "📌 Final Suggestion",
            "knowledge_header": "📚 Knowledge Reference",
            "explanation_text": issue_text,
            "organic_intro": "Natural and eco-friendly control methods:",
            "prevent_organic_header": "- **Steps to Prevent**",
            "step1_organic": "How to stop it early: Clear weeds and balance water.",
            "treatment_organic_header": "- **Treatment**",
            "step2_organic": "Apply natural solutions (Neem, Ash, or cleaning).",
            "step3_organic": "Keep soil healthy and rotate crops.",
            "benefits_organic": "Safe / No Chem / Low Cost",
            "inorganic_header": "Strong Treatment",
            "inorganic_intro": "When chemicals are needed:",
            "prevent_inorganic_header": "- **Steps to Prevent**",
            "step1_inorganic": "Technical prevention: Use treated seeds.",
            "treatment_inorganic_header": "- **Treatment**",
            "step2_inorganic": "Use recommended Pesticide correctly.",
            "step3_inorganic": "Wear safety gear.",
            "suggestion_text": "Start natural. Use chemical only if severe.",
            "note": "Demo only. Ask experts for final word."
        }
    }
    
    # Get template
    lang = language if language in templates else "English"
    t = templates[lang]
    
    # Simple build
    response = f"""{t['question_header']}
{query}

{t['explanation_header']}
{t['explanation_text']}

{t['organic_header']}
{t['organic_intro']}
{t['prevent_organic_header']}
- {t['step1_organic']}
{t['treatment_organic_header']}
- {t['step2_organic']}
- {t['step3_organic']}

{t['inorganic_header']}
{t['inorganic_intro']}
{t['prevent_inorganic_header']}
- {t['step1_inorganic']}
{t['treatment_inorganic_header']}
- {t['step2_inorganic']}
- {t['step3_inorganic']}

{t['suggestion_header']}
{t['suggestion_text']}

{t['note']}"""
    return response

CROP_PROFILES = {
    "template": """I can help you find better ways to care for your crops. Let's look at what's happening with your crop and how significant it is for farmers. 

## {crop_name} Profile

**{about_intro}**

**Importance of {crop_name}:**
*   **Fundamental Food Security:** {crop_name} is a primary staple, providing nourishment for millions.
*   **Economic Impact:** It's a major cash crop, significantly contributing to rural income.
*   **Sustainable Agriculture:** Many varieties are hardy and can be grown using eco-friendly practices.

**Estimated Market Value (Current Trends):**
*   **Wholesale Price (Mandi):** The typical price range is approximately {price_range} per quintal, depending on variety and quality. 
*   **Retail Market:** Prices vary locally but typically reflect {crop_name}’s value as an essential daily commodity. 

*(Note: Prices fluctuate based on season, supply, and local market conditions.)*

---

Would you like tips on how to improve your yield or manage common pests for your {crop_name} crop?""",
    "crop_data": {
        "rice": {"name": "Rice", "about": "Rice is a staple food in India, grown in wet, low-lying areas.", "price": "₹2100 - ₹2300"},
        "wheat": {"name": "Wheat", "about": "Essential grain for bread, grown in winter in North India.", "price": "₹2200 - ₹2600"},
        "cotton": {"name": "Cotton", "about": "A key fiber crop, requires warm climate.", "price": "₹6500 - ₹8000"}
    }
}

def generate_crop_info_response(query: str, language: str = "English") -> str:
    query_lower = query.lower()
    match = next((k for k in CROP_PROFILES["crop_data"] if k in query_lower), "rice")
    data = CROP_PROFILES["crop_data"][match]
    return CROP_PROFILES["template"].format(crop_name=data["name"], about_intro=data["about"], price_range=data["price"])

def invoke_with_retry(model_instance, messages, max_retries=None):
    """
    Invoke the model with exponential backoff retry logic for rate limits.
    
    Args:
        model_instance: ChatGroq instance
        messages: List of messages to send
        max_retries: Maximum number of retry attempts (default: MAX_RETRIES)
        
    Returns:
        Model response
        
    Raises:
        RuntimeError: If all retries fail
    """
    if max_retries is None:
        max_retries = MAX_RETRIES
        
    for attempt in range(max_retries):
        try:
            logger.debug(f"Invoking model (attempt {attempt + 1}/{max_retries})...")
            response = model_instance.invoke(messages)
            logger.debug("Model invocation successful")
            return response
        except Exception as exc:
            err_msg = str(exc).lower()
            is_rate_limit = any(x in err_msg for x in ["rate limit", "429", "503", "overloaded", "busy"])
            is_auth_error = any(x in err_msg for x in ["401", "unauthorized", "invalid api key", "auth"])
            
            if is_auth_error:
                logger.error(f"Authentication error: {exc}")
                raise
            
            if not is_rate_limit or attempt == max_retries - 1:
                logger.error(f"Model invocation failed (attempt {attempt + 1}/{max_retries}): {exc}")
                raise
            
            # Calculate exponential backoff with jitter for rate limits
            wait_time = (RETRY_BACKOFF_BASE ** attempt) + random.uniform(0, 1)
            logger.warning(f"Rate limit/throttle detected. Retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
    
    raise RuntimeError(f"Failed to invoke model after {max_retries} retry attempts")

def generate_answer(query, k=None, model=None, solution_type="Both", use_history=True, language="English"):
    """
    Generate a structured response for the given query.
    Routes to GLOBAL, DIRECT, or ADVISORY modes based on intent.
    """
    start_time = time.time()
    if k is None: k = DEFAULT_K
    if model is None: model = DEFAULT_MODEL
        
    if not query or not query.strip():
        raise ValueError("Empty query provided")
    
    # Initialize model early
    try:
        model_instance = ChatGroq(
            model=model,
            api_key=os.getenv("GROK_API_KEY"),
            temperature=MODEL_CONFIG.get("temperature", 0.3)
        )
    except Exception as exc:
        logger.error(f"Model init failed: {exc}")
        return "I'm having trouble starting my AI brain. Please try again later.", []

    # 1. Detect Intent
    intent = detect_query_intent(query, model_instance)
    logger.info(f"Detected Intent: {intent}")
    
    answer_text = ""
    relevant_docs = []
    metrics = {"avg_score": 0}

    # 2. Route based on Intent
    if intent == "GLOBAL":
        answer_text, relevant_docs = handle_global_query(query, model_instance, language)
    elif intent == "GENERAL":
        answer_text = OOS_MESSAGES.get(language, OOS_MESSAGES["English"])
        relevant_docs = []
    else:
        # Standard RAG for DIRECT or ADVISORY
        search_query = query
        if use_history and chat_history:
            try:
                rewrite_msgs = [SystemMessage(content="Rewrite for standalone RAG search.")] + chat_history + [HumanMessage(content=query)]
                search_query = invoke_with_retry(model_instance, rewrite_msgs, max_retries=1).content.strip()
            except: pass

        retrieval_result = retrieve_documents(search_query, k=k)
        relevant_docs = retrieval_result["documents"]
        metrics = retrieval_result["metrics"]

        if not relevant_docs:
            answer_text = OOS_MESSAGES.get(language, OOS_MESSAGES["English"])
        elif intent == "DIRECT":
            answer_text = generate_direct_response(query, relevant_docs, model_instance, language)
        else:
            # Full Advisory
            context = "\n\n".join([f"[Source {i+1}] {d.page_content}" for i, d in enumerate(relevant_docs)])

            # ── Language-specific section labels & writing guidance ──────────
            LANG_CONFIG = {
                "English": {
                    "intro": "You are 'FarmDoctor', a friendly and wise agricultural expert for Indian farmers. Give clear, practical, detailed advice.",
                    "rules": "Write in simple English. Use short sentences. Avoid jargon. Be warm like a helpful neighbour.",
                    "problem_label":    "Problem",
                    "organic_label":    "Natural Solution (Organic)",
                    "organic_sub1":     "Steps to Prevent",
                    "organic_sub2":     "Treatment",
                    "inorganic_label":  "Strong Medicine (Inorganic)",
                    "inorganic_sub1":   "Steps to Prevent",
                    "inorganic_sub2":   "Treatment (with safety rules)",
                    "tip_label":        "Success Tip",
                    "additional_label": "Additional Tips",
                },
                "Hindi": {
                    "intro": "आप 'FarmDoctor' हैं — भारतीय किसानों के लिए एक विश्वसनीय और अनुभवी कृषि विशेषज्ञ। सरल, स्पष्ट और व्यावहारिक सलाह दें।",
                    "rules": (
                        "हिंदी में लिखें। छोटे और स्पष्ट वाक्य उपयोग करें। "
                        "कठिन शब्दों से बचें — जैसे 'रोगाणु' की जगह 'कीटाणु' कहें। "
                        "किसान को एक समझदार पड़ोसी की तरह समझाएं। "
                        "हर बिंदु में 2–3 वाक्य लिखें ताकि किसान को पूरी जानकारी मिले।"
                    ),
                    "problem_label":    "समस्या",
                    "organic_label":    "प्राकृतिक उपाय (जैविक)",
                    "organic_sub1":     "बचाव के तरीके",
                    "organic_sub2":     "उपचार",
                    "inorganic_label":  "रासायनिक उपाय",
                    "inorganic_sub1":   "बचाव के तरीके",
                    "inorganic_sub2":   "उपचार (सुरक्षा नियमों के साथ)",
                    "tip_label":        "सफलता का सुझाव",
                    "additional_label": "अतिरिक्त सुझाव",
                },
                "Telugu": {
                    "intro": "మీరు 'FarmDoctor' — భారతీయ రైతులకు నమ్మకమైన వ్యవసాయ నిపుణుడు. స్పష్టమైన, ఆచరణాత్మక సలహాలు ఇవ్వండి.",
                    "rules": (
                        "తెలుగులో రాయండి. చిన్న, స్పష్టమైన వాక్యాలు వాడండి. "
                        "కష్టమైన పదాలు వాడకండి — రైతుకు అర్థమయ్యేలా సులభంగా చెప్పండి. "
                        "పొరుగువారిలా స్నేహపూర్వకంగా వివరించండి. "
                        "ప్రతి అంశంలో 2–3 వాక్యాలు రాయండి."
                    ),
                    "problem_label":    "సమస్య",
                    "organic_label":    "సేంద్రీయ పరిష్కారం (సహజ)",
                    "organic_sub1":     "నివారణ చర్యలు",
                    "organic_sub2":     "చికిత్స",
                    "inorganic_label":  "రసాయన పరిష్కారం",
                    "inorganic_sub1":   "నివారణ చర్యలు",
                    "inorganic_sub2":   "చికిత్స (భద్రతా నియమాలతో)",
                    "tip_label":        "విజయ చిట్కా",
                    "additional_label": "అదనపు చిట్కాలు",
                },
                "Marathi": {
                    "intro": "तुम्ही 'FarmDoctor' आहात — भारतीय शेतकऱ्यांसाठी एक विश्वासू कृषी तज्ञ. स्पष्ट आणि व्यावहारिक सल्ला द्या.",
                    "rules": (
                        "मराठीत लिहा. छोटी आणि सोपी वाक्ये वापरा. "
                        "कठीण शब्द टाळा — शेतकऱ्याला सहज समजेल असे सांगा. "
                        "शेजाऱ्यासारखे आपुलकीने समजवा. "
                        "प्रत्येक मुद्द्यात 2–3 वाक्ये लिहा."
                    ),
                    "problem_label":    "समस्या",
                    "organic_label":    "सेंद्रीय उपाय (नैसर्गिक)",
                    "organic_sub1":     "प्रतिबंधक उपाय",
                    "organic_sub2":     "उपचार",
                    "inorganic_label":  "रासायनिक उपाय",
                    "inorganic_sub1":   "प्रतिबंधक उपाय",
                    "inorganic_sub2":   "उपचार (सुरक्षा नियमांसह)",
                    "tip_label":        "यशाची टीप",
                    "additional_label": "अतिरिक्त टिप्स",
                },
                "Tamil": {
                    "intro": "நீங்கள் 'FarmDoctor' — இந்திய விவசாயிகளுக்கான நம்பகமான வேளாண் நிபுணர். தெளிவான, நடைமுறை ஆலோசனைகள் வழங்குங்கள்.",
                    "rules": (
                        "தமிழில் எழுதுங்கள். சிறிய, தெளிவான வாக்கியங்கள் பயன்படுத்துங்கள். "
                        "கடினமான வார்த்தைகள் தவிர்க்கவும் — விவசாயிக்கு புரியும் வகையில் சொல்லுங்கள். "
                        "அண்டை வீட்டாரைப் போல் அன்பாக விளக்குங்கள். "
                        "ஒவ்வொரு புள்ளியிலும் 2–3 வாக்கியங்கள் எழுதுங்கள்."
                    ),
                    "problem_label":    "பிரச்சனை",
                    "organic_label":    "இயற்கை தீர்வு (சேதன)",
                    "organic_sub1":     "தடுப்பு நடவடிக்கைகள்",
                    "organic_sub2":     "சிகிச்சை",
                    "inorganic_label":  "வேதியியல் தீர்வு",
                    "inorganic_sub1":   "தடுப்பு நடவடிக்கைகள்",
                    "inorganic_sub2":   "சிகிச்சை (பாதுகாப்பு விதிகளுடன்)",
                    "tip_label":        "வெற்றி குறிப்பு",
                    "additional_label": "கூடுதல் குறிப்புகள்",
                },
                "Kannada": {
                    "intro": "ನೀವು 'FarmDoctor' — ಭಾರತೀಯ ರೈತರಿಗೆ ವಿಶ್ವಾಸಾರ್ಹ ಕೃಷಿ ತಜ್ಞರು. ಸ್ಪಷ್ಟ ಮತ್ತು ಪ್ರಾಯೋಗಿಕ ಸಲಹೆ ನೀಡಿ.",
                    "rules": (
                        "ಕನ್ನಡದಲ್ಲಿ ಬರೆಯಿರಿ. ಚಿಕ್ಕ, ಸ್ಪಷ್ಟ ವಾಕ್ಯಗಳನ್ನು ಬಳಸಿ. "
                        "ಕಷ್ಟದ ಪದಗಳನ್ನು ತಪ್ಪಿಸಿ — ರೈತನಿಗೆ ಅರ್ಥವಾಗುವಂತೆ ಹೇಳಿ. "
                        "ನೆರೆಹೊರೆಯವರಂತೆ ಪ್ರೀತಿಯಿಂದ ವಿವರಿಸಿ. "
                        "ಪ್ರತಿ ಅಂಶದಲ್ಲಿ 2–3 ವಾಕ್ಯಗಳನ್ನು ಬರೆಯಿರಿ."
                    ),
                    "problem_label":    "ಸಮಸ್ಯೆ",
                    "organic_label":    "ಸಾವಯವ ಪರಿಹಾರ (ನೈಸರ್ಗಿಕ)",
                    "organic_sub1":     "ತಡೆಗಟ್ಟುವ ಕ್ರಮಗಳು",
                    "organic_sub2":     "ಚಿಕಿತ್ಸೆ",
                    "inorganic_label":  "ರಾಸಾಯನಿಕ ಪರಿಹಾರ",
                    "inorganic_sub1":   "ತಡೆಗಟ್ಟುವ ಕ್ರಮಗಳು",
                    "inorganic_sub2":   "ಚಿಕಿತ್ಸೆ (ಸುರಕ್ಷತಾ ನಿಯಮಗಳೊಂದಿಗೆ)",
                    "tip_label":        "ಯಶಸ್ಸಿನ ಸಲಹೆ",
                    "additional_label": "ಹೆಚ್ಚುವರಿ ಸಲಹೆಗಳು",
                },
            }

            cfg = LANG_CONFIG.get(language, LANG_CONFIG["English"])

            sys_prompt = f"""{cfg['intro']}

IMPORTANT RULES:
- {cfg['rules']}
- ALWAYS use these exact emoji markers to start each section (they are required for parsing):
  🔎  💊  🌿  💡  🌾
- Write each section in {language} ONLY.
- Give detailed, practical, actionable advice — not generic statements.
- Each bullet point should have at least 1–2 full sentences of explanation.
- NEVER repeat content across sections.

REQUIRED OUTPUT FORMAT (use exactly these emojis and bold labels):

🔎 **{cfg['problem_label']}**:
[Explain the crop problem clearly. What is causing it? What symptoms does the farmer see?]

🌿 **{cfg['organic_label']}**:
- **{cfg['organic_sub1']}**: [How to prevent this problem naturally. Specific steps.]
- **{cfg['organic_sub2']}**: [How to treat it using natural materials like Neem, ash, cow urine, compost, etc.]

💊 **{cfg['inorganic_label']}**:
- **{cfg['inorganic_sub1']}**: [Technical prevention steps, seed treatment, crop rotation, etc.]
- **{cfg['inorganic_sub2']}**: [Specific chemical/pesticide names, dosage, application method, and safety precautions.]

💡 **{cfg['tip_label']}**:
[One powerful long-term tip for keeping the crop healthy.]

🌾 **{cfg['additional_label']}**:
[2–3 extra tips: soil testing, intercropping, seasonal care, water management, etc.]
"""
            sol_type_map = {
                "Organic":   f"Give ONLY the 🌿 organic section fully. For 💊 inorganic section, write 'Not applicable'.",
                "Inorganic": f"Give ONLY the 💊 inorganic section fully. For 🌿 organic section, write 'Not applicable'.",
                "Both":      "Give BOTH organic and inorganic sections with full detail.",
            }
            sol_type_text = sol_type_map.get(solution_type, sol_type_map["Both"])
            user_prompt = (
                f"Farmer's question: {query}\n\n"
                f"Reference knowledge:\n{context}\n\n"
                f"Instructions: {sol_type_text}\n"
                f"Answer entirely in {language}. Be specific, practical, and helpful."
            )
            
            try:
                if DEMO_MODE:
                    answer_text = generate_demo_response(query, relevant_docs, solution_type, language)
                else:
                    msgs = [SystemMessage(content=sys_prompt), HumanMessage(content=user_prompt)]
                    answer_text = invoke_with_retry(model_instance, msgs).content
            except:
                answer_text = generate_demo_response(query, relevant_docs, solution_type, language)

    # 3. Finalize and Log
    if use_history:
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=answer_text))

    # Calculate confidence for telemetry
    confidence = score_answer_confidence(query, answer_text, relevant_docs, metrics)
    
    # Telemetry Log (Accuracy Logger)
    try:
        accuracy_logger.log_query_response({
            "query": query,
            "demo_mode": DEMO_MODE,
            "docs_retrieved": len(relevant_docs),
            "retrieval_score": metrics.get("avg_score", 0),
            "confidence_score": confidence.get("confidence_score", 0),
            "mode": intent,
            "language": language,
            "solution_type": solution_type,
            "response_length": len(answer_text),
            "has_sources": len(relevant_docs) > 0,
            "notes": f"Process time: {time.time() - start_time:.2f}s"
        })
    except Exception as log_err:
        logger.warning(f"Logging failed: {log_err}")

    return answer_text, relevant_docs



