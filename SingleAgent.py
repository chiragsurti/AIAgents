import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Create Azure OpenAI model client
model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=os.environ.get("AZURE_OPENAI_MODEL"),
    model=os.environ.get("AZURE_OPENAI_MODEL"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_KEY")
)

# Create an instance of the AssistantAgent class for a comedian
comedian = AssistantAgent(
    name="comedian",
    model_client=model_client,
    system_message="You are a professional comedian. You can tell jokes and entertain people.",
    description="This agent is a great comedian telling interesting and funny jokes."
)


async def main():
    """Main function to run the agent."""
    # Create task message
    task = TextMessage(content="Tell me a joke about cats and ninjas.", source="user")
    
    # Run the agent and stream to console
    await Console(comedian.run_stream(task=task))


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())