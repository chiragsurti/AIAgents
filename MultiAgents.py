import asyncio
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Configuration for Ollama (local LLM)
model_client_ollama = OpenAIChatCompletionClient(
    model="llama3.2:latest",
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# Configuration for Azure OpenAI
# Note: azure_deployment is your deployment name in Azure Portal
# model specifies the OpenAI model capabilities to expect
model_client_azure = AzureOpenAIChatCompletionClient(
    azure_deployment=os.environ.get("AZURE_OPENAI_MODEL"),  # Your Azure deployment name
    model=os.environ.get("AZURE_OPENAI_MODEL"),  # The model type (e.g., gpt-4o)
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_KEY")
)

# ## The task!
# The task is to write a blogpost about the Weather Conditions in Arizona and New York.

task = (
    "Write a blogpost about the Weather Conditions in Arizona and New York. "
    "Include the current Max weather of Arizona and New York, and how the weather has changed over the past month in terms of percentage change. "
    "Use open-meteo API for the data (optional api key). Investigate possible reasons of the weather."
)


# ## Build a group chat
# 
# This group chat will include these agents:
# 
# 1. **Planner**: to determine relevant information needed to complete the task.
# 2. **Engineer**: to write code using the defined plan by the planner.
# 3. **Executor**: to execute the code written by the engineer.
# 4. **Writer**: to write the report.

planner = AssistantAgent(
    name="Planner",
    model_client=model_client_azure,
    system_message=(
        "Given a task, please determine what information is needed to complete the task. "
        "Please note that the information will all be retrieved using Python code. "
        "Please only suggest information that can be retrieved using Python code and APIs which are available. "
        "After each step is done by others, check the progress and instruct the remaining steps. "
        "If a step fails, try to workaround."
    ),
    description=(
        "Planner. Given a task, determine what information is needed to complete the task. "
        "After each step is done by others, check the progress and instruct the remaining steps."
    )
)

engineer = AssistantAgent(
    name="Engineer",
    model_client=model_client_azure,
    system_message="You are an engineer that writes code based on the plan provided by the planner.",
    description="An engineer that writes code based on the plan provided by the planner."
)

# Create code executor with local command line execution
code_executor = LocalCommandLineCodeExecutor(work_dir="coding")

executor = CodeExecutorAgent(
    name="Executor",
    code_executor=code_executor,
    description="Execute the code written by the engineer and report the result."
)

writer = AssistantAgent(
    name="Writer",
    model_client=model_client_ollama,
    system_message=(
        "Writer. Please write blogs in markdown format (with relevant titles) "
        "and put the content in pseudo ```md``` code block. "
        "You take feedback from the admin and refine your blog."
    ),
    description=(
        "Writer. Write blogs based on the code execution results and take "
        "feedback from the admin to refine the blog."
    )
)


async def main():
    """Main function to run the multi-agent workflow."""
    # Define the group chat with termination condition
    termination = MaxMessageTermination(max_messages=10)
    
    team = RoundRobinGroupChat(
        participants=[planner, engineer, executor, writer],
        termination_condition=termination
    )
    
    # Create task message
    task_message = TextMessage(content=task, source="user")
    
    # Run the team and stream to console
    await Console(team.run_stream(task=task_message))


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())