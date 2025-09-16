from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class OpenAIAdapter:
    """
    OpenAI adapter for AI services.
    Currently set up without API key for scaffold phase.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.is_enabled = api_key is not None
        
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate AI response for given prompt.
        Returns mock response when API key is not configured.
        """
        if not self.is_enabled:
            return self._mock_response(prompt, context)
        
        # TODO: Implement actual OpenAI API call
        try:
            # Placeholder for OpenAI API integration
            logger.info(f"AI prompt: {prompt[:100]}...")
            return "AI integration pending - configure OpenAI API key"
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "Error generating AI response"
    
    async def analyze_sales_data(self, sales_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sales data and provide insights.
        """
        if not self.is_enabled:
            return self._mock_sales_analysis(sales_data)
        
        # TODO: Implement sales analysis with OpenAI
        try:
            prompt = f"Analyze this sales data and provide insights: {json.dumps(sales_data[:5])}"
            analysis = await self.generate_response(prompt)
            return {
                "summary": analysis,
                "recommendations": [],
                "trends": {},
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Sales analysis error: {e}")
            return {"error": "Failed to analyze sales data"}
    
    async def generate_menu_suggestions(self, cafe_context: Dict[str, Any]) -> List[str]:
        """
        Generate menu suggestions based on cafe context.
        """
        if not self.is_enabled:
            return self._mock_menu_suggestions()
        
        # TODO: Implement menu suggestions with OpenAI
        try:
            prompt = f"Suggest menu items for a cafe with this context: {json.dumps(cafe_context)}"
            suggestions = await self.generate_response(prompt)
            return [suggestions]
        except Exception as e:
            logger.error(f"Menu suggestions error: {e}")
            return ["Error generating menu suggestions"]
    
    def _mock_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Mock response when OpenAI is not configured."""
        return f"Mock AI response for prompt: '{prompt[:50]}...' (Configure OpenAI API key to enable AI features)"
    
    def _mock_sales_analysis(self, sales_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock sales analysis."""
        return {
            "summary": "Sales analysis shows steady growth with peak hours from 8-10 AM and 2-4 PM",
            "recommendations": [
                "Increase staff during peak hours",
                "Introduce afternoon specials",
                "Focus on coffee and pastry combinations"
            ],
            "trends": {
                "best_selling_category": "coffee",
                "peak_hours": ["08:00-10:00", "14:00-16:00"],
                "growth_rate": "+15%"
            },
            "generated_at": datetime.utcnow().isoformat(),
            "is_mock": True
        }
    
    def _mock_menu_suggestions(self) -> List[str]:
        """Mock menu suggestions."""
        return [
            "Specialty Seasonal Latte",
            "Artisan Breakfast Sandwich",
            "Fresh Fruit Smoothie Bowl",
            "Homemade Pastry Selection",
            "Local Roast Coffee Blend"
        ]

class AIService:
    """
    Main AI service class that coordinates AI operations.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_adapter = OpenAIAdapter(openai_api_key)
        self.prompt_cache = {}
        
    async def get_assistant_response(self, prompt: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get AI assistant response with logging and caching.
        """
        try:
            # Log the prompt for future iteration
            self._log_prompt(prompt, user_id, context)
            
            # Check cache first (simple implementation)
            cache_key = self._generate_cache_key(prompt, context)
            if cache_key in self.prompt_cache:
                logger.info(f"Cache hit for prompt: {prompt[:50]}...")
                return self.prompt_cache[cache_key]
            
            # Generate response
            response = await self.openai_adapter.generate_response(prompt, context)
            
            result = {
                "response": response,
                "prompt": prompt,
                "user_id": user_id,
                "context": context,
                "timestamp": datetime.utcnow().isoformat(),
                "cached": False
            }
            
            # Cache the result
            self.prompt_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"AI service error: {e}")
            return {
                "response": "Sorry, I'm experiencing technical difficulties. Please try again later.",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def analyze_cafe_performance(self, cafe_id: str, sales_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze cafe performance using AI.
        """
        try:
            analysis = await self.openai_adapter.analyze_sales_data(sales_data)
            analysis["cafe_id"] = cafe_id
            return analysis
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            return {"error": "Failed to analyze cafe performance"}
    
    def _log_prompt(self, prompt: str, user_id: str, context: Optional[Dict[str, Any]] = None):
        """Log prompts for future analysis and improvement."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "prompt": prompt,
            "context": context
        }
        # TODO: Store in database for future iteration
        logger.info(f"AI prompt logged: {log_entry}")
    
    def _generate_cache_key(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key for prompt and context."""
        context_str = json.dumps(context, sort_keys=True) if context else ""
        return f"{hash(prompt + context_str)}"

# Global AI service instance
ai_service: Optional[AIService] = None

def get_ai_service() -> AIService:
    """Get the global AI service instance."""
    global ai_service
    if ai_service is None:
        # This will be initialized with proper config in main.py
        ai_service = AIService()
    return ai_service

def initialize_ai_service(openai_api_key: Optional[str] = None):
    """Initialize the AI service with configuration."""
    global ai_service
    ai_service = AIService(openai_api_key)