import json
import requests
import os
from fpdf import FPDF
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def delete_existing_index(assistant_index_id, access_token):
    url = f"https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/indexes/{assistant_index_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'accept': '*/*'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"Index {assistant_index_id} deleted successfully.")
    else:
        print(f"Failed to delete index {assistant_index_id}: {response.status_code} - {response.text}")

def delete_existing_agent(assistant_id, access_token):
    url = f"https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/agents/{assistant_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'accept': '*/*'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"Agent {assistant_id} deleted successfully.")
    else:
        print(f"Failed to delete agent {assistant_id}: {response.status_code} - {response.text}")

def create_agent(assistant_name, description, system_prompt, default_model='gpt-4o'):
    # Load authentication data
    with open('authentication.json', 'r', encoding='utf-8') as f:
        authentication = json.load(f)

    access_token = authentication['access_token']

    # LLM configuration
    llm_config_temperature = 0.4
    llm_config_max_tokens = 4000
    publish_mode = 'internal'
    agent_type = 'BaseQuestionAnswerAgent'
    assistant_id = assistant_name.lower().replace(" ", "-")
    assistant_index_id = assistant_id + '-index'

    # Delete existing index and agent if they exist
    delete_existing_index(assistant_index_id, access_token)
    delete_existing_agent(assistant_id, access_token)

    # Step 1: Create an index (knowledge store) for your agent
    url = "https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/indexes"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    body = {
        'owners': [],
        'viewers': [],
        'id': assistant_index_id
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    print(response.json())

    # Step 2: Create a custom agent
    url = "https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/agents"
    body = {
        "owners": [
            {"subjectId": "1", "name": "AkashV"}
        ],
        'viewers': [],
        'id': assistant_id,
        'name': assistant_name,
        'type': agent_type,
        'description': description,
        'system_prompt': system_prompt,
        'search_config': {
            'use_vector': True,
            'query_prompt_template': (
                "Below is a history of the conversation so far,\n"
                "and a new question asked by the user that needs to be answered by searching in a knowledge base.\n\n"
                "Chat History:\n"
                "{chat_history}\n\n"
                "Question:\n"
                "{question}\n"
            ),
            'index_name': assistant_index_id
        },
        'llm_config': {
            'temperature': llm_config_temperature,
            'max_tokens': llm_config_max_tokens,
            'default_model': default_model
        },
        'publish': publish_mode
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    print(response.json())

# Define agents with their roles, descriptions, and expected outputs
agents = [
    {
        "name": "Trend Analysis Agent",
        "description": "Monitor and analyze market trends. Collect data from various sources like news articles, industry reports, and social media. Identify emerging trends and shifts in the market. Generate trend analysis reports.",
        "output": "Trend analysis report"
    },
    {
        "name": "Competitor Analysis Agent",
        "description": "Monitor and analyze competitor activities. Track competitors’ product launches, pricing strategies, and marketing campaigns. Analyze competitors’ strengths, weaknesses, opportunities, and threats (SWOT analysis). Generate comprehensive competitor analysis reports.",
        "output": "SWOT analysis report"
    },
    {
        "name": "Customer Sentiment Analysis Agent",
        "description": "Analyze customer sentiments from various sources. Collect and analyze customer reviews, social media posts, and survey responses. Identify positive and negative sentiments and key drivers behind them. Generate customer sentiment analysis reports.",
        "output": "Customer sentiment analysis report"
    },
    {
        "name": "Market Forecasting Agent",
        "description": "Forecast future market conditions. Use historical data and current market conditions to predict future trends. Develop forecasting models using machine learning techniques. Generate market forecasts and scenario analyses.",
        "output": "Market forecast report"
    }
]

# Predefined prompts for each agent
agent_queries = {
    "Trend Analysis Agent": "Analyze the latest market trends for Coca-Cola.",
    "Competitor Analysis Agent": "Provide a SWOT analysis of Coca-Cola's main competitors.",
    "Customer Sentiment Analysis Agent": "Analyze customer sentiments about Coca-Cola from social media and reviews.",
    "Market Forecasting Agent": "Forecast the market conditions for Coca-Cola for the next year."
}

# Create agents
for agent in agents:
    name = agent["name"]
    description = agent["description"]
    system_prompt = f"You are a helpful assistant specialized in handling {name} related queries. {description} The expected output format is: {agent['output']}."
    create_agent(name, description, system_prompt)

# Load cookies for session ID and interlocutor ID
with open('cookies.json', 'r', encoding='utf-8') as f:
    cookies = json.load(f)

session_id = cookies['session_id']
interlocutor_id = cookies['interlocutor_id']
model = 'gpt-4'  # Select from [gpt-3.5-turbo, gpt-4, gpt-4o]

# Function to query agents
def query_agent(agent_name, prompt, session_id, interlocutor_id, access_token):
    url = f"https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/agents/{agent_name.lower().replace(' ', '-')}/messages"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    body = {
        "message": prompt,
        "session_id": session_id,
        "interlocutor_id": interlocutor_id,
        "stream": False,
        "model_id": model
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    response_json = response.json()
    if 'message' in response_json:
        return response_json['message']
    else:
        print("message not found in the response")
        print(response_json)
        return None

# Query each agent and collect responses
# Load authentication data
with open('authentication.json', 'r', encoding='utf-8') as f:
    authentication = json.load(f)
responses = {}
for agent in agents:
    name = agent["name"]
    prompt = agent_queries[name]
    response = query_agent(name, prompt, session_id, interlocutor_id, authentication['access_token'])
    responses[name] = response

# Function to create PDF from responses
def create_pdf(responses, filename='output.pdf'):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Market Research and Analysis Report for Coca-Cola\n\n")
    for agent_name, response in responses.items():
        pdf.multi_cell(0, 10, f"{agent_name}:\n{response}\n\n")
    pdf.output(filename)

# Create the PDF
create_pdf(responses)

print("PDF created successfully.")
