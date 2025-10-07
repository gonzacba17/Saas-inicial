"""
Vector store service using ChromaDB for persistent document storage and retrieval.
Enables RAG (Retrieval-Augmented Generation) for contextual chatbot responses.
"""
import os
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    from langchain_openai import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.docstore.document import Document
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB dependencies not installed. Running in mock mode.")


class VectorStoreService:
    """Service for managing ChromaDB vector store with persistent storage."""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize ChromaDB vector store.
        
        Args:
            persist_directory: Directory for persistent storage (default: ./chroma_db)
        """
        self.available = CHROMADB_AVAILABLE
        
        if not self.available:
            logger.warning("VectorStore service initialized in mock mode")
            return
        
        if persist_directory is None:
            backend_dir = Path(__file__).parent.parent.parent
            persist_directory = str(backend_dir / "chroma_db")
        
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            self.available = False
            return
        
        try:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.openai_api_key
            )
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            logger.info(f"ChromaDB initialized with persist_directory: {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if vector store is available."""
        return self.available
    
    def get_or_create_collection(
        self,
        collection_name: str,
        user_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get or create a ChromaDB collection for a user.
        
        Args:
            collection_name: Base name for collection
            user_id: Optional user ID to namespace the collection
        
        Returns:
            Chroma vector store instance or None
        """
        if not self.available:
            return None
        
        try:
            if user_id:
                full_collection_name = f"{collection_name}_{user_id}"
            else:
                full_collection_name = collection_name
            
            full_collection_name = full_collection_name.replace("-", "_")
            
            vectorstore = Chroma(
                collection_name=full_collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
                client=self.client
            )
            
            logger.info(f"Collection '{full_collection_name}' ready")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error getting/creating collection: {e}")
            return None
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add documents to vector store.
        
        Args:
            collection_name: Collection name
            documents: List of document texts
            metadatas: Optional list of metadata dicts for each document
            user_id: Optional user ID for namespacing
        
        Returns:
            Dict with success status and document IDs
        """
        if not self.available:
            return self._mock_add_documents(documents)
        
        try:
            vectorstore = self.get_or_create_collection(collection_name, user_id)
            
            if vectorstore is None:
                raise Exception("Failed to get vector store")
            
            if metadatas is None:
                metadatas = [{} for _ in documents]
            
            doc_objects = [
                Document(page_content=text, metadata=meta)
                for text, meta in zip(documents, metadatas)
            ]
            
            ids = vectorstore.add_documents(doc_objects)
            
            logger.info(f"Added {len(documents)} documents to '{collection_name}'")
            
            return {
                "success": True,
                "document_ids": ids,
                "count": len(documents),
                "collection": collection_name,
                "mock": False
            }
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return {
                "success": False,
                "error": str(e),
                "mock": False
            }
    
    def add_comprobante_data(
        self,
        user_id: str,
        comprobante: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add comprobante data as searchable document.
        
        Args:
            user_id: User ID
            comprobante: Comprobante data dict
        
        Returns:
            Dict with success status
        """
        text = f"""
        Tipo: {comprobante.get('tipo', 'N/A')}
        Número: {comprobante.get('numero', 'N/A')}
        Fecha: {comprobante.get('fecha_emision', 'N/A')}
        Total: ${comprobante.get('total', 0):.2f}
        CUIT Emisor: {comprobante.get('cuit_emisor', 'N/A')}
        Razón Social: {comprobante.get('razon_social', 'N/A')}
        Estado: {comprobante.get('status', 'N/A')}
        """
        
        metadata = {
            "type": "comprobante",
            "comprobante_id": str(comprobante.get('id', '')),
            "numero": comprobante.get('numero', ''),
            "fecha_emision": str(comprobante.get('fecha_emision', '')),
            "total": comprobante.get('total', 0),
            "user_id": user_id
        }
        
        return self.add_documents(
            collection_name="comprobantes",
            documents=[text],
            metadatas=[metadata],
            user_id=user_id
        )
    
    def add_vencimiento_data(
        self,
        user_id: str,
        vencimiento: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add vencimiento data as searchable document.
        
        Args:
            user_id: User ID
            vencimiento: Vencimiento data dict
        
        Returns:
            Dict with success status
        """
        text = f"""
        Tipo: {vencimiento.get('tipo', 'N/A')}
        Descripción: {vencimiento.get('descripcion', 'N/A')}
        Monto: ${vencimiento.get('monto', 0):.2f}
        Fecha Vencimiento: {vencimiento.get('fecha_vencimiento', 'N/A')}
        Estado: {vencimiento.get('status', 'N/A')}
        Recordatorio: {vencimiento.get('recordatorio_dias_antes', 7)} días antes
        """
        
        metadata = {
            "type": "vencimiento",
            "vencimiento_id": str(vencimiento.get('id', '')),
            "tipo": vencimiento.get('tipo', ''),
            "fecha_vencimiento": str(vencimiento.get('fecha_vencimiento', '')),
            "monto": vencimiento.get('monto', 0),
            "user_id": user_id
        }
        
        return self.add_documents(
            collection_name="vencimientos",
            documents=[text],
            metadatas=[metadata],
            user_id=user_id
        )
    
    def search(
        self,
        collection_name: str,
        query: str,
        user_id: Optional[str] = None,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Search for similar documents.
        
        Args:
            collection_name: Collection to search
            query: Search query
            user_id: Optional user ID for namespaced collection
            k: Number of results to return
        
        Returns:
            Dict with search results
        """
        if not self.available:
            return self._mock_search(query)
        
        try:
            vectorstore = self.get_or_create_collection(collection_name, user_id)
            
            if vectorstore is None:
                raise Exception("Failed to get vector store")
            
            results = vectorstore.similarity_search(query, k=k)
            
            formatted_results = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in results
            ]
            
            return {
                "success": True,
                "results": formatted_results,
                "count": len(formatted_results),
                "query": query,
                "mock": False
            }
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "mock": False
            }
    
    def get_retriever(
        self,
        collection_name: str,
        user_id: Optional[str] = None,
        k: int = 5
    ):
        """
        Get LangChain retriever for RAG.
        
        Args:
            collection_name: Collection name
            user_id: Optional user ID
            k: Number of documents to retrieve
        
        Returns:
            LangChain retriever or None
        """
        if not self.available:
            return None
        
        try:
            vectorstore = self.get_or_create_collection(collection_name, user_id)
            
            if vectorstore is None:
                return None
            
            return vectorstore.as_retriever(search_kwargs={"k": k})
            
        except Exception as e:
            logger.error(f"Error creating retriever: {e}")
            return None
    
    def delete_collection(
        self,
        collection_name: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a collection.
        
        Args:
            collection_name: Collection to delete
            user_id: Optional user ID
        
        Returns:
            Dict with success status
        """
        if not self.available:
            return {"success": False, "mock": True}
        
        try:
            if user_id:
                full_collection_name = f"{collection_name}_{user_id}"
            else:
                full_collection_name = collection_name
            
            full_collection_name = full_collection_name.replace("-", "_")
            
            self.client.delete_collection(name=full_collection_name)
            
            logger.info(f"Deleted collection '{full_collection_name}'")
            
            return {
                "success": True,
                "collection": full_collection_name,
                "mock": False
            }
            
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return {
                "success": False,
                "error": str(e),
                "mock": False
            }
    
    def _mock_add_documents(self, documents: List[str]) -> Dict[str, Any]:
        """Mock response for adding documents."""
        return {
            "success": False,
            "document_ids": [str(uuid.uuid4()) for _ in documents],
            "count": len(documents),
            "mock": True,
            "message": "ChromaDB not installed. Documents not actually stored."
        }
    
    def _mock_search(self, query: str) -> Dict[str, Any]:
        """Mock response for search."""
        return {
            "success": False,
            "results": [
                {
                    "content": "Resultado simulado para demostración.",
                    "metadata": {"mock": True}
                }
            ],
            "count": 1,
            "query": query,
            "mock": True,
            "message": "ChromaDB not installed. Showing mock results."
        }


vector_store = VectorStoreService()
