import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from app.schemas.proposal import ProposalRequest, ProposalResponse

load_dotenv()


class ProposalService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment or .env file.")

        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=api_key)

        self.system_instruction = (
            "You are a Principal Enterprise Solutions Architect and Tech Lead. "
            "Your job is to analyze client RFP requirements, technical briefs, and constraints, "
            "then generate a realistic, production-ready, highly professional Technical Proposal. "
            "Estimates must be pragmatic (not overly optimistic). "
            "Select modern, industry-standard technologies suitable for production."
        )

    async def generate_proposal(self, request: ProposalRequest) -> ProposalResponse:
        """
        Analyzes client input and produces a strictly typed ProposalResponse
        using Gemini Structured Outputs.
        """
        user_prompt = f"""
Analyze the following client request and build a detailed technical proposal:

CLIENT NAME: {request.client_name}
BUDGET TIER: {request.budget_level}
TARGET TIMELINE: {request.target_timeline_weeks or 'Flexible / Not specified'}

PROJECT REQUIREMENTS & BRIEF:
{request.project_description}

GUIDELINES:
1. Provide a clear, compelling project title and executive summary.
2. Recommend an appropriate modern tech stack with clear justification for each choice.
3. Break down the scope into distinct modules/features with realistic min and max engineering hours.
4. Highlight real technical risks and actionable mitigation strategies.
5. Calculate aggregate min and max hours accurately.
"""

        # Using the async client (.aio) to avoid blocking the FastAPI event loop
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema=ProposalResponse,
                temperature=0.2,  # Low temperature for deterministic, analytical output
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        # Validate and parse the JSON string into our Pydantic model
        return ProposalResponse.model_validate_json(response.text)