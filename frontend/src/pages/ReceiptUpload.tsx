import React, { useState } from 'react';
import OCRViewer from '../components/OCRViewer';

interface OCRResult {
  success: boolean;
  filename: string;
  file_size: number;
  processing_time: number;
  data: {
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
  };
  saved_to_comprobante: boolean;
  comprobante_id: string | null;
}

const ReceiptUpload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [businessId, setBusinessId] = useState<string>('');
  const [autoSave, setAutoSave] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [ocrResult, setOcrResult] = useState<OCRResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const validateAndSetFile = (file: File) => {
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      setError('Tipo de archivo no soportado. Usa PDF, JPG o PNG.');
      return;
    }

    if (file.size > maxSize) {
      setError('Archivo muy grande. Máximo 10MB.');
      return;
    }

    setSelectedFile(file);
    setError(null);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Selecciona un archivo primero');
      return;
    }

    setUploading(true);
    setError(null);
    setOcrResult(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No estás autenticado');
      }

      const formData = new FormData();
      formData.append('file', selectedFile);
      if (businessId) {
        formData.append('business_id', businessId);
      }
      formData.append('auto_save', autoSave.toString());

      const response = await fetch('http://localhost:8000/api/v1/ocr/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al procesar el archivo');
      }

      const data = await response.json();
      setOcrResult(data.ocr_result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setUploading(false);
    }
  };

  const resetForm = () => {
    setSelectedFile(null);
    setOcrResult(null);
    setError(null);
    setBusinessId('');
    setAutoSave(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📄 Extracción OCR de Comprobantes
          </h1>
          <p className="text-gray-600 mb-6">
            Sube facturas, recibos o comprobantes (PDF o imagen) y extrae automáticamente los datos.
          </p>

          {/* Upload Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center mb-6 transition-colors ${
              dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {selectedFile ? (
              <div>
                <p className="text-lg font-semibold text-gray-700">
                  Archivo seleccionado:
                </p>
                <p className="text-gray-600">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
                <button
                  onClick={resetForm}
                  className="mt-2 text-red-600 hover:text-red-700 underline"
                >
                  Cambiar archivo
                </button>
              </div>
            ) : (
              <div>
                <svg
                  className="mx-auto h-12 w-12 text-gray-400 mb-4"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <label className="cursor-pointer">
                  <span className="text-blue-600 hover:text-blue-700 font-semibold">
                    Haz clic para seleccionar
                  </span>
                  <span className="text-gray-600"> o arrastra el archivo aquí</span>
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileChange}
                  />
                </label>
                <p className="text-xs text-gray-500 mt-2">
                  PDF, JPG, PNG (máx. 10MB)
                </p>
              </div>
            )}
          </div>

          {/* Options */}
          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                ID del Negocio (opcional)
              </label>
              <input
                type="text"
                value={businessId}
                onChange={(e) => setBusinessId(e.target.value)}
                placeholder="UUID del negocio"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="autoSave"
                checked={autoSave}
                onChange={(e) => setAutoSave(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="autoSave" className="ml-2 block text-sm text-gray-700">
                Guardar automáticamente como Comprobante
              </label>
            </div>
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            className={`w-full py-3 px-4 rounded-md font-semibold text-white transition-colors ${
              !selectedFile || uploading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {uploading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
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
                Procesando...
              </span>
            ) : (
              '🚀 Extraer Datos'
            )}
          </button>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">❌ {error}</p>
            </div>
          )}
        </div>

        {/* OCR Results */}
        {ocrResult && (
          <div className="mt-6">
            <OCRViewer ocrResult={ocrResult} />
          </div>
        )}
      </div>
    </div>
  );
};

export default ReceiptUpload;
