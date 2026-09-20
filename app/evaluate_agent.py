import sys
import unittest
from unittest.mock import MagicMock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent.digest_agent import DigestAgent, DigestOutput
from app.agent.qa_agent import QAAgent

class TestAgentEvaluation(unittest.TestCase):

    def setUp(self):
        self.digest_agent = DigestAgent()
        self.qa_agent = QAAgent()

    def test_task_extraction(self):
        """Test that the digest agent successfully extracts structured tasks and actionable plans."""
        test_article = (
            "OpenAI has released a new update to its API. "
            "Developers must migrate their endpoints to v2 by December 31st to avoid service disruption. "
            "The priority is high. John Doe is leading the migration effort."
        )

        # Mock the OpenAI client
        mock_output = DigestOutput(
            title="API Update Notice",
            summary="OpenAI API v2 migration required by Dec 31.",
            tasks=["Migrate endpoints to v2"],
            deadlines=["December 31st"],
            entities=["OpenAI", "John Doe"],
            priorities=["High"],
            decisions=[],
            actionable_plan="Developers should begin migrating to v2 immediately.",
            confidence_score=0.9,
            reasoning_context="Directly stated in the notice."
        )

        mock_response = MagicMock()
        mock_response.output_parsed = mock_output
        self.digest_agent.client.responses.parse = MagicMock(return_value=mock_response)

        result = self.digest_agent.generate_digest(
            title="API Update Notice",
            content=test_article,
            article_type="notice"
        )

        self.assertIsNotNone(result)
        self.assertTrue(len(result.tasks) > 0, "Agent failed to extract tasks.")
        self.assertTrue(len(result.deadlines) > 0, "Agent failed to extract deadlines.")
        self.assertTrue("v2" in result.actionable_plan or "migrate" in result.actionable_plan.lower(), "Actionable plan missing key details.")

    def test_qa_grounding(self):
        """Test that the QA agent only answers using the provided context and admits when it doesn't know."""

        # Manually load known facts into the ephemeral knowledge base
        self.qa_agent.knowledge_base = [
            {
                "id": "test_1",
                "text": "The secret code for the server is 9942. It was updated by Alice.",
                "embedding": [0.1, 0.2, 0.3], # Mock embedding
                "source": "internal_wiki"
            }
        ]

        # Mock get_embedding
        self.qa_agent.get_embedding = MagicMock(return_value=[0.1, 0.2, 0.3])

        # Mock chat completion for grounded answer
        mock_completion_grounded = MagicMock()
        mock_completion_grounded.choices[0].message.content = "The secret code is 9942."

        # Mock chat completion for unknown answer
        mock_completion_unknown = MagicMock()
        mock_completion_unknown.choices[0].message.content = "I don't have enough information to answer this question."

        def side_effect(*args, **kwargs):
            messages = kwargs.get("messages", [])
            query = messages[1]["content"] if len(messages) > 1 else ""
            if "population of Paris" in query:
                return mock_completion_unknown
            else:
                return mock_completion_grounded

        self.qa_agent.client.chat.completions.create = MagicMock(side_effect=side_effect)

        # Test 1: Grounded answer
        ans = self.qa_agent.answer_question("What is the secret code for the server?")
        self.assertIn("9942", ans, "Agent failed to answer using grounded context.")

        # Test 2: Unanswerable question
        ans_unknown = self.qa_agent.answer_question("What is the population of Paris?")
        self.assertTrue("don't have enough information" in ans_unknown.lower() or "do not have enough information" in ans_unknown.lower(), f"Agent hallucinated an answer instead of admitting lack of knowledge. Response: {ans_unknown}")

if __name__ == '__main__':
    unittest.main()
