"""
Advanced chatbot endpoints with LangChain + ChromaDB RAG integration.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from uuid import UUID

from app.db.db import get_db, ChatHistoryCRUD, User
from app.api.v1.auth import get_current_user
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    AddDocumentRequest,
    AddDocumentResponse,
    ChatHistoryItem
)
from app.services_directory.langchain_service import langchain_service
from app.services_directory.vector_store import vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI assistant. Optionally use RAG with vector store.
    """
    try:
        user_id = str(current_user.id)
        
        conversation_history = []
        recent_chats = ChatHistoryCRUD.get_conversation(db, current_user.id, limit=10)
        
        for chat in recent_chats:
            conversation_history.append({
                "role": chat.role,
                "content": chat.content
            })
        
        if request.use_rag and request.collection_name:
            if not vector_store.is_available():
                raise HTTPException(
                    status_code=503,
                    detail="Vector store not available. RAG disabled."
                )
            
            retriever = vector_store.get_retriever(
                collection_name=request.collection_name,
                user_id=user_id,
                k=5
            )
            
            if retriever:
                result = await langchain_service.query_with_rag(
                    question=request.message,
                    user_id=user_id,
                    retriever=retriever,
                    conversation_history=conversation_history
                )
            else:
                result = await langchain_service.chat(
                    message=request.message,
                    user_id=user_id,
                    conversation_history=conversation_history
                )
        else:
            result = await langchain_service.chat(
                message=request.message,
                user_id=user_id,
                conversation_history=conversation_history
            )
        
        ChatHistoryCRUD.create(db, {
            "user_id": current_user.id,
            "business_id": UUID(request.business_id) if request.business_id else None,
            "role": "user",
            "content": request.message,
            "tokens_used": 0,
            "model": result.get("model", "gpt-4")
        })
        
        ChatHistoryCRUD.create(db, {
            "user_id": current_user.id,
            "business_id": UUID(request.business_id) if request.business_id else None,
            "role": "assistant",
            "content": result.get("response") or result.get("answer", ""),
            "tokens_used": result.get("tokens_used", {}).get("total_tokens", 0) if isinstance(result.get("tokens_used"), dict) else 0,
            "model": result.get("model", "gpt-4")
        })
        
        return ChatResponse(
            success=result.get("success", False),
            response=result.get("response") or result.get("answer", ""),
            user_id=user_id,
            timestamp=result.get("timestamp", ""),
            tokens_used=result.get("tokens_used"),
            model=result.get("model"),
            mock=result.get("mock", False),
            message=result.get("message")
        )
        
    except Exception as e:
        logger.error(f"Chat query error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat query: {str(e)}"
        )


@router.post("/add-document", response_model=AddDocumentResponse)
async def add_document(
    request: AddDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add document to vector store for RAG.
    """
    try:
        if not vector_store.is_available():
            raise HTTPException(
                status_code=503,
                detail="Vector store not available"
            )
        
        user_id = str(current_user.id)
        
        texts = langchain_service.split_text(request.text)
        
        metadatas = []
        for i, _ in enumerate(texts):
            meta = request.metadata.copy() if request.metadata else {}
            meta.update({
                "user_id": user_id,
                "chunk_index": i,
                "total_chunks": len(texts)
            })
            metadatas.append(meta)
        
        result = vector_store.add_documents(
            collection_name=request.collection_name,
            documents=texts,
            metadatas=metadatas,
            user_id=user_id if not request.business_id else None
        )
        
        return AddDocumentResponse(
            success=result.get("success", False),
            document_ids=result.get("document_ids", []),
            count=result.get("count", 0),
            collection=result.get("collection", request.collection_name),
            mock=result.get("mock", False),
            message=result.get("message")
        )
        
    except Exception as e:
        logger.error(f"Add document error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding document: {str(e)}"
        )


@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history for current user.
    """
    try:
        history = ChatHistoryCRUD.get_user_history(db, current_user.id, limit=limit, skip=skip)
        
        history_items = [
            ChatHistoryItem(
                id=str(chat.id),
                user_id=str(chat.user_id),
                business_id=str(chat.business_id) if chat.business_id else None,
                role=chat.role,
                content=chat.content,
                tokens_used=chat.tokens_used or 0,
                model=chat.model or "gpt-4",
                created_at=chat.created_at
            )
            for chat in history
        ]
        
        return ChatHistoryResponse(
            success=True,
            history=history_items,
            count=len(history_items)
        )
        
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )


@router.delete("/history", status_code=204)
def delete_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete all chat history for current user.
    """
    try:
        ChatHistoryCRUD.delete_user_history(db, current_user.id)
        return None
        
    except Exception as e:
        logger.error(f"Delete history error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting history: {str(e)}"
        )


@router.get("/status")
def chatbot_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check chatbot service status.
    """
    return {
        "langchain_available": langchain_service.is_available(),
        "vector_store_available": vector_store.is_available(),
        "openai_api_configured": bool(langchain_service.openai_api_key),
        "message": "Chatbot service ready" if langchain_service.is_available() else "Running in mock mode"
    }
