import os
from typing import Optional, List
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class DigestOutput(BaseModel):
    title: str
    summary: str
    tasks: List[str]
    deadlines: List[str]
    entities: List[str]
    priorities: List[str]
    decisions: List[str]
    actionable_plan: str
    confidence_score: float
    reasoning_context: str

PROMPT = """You are an expert AI news analyst specializing in summarizing and extracting structured information from technical articles, research papers, and video content about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly understand the key points and significance of AI-related content, and to extract actionable plans rather than just summaries.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content.
- Write a 2-3 sentence summary that highlights the main points and why they matter.
- Extract any tasks, deadlines, entities (companies, people, models), priorities, and decisions mentioned in the text.
- Generate an actionable plan detailing what a practitioner should do with this information.
- Provide a confidence score (0.0 to 1.0) indicating how certain you are of your extraction based on the source text.
- Provide a brief reasoning context explaining your extraction and the source of the facts.
- **CRITICAL**: Explicitly handle uncertainty. If tasks, deadlines, decisions, or any other specific information is unavailable in the text, you must clearly state that it is unavailable or leave the list empty rather than hallucinating details.
- Use clear, accessible language while maintaining technical accuracy.
- Avoid marketing fluff - focus on substance."""


class DigestAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.system_prompt = PROMPT

    def generate_digest(self, title: str, content: str, article_type: str) -> Optional[DigestOutput]:
        try:
            user_prompt = f"Create a digest for this {article_type}: \n Title: {title} \n Content: {content[:8000]}"

            response = self.client.responses.parse(
                model=self.model,
                instructions=self.system_prompt,
                temperature=0.7,
                input=user_prompt,
                text_format=DigestOutput
            )
            
            return response.output_parsed
        except Exception as e:
            print(f"Error generating digest: {e}")
            return None

