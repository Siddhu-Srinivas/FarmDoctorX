import os
import glob
from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import logging
from config import INGESTION_CONFIG, KNOWLEDGE_BASE_REQUIREMENTS

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants - MUST match answer_generation.py
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # CRITICAL: Must match answer_generation.py
EMBEDDING_DIMENSION = 384
CHUNK_SIZE = INGESTION_CONFIG["chunk_size"]  # Updated from 500
CHUNK_OVERLAP = INGESTION_CONFIG["chunk_overlap"]  # Updated from 100
PINECONE_INDEX_NAME = "farmsdoctor-rag"

logger.info(f"Embedding model: {EMBEDDING_MODEL_NAME}, Dimension: {EMBEDDING_DIMENSION}")
logger.info(f"Chunk config: size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")

def validate_knowledge_base_readiness():
    """Validate that knowledge base meets minimum requirements"""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_path = os.path.normpath(os.path.join(base_dir, "docs"))
    
    logger.info("Validating knowledge base...")
    
    files = []
    for ext in ["*.txt", "*.pdf"]:
        files.extend(glob.glob(os.path.join(docs_path, ext)))
    
    num_docs = len(files)
    min_docs = KNOWLEDGE_BASE_REQUIREMENTS["min_documents"]
    
    if num_docs < min_docs:
        logger.error(f"⚠️ INSUFFICIENT KNOWLEDGE BASE: {num_docs} docs found, {min_docs} required")
        logger.info("Add agricultural domain documents to /docs folder:")
        for cat in KNOWLEDGE_BASE_REQUIREMENTS["required_categories"]:
            logger.info(f"  - {cat}")
        return False
    
    logger.info(f"✓ Knowledge base ready: {num_docs} documents found")
    return True

def validate_ingestion_results(documents, chunks):
    """Validate ingestion quality metrics"""
    logger.info("Validating ingestion results...")
    
    total_docs = len(documents)
    total_chunks = len(chunks)
    avg_chunk_size = sum(len(c.page_content) for c in chunks) / total_chunks if chunks else 0
    
    metrics = {
        "documents": total_docs,
        "chunks": total_chunks,
        "avg_chunk_size": avg_chunk_size,
        "coverage": {
            "files": [d.metadata.get('source', 'Unknown') for d in documents]
        }
    }
    
    # Validation checks
    if total_chunks < 50:
        logger.warning(f"⚠️ Low chunk count: {total_chunks}. Consider larger KB")
    if avg_chunk_size < 400:
        logger.warning(f"⚠️ Small average chunk: {avg_chunk_size} chars")
    
    logger.info(f"✓ Ingestion: {total_docs} docs → {total_chunks} chunks (avg {avg_chunk_size:.0f} chars)")
    return metrics

