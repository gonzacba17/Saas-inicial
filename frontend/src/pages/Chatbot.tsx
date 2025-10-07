import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from '../components/ChatMessage';

interface ChatHistoryItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tokens_used: number;
  model: string;
  created_at: string;
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<ChatHistoryItem[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [useRAG, setUseRAG] = useState<boolean>(false);
  const [collectionName, setCollectionName] = useState<string>('documents');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch('http://localhost:8000/api/v1/chatbot/history?limit=50', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(data.history);
      }
    } catch (err) {
      console.error('Error loading history:', err);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const token = localStorage.getItem('token');
    if (!token) {
      setError('No estás autenticado');
      return;
    }

    setLoading(true);
    setError(null);

    const userMessage: ChatHistoryItem = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: inputMessage,
      tokens_used: 0,
      model: '',
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/chatbot/query', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: inputMessage,
          use_rag: useRAG,
          collection_name: useRAG ? collectionName : undefined
        })
      });

      if (!response.ok) {
        throw new Error('Error al enviar mensaje');
      }

      const data = await response.json();

      const assistantMessage: ChatHistoryItem = {
        id: `temp-${Date.now()}-assistant`,
        role: 'assistant',
        content: data.response,
        tokens_used: data.tokens_used?.total_tokens || 0,
        model: data.model || 'gpt-4',
        created_at: data.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearHistory = async () => {
    if (!confirm('¿Seguro que quieres borrar todo el historial?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/chatbot/history', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setMessages([]);
      }
    } catch (err) {
      setError('Error al borrar historial');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-4 shadow-lg">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-3xl mr-3">🤖</span>
            <div>
              <h1 className="text-2xl font-bold">CaféBot IA</h1>
              <p className="text-sm text-blue-100">Asistente inteligente para tu negocio</p>
            </div>
          </div>
          
          <button
            onClick={clearHistory}
            className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-md text-sm transition-colors"
          >
            🗑️ Borrar Historial
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <span className="text-6xl mb-4 block">💬</span>
              <h2 className="text-2xl font-bold text-gray-700 mb-2">
                ¡Hola! Soy CaféBot IA
              </h2>
              <p className="text-gray-600 mb-6">
                Puedo ayudarte con gestión de facturas, vencimientos, consultas fiscales y más.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8 text-left">
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                  <div className="text-2xl mb-2">📄</div>
                  <h3 className="font-semibold mb-1">Comprobantes</h3>
                  <p className="text-sm text-gray-600">
                    Consulta sobre facturas, recibos y notas de crédito
                  </p>
                </div>
                
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                  <div className="text-2xl mb-2">⏰</div>
                  <h3 className="font-semibold mb-1">Vencimientos</h3>
                  <p className="text-sm text-gray-600">
                    Información sobre pagos pendientes y fechas límite
                  </p>
                </div>
                
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                  <div className="text-2xl mb-2">🏛️</div>
                  <h3 className="font-semibold mb-1">Consultas Fiscales</h3>
                  <p className="text-sm text-gray-600">
                    Ayuda con normativas AFIP, CUIT e impuestos
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div>
              {messages.map((msg, index) => (
                <ChatMessage
                  key={msg.id || index}
                  role={msg.role}
                  content={msg.content}
                  timestamp={msg.created_at}
                  tokensUsed={msg.tokens_used}
                  model={msg.model}
                />
              ))}
              
              {loading && (
                <div className="flex justify-start mb-4">
                  <div className="bg-gray-100 rounded-lg px-4 py-3 border border-gray-200">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="px-4 py-3 bg-red-50 border-t border-red-200">
          <div className="max-w-4xl mx-auto">
            <p className="text-red-800 text-sm">❌ {error}</p>
          </div>
        </div>
      )}

      <div className="bg-white border-t border-gray-200 px-4 py-4 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center mb-2 space-x-4">
            <label className="flex items-center text-sm text-gray-600">
              <input
                type="checkbox"
                checked={useRAG}
                onChange={(e) => setUseRAG(e.target.checked)}
                className="mr-2 rounded"
              />
              Usar contexto de documentos (RAG)
            </label>
            
            {useRAG && (
              <input
                type="text"
                value={collectionName}
                onChange={(e) => setCollectionName(e.target.value)}
                placeholder="Nombre de colección"
                className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            )}
          </div>
          
          <div className="flex items-end space-x-2">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu mensaje aquí..."
              rows={2}
              disabled={loading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
            
            <button
              onClick={sendMessage}
              disabled={loading || !inputMessage.trim()}
              className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
                loading || !inputMessage.trim()
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {loading ? (
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              ) : (
                '🚀 Enviar'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
