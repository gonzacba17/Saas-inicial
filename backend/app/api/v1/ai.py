"""
AI assistant endpoints for business insights and analysis.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.db import (
    get_db, Business, AIConversation, AIConversationCRUD, AIAssistantType,
    UserBusinessCRUD, UserBusinessRole
)
from app.schemas import (
    AIQueryRequest, AIResponse, AIConversation as AIConversationSchema,
    AIUsageStats, User as UserSchema
)
from app.api.v1.auth import get_current_user
from app.services_directory.ai_service import ai_service

router = APIRouter()

def check_business_permission(
    business_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
) -> bool:
    """Check if user has permission to access/modify business."""
    if required_roles is None:
        required_roles = [UserBusinessRole.OWNER, UserBusinessRole.MANAGER, UserBusinessRole.EMPLOYEE]
    
    return UserBusinessCRUD.has_permission(db, current_user.id, business_id, required_roles)

def require_business_permission(
    business_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
):
    """Raise HTTPException if user doesn't have permission to access business."""
    if not check_business_permission(business_id, current_user, db, required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this business"
        )

# ========================================
# AI ASSISTANT ENDPOINTS
# ========================================

@router.post("/query", response_model=AIResponse)
def ai_query(
    query: AIQueryRequest,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Process AI query for business insights."""
    # If business_id is provided, check permissions
    if query.business_id:
        business = db.query(Business).filter(Business.id == query.business_id).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Check permissions for business-specific queries
        require_business_permission(query.business_id, current_user, db)
    
    try:
        # Process AI query
        response = ai_service.process_query(
            user_id=str(current_user.id),
            business_id=str(query.business_id) if query.business_id else None,
            query_text=query.query,
            assistant_type=query.assistant_type or AIAssistantType.GENERAL_QUERY
        )
        
        # Save conversation to database
        conversation_data = {
            "user_id": current_user.id,
            "business_id": query.business_id,
            "assistant_type": query.assistant_type or AIAssistantType.GENERAL_QUERY,
            "prompt": query.query,
            "response": response["response"],
            "tokens_used": response.get("tokens_used", 0),
            "response_time_ms": response.get("response_time_ms", 0)
        }
        
        conversation = AIConversationCRUD.create(db, conversation_data)
        
        return {
            "response": response["response"],
            "assistant_type": query.assistant_type or AIAssistantType.GENERAL_QUERY,
            "conversation_id": str(conversation.id),
            "tokens_used": response.get("tokens_used", 0),
            "response_time_ms": response.get("response_time_ms", 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"AI service error: {str(e)}"
        )

@router.get("/conversations", response_model=List[AIConversationSchema])
def list_user_conversations(
    skip: int = 0, 
    limit: int = 100, 
    assistant_type: Optional[AIAssistantType] = None,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """List current user's AI conversations."""
    if assistant_type:
        conversations = AIConversationCRUD.get_by_type(
            db, current_user.id, assistant_type, skip=skip, limit=limit
        )
    else:
        conversations = AIConversationCRUD.get_user_conversations(
            db, current_user.id, skip=skip, limit=limit
        )
    
    return conversations

@router.get("/conversations/business/{business_id}", response_model=List[AIConversationSchema])
def list_business_conversations(
    business_id: UUID,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """List AI conversations for a specific business (business members only)."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    conversations = AIConversationCRUD.get_business_conversations(
        db, business_id, skip=skip, limit=limit
    )
    return conversations

@router.get("/conversations/{conversation_id}", response_model=AIConversationSchema)
def get_conversation(
    conversation_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get AI conversation by ID."""
    conversation = AIConversationCRUD.get_by_id(db, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if user can access this conversation
    if conversation.user_id != current_user.id:
        # If it's a business conversation, check business permissions
        if conversation.business_id:
            require_business_permission(conversation.business_id, current_user, db)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )
    
    return conversation

@router.get("/usage-stats", response_model=AIUsageStats)
def get_usage_stats(
    business_id: Optional[UUID] = None,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get AI usage statistics for current user or specific business."""
    # If business_id is provided, check permissions
    if business_id:
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        require_business_permission(business_id, current_user, db)
    
    stats = AIConversationCRUD.get_usage_stats(db, current_user.id, business_id)
    return stats

@router.post("/product-suggestions")
def get_product_suggestions(
    business_id: UUID,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get AI-powered product suggestions for a business."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    try:
        # Get product suggestions from AI service
        suggestions = ai_service.get_product_suggestions(
            business_id=str(business_id),
            business_type=business.business_type,
            business_name=business.name
        )
        
        # Save conversation
        conversation_data = {
            "user_id": current_user.id,
            "business_id": business_id,
            "assistant_type": AIAssistantType.PRODUCT_SUGGESTION,
            "prompt": f"Product suggestions for {business.name} ({business.business_type})",
            "response": suggestions["response"],
            "tokens_used": suggestions.get("tokens_used", 0),
            "response_time_ms": suggestions.get("response_time_ms", 0)
        }
        
        conversation = AIConversationCRUD.create(db, conversation_data)
        
        return {
            "business_id": str(business_id),
            "suggestions": suggestions["suggestions"],
            "explanation": suggestions["response"],
            "conversation_id": str(conversation.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get product suggestions: {str(e)}"
        )

@router.post("/sales-analysis")
def get_sales_analysis(
    business_id: UUID,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get AI-powered sales analysis for a business."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    try:
        # Get sales analysis from AI service
        analysis = ai_service.get_sales_analysis(
            business_id=str(business_id)
        )
        
        # Save conversation
        conversation_data = {
            "user_id": current_user.id,
            "business_id": business_id,
            "assistant_type": AIAssistantType.SALES_ANALYSIS,
            "prompt": f"Sales analysis for {business.name}",
            "response": analysis["response"],
            "tokens_used": analysis.get("tokens_used", 0),
            "response_time_ms": analysis.get("response_time_ms", 0)
        }
        
        conversation = AIConversationCRUD.create(db, conversation_data)
        
        return {
            "business_id": str(business_id),
            "analysis": analysis["analysis"],
            "insights": analysis["insights"],
            "recommendations": analysis["recommendations"],
            "conversation_id": str(conversation.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get sales analysis: {str(e)}"
        )
