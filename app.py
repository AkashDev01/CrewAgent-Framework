import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import json
from Agent.create_custom_agent import create_agent
from Agent.moderator_agent_generate_result import generate_result

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder=os.path.join('UI', 'templates'), static_folder=os.path.join('UI', 'static'))

# Run authentication, generate-cookies, and create moderator agent scripts
os.system('python Agent/authentication.py')
os.system('python Agent/generate-cookies.py')
os.system('python Agent/moderator_agent_creation.py')

agent_counter = 0
agents_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_agent', methods=['POST'])
def add_agent():
    global agent_counter
    data = request.json
    role = data.get('role')
    output = data.get('output')
    if not role or not output:
        return jsonify({"message": "Role and Output Expected fields are required"}), 400
    
    assistant_name = f'crew-agent-{agent_counter + 1}'
    description = f"This agent handles {role} related queries."
    system_prompt = (
        f"You are a helpful assistant specialized in handling {role} related queries. "
        f"Provide detailed information and be concise. The expected output format is: {output}.\n\n"
        "Sources:\n"
        "{sources}\n"
    )
    
    try:
        create_agent(assistant_name, description, system_prompt)
        agents_data.append({'id': assistant_name, 'role': role, 'output': output})
        agent_counter += 1
        return jsonify({"message": "Agent added successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Failed to add agent: {str(e)}"}), 500

@app.route('/generate_output', methods=['POST'])
def generate_output():
    data = request.json
    crew_goal = data.get('crewPurpose')
    
    pdf_filename = generate_result(crew_goal, agents_data)
    return jsonify({"message": "PDF generated successfully", "pdf_url": pdf_filename}), 200

if __name__ == '__main__':
    app.run(debug=True)