def load_documents(docs_path="docs"):
    """Load all text and PDF files from the docs directory

    The default ``docs_path`` is relative to the project root, not the
    current working directory.  When the script is invoked from the ``bankend``
    subfolder (as in development), the simple relative path would point at
    ``bankend/docs`` which usually doesn't exist.  We compute an absolute path
    based on this file's location so the pipeline works no matter where it is
    executed from.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_path = os.path.normpath(os.path.join(base_dir, docs_path))

    logger.info(f"Loading documents from {docs_path}...")
    
    # Check if docs directory exists
    if not os.path.exists(docs_path):
        logger.error(f"Document directory {docs_path} not found, creating empty folder.")
        os.makedirs(docs_path, exist_ok=True)
        raise FileNotFoundError(
            f"The directory {docs_path} did not exist. A new empty folder has been created. "
            "Please add your company documents (txt/pdf) to this directory and rerun the script."
        )
    
    documents = []
    
    # Load all .txt files from the docs directory
    try:
        txt_loader = DirectoryLoader(
            path=docs_path,
            glob="*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8-sig"}
        )
        txt_documents = txt_loader.load()
        documents.extend(txt_documents)
        logger.info(f"Loaded {len(txt_documents)} text files")
    except Exception as e:
        logger.warning(f"No text files found: {e}")
    
    # Load all .pdf files from the docs directory
    try:
        pdf_loader = DirectoryLoader(
            path=docs_path,
            glob="*.pdf",
            loader_cls=PyPDFLoader
        )
        pdf_documents = pdf_loader.load()
        documents.extend(pdf_documents)
        logger.info(f"Loaded {len(pdf_documents)} PDF documents")
    except Exception as e:
        logger.warning(f"No PDF files found: {e}")
    
    if not documents:
        raise FileNotFoundError(f"No .txt or .pdf files found in {docs_path}. Please add your company documents.")
    
    logger.info(f"Total documents loaded: {len(documents)}")
    
    # Show first 2 documents for verification
    for i, doc in enumerate(documents[:2]):
        source = doc.metadata.get('source', 'Unknown')
        content_len = len(doc.page_content)
        logger.info(f"Document {i+1}: {source} ({content_len} chars)")

    return documents

def split_documents(documents, chunk_size=None, chunk_overlap=None):
    """Split documents into semantically meaningful chunks with overlap.
    
    Uses RecursiveCharacterTextSplitter for better semantic boundaries.
    
    Args:
        documents: List of documents to split
        chunk_size: Size of each chunk (default: CHUNK_SIZE)
        chunk_overlap: Overlap between chunks (default: CHUNK_OVERLAP)
        
    Returns:
        List of document chunks
    """
    if chunk_size is None:
        chunk_size = CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = CHUNK_OVERLAP
        
    logger.info(f"Splitting documents into chunks: size={chunk_size}, overlap={chunk_overlap}...")
    
    # Use RecursiveCharacterTextSplitter for better semantic boundaries
    # This splits on multiple delimiters (newlines, spaces, punctuation) to maintain semantic meaning
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=INGESTION_CONFIG["separators"],  # Updated separators for agricultural content
        length_function=len
    )
    
    chunks = text_splitter.split_documents(documents)
    
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
    
    # Show sample chunks for verification
    if chunks:
        for i, chunk in enumerate(chunks[:3]):
            source = chunk.metadata.get('source', 'Unknown')
            content_len = len(chunk.page_content)
            logger.debug(f"Chunk {i+1} from {source}: {content_len} chars")
        
        if len(chunks) > 3:
            logger.info(f"... and {len(chunks) - 3} more chunks")
    
    return chunks

def clear_vector_store(index_name=None):
    """Clear the existing Pinecone index to remove old data.
    
    Args:
        index_name: Name of the Pinecone index (default: PINECONE_INDEX_NAME)
    """
    if index_name is None:
        index_name = PINECONE_INDEX_NAME
        
    try:
        logger.info(f"Clearing Pinecone index: {index_name}...")
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        pc.delete_index(index_name)
        logger.info(f"Pinecone index {index_name} deleted successfully.")
    except Exception as e:
        logger.warning(f"No existing index found at {index_name} or error during deletion: {e}")

def create_vector_store(chunks, index_name=None):
    """Create and store vectors in Pinecone.
    
    Uses the SAME embedding model as answer_generation.py for consistency.
    
    Args:
        chunks: List of document chunks to embed
        index_name: Name of the Pinecone index (default: PINECONE_INDEX_NAME)
        
    Returns:
        PineconeVectorStore instance
    """
    if index_name is None:
        index_name = PINECONE_INDEX_NAME
        
    logger.info("Creating embeddings and storing in Pinecone...")
    
    # CRITICAL: Use the SAME embedding model as answer_generation.py
    logger.info(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}...")
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    logger.info("Embedding model initialized successfully")
    
    # Initialize Pinecone
    logger.info("Connecting to Pinecone...")
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    
    # Get or create index
    try:
        logger.info(f"Checking for existing Pinecone index: {index_name}")
        index = pc.Index(index_name)
        logger.info(f"Using existing Pinecone index: {index_name}")
    except Exception as e:
        logger.warning(f"Index not found, creating new one: {index_name}")
        logger.info(f"Creating new Pinecone index with dimension {EMBEDDING_DIMENSION}...")
        # Create index with dimension matching the embedding model
        pc.create_index(
            name=index_name,
            dimension=EMBEDDING_DIMENSION,  # Must match the embedding model output dimension
            metric="cosine",  # Cosine similarity for semantic search
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        import time
        logger.info("Waiting for index to initialize...")
        time.sleep(3)  # Wait for index to be created
        index = pc.Index(index_name)
        logger.info(f"Pinecone index {index_name} created successfully")
    
    # Create vector store and upload documents
    logger.info(f"Creating vector store and uploading {len(chunks)} chunks to Pinecone...")
    try:
        vectorstore = PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embedding_model,
            index_name=index_name
        )
        logger.info(f"Vector store created in Pinecone index: {index_name}")
        logger.info(f"Successfully stored {len(chunks)} document chunks")
    except Exception as e:
        logger.error(f"Failed to create vector store: {e}")
        raise
    
    return vectorstore

def main(reset=False):
    """Main ingestion pipeline.
    
    Args:
        reset: If True, deletes existing index and re-ingests all documents
    """
    logger.info("="*80)
    logger.info("RAG Document Ingestion Pipeline (Pinecone + HuggingFace Embeddings)")
    logger.info("="*80)
    logger.info(f"Embedding Model: {EMBEDDING_MODEL_NAME}")
    logger.info(f"Chunk Configuration: size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")
    logger.info(f"Pinecone Index: {PINECONE_INDEX_NAME}")
    
    # Validate API keys
    if not os.getenv("PINECONE_API_KEY"):
        logger.error("PINECONE_API_KEY not found in environment variables.")
        raise ValueError("PINECONE_API_KEY not found in .env file. Please set it first.")
    
    # Clear old data if requested
    if reset:
        logger.info("Reset flag set: Clearing existing index...")
        clear_vector_store(PINECONE_INDEX_NAME)
    
    logger.info("\nInitializing Pinecone vector store...\n")
    
    # Step 1: Load documents
    try:
        documents = load_documents("docs")
    except FileNotFoundError as fnf:
        logger.error(f"{fnf}")
        logger.error("Pipeline terminating because document directory is empty.")
        raise

    # Validate knowledge base readiness
    kb_ready = validate_knowledge_base_readiness()
    if not kb_ready:
        logger.warning("Knowledge base validation failed - proceeding with available documents for testing")
        logger.info("For production accuracy >90%, add 15+ agricultural domain documents")
    else:
        logger.info("Knowledge base validation passed")

    # Step 2: Split into chunks
    chunks = split_documents(documents)
    
    # Validate ingestion results
    ingestion_metrics = validate_ingestion_results(documents, chunks)
    
    # Step 3: Create vector store in Pinecone
    vectorstore = create_vector_store(chunks, PINECONE_INDEX_NAME)
    
    logger.info("\n" + "="*80)
    logger.info("SUCCESS! Ingestion complete!")
    logger.info(f"Documents: {len(documents)} | Chunks: {len(chunks)}")
    logger.info(f"Vector store ready at Pinecone index: {PINECONE_INDEX_NAME}")
    logger.info("RAG queries will now retrieve relevant documents for each question.")
    logger.info("="*80)
    
    return vectorstore

if __name__ == "__main__":
    # Set reset=True to clear old data and re-ingest documents
    main(reset=True)

