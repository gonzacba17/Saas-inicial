import React from 'react';

interface ErrorDisplayProps {
  error: any;
  onRetry?: () => void;
  className?: string;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ 
  error, 
  onRetry, 
  className = '' 
}) => {
  if (!error) return null;

  const getErrorMessage = (error: any): string => {
    if (typeof error === 'string') return error;
    if (error?.message) return error.message;
    return 'An unexpected error occurred';
  };

  const getErrorType = (error: any): string => {
    if (error?.type) return error.type;
    if (error?.status) {
      switch (error.status) {
        case 401: return 'UNAUTHORIZED';
        case 403: return 'FORBIDDEN';
        case 404: return 'NOT_FOUND';
        case 422: return 'VALIDATION_ERROR';
        case 500: return 'SERVER_ERROR';
        default: return 'UNKNOWN_ERROR';
      }
    }
    return 'UNKNOWN_ERROR';
  };

  const getErrorIcon = (type: string): string => {
    switch (type) {
      case 'UNAUTHORIZED':
      case 'INVALID_CREDENTIALS':
        return '🔒';
      case 'FORBIDDEN':
        return '🚫';
      case 'NOT_FOUND':
        return '❓';
      case 'VALIDATION_ERROR':
        return '⚠️';
      case 'SERVER_ERROR':
        return '💥';
      case 'NETWORK_ERROR':
        return '🌐';
      default:
        return '❌';
    }
  };

  const getErrorColor = (type: string): string => {
    switch (type) {
      case 'UNAUTHORIZED':
      case 'INVALID_CREDENTIALS':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'FORBIDDEN':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'NOT_FOUND':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'VALIDATION_ERROR':
        return 'bg-orange-50 border-orange-200 text-orange-800';
      case 'SERVER_ERROR':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'NETWORK_ERROR':
        return 'bg-gray-50 border-gray-200 text-gray-800';
      default:
        return 'bg-red-50 border-red-200 text-red-800';
    }
  };

  const getErrorTitle = (type: string): string => {
    switch (type) {
      case 'UNAUTHORIZED':
      case 'INVALID_CREDENTIALS':
        return 'Authentication Required';
      case 'FORBIDDEN':
        return 'Access Denied';
      case 'NOT_FOUND':
        return 'Resource Not Found';
      case 'VALIDATION_ERROR':
        return 'Validation Error';
      case 'SERVER_ERROR':
        return 'Server Error';
      case 'NETWORK_ERROR':
        return 'Network Error';
      default:
        return 'Error';
    }
  };

  const errorType = getErrorType(error);
  const errorMessage = getErrorMessage(error);
  const errorIcon = getErrorIcon(errorType);
  const errorColor = getErrorColor(errorType);
  const errorTitle = getErrorTitle(errorType);

  return (
    <div className={`rounded-lg border p-4 ${errorColor} ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <span className="text-2xl">{errorIcon}</span>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium">{errorTitle}</h3>
          <div className="mt-2 text-sm">
            <p>{errorMessage}</p>
            {error?.status && (
              <p className="mt-1 text-xs opacity-75">
                Status: {error.status} {error.statusText && `- ${error.statusText}`}
              </p>
            )}
          </div>
          {onRetry && (
            <div className="mt-3">
              <button
                type="button"
                onClick={onRetry}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Hook for handling API errors consistently
export const useErrorHandler = () => {
  const handleError = (error: any) => {
    console.error('API Error:', error);
    
    // Handle specific error types
    switch (error?.type) {
      case 'UNAUTHORIZED':
      case 'INVALID_CREDENTIALS':
        // Redirect to login if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        break;
      case 'FORBIDDEN':
        // Show forbidden message, don't redirect
        break;
      case 'NETWORK_ERROR':
        // Could show network status indicator
        break;
      default:
        // Generic error handling
        break;
    }

    return error;
  };

  return { handleError };
};

export default ErrorDisplay;