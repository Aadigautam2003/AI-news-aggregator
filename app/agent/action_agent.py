import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.agent.qa_agent import QAAgent
from app.database.repository import Repository
import sys

load_dotenv()

class ActionAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.qa_agent = QAAgent()
        self.qa_agent.load_knowledge_base()
        self.repo = Repository()

    def search_knowledge_base(self, query: str) -> str:
        """Searches the knowledge base for an answer."""
        print(f"\n[Tool Execution] Searching knowledge base for: '{query}'")
        return self.qa_agent.answer_question(query)

    def extract_tasks_from_digest(self, digest_id: str) -> str:
        """Fetches tasks for a specific digest ID."""
        print(f"\n[Tool Execution] Extracting tasks for digest: '{digest_id}'")
        digests = self.repo.get_recent_digests(hours=720)
        for digest in digests:
            if digest["id"] == digest_id:
                if digest.get("tasks"):
                    return f"Tasks for {digest_id}: {digest['tasks']}"
                else:
                    return f"No tasks found for {digest_id}"
        return f"Digest {digest_id} not found."

    def execute_sensitive_action(self, action_description: str) -> str:
        """Executes a sensitive action, requiring human approval."""
        print(f"\n[WARNING] The agent wants to execute a sensitive action:")
        print(f"Action: {action_description}")

        if not sys.stdin.isatty():
            print("[Tool Execution] Non-interactive environment detected. Action denied by default.")
            return "Action was denied because human approval could not be obtained in a non-interactive environment."

        while True:
            try:
                user_input = input("Approve action? [y/N]: ").strip().lower()
                if user_input in ['y', 'yes']:
                    print("[Tool Execution] Action approved and executed.")
                    return f"Action executed successfully: {action_description}"
                elif user_input in ['n', 'no', '']:
                    print("[Tool Execution] Action denied.")
                    return "Action was denied by the user."
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")
            except EOFError:
                print("[Tool Execution] Action denied (EOF).")
                return "Action was denied by the user."

    def run_workflow(self, user_prompt: str):
        print(f"\n=== Starting Agentic Workflow ===")
        print(f"User Request: {user_prompt}\n")

        messages = [
            {"role": "system", "content": "You are an intelligent agent that plans multi-step tasks and uses tools to answer queries and execute actions. You must rely on the tools provided."},
            {"role": "user", "content": user_prompt}
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Searches the AI news knowledge base for an answer to a query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The question to ask the knowledge base."
                            }
                        },
                        "required": ["query"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "extract_tasks_from_digest",
                    "description": "Fetches the extracted tasks for a specific digest ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "digest_id": {
                                "type": "string",
                                "description": "The ID of the digest (e.g., openai:some-guid)"
                            }
                        },
                        "required": ["digest_id"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_sensitive_action",
                    "description": "Executes a sensitive action such as creating official tasks in an external system or sending an email.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action_description": {
                                "type": "string",
                                "description": "A detailed description of the action to execute."
                            }
                        },
                        "required": ["action_description"],
                    },
                }
            }
        ]

        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )

            response_message = response.choices[0].message
            messages.append(response_message)

            if response_message.content:
                print(f"Agent: {response_message.content}")

            tool_calls = response_message.tool_calls
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    if function_name == "search_knowledge_base":
                        function_response = self.search_knowledge_base(
                            query=function_args.get("query")
                        )
                    elif function_name == "extract_tasks_from_digest":
                        function_response = self.extract_tasks_from_digest(
                            digest_id=function_args.get("digest_id")
                        )
                    elif function_name == "execute_sensitive_action":
                        function_response = self.execute_sensitive_action(
                            action_description=function_args.get("action_description")
                        )
                    else:
                        function_response = f"Error: function {function_name} does not exist"

                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )
            else:
                break

        print("\n=== Workflow Complete ===")

if __name__ == "__main__":
    agent = ActionAgent()
    agent.run_workflow("Search the knowledge base for recent news about language models. If you find any, execute an action to create a report.")
