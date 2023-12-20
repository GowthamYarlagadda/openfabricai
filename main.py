import os
import warnings
from typing import Dict

from openfabric_pysdk.utility import SchemaUtil
from ontology_dc8f06af066e4a7880a5938933236037.simple_text import SimpleText
from openfabric_pysdk.context import Ray, State
from openfabric_pysdk.loader import ConfigClass

from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain import HuggingFaceHub, PromptTemplate, ChatPromptTemplate, SystemMessage, MessagesPlaceholder
from langchain.prompts import HumanMessagePromptTemplate
import gradio as gr

# Callback function called on update config
def config(configuration: Dict[str, ConfigClass], state: State):
    # Example: Print the configuration and update the state
    print("Updated configuration:", configuration)
    state.some_variable = configuration.get("some_variable", default_value)

# Callback function called on each execution pass
def execute(request: SimpleText, ray: Ray, state: State) -> SimpleText:
    output = []
    for text in request.text:
        # Integrate chatbot function here
        chatbot_response = run_model(text)
        output.append(chatbot_response)

    return SchemaUtil.create(SimpleText(), dict(text=output))

# Chatbot setup
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
huggingfacehub_api_token = "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"
repo_id = "tiiuae/falcon-7b-instruct"

llm = HuggingFaceHub(
    huggingfacehub_api_token=huggingfacehub_api_token,
    repo_id=repo_id,
    model_kwargs={"temperature": 0.01, "max_new_tokens": 250}
)

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are an AI assistant designed to be the perfect resource for answering questions in the field of science. Your capabilities span across various scientific disciplines, including physics, chemistry, biology, astronomy, geology, and environmental science. Your primary objective is to provide accurate and detailed responses to user inquiries, ranging from fundamental concepts to advanced theories. Adapt your explanations to the user's level of expertise, ensuring clarity in communication. Your knowledge should encompass the latest research developments and emerging trends in the scientific community. Prioritize accuracy, conciseness, and up-to-date information in delivering your responses."),  
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{human_input}"),
])

llm_chain = LLMChain(prompt=prompt, llm=llm, memory=memory)

# Chatbot interaction function
def crop_until_user(input_string):
    index = input_string.find("User")
    if index != -1:
        cropped_string = input_string[:index]
        return cropped_string
    else:
        return input_string

def run_model(text):
    if text.lower() == 'bye':
        memory.clear()
        return None
    else:
        return crop_until_user(llm_chain.run(text))

# Gradio Interface for testing the chatbot
iface = gr.Interface(fn=run_model, inputs=[gr.Textbox(info="Enter 'bye' to clear the conversation", label="Input Text")], outputs="text")
iface.launch(debug=True)
