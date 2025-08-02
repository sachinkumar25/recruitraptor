"""LLM service for narrative generation."""

import time
import httpx
from typing import Dict, Any, Optional, List
from openai import OpenAI
from anthropic import Anthropic

from ..core.config import settings
from ..core.models import LLMProvider, NarrativeStyle
from ..utils.logger import llm_logger, log_llm_request, log_llm_response, log_error


class LLMService:
    """Service for interacting with LLM providers."""
    
    def __init__(self):
        """Initialize LLM service with configured providers."""
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize LLM clients."""
        if settings.openai_api_key and settings.openai_api_key != "your_openai_key_here":
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
            llm_logger.info("OpenAI client initialized")
        
        if settings.anthropic_api_key and settings.anthropic_api_key != "your_anthropic_key_here":
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
            llm_logger.info("Anthropic client initialized")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers."""
        providers = []
        if self.openai_client:
            providers.append(LLMProvider.OPENAI)
        if self.anthropic_client:
            providers.append(LLMProvider.ANTHROPIC)
        return providers
    
    def generate_narrative(
        self,
        prompt: str,
        provider: LLMProvider = None,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate narrative using specified LLM provider."""
        
        # Use defaults if not specified
        provider = provider or LLMProvider(settings.default_llm_provider)
        model = model or settings.default_model
        max_tokens = max_tokens or settings.max_tokens
        temperature = temperature or settings.temperature
        
        start_time = time.time()
        
        try:
            if provider == LLMProvider.OPENAI:
                return self._generate_with_openai(
                    prompt, model, max_tokens, temperature, **kwargs
                )
            elif provider == LLMProvider.ANTHROPIC:
                return self._generate_with_anthropic(
                    prompt, model, max_tokens, temperature, **kwargs
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
                
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            log_error(
                "llm_generation_failed",
                str(e),
                context={
                    "provider": provider,
                    "model": model,
                    "processing_time_ms": processing_time
                }
            )
            raise
    
    def _generate_with_openai(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate narrative using OpenAI."""
        
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        start_time = time.time()
        
        log_llm_request(
            provider="openai",
            model=model,
            prompt_length=len(prompt),
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            processing_time = (time.time() - start_time) * 1000
            content = response.choices[0].message.content
            
            log_llm_response(
                provider="openai",
                model=model,
                response_length=len(content),
                tokens_used=response.usage.total_tokens if response.usage else None,
                processing_time_ms=processing_time
            )
            
            return {
                "content": content,
                "provider": LLMProvider.OPENAI,
                "model": model,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            log_error(
                "openai_generation_failed",
                str(e),
                context={
                    "model": model,
                    "processing_time_ms": processing_time
                }
            )
            raise
    
    def _generate_with_anthropic(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate narrative using Anthropic."""
        
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")
        
        start_time = time.time()
        
        log_llm_request(
            provider="anthropic",
            model=model,
            prompt_length=len(prompt),
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            processing_time = (time.time() - start_time) * 1000
            content = response.content[0].text
            
            log_llm_response(
                provider="anthropic",
                model=model,
                response_length=len(content),
                tokens_used=response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                processing_time_ms=processing_time
            )
            
            return {
                "content": content,
                "provider": LLMProvider.ANTHROPIC,
                "model": model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            log_error(
                "anthropic_generation_failed",
                str(e),
                context={
                    "model": model,
                    "processing_time_ms": processing_time
                }
            )
            raise
    
    def test_provider_connectivity(self, provider: LLMProvider) -> bool:
        """Test connectivity to LLM provider."""
        try:
            if provider == LLMProvider.OPENAI and self.openai_client:
                # Simple test with minimal tokens
                self._generate_with_openai(
                    "Hello", "gpt-3.5-turbo", 10, 0.1
                )
                return True
            elif provider == LLMProvider.ANTHROPIC and self.anthropic_client:
                # Simple test with minimal tokens
                self._generate_with_anthropic(
                    "Hello", "claude-3-haiku-20240307", 10, 0.1
                )
                return True
            return False
        except Exception as e:
            llm_logger.warning(f"Provider connectivity test failed for {provider}: {e}")
            return False


# Global LLM service instance
llm_service = LLMService() 