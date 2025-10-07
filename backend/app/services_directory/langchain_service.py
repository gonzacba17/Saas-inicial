"""
LangChain service for advanced chatbot with RAG (Retrieval-Augmented Generation).
Integrates OpenAI LLM with ChromaDB vector store for contextual conversations.
"""
import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain dependencies not installed. Running in mock mode.")


SYSTEM_PROMPT = """Eres un asistente virtual inteligente para gestión de cafeterías y negocios.
Tu nombre es CaféBot IA y tu objetivo es ayudar a los usuarios con:

- Gestión de comprobantes (facturas, recibos, notas de crédito)
- Análisis de vencimientos y pagos pendientes
- Consultas sobre normativas fiscales argentinas (AFIP, CUIT, IVA)
- Interpretación de datos extraídos por OCR
- Recomendaciones para optimización de gastos

Responde siempre en español argentino, de forma clara, profesional y concisa.
Si tienes acceso a documentos del usuario (via RAG), úsalos para dar respuestas precisas.
Si no tienes información suficiente, indícalo claramente."""


class LangChainService:
    """Service for LangChain-powered conversational AI with memory and RAG."""
    
    def __init__(self):
        """Initialize LangChain service with OpenAI and embeddings."""
        self.available = LANGCHAIN_AVAILABLE
        
        if not self.available:
            logger.warning("LangChain service initialized in mock mode")
            return
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            self.available = False
            return
        
        try:
            self.llm = ChatOpenAI(
                model_name="gpt-4",
                temperature=0.7,
                openai_api_key=self.openai_api_key,
                max_tokens=1000
            )
            
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.openai_api_key
            )
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            logger.info("LangChain service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain service: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if LangChain service is available."""
        return self.available
    
    async def chat(
        self,
        message: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context_documents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Chat with the AI assistant with conversation history and optional RAG context.
        
        Args:
            message: User's message
            user_id: User ID for tracking
            conversation_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
            context_documents: Optional list of document texts for RAG context
        
        Returns:
            Dict with response, tokens used, and metadata
        """
        if not self.available:
            return self._mock_chat(message)
        
        try:
            messages = [SystemMessage(content=SYSTEM_PROMPT)]
            
            if conversation_history:
                for msg in conversation_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            if context_documents:
                context_text = "\n\n".join(context_documents)
                context_msg = f"Contexto relevante de documentos del usuario:\n{context_text}"
                messages.append(SystemMessage(content=context_msg))
            
            messages.append(HumanMessage(content=message))
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "success": True,
                "response": response.content,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": response.response_metadata.get("token_usage", {}),
                "model": "gpt-4",
                "mock": False
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Lo siento, ocurrió un error al procesar tu mensaje.",
                "mock": False
            }
    
    async def query_with_rag(
        self,
        question: str,
        user_id: str,
        retriever,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Query with Retrieval-Augmented Generation using vector store.
        
        Args:
            question: User's question
            user_id: User ID
            retriever: LangChain retriever from vector store
            conversation_history: Previous conversation
        
        Returns:
            Dict with answer and source documents
        """
        if not self.available:
            return self._mock_query(question)
        
        try:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            if conversation_history:
                for msg in conversation_history:
                    if msg["role"] == "user":
                        memory.chat_memory.add_user_message(msg["content"])
                    elif msg["role"] == "assistant":
                        memory.chat_memory.add_ai_message(msg["content"])
            
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                return_source_documents=True,
                verbose=False
            )
            
            result = await qa_chain.ainvoke({"question": question})
            
            source_docs = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in result.get("source_documents", [])
            ]
            
            return {
                "success": True,
                "answer": result["answer"],
                "source_documents": source_docs,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mock": False
            }
            
        except Exception as e:
            logger.error(f"RAG query error: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "No pude procesar tu pregunta con el contexto disponible.",
                "mock": False
            }
    
    async def simple_query(self, question: str, user_id: str) -> Dict[str, Any]:
        """
        Simple query without RAG or conversation history.
        
        Args:
            question: User's question
            user_id: User ID
        
        Returns:
            Dict with answer
        """
        if not self.available:
            return self._mock_query(question)
        
        try:
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=question)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "success": True,
                "answer": response.content,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mock": False
            }
            
        except Exception as e:
            logger.error(f"Simple query error: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "No pude procesar tu pregunta.",
                "mock": False
            }
    
    def split_text(self, text: str) -> List[str]:
        """
        Split long text into chunks for embedding.
        
        Args:
            text: Text to split
        
        Returns:
            List of text chunks
        """
        if not self.available:
            return [text]
        
        return self.text_splitter.split_text(text)
    
    def _mock_chat(self, message: str) -> Dict[str, Any]:
        """Mock chat response when LangChain unavailable."""
        mock_responses = {
            "hola": "¡Hola! Soy CaféBot IA, tu asistente para gestión de cafeterías. ¿En qué puedo ayudarte?",
            "factura": "Las facturas en Argentina se clasifican en Tipo A (para responsables inscriptos), Tipo B (para consumidores finales y monotributistas), y Tipo C (sin discriminar IVA). ¿Necesitas ayuda con alguna factura específica?",
            "cuit": "El CUIT (Clave Única de Identificación Tributaria) es un número de 11 dígitos que identifica a personas y empresas ante AFIP. Formato: XX-XXXXXXXX-X",
            "vencimiento": "Puedo ayudarte a gestionar vencimientos de impuestos y pagos. ¿Qué información necesitas?",
            "default": "Entiendo tu consulta. Soy CaféBot IA y puedo ayudarte con gestión de comprobantes, vencimientos, consultas fiscales y análisis de datos. (Nota: Actualmente en modo demo - LangChain no está instalado)"
        }
        
        message_lower = message.lower()
        response = mock_responses.get("default")
        
        for keyword, resp in mock_responses.items():
            if keyword in message_lower:
                response = resp
                break
        
        return {
            "success": False,
            "response": response,
            "timestamp": datetime.utcnow().isoformat(),
            "mock": True,
            "message": "LangChain dependencies not installed. Showing mock response."
        }
    
    def _mock_query(self, question: str) -> Dict[str, Any]:
        """Mock query response when LangChain unavailable."""
        return {
            "success": False,
            "answer": "Esta es una respuesta simulada. Para respuestas reales con IA, instala las dependencias de LangChain (langchain, chromadb, sentence-transformers).",
            "source_documents": [],
            "mock": True,
            "timestamp": datetime.utcnow().isoformat()
        }


langchain_service = LangChainService()
