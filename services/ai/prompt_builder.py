"""
Prompt Builder for assembling structured LLM queries.
Generates template prompts with strict output format guidelines.
"""

import json
from models import CompanyOverview, FinancialRatios, SentimentResult, RiskAssessment

class PromptBuilder:
    """
    Formulates context-rich prompt templates designed for Gemini to generate structured reports.
    """

    @staticmethod
    def build_advisory_prompt(
        overview: CompanyOverview,
        ratios: FinancialRatios,
        sentiment: SentimentResult,
        risk: RiskAssessment
    ) -> str:
        """
        Builds a structured prompt detailing corporate profile, financial ratios,
        news sentiment metrics, and computed risk indicators.
        Instructs the model to output a strict JSON format.
        """
        # Format the financial indicators
        ratios_dict = {
            "pe_ratio": ratios.pe_ratio if ratios.pe_ratio is not None else "Not Available",
            "pb_ratio": ratios.pb_ratio if ratios.pb_ratio is not None else "Not Available",
            "roe": f"{ratios.roe * 100:.2f}%" if ratios.roe is not None else "Not Available",
            "profit_margin": f"{ratios.profit_margin * 100:.2f}%" if ratios.profit_margin is not None else "Not Available",
            "dividend_yield": f"{ratios.dividend_yield * 100:.2f}%" if ratios.dividend_yield is not None else "Not Available",
            "eps": f"{ratios.currency} {ratios.eps:.2f}" if ratios.eps is not None else "Not Available"
        }

        factor_lines = []
        for factor in risk.risk_factors:
            factor_lines.append(f"- {factor}")
        formatted_factors = "\n".join(factor_lines)

        prompt = f"""You are an expert financial explanation layer.
Analyze the following corporate metadata, financial indicators, recent news sentiment averages, and computed risk assessment factors for {overview.name} ({overview.ticker}).

Your goal is to explain the company's financial position in simple, beginner-friendly language. Follow these rules:
1. Ground your response ONLY in the provided metrics. Do not search the web or make assumptions.
2. State when information is "Not Available" instead of inventing facts.
3. Highlight key strengths/opportunities and weaknesses/concerns supported by the data.
4. Reference the calculated risk level.
5. Avoid speculation, predictions, or direct buy/sell investment advice. Maintain a neutral, educational tone.

### 1. CORPORATE PROFILE
Ticker: {overview.ticker}
Name: {overview.name}
Sector: {overview.sector}
Industry: {overview.industry}
Business Description: {overview.business_summary}

### 2. FINANCIAL PERFORMANCE INDICATORS
Currency: {ratios.currency}
{json.dumps(ratios_dict, indent=2)}

### 3. NEWS SENTIMENT METRICS
Average Sentiment Score (Range -1 to 1): {sentiment.average_score:+.2f}
Overall Sentiment Label: {sentiment.sentiment_label}
Number of Articles Analyzed: {sentiment.article_count}
Positive Count: {sentiment.positive_count}
Neutral Count: {sentiment.neutral_count}
Negative Count: {sentiment.negative_count}

### 4. COMPUTED RISK ASSESSMENT
Overall Risk Level: {risk.risk_level}
Risk Factors / Considerations Identified:
{formatted_factors}
Detailed Explanation: {risk.risk_explanation}

### RESPONSE FORMAT:
You MUST respond ONLY with a raw JSON object containing exactly the following keys (no markdown packaging, no backticks, no explanation outside of the JSON):
{{
  "executive_summary": "Your beginner-friendly overview explanation here (approximately 150-200 words).",
  "strengths": ["Strength/Opportunity 1 based on positive ROE/margins/sentiment", "Strength/Opportunity 2"],
  "weaknesses": ["Weakness/Concern 1 based on negative ratios/sentiment/risk factors", "Weakness/Concern 2"],
  "investment_thesis": "Your neutral educational thesis summarizing the financial picture (1-2 sentences)."
}}
"""
        return prompt.strip()
