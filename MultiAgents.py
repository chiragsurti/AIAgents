from autogen import AssistantAgent, UserProxyAgent, ConversableAgent,GroupChatManager, GroupChat
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

config_list_Ollama = {
    "model": "llama3.2:latest",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
  }



config_list_AzureOpenAI = {
      "model": os.environ.get("AZURE_OPENAI_MODEL"),
      "api_key": os.environ.get("AZURE_OPENAI_KEY"),
      "api_type": "azure",
      "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
      "api_version": os.environ.get("AZURE_OPENAI_API_VERSION")
  }




# ## The task!
# The task is to write a blogpost about the stock price performance of Nvidia in the past month. Today's date is 2024-04-23.

task = "Write a blogpost about the Weather Conditions in Arizona and New York."\
"Include the current Max weather of Arizona and New York, and how the weather has changed over the past month in terms of percentage change.\". "\
"Use open-meteo API for the data optional api key. Investigate possible reasons of the weather."


# ## Build a group chat
# 
# This group chat will include these agents:
# 
# 1. **User_proxy** or **Admin**: to allow the user to comment on the report and ask the writer to refine it.
# 2. **Planner**: to determine relevant information needed to complete the task.
# 3. **Engineer**: to write code using the defined plan by the planner.
# 4. **Executor**: to execute the code written by the engineer.
# 5. **Writer**: to write the report.


user_proxy = ConversableAgent(
    name="Admin",
    system_message="Give the task, and send "
    "instructions to writer to refine the blog post.",
    code_execution_config=False,
    llm_config=config_list_AzureOpenAI,
    human_input_mode="ALWAYS",
)





planner = ConversableAgent(
    name="Planner",
    system_message="Given a task, please determine "
    "what information is needed to complete the task. "
    "Please note that the information will all be retrieved using"
    " Python code. Please only suggest information that can be "
    "retrieved using Python code and APIs which are available "
    "After each step is done by others, check the progress and "
    "instruct the remaining steps. If a step fails, try to "
    "workaround",
    description="Planner. Given a task, determine what "
    "information is needed to complete the task. "
    "After each step is done by others, check the progress and "
    "instruct the remaining steps",
    llm_config=config_list_AzureOpenAI,
)


engineer = AssistantAgent(
    name="Engineer",
    llm_config=config_list_AzureOpenAI,
    description="An engineer that writes code based on the plan "
    "provided by the planner.",
)


# **Note**: In this lesson, you'll use an alternative method of code execution by providing a dict config. However, you can always use the LocalCommandLineCodeExecutor if you prefer. For more details about code_execution_config, check this: https://microsoft.github.io/autogen/docs/reference/agentchat/conversable_agent/#__init__


executor = ConversableAgent(
    name="Executor",
    system_message="Execute the code written by the "
    "engineer and report the result. Read api_key from the environment variable.",
    human_input_mode="NEVER",
    code_execution_config={
        "last_n_messages": 3,
        "work_dir": "coding",
        "use_docker": False,
    },
)





writer = ConversableAgent(
    name="Writer",
    llm_config=config_list_Ollama,
    system_message="Writer."
    "Please write blogs in markdown format (with relevant titles)"
    " and put the content in pseudo ```md``` code block. "
    "You take feedback from the admin and refine your blog.",
    description="Writer."
    "Write blogs based on the code execution results and take "
    "feedback from the admin to refine the blog."
)


# ## Define the group chat




groupchat = GroupChat(
    agents=[user_proxy, engineer, writer, executor, planner],
    messages=[],
    max_round=10,
)





manager = GroupChatManager(
    groupchat=groupchat, llm_config=config_list_AzureOpenAI
)


# ## Start the group chat!


groupchat_result = user_proxy.initiate_chat(
    manager,
    message=task,
)