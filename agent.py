from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from .util import load_instruction_from_file
from dotenv import load_dotenv

# --- Sub Agent 1: Summarizing Agent ---
# Extracts a concise summary from the full blog text to capture key ideas or sections.
summarizing_agent = LlmAgent(
    name="SummarizingAgent",
    model="gemini-2.0-flash",
    instruction=load_instruction_from_file("summarizing_instruction.txt"),
    description="Generate summary based on the provided blog content",
    output_key="generated_summary",  # Save result to state
)

# --- Sub Agent 2: Review Agent ---
# Analyzes the generated summary or blog text and provides actionable review points or improvement suggestions.
review_agent = LlmAgent(
    name="ReviewAgent",
    model="gemini-2.0-flash",
    instruction=load_instruction_from_file("review_instruction.txt"),
    description="Provide review on the generated content",
    output_key="review_content",  
)

# --- Sub Agent 3: Editing Agent ---
# Takes the original blog and reviewer feedback, applies the suggestions, and returns only the modified parts for clear tracking.
editing_agent = LlmAgent(
    name="EditingAgent",
    model="gemini-2.0-flash",
    instruction=load_instruction_from_file("editing_instruction.txt"),
    description="Applies review feedback to revise to blog draft. Outputs only the edited segments alongside their original versions, clearly formatted for comparison.",
    output_key="final_content",
)

# # --- Llm Agent Workflow ---
# blog_agent = LlmAgent(
#     name="blog_agent",
#     model="gemini-2.0-flash",
#     instruction=load_instruction_from_file("blog_agent_instruction.txt"),
#     description="You are an agent that can summarize, review and rewrite suggestion on blogs. You have subagents that can do this",
#     sub_agents=[summarizing_agent, review_agent, suggestion_agent],
# )

# --- Sequential Agent Workflow ---
# This composite agent manages a fixed multi-step workflow.
blog_agent = SequentialAgent(
    name="blog_agent",
    sub_agents=[summarizing_agent, review_agent, editing_agent],
    description="Executes a sequence of summarizing, reviewing, and editing blog.",
)

# --- Root Agent ---
# This is the main interface agent for the user. It handles:
# - Greeting and collecting blog input
# - Validating user input
# - Delegating summarization, review, and editing to sub-agents if input is valid
root_agent =  LlmAgent(
    name="root_agent",
    model="gemini-2.0-flash",
    instruction=load_instruction_from_file("blog_agent_instruction.txt"),
    description="""
You are a helpful blog assistant.

Step 1: Greet the user with a friendly message asking them to paste their blog or topic idea.
Step 2: If the user's message does not appear to contain blog content, gently prompt them again to provide it.
Step 3: Once you detect valid blog content, proceed with summarizing, reviewing, and revising using your sub-agents.
""",
    sub_agents=[blog_agent],
)

load_dotenv()
# Instantiate constants
APP_NAME = "editiors_copilot"
USER_ID = "test"
SESSION_ID = "123344"

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)
runner = Runner(
    agent=root_agent, app_name=APP_NAME, session_service=session_service
)

# Agent Interaction
def call_agent(query):
    print("🔍 Running Editiors Copilot App...\n")
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

#call_agent("Here's a sample blog draft I want reviewed and improved.")
