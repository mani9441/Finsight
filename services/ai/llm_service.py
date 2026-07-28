"""
LLM Service implementation using Google Gemini 2.5 Flash API (REST).
Includes mock fallback mode for development without API keys.
"""

import json
import requests
import time
from datetime import datetime
from typing import Optional

from core import get_logger
from core.exceptions import ServiceError, DataRetrievalError
from models import CompanyOverview, FinancialRatios, SentimentResult, RiskAssessment, AISummary
from services.interfaces import IAISummaryService
from services.ai.prompt_builder import PromptBuilder
from services.common.response_validator import ResponseValidator
from config.settings import settings

logger = get_logger("gemini_service")

class LlmService(IAISummaryService):
    """
    Communicates with Google Gemini 2.5 Flash to generate advisory reports.
    Falls back to high-fidelity mock generators if credentials are not configured.
    """

    def generate_advisory_summary(
        self,
        company_overview: CompanyOverview,
        ratios: FinancialRatios,
        sentiment: SentimentResult,
        risk: RiskAssessment
    ) -> AISummary:

        ticker = company_overview.ticker.upper()
        logger.info(f"LLM Service: Initiating Gemini summary generation for '{ticker}'")

        prompt = PromptBuilder.build_advisory_prompt(
            company_overview,
            ratios,
            sentiment,
            risk
        )

        api_key = settings.GEMINI_API_KEY

        is_mock_mode = (
            not api_key
            or api_key == "your_gemini_api_key_here"
            or "your_" in api_key.lower()
        )

        if is_mock_mode:
            logger.info(
                f"LLM Service: Gemini key missing. Returning mock report for {ticker}."
            )
            return self._generate_mock_report(
                company_overview,
                ratios,
                sentiment,
                risk
            )

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.GEMINI_MODEL}:generateContent?key={api_key}"
        )

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        start_time = time.time()

        try:

            logger.info("Sending request to Gemini...")

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )

            latency = (time.time() - start_time) * 1000

            logger.info(
                f"Gemini Status={response.status_code} "
                f"Latency={latency:.2f}ms"
            )

            logger.info("========== GEMINI RAW RESPONSE ==========")
            logger.info(response.text)
            logger.info("=========================================")

            if response.status_code != 200:
                raise ServiceError(
                    f"Gemini API Error {response.status_code}\n\n{response.text}"
                )

            response_data = response.json()

            logger.info("Parsed Gemini response successfully.")

            candidates = response_data.get("candidates")

            if not candidates:
                raise ServiceError(
                    f"No candidates returned.\n\n{response.text}"
                )

            candidate = candidates[0]

            finish_reason = candidate.get("finishReason")

            if finish_reason and finish_reason != "STOP":
                raise ServiceError(
                    f"Gemini stopped with reason: {finish_reason}"
                )

            content = candidate.get("content")

            if not content:
                raise ServiceError(
                    f"No content field.\n\n{response.text}"
                )

            parts = content.get("parts")

            if not parts:
                raise ServiceError(
                    f"No parts found.\n\n{response.text}"
                )

            text_content = parts[0].get("text")

            if not text_content:
                raise ServiceError(
                    f"Gemini returned empty text.\n\n{response.text}"
                )

            logger.info("========== GEMINI GENERATED TEXT ==========")
            logger.info(text_content)
            logger.info("===========================================")

            text_content = (
                text_content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            try:
                data = json.loads(text_content)

            except Exception as e:
                logger.exception("JSON Parsing Failed")
                logger.error(text_content)
                raise ServiceError(
                    f"Gemini returned invalid JSON.\n\n{text_content}"
                ) from e

            ResponseValidator.validate_keys(
                data,
                [
                    "executive_summary",
                    "investment_thesis",
                    "strengths",
                    "weaknesses"
                ],
                "Gemini AI Summary"
            )

            summary = data["executive_summary"]

            if not isinstance(summary, str):
                raise ServiceError(
                    "Executive summary is not a string."
                )

            if len(summary.split()) < 30:
                raise ServiceError(
                    "Executive summary too short."
                )

            logger.info("Gemini response validation successful.")

            return AISummary(
                ticker=ticker,
                executive_summary=summary,
                investment_thesis=data["investment_thesis"],
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                model_name=settings.GEMINI_MODEL,
                status="Success",
                generated_at=datetime.now()
            )

        except requests.exceptions.RequestException as e:
            logger.exception("Network Error")
            raise ServiceError(
                f"Unable to connect to Gemini.\n\n{e}"
            ) from e

        except Exception as e:
            logger.exception("Gemini Processing Error")
            raise ServiceError(str(e)) from e


    def _generate_mock_report(
        self,
        company_overview: CompanyOverview,
        ratios: FinancialRatios,
        sentiment: SentimentResult,
        risk: RiskAssessment
    ) -> AISummary:
        """
        Generates realistic, details-rich mockup reports based on ratios, sentiment, and risk profile.
        """
        ticker = company_overview.ticker.upper()
        
        # Build customized content
        exec_summary = (
            f"An analysis of {company_overview.name} ({ticker}) indicates a profile situated in the "
            f"{company_overview.industry} industry within the {company_overview.sector} sector. "
            f"Based on evaluated metrics, the company operates with a computed risk profile rated as "
            f"{risk.risk_level}. The market shows {sentiment.sentiment_label.lower()} news coverage, "
            f"while the P/E ratio is {ratios.pe_ratio if ratios.pe_ratio is not None else 'N/A'} and the ROE is "
            f"{f'{ratios.roe*100:.2f}%' if ratios.roe is not None else 'N/A'}. This summary is for educational "
            f"purposes only and relies exclusively on FinSight's internal calculations."
        )

        thesis = (
            f"While {ticker} faces considerations related to {risk.risk_factors[0] if risk.risk_factors else 'market sector fluctuations'}, "
            f"its overall position makes it an interesting case study for valuation."
        )

        strengths = [
            f"Operations in the established {company_overview.industry} space.",
            f"Favorable public profile with news sentiment label of {sentiment.sentiment_label}."
        ]
        
        if ratios.roe is not None and ratios.roe > 0:
            strengths.append(f"Positive Return on Equity indicating capital generation capacity.")

        weaknesses = [
            f"Classified at {risk.risk_level} based on active factor flags.",
            f"Exposed to sector regulations and overall macroeconomic shifts."
        ]
        
        if ratios.pe_ratio is not None and ratios.pe_ratio > 30:
            weaknesses.append("High price multiples relative to baseline corporate book earnings.")

        return AISummary(
            ticker=ticker,
            executive_summary=exec_summary,
            investment_thesis=thesis,
            strengths=strengths,
            weaknesses=weaknesses,
            model_name="Gemini 2.5 Flash",
            status="Mocked",
            generated_at=datetime.now()
        )
