from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 80)
print("DIAGNOSTIC TEST: Knowledge Base Content")
print("=" * 80)

embedding = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
db = PineconeVectorStore(index_name="farmsdoctor-rag", embedding=embedding)

test_queries = [
    "rice issue",
    "disease problem",
    "crop damage",
    "agricultural problem",
    "pest disease",
    "what is rice"
]

print("\nTesting retrieval with different queries:\n")
for query in test_queries:
    docs = db.similarity_search(query, k=3)
    print(f"Query: '{query}' ")
    print(f"  ✓ Found: {len(docs)} documents")
    if docs:
        print(f"  Top match (first 100 chars): {docs[0].page_content[:100]}...")
    else:
        print(f"  ✗ NO MATCHES!")
    print()

# Now try the user's exact query
print("=" * 80)
print("EXACT USER QUERY:")
print("=" * 80)
user_query = "what is the issue of rice?"
docs = db.similarity_search(user_query, k=5)
print(f"\nQuery: '{user_query}'")
print(f"Results: {len(docs)} documents found")
if not docs:
    print("✗ This is why you're seeing the error message!")
    print("\nPossible Reasons:")
    print("1. The DATASETS.pdf doesn't contain disease/issue information")
    print("2. The content is too different from your search query")
    print("3. Semantic similarity is too low")
else:
    print("\n✓ Successfully retrieved documents!")
    for i, doc in enumerate(docs, 1):
        print(f"  Document {i}: {doc.page_content[:150]}...")
