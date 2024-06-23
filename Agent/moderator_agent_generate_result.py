import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_moderator_output(crew_goal, agents_data, access_token):
    url = "https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/agents/crew-moderator-agent/completions"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    system_prompt = (
        f"Given the following goal: {crew_goal}\n"
        f"And the following agent details:\n"
    )
    for agent in agents_data:
        system_prompt += f"Agent {agent['id']} - Role: {agent['role']}, Output Expected: {agent['output']}\n"

    body = {
        "prompt": system_prompt,
        "temperature": 0.4,
        "max_tokens": 1500
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    response_json = response.json()

    if 'choices' not in response_json:
        print(f"Error in get_moderator_output: {response_json}")
        return None

    return response_json

def query_agents(prompts, access_token):
    results = {}
    for agent_id, prompt in prompts.items():
        url = f"https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/admin/agents/{agent_id}/completions"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        body = {
            "prompt": prompt,
            "temperature": 0.4,
            "max_tokens": 1500
        }
        response = requests.post(url, headers=headers, data=json.dumps(body))
        response_json = response.json()

        if 'choices' not in response_json:
            print(f"Error in query_agents for {agent_id}: {response_json}")
            results[agent_id] = "Error retrieving response"
        else:
            results[agent_id] = response_json['choices'][0]['text']

    return results

def create_pdf(content, filename='output.pdf'):
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_result(crew_goal, agents_data):
    # Load authentication data
    with open('authentication.json', 'r', encoding='utf-8') as f:
        authentication = json.load(f)

    access_token = authentication['access_token']

    # Get prompts from the moderator agent
    moderator_output = get_moderator_output(crew_goal, agents_data, access_token)
    if not moderator_output:
        return "Error in getting moderator output"

    prompts_text = moderator_output['choices'][0]['text']
    try:
        prompts = json.loads(prompts_text)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from moderator output: {prompts_text}")
        return "Error decoding JSON from moderator output"

    # Query each agent with their respective prompts
    results = query_agents(prompts, access_token)

    # Compile the results into a single content
    combined_output = f"Crew Goal: {crew_goal}\n\n"
    for agent_id, result in results.items():
        combined_output += f"{agent_id}: {result}\n\n"

    # Create a PDF from the combined output
    pdf_filename = create_pdf(combined_output)
    return pdf_filename

if __name__ == "__main__":
    # Example usage
    crew_goal = "The goal of the crew is to create a comprehensive report on the project's status and future steps."
    agents_data = [
        {'id': 'crew_agent_1', 'role': 'Research', 'output': 'Detailed research report'},
        {'id': 'crew_agent_2', 'role': 'Analysis', 'output': 'Analysis of research data'},
        {'id': 'crew_agent_3', 'role': 'Summary', 'output': 'Summary of findings'}
    ]

    pdf_filename = generate_result(crew_goal, agents_data)
    print(f"PDF created: {pdf_filename}")
