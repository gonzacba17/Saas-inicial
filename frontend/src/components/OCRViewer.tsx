import React from 'react';

interface OCRData {
  success: boolean;
  tipo: string | null;
  numero: string | null;
  fecha_emision: string | null;
  total: number | null;
  subtotal: number | null;
  iva: number | null;
  cuit_emisor: string | null;
  razon_social: string | null;
  confidence: number | null;
  raw_text: string | null;
  mock: boolean;
  message: string | null;
}

interface OCRResult {
  success: boolean;
  filename: string;
  file_size: number;
  processing_time: number;
  data: OCRData;
  saved_to_comprobante: boolean;
  comprobante_id: string | null;
}

interface OCRViewerProps {
  ocrResult: OCRResult;
}

const OCRViewer: React.FC<OCRViewerProps> = ({ ocrResult }) => {
  const { data, filename, processing_time, saved_to_comprobante, comprobante_id } = ocrResult;

  const getConfidenceColor = (confidence: number | null) => {
    if (!confidence) return 'text-gray-600';
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceBadge = (confidence: number | null) => {
    if (!confidence) return 'bg-gray-100 text-gray-800';
    if (confidence >= 0.8) return 'bg-green-100 text-green-800';
    if (confidence >= 0.5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'No detectada';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('es-AR');
    } catch {
      return dateStr;
    }
  };

  const formatCurrency = (amount: number | null) => {
    if (amount === null) return 'No detectado';
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS'
    }).format(amount);
  };

  const formatCuit = (cuit: string | null) => {
    if (!cuit) return 'No detectado';
    if (cuit.length === 11) {
      return `${cuit.slice(0, 2)}-${cuit.slice(2, 10)}-${cuit.slice(10)}`;
    }
    return cuit;
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
        <h2 className="text-2xl font-bold text-white">
          ✨ Resultados de Extracción OCR
        </h2>
        <p className="text-blue-100 text-sm mt-1">
          Archivo: {filename} • Procesado en {processing_time}s
        </p>
      </div>

      {/* Mock Warning */}
      {data.mock && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700 font-semibold">
                ⚠️ Modo Demo - Datos Simulados
              </p>
              <p className="text-xs text-yellow-600 mt-1">
                {data.message || 'OCR dependencies not installed. Showing mock data.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Saved Status */}
      {saved_to_comprobante && (
        <div className="bg-green-50 border-l-4 border-green-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-green-700 font-semibold">
                ✅ Guardado como Comprobante
              </p>
              <p className="text-xs text-green-600 mt-1">
                ID: {comprobante_id}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Confidence Score */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Confianza de Extracción:</span>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getConfidenceBadge(data.confidence)}`}>
            {data.confidence !== null ? `${(data.confidence * 100).toFixed(0)}%` : 'N/A'}
          </span>
        </div>
      </div>

      {/* Extracted Data */}
      <div className="px-6 py-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Tipo */}
          <div className="border-l-4 border-blue-500 pl-4">
            <p className="text-xs text-gray-500 uppercase font-semibold">Tipo de Comprobante</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">
              {data.tipo ? data.tipo.replace('_', ' ').toUpperCase() : 'No detectado'}
            </p>
          </div>

          {/* Número */}
          <div className="border-l-4 border-purple-500 pl-4">
            <p className="text-xs text-gray-500 uppercase font-semibold">Número</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">
              {data.numero || 'No detectado'}
            </p>
          </div>

          {/* Fecha */}
          <div className="border-l-4 border-green-500 pl-4">
            <p className="text-xs text-gray-500 uppercase font-semibold">Fecha de Emisión</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">
              {formatDate(data.fecha_emision)}
            </p>
          </div>

          {/* Total */}
          <div className="border-l-4 border-red-500 pl-4">
            <p className="text-xs text-gray-500 uppercase font-semibold">Total</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {formatCurrency(data.total)}
            </p>
          </div>

          {/* Subtotal */}
          <div className="border-l-4 border-yellow-500 pl-4">
            <p className="text-xs text-gray-500 uppercase font-semibold">Subtotal</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">
              {formatCurrency(data.subtotal)}
            </p>
          </div>

          {/* IVA */}
          <div className="border-l-4 border-orange-500 pl-4">
            <p className="text-xs text-gray-500 uppercase font-semibold">IVA</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">
              {formatCurrency(data.iva)}
            </p>
          </div>

          {/* CUIT */}
          <div className="border-l-4 border-indigo-500 pl-4">
            <p className="text-xs text-gray-500 uppercase font-semibold">CUIT Emisor</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">
              {formatCuit(data.cuit_emisor)}
            </p>
          </div>

          {/* Razón Social */}
          <div className="border-l-4 border-pink-500 pl-4">
            <p className="text-xs text-gray-500 uppercase font-semibold">Razón Social</p>
            <p className="text-lg font-semibold text-gray-900 mt-1">
              {data.razon_social || 'No detectado'}
            </p>
          </div>
        </div>
      </div>

      {/* Raw Text (collapsed) */}
      {data.raw_text && (
        <details className="px-6 py-4 border-t border-gray-200">
          <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
            📝 Ver Texto Extraído Completo
          </summary>
          <pre className="mt-4 p-4 bg-gray-50 rounded-md text-xs text-gray-800 overflow-x-auto whitespace-pre-wrap">
            {data.raw_text}
          </pre>
        </details>
      )}

      {/* Actions */}
      {!saved_to_comprobante && data.success && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-3">
            ¿Los datos son correctos? Puedes copiarlos manualmente o crear el comprobante desde la página de Comprobantes.
          </p>
          <button
            onClick={() => {
              const dataStr = JSON.stringify(data, null, 2);
              navigator.clipboard.writeText(dataStr);
              alert('Datos copiados al portapapeles');
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            📋 Copiar Datos JSON
          </button>
        </div>
      )}
    </div>
  );
};

export default OCRViewer;
