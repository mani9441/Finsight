"""
LLM Service implementation using the OpenAI SDK.
Includes mock fallback mode for development without API keys.
"""

import json
from datetime import datetime
from typing import Optional

from core import get_logger
from core.exceptions import ServiceError
from models import CompanyInfo, FinancialMetrics, SentimentResult, RiskAssessment, AISummary
from services.interfaces import IAISummaryService
from services.ai.prompt_builder import PromptBuilder
from services.common.response_validator import ResponseValidator
from config.settings import settings

logger = get_logger("llm_service")

class LlmService(IAISummaryService):
    """
    Communicates with OpenAI models to generate advisory reports.
    Falls back to high-fidelity mock generators if credentials are not configured.
    """

    def generate_advisory_summary(
        self, 
        company_info: CompanyInfo, 
        metrics: FinancialMetrics, 
        sentiment: SentimentResult,
        risk: RiskAssessment
    ) -> AISummary:
        """
        Generates an AI summary. Detects key presence and routes to API or mock mode.
        """
        ticker = company_info.ticker.upper()
        logger.info(f"Generating advisory report summary for: {ticker}")
        
        # Build prompt using PromptBuilder
        prompt = PromptBuilder.build_advisory_prompt(company_info, metrics, sentiment, risk)

        # Check API key configuration status
        api_key = settings.OPENAI_API_KEY
        is_mock_mode = (
            not api_key 
            or api_key == "your_openai_api_key_here" 
            or "your_" in api_key.lower()
        )

        if is_mock_mode:
            logger.info(f"OpenAI key is missing or set to placeholder. Generating high-fidelity mock report for {ticker}.")
            return self._generate_mock_report(company_info, metrics, sentiment, risk)

        try:
            # Import OpenAI client locally
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            # Query model (using standard gpt-4o-mini or gpt-3.5-turbo models for efficiency)
            model_name = "gpt-4o-mini"
            logger.info(f"Dispatching prompt query to OpenAI API ({model_name})...")
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional financial analyst that outputs strict JSON formats."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            response_content = response.choices[0].message.content
            if not response_content:
                raise ServiceError("LLM response payload content was empty.")

            logger.info(f"OpenAI response received. Parsing JSON payload.")
            data = json.loads(response_content.strip())
            
            # Validate output keys
            ResponseValidator.validate_keys(
                data, ["executive_summary", "strengths", "weaknesses", "investment_thesis"], "AISummary Output"
            )

            return AISummary(
                ticker=ticker,
                executive_summary=data["executive_summary"],
                investment_thesis=data["investment_thesis"],
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                generated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}. Falling back to mock generator.")
            # Graceful fallback to mock reporting rather than raising breaking exception to UI
            return self._generate_mock_report(company_info, metrics, sentiment, risk)

    def _generate_mock_report(
        self,
        company_info: CompanyInfo,
        metrics: FinancialMetrics,
        sentiment: SentimentResult,
        risk: RiskAssessment
    ) -> AISummary:
        """
        Generates realistic, details-rich mockup reports based on the metrics, sentiment, and risk profile.
        """
        ticker = company_info.ticker.upper()
        
        # Determine analytical adjectives based on financial variables
        health_adjective = "fundamentally robust" if risk.risk_level in ["Low", "Medium"] else "structurally volatile"
        sentiment_review = "highly encouraging news coverage" if sentiment.average_score > 0.1 else "subdued or cautious market consensus"
        
        # Build customized content
        exec_summary = (
            f"An analysis of {company_info.name} ({ticker}) indicates a {health_adjective} market profile. "
            f"The company demonstrates a business presence within the {company_info.industry} industry, "
            f"supported by sector dynamics in {company_info.sector}. Recent operations are accompanied by "
            f"{sentiment_review}, while risk scoring tools compile a composite risk score of {risk.risk_score:.1f}/100, "
            f"pointing to a {risk.risk_level.lower()} threat level for prospective shareholders."
        )

        thesis = (
            f"While {ticker} faces industry head-winds related to {risk.risk_factors[0] if risk.risk_factors else 'market cycles'}, "
            f"its {health_adjective} profile and sector position support long-term holding."
        )

        strengths = [
            f"Established leadership in the {company_info.industry} sector.",
            f"Favorable public profile with average sentiment score of {sentiment.average_score:+.2f}.",
            f"Solid scale with a market capitalization of {format_large_number_local(metrics.market_cap)}."
        ]

        weaknesses = [
            f"Exposed to risks concerning: {risk.risk_factors[0] if risk.risk_factors else 'general macro-economic volatility'}.",
            f"Sensitive to shifts in the {company_info.sector} sector regulations."
        ]

        return AISummary(
            ticker=ticker,
            executive_summary=exec_summary,
            investment_thesis=thesis,
            strengths=strengths,
            weaknesses=weaknesses,
            generated_at=datetime.now()
        )


def format_large_number_local(val: Optional[float]) -> str:
    """
    Local helper to mock format large numbers if needed without creating imports loop.
    """
    if val is None:
        return "N/A"
    if val >= 1e12:
        return f"${val / 1e12:.2f}T"
    elif val >= 1e9:
        return f"${val / 1e9:.2f}B"
    elif val >= 1e6:
        return f"${val / 1e6:.2f}M"
    else:
        return f"${val:,.2f}"
