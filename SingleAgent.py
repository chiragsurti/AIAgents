from autogen import AssistantAgent, UserProxyAgent
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

config_list = {
      "model": os.environ.get("AZURE_OPENAI_MODEL"),
      "api_key": os.environ.get("AZURE_OPENAI_KEY"),
      "api_type": "azure",
      "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
      "api_version": os.environ.get("AZURE_OPENAI_API_VERSION")
  }


# Create an instance of the AssistantAgent class for a comedian
comedian = AssistantAgent(
    name="comedian",
    system_message="You are a professional comedian. You can tell jokes and entertain people.",
    description="This agent is a great comedian telling interesting and funny jokes.",
    llm_config=config_list
)

# Create an instance of the UserProxyAgent class
user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_config={"work_dir": "coding", "use_docker": False}
)

# Initiate a chat between the user_proxy agent and the comedian agent
user_proxy.initiate_chat(
    comedian,
    message="Tell me a joke about cats and ninjas."
)