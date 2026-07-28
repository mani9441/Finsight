"""
Prompt Builder for assembling structured LLM queries.
Generates template prompts with strict output format guidelines.
"""

import json
from typing import List
from models import CompanyInfo, FinancialMetrics, SentimentResult, RiskAssessment

class PromptBuilder:
    """
    Formulates context-rich prompt templates designed for LLMs to generate structured reports.
    """

    @staticmethod
    def build_advisory_prompt(
        company_info: CompanyInfo,
        metrics: FinancialMetrics,
        sentiment: SentimentResult,
        risk: RiskAssessment
    ) -> str:
        """
        Builds a structured prompt detailing corporate profile, financial ratios,
        news sentiment metrics, and computed risk indicators.
        Instructs the model to output a strict JSON format.
        """
        # Format the financial indicators
        metrics_dict = {
            "pe_ratio": metrics.pe_ratio,
            "ps_ratio": metrics.ps_ratio,
            "pb_ratio": metrics.pb_ratio,
            "gross_margin": f"{metrics.gross_margin * 100:.2f}%" if metrics.gross_margin is not None else "N/A",
            "operating_margin": f"{metrics.operating_margin * 100:.2f}%" if metrics.operating_margin is not None else "N/A",
            "debt_to_equity": metrics.debt_to_equity,
            "roe": f"{metrics.roe * 100:.2f}%" if metrics.roe is not None else "N/A"
        }

        prompt = f"""You are an expert financial analyst and investment advisor.
Analyze the following corporate metadata, financial indicators, recent news sentiment averages, and computed risk assessment factors for {company_info.name} ({company_info.ticker}).

### 1. CORPORATE PROFILE
Ticker: {company_info.ticker}
Name: {company_info.name}
Sector: {company_info.sector}
Industry: {company_info.industry}
Business Description: {company_info.summary}

### 2. FINANCIAL PERFORMANCE INDICATORS
Currency: {metrics.currency}
Market Cap: {metrics.market_cap}
{json.dumps(metrics_dict, indent=2)}

### 3. NEWS SENTIMENT METRICS
Average Sentiment Score (Range -1 to 1): {sentiment.average_score:+.2f}
Overall Sentiment Label: {sentiment.sentiment_label}
Number of Articles Analyzed: {sentiment.article_count}

### 4. COMPUTED RISK ASSESSMENT
Overall Risk Level: {risk.risk_level}
Composite Risk Score (Range 0 to 100): {risk.risk_score:.1f}
Key Risk Factors Identified:
{chr(10).join([f'- {factor}' for factor in risk.risk_factors])}

### INSTRUCTIONS:
- Review the data thoroughly. 
- Formulate an educational summary of the company's status.
- Highlight key strengths/opportunities (minimum 2, maximum 5).
- Highlight key weaknesses/threats (minimum 2, maximum 5).
- Create a concise investment thesis summarizing the outlook.
- Do not provide actual binary buy/sell recommendations (avoid giving direct financial advice). Focus on analytical evaluation.

### RESPONSE FORMAT:
You MUST respond ONLY with a raw JSON object containing exactly the following keys (no markdown packaging, no explanation outside of the JSON):
{{
  "executive_summary": "Your executive summary paragraph here (3-5 sentences).",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
  "investment_thesis": "Your investment thesis sentence here (1-2 sentences)."
}}
"""
        return prompt.strip()
