"""
AI Service for integrating with OpenAI and generating business insights.
This service provides intelligent suggestions for products, sales analysis, and business insights.
"""
import time
import os
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.db import AIConversationCRUD, AIAssistantType, AnalyticsCRUD, ProductCRUD, BusinessCRUD
from app.schemas import AIQueryRequest

class AIService:
    """Service for handling AI assistant functionality."""
    
    def __init__(self):
        # For development, we'll use a mock AI service
        # In production, this would integrate with OpenAI API
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.mock_mode = not self.api_key or self.api_key == "mock"
    
    async def process_query(self, db: Session, user_id: str, query: AIQueryRequest) -> Dict[str, Any]:
        """Process an AI query and return response with metadata."""
        start_time = time.time()
        
        try:
            # Generate response based on assistant type
            if query.assistant_type == AIAssistantType.PRODUCT_SUGGESTION:
                response = await self._generate_product_suggestions(db, user_id, query)
            elif query.assistant_type == AIAssistantType.SALES_ANALYSIS:
                response = await self._generate_sales_analysis(db, user_id, query)
            elif query.assistant_type == AIAssistantType.BUSINESS_INSIGHTS:
                response = await self._generate_business_insights(db, user_id, query)
            else:
                response = await self._generate_general_response(db, user_id, query)
            
            response_time_ms = int((time.time() - start_time) * 1000)
            tokens_used = self._estimate_tokens(query.prompt + response)
            
            # Save conversation to database
            conversation_data = {
                "user_id": user_id,
                "business_id": query.business_id,
                "assistant_type": query.assistant_type,
                "prompt": query.prompt,
                "response": response,
                "tokens_used": tokens_used,
                "response_time_ms": response_time_ms
            }
            
            conversation = AIConversationCRUD.create(db, conversation_data)
            
            return {
                "response": response,
                "conversation_id": conversation.id,
                "tokens_used": tokens_used,
                "response_time_ms": response_time_ms
            }
            
        except Exception as e:
            # In case of error, still save the failed attempt
            response_time_ms = int((time.time() - start_time) * 1000)
            error_response = f"Lo siento, hubo un error procesando tu consulta: {str(e)}"
            
            conversation_data = {
                "user_id": user_id,
                "business_id": query.business_id,
                "assistant_type": query.assistant_type,
                "prompt": query.prompt,
                "response": error_response,
                "tokens_used": 0,
                "response_time_ms": response_time_ms
            }
            
            conversation = AIConversationCRUD.create(db, conversation_data)
            
            return {
                "response": error_response,
                "conversation_id": conversation.id,
                "tokens_used": 0,
                "response_time_ms": response_time_ms
            }
    
    async def _generate_product_suggestions(self, db: Session, user_id: str, query: AIQueryRequest) -> str:
        """Generate product suggestions based on business data."""
        if not query.business_id:
            return "Para generar sugerencias de productos, necesito que especifiques el negocio."
        
        # Get business data for context
        business = BusinessCRUD.get_by_id(db, query.business_id)
        if not business:
            return "No se encontró el negocio especificado."
        
        # Get existing products for context
        products = ProductCRUD.get_by_business(db, query.business_id)
        
        if self.mock_mode:
            return self._mock_product_suggestions(business, products, query.prompt)
        else:
            return await self._openai_product_suggestions(business, products, query.prompt)
    
    async def _generate_sales_analysis(self, db: Session, user_id: str, query: AIQueryRequest) -> str:
        """Generate sales analysis based on business analytics."""
        if not query.business_id:
            return "Para generar análisis de ventas, necesito que especifiques el negocio."
        
        # Get analytics data
        analytics = AnalyticsCRUD.get_business_analytics(db, query.business_id)
        daily_sales = AnalyticsCRUD.get_daily_sales(db, query.business_id, 30)
        
        if self.mock_mode:
            return self._mock_sales_analysis(analytics, daily_sales, query.prompt)
        else:
            return await self._openai_sales_analysis(analytics, daily_sales, query.prompt)
    
    async def _generate_business_insights(self, db: Session, user_id: str, query: AIQueryRequest) -> str:
        """Generate general business insights."""
        if not query.business_id:
            return "Para generar insights de negocio, necesito que especifiques el negocio."
        
        # Get comprehensive business data
        business = BusinessCRUD.get_by_id(db, query.business_id)
        analytics = AnalyticsCRUD.get_business_analytics(db, query.business_id)
        
        if self.mock_mode:
            return self._mock_business_insights(business, analytics, query.prompt)
        else:
            return await self._openai_business_insights(business, analytics, query.prompt)
    
    async def _generate_general_response(self, db: Session, user_id: str, query: AIQueryRequest) -> str:
        """Generate general AI response."""
        if self.mock_mode:
            return self._mock_general_response(query.prompt)
        else:
            return await self._openai_general_response(query.prompt)
    
    # Mock AI responses for development
    def _mock_product_suggestions(self, business, products, prompt) -> str:
        product_names = [p.name for p in products[:3]]
        return f"""**Sugerencias de productos para {business.name}:**

Basándome en tu consulta "{prompt}" y analizando tus productos actuales ({', '.join(product_names) if product_names else 'sin productos'}), aquí tienes algunas recomendaciones:

🎯 **Productos recomendados:**
1. **Combo especial** - Combina tus productos más populares con descuento
2. **Producto premium** - Versión mejorada de tu producto estrella  
3. **Producto complementario** - Algo que complemente tu oferta actual

💡 **Estrategias:**
- Considera productos de temporada
- Analiza qué piden más tus clientes
- Explora productos con mayor margen de ganancia

¿Te gustaría que profundice en alguna de estas sugerencias?"""
    
    def _mock_sales_analysis(self, analytics, daily_sales, prompt) -> str:
        return f"""**Análisis de ventas:**

📊 **Resumen actual:**
- Total de órdenes: {analytics['total_orders']}
- Ingresos totales: ${analytics['total_revenue']:.2f}
- Órdenes pendientes: {analytics['pending_orders']}

📈 **Tendencias identificadas:**
- Promedio de ventas diarias: ${sum(d['revenue'] for d in daily_sales[-7:]) / 7:.2f}
- Productos top: {len(analytics['top_products'])} productos destacados
- Tasa de conversión estimada: 65%

🎯 **Recomendaciones:**
1. Optimizar horarios de mayor venta
2. Promocionar productos con bajo rendimiento
3. Implementar estrategias de retención de clientes

¿Qué aspecto específico te gustaría analizar más a fondo?"""
    
    def _mock_business_insights(self, business, analytics, prompt) -> str:
        completion_rate = (analytics['completed_orders'] / max(analytics['total_orders'], 1)) * 100
        return f"""**Insights para {business.name}:**

🏢 **Estado del negocio:**
- Tipo: {business.business_type}
- Tasa de completación: {completion_rate:.1f}%
- Ingresos totales: ${analytics['total_revenue']:.2f}

📊 **Oportunidades identificadas:**
1. **Mejora operacional**: {analytics['pending_orders']} órdenes pendientes requieren atención
2. **Crecimiento**: Los productos top generan el 70% de los ingresos
3. **Retención**: Implementar programa de fidelización

🚀 **Próximos pasos recomendados:**
- Automatizar procesos de órdenes
- Diversificar catálogo de productos
- Implementar métricas de satisfacción

¿En qué área te gustaría enfocar los esfuerzos?"""
    
    def _mock_general_response(self, prompt) -> str:
        return f"""Entiendo tu consulta: "{prompt}"

Como asistente de negocio, puedo ayudarte con:
- 📦 Sugerencias de productos
- 📊 Análisis de ventas  
- 💡 Insights de negocio
- 📈 Estrategias de crecimiento

Para brindarte una respuesta más específica, ¿podrías contarme más sobre tu negocio o el aspecto particular que te interesa analizar?"""
    
    # Placeholder for OpenAI integration
    async def _openai_product_suggestions(self, business, products, prompt) -> str:
        # Here would go the actual OpenAI API call
        return "OpenAI integration pending - using mock response for now."
    
    async def _openai_sales_analysis(self, analytics, daily_sales, prompt) -> str:
        # Here would go the actual OpenAI API call
        return "OpenAI integration pending - using mock response for now."
    
    async def _openai_business_insights(self, business, analytics, prompt) -> str:
        # Here would go the actual OpenAI API call
        return "OpenAI integration pending - using mock response for now."
    
    async def _openai_general_response(self, prompt) -> str:
        # Here would go the actual OpenAI API call
        return "OpenAI integration pending - using mock response for now."
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimation: 1 token ≈ 4 characters for Spanish/English
        return len(text) // 4

# Global instance
ai_service = AIService()