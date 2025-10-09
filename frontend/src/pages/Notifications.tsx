import React, { useState, useEffect } from 'react';

interface NotificationTemplate {
  name: string;
  subject: string;
  description: string;
  variables: string[];
}

interface NotificationStatus {
  email_service_available: boolean;
  push_service_available: boolean;
  celery_worker_active: boolean;
  templates_loaded: number;
  message: string;
}

const Notifications: React.FC = () => {
  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [status, setStatus] = useState<NotificationStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [testEmail, setTestEmail] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('comprobante_created');
  const [testResult, setTestResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const [templatesRes, statusRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/notifications/templates', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/api/v1/notifications/status', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (templatesRes.ok) {
        const templatesData = await templatesRes.json();
        setTemplates(templatesData);
      }

      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setStatus(statusData);
      }

      setLoading(false);
    } catch (err) {
      setError('Error al cargar datos');
      setLoading(false);
    }
  };

  const sendTestNotification = async () => {
    if (!testEmail) {
      setError('Ingresa un email');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setTestResult(null);

      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/notifications/test', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          recipient_email: testEmail,
          notification_type: selectedType
        })
      });

      if (response.ok) {
        const data = await response.json();
        setTestResult(data.email_sent || data.push_sent ? 'Notificación enviada exitosamente' : 'Notificación procesada (mock mode)');
      } else {
        throw new Error('Error al enviar notificación');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (available: boolean) => {
    return available ? '✅' : '⚠️';
  };

  if (loading && !status) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📬 Notificaciones</h1>
          <p className="text-gray-600">Gestiona notificaciones por email y push</p>
        </div>

        {status && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Estado del Sistema</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Servicio Email</span>
                  <span className="text-2xl">{getStatusIcon(status.email_service_available)}</span>
                </div>
                <p className="text-xs text-gray-500">
                  {status.email_service_available ? 'Operacional' : 'Mock Mode'}
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Push Notifications</span>
                  <span className="text-2xl">{getStatusIcon(status.push_service_available)}</span>
                </div>
                <p className="text-xs text-gray-500">
                  {status.push_service_available ? 'Operacional' : 'Mock Mode'}
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Celery Worker</span>
                  <span className="text-2xl">{getStatusIcon(status.celery_worker_active)}</span>
                </div>
                <p className="text-xs text-gray-500">
                  {status.celery_worker_active ? 'Activo' : 'Inactivo'}
                </p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Templates</span>
                  <span className="text-2xl font-bold text-blue-600">{status.templates_loaded}</span>
                </div>
                <p className="text-xs text-gray-500">Plantillas cargadas</p>
              </div>
            </div>

            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm text-blue-800">{status.message}</p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🧪 Enviar Notificación de Prueba</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Destinatario
              </label>
              <input
                type="email"
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder="usuario@ejemplo.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Notificación
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="comprobante_created">📄 Comprobante Creado</option>
                <option value="vencimiento_proximo">⏰ Vencimiento Próximo</option>
                <option value="vencimiento_vencido">🚨 Vencimiento Vencido</option>
                <option value="chatbot_insight">💡 Insight del Chatbot</option>
                <option value="daily_summary">📊 Resumen Diario</option>
              </select>
            </div>

            <button
              onClick={sendTestNotification}
              disabled={loading || !testEmail}
              className={`w-full py-3 rounded-md font-semibold text-white transition-colors ${
                loading || !testEmail
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {loading ? 'Enviando...' : '🚀 Enviar Prueba'}
            </button>

            {testResult && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                <p className="text-green-800 font-semibold">✅ {testResult}</p>
              </div>
            )}

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-800">❌ {error}</p>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">📝 Plantillas Disponibles</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map((template, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{template.name}</h3>
                  <span className="text-2xl">📧</span>
                </div>
                
                <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                
                <div className="mb-2">
                  <span className="text-xs font-semibold text-gray-500">Asunto:</span>
                  <p className="text-sm text-gray-700">{template.subject}</p>
                </div>
                
                <div>
                  <span className="text-xs font-semibold text-gray-500">Variables:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {template.variables.map((variable, vIndex) => (
                      <span
                        key={vIndex}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                      >
                        {variable}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <h3 className="font-semibold text-yellow-900 mb-2">ℹ️ Configuración</h3>
          <p className="text-sm text-yellow-800">
            Para habilitar el envío real de emails, configura las variables de entorno SMTP en el archivo .env del backend.
          </p>
          <p className="text-sm text-yellow-800 mt-1">
            Para push notifications, configura FCM_ENABLED y FCM_SERVER_KEY.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Notifications;
