from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from history_db import (
    save_conversation,
    get_all_conversations,
    get_conversation_by_id,
    delete_conversation,
    clear_all_conversations,
    get_conversations_paginated,
    search_conversations,
    filter_by_solution_type
)


router = APIRouter(prefix="/api/history", tags=["history"])

class HistoryRequest(BaseModel):
    question: str
    answer: str
    solution_type: str

class HistoryResponse(BaseModel):
    id: int
    question: str
    answer: str
    solution_type: str
    timestamp: str

@router.post("/save")
async def save_history(request: HistoryRequest):
    """Save a new conversation to history."""
    try:
        conversation_id = save_conversation(
            question=request.question,
            answer=request.answer,
            solution_type=request.solution_type
        )
        return {
            "success": True,
            "id": conversation_id,
            "message": "Conversation saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
async def get_history():
    """Get all conversations from history."""
    try:
        conversations = get_all_conversations()
        return {
            "success": True,
            "count": len(conversations),
            "conversations": conversations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/paginated")
async def get_paginated_history(page: int = 1, per_page: int = 20):
    """Get paginated conversations."""
    try:
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
            
        result = get_conversations_paginated(page, per_page)
        return {
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: int):
    """Get a specific conversation by ID."""
    try:
        conversation = get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "success": True,
            "conversation": conversation
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{conversation_id}")
async def delete_from_history(conversation_id: int):
    """Delete a specific conversation."""
    try:
        # Check if conversation exists
        conversation = get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        delete_conversation(conversation_id)
        return {
            "success": True,
            "message": "Conversation deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("")
async def clear_history():
    """Clear all conversations from history."""
    try:
        clear_all_conversations()
        return {
            "success": True,
            "message": "All conversations cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_history(q: str):
    """Search conversations by keyword."""
    try:
        if not q or len(q) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        conversations = search_conversations(q)
        return {
            "success": True,
            "query": q,
            "count": len(conversations),
            "conversations": conversations
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filter/{solution_type}")
async def filter_history(solution_type: str):
    """Filter conversations by solution type."""
    try:
        valid_types = ["Organic Only", "Inorganic Only", "Both"]
        if solution_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid solution type. Must be one of: {', '.join(valid_types)}"
            )
        
        conversations = filter_by_solution_type(solution_type)
        return {
            "success": True,
            "solution_type": solution_type,
            "count": len(conversations),
            "conversations": conversations
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
