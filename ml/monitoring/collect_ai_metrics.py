"""
Script para recolectar métricas de inferencia AI desde ai_audit_logs
y exponerlas para Prometheus/Grafana
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import func
from app.db.db import get_db, AIAuditLog


class AIMetricsCollector:
    
    def __init__(self):
        self.db = next(get_db())
    
    def get_metrics_summary(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        business_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if not end_date:
            end_date = datetime.utcnow()
        
        query = self.db.query(AIAuditLog).filter(
            AIAuditLog.timestamp >= start_date,
            AIAuditLog.timestamp <= end_date
        )
        
        if business_id:
            query = query.filter(AIAuditLog.business_id == business_id)
        
        logs = query.all()
        
        if not logs:
            return {
                "total_requests": 0,
                "success_rate": 0.0,
                "avg_response_time_ms": 0,
                "total_tokens": 0
            }
        
        total_requests = len(logs)
        successful_requests = len([log for log in logs if log.status == "success"])
        total_tokens = sum(log.tokens_used for log in logs)
        total_response_time = sum(log.response_time_ms for log in logs)
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": total_requests - successful_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0.0,
            "avg_response_time_ms": total_response_time / total_requests if total_requests > 0 else 0,
            "total_tokens": total_tokens,
            "avg_tokens_per_request": total_tokens / total_requests if total_requests > 0 else 0,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat()
        }
    
    def get_metrics_by_endpoint(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if not end_date:
            end_date = datetime.utcnow()
        
        results = self.db.query(
            AIAuditLog.endpoint,
            func.count(AIAuditLog.id).label('total_requests'),
            func.avg(AIAuditLog.response_time_ms).label('avg_response_time'),
            func.sum(AIAuditLog.tokens_used).label('total_tokens')
        ).filter(
            AIAuditLog.timestamp >= start_date,
            AIAuditLog.timestamp <= end_date
        ).group_by(AIAuditLog.endpoint).all()
        
        return [
            {
                "endpoint": result.endpoint or "unknown",
                "total_requests": result.total_requests,
                "avg_response_time_ms": float(result.avg_response_time or 0),
                "total_tokens": int(result.total_tokens or 0)
            }
            for result in results
        ]
    
    def get_metrics_by_model(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if not end_date:
            end_date = datetime.utcnow()
        
        results = self.db.query(
            AIAuditLog.model_name,
            func.count(AIAuditLog.id).label('total_requests'),
            func.avg(AIAuditLog.response_time_ms).label('avg_response_time'),
            func.sum(AIAuditLog.tokens_used).label('total_tokens')
        ).filter(
            AIAuditLog.timestamp >= start_date,
            AIAuditLog.timestamp <= end_date
        ).group_by(AIAuditLog.model_name).all()
        
        return [
            {
                "model": result.model_name,
                "total_requests": result.total_requests,
                "avg_response_time_ms": float(result.avg_response_time or 0),
                "total_tokens": int(result.total_tokens or 0)
            }
            for result in results
        ]
    
    def get_error_rate(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if not end_date:
            end_date = datetime.utcnow()
        
        total = self.db.query(func.count(AIAuditLog.id)).filter(
            AIAuditLog.timestamp >= start_date,
            AIAuditLog.timestamp <= end_date
        ).scalar()
        
        errors = self.db.query(func.count(AIAuditLog.id)).filter(
            AIAuditLog.timestamp >= start_date,
            AIAuditLog.timestamp <= end_date,
            AIAuditLog.status == "error"
        ).scalar()
        
        return {
            "total_requests": total,
            "total_errors": errors,
            "error_rate": (errors / total * 100) if total > 0 else 0.0
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        errors = self.db.query(AIAuditLog).filter(
            AIAuditLog.status == "error"
        ).order_by(AIAuditLog.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "timestamp": error.timestamp.isoformat(),
                "endpoint": error.endpoint,
                "model": error.model_name,
                "error_message": error.error_message,
                "user_id": error.user_id,
                "business_id": error.business_id
            }
            for error in errors
        ]
    
    def close(self):
        self.db.close()


def export_metrics_to_prometheus_format() -> str:
    collector = AIMetricsCollector()
    
    try:
        summary = collector.get_metrics_summary()
        by_endpoint = collector.get_metrics_by_endpoint()
        by_model = collector.get_metrics_by_model()
        error_rate = collector.get_error_rate()
        
        metrics_output = []
        
        metrics_output.append("# HELP ai_requests_total Total AI requests")
        metrics_output.append("# TYPE ai_requests_total counter")
        metrics_output.append(f"ai_requests_total {summary['total_requests']}")
        
        metrics_output.append("# HELP ai_tokens_total Total tokens consumed")
        metrics_output.append("# TYPE ai_tokens_total counter")
        metrics_output.append(f"ai_tokens_total {summary['total_tokens']}")
        
        metrics_output.append("# HELP ai_response_time_avg Average response time in milliseconds")
        metrics_output.append("# TYPE ai_response_time_avg gauge")
        metrics_output.append(f"ai_response_time_avg {summary['avg_response_time_ms']}")
        
        metrics_output.append("# HELP ai_success_rate Success rate percentage")
        metrics_output.append("# TYPE ai_success_rate gauge")
        metrics_output.append(f"ai_success_rate {summary['success_rate']}")
        
        metrics_output.append("# HELP ai_error_rate Error rate percentage")
        metrics_output.append("# TYPE ai_error_rate gauge")
        metrics_output.append(f"ai_error_rate {error_rate['error_rate']}")
        
        for endpoint_metric in by_endpoint:
            endpoint_name = endpoint_metric['endpoint'].replace('/', '_').replace('-', '_')
            metrics_output.append(f"ai_requests_by_endpoint{{endpoint=\"{endpoint_metric['endpoint']}\"}} {endpoint_metric['total_requests']}")
        
        for model_metric in by_model:
            metrics_output.append(f"ai_requests_by_model{{model=\"{model_metric['model']}\"}} {model_metric['total_requests']}")
        
        return "\n".join(metrics_output)
    
    finally:
        collector.close()


if __name__ == "__main__":
    collector = AIMetricsCollector()
    
    try:
        print("=== AI Metrics Summary (Last 24h) ===")
        summary = collector.get_metrics_summary()
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        print("\n=== Metrics by Endpoint ===")
        by_endpoint = collector.get_metrics_by_endpoint()
        for metric in by_endpoint:
            print(f"{metric['endpoint']}: {metric['total_requests']} requests, {metric['avg_response_time_ms']:.2f}ms avg")
        
        print("\n=== Metrics by Model ===")
        by_model = collector.get_metrics_by_model()
        for metric in by_model:
            print(f"{metric['model']}: {metric['total_requests']} requests, {metric['total_tokens']} tokens")
        
        print("\n=== Recent Errors ===")
        errors = collector.get_recent_errors(limit=5)
        for error in errors:
            print(f"[{error['timestamp']}] {error['endpoint']}: {error['error_message']}")
    
    finally:
        collector.close()
