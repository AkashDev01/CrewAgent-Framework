import json
import requests
import os

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
    # Load authentication and cookie data
    with open('authentication.json', 'r', encoding='utf-8') as f:
        authentication = json.load(f)

    with open('cookies.json', 'r', encoding='utf-8') as f:
        cookies = json.load(f)

    access_token = authentication['access_token']

    # LLM configuration
    llm_config_temperature = 0.4
    llm_config_max_tokens = 4000
    publish_mode = 'internal'
    agent_type = 'BaseQuestionAnswerAgent'
    assistant_id = assistant_name.lower().replace(" ", "-")
    assistant_index_id = assistant_id + '-index'

    # Delete existing index if it exists
    delete_existing_index(assistant_index_id, access_token)


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

if __name__ == "__main__":
    # Example usage
    assistant_name = 'ExampleAgent'
    description = 'This is an example agent.'
    system_prompt = (
        "You are a helpful assistant specialized in handling example-related queries. "
        "You have access to a knowledge base containing details of all example data for a project. "
        "You can help users understand which examples are relevant, identify areas with recurring issues, "
        "and provide information on the status and details of various examples. "
        "Always include the relevant example details in your response and be brief. "
        "If a question is asked that you cannot answer, suggest looking it up directly in the example database.\n\n"
        "Sources:\n"
        "{sources}\n"
    )

    create_agent(assistant_name, description, system_prompt)
