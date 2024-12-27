from flask import Flask,  render_template, request,jsonify
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')


from crewai import Agent,Task, Crew, LLM
import os

import yaml
import requests


#internal imports


##trello 

trello_api_key="env"
trello_token="env"
def create_board(board_name):
    url = "https://api.trello.com/1/boards/"
    querystring = {"name": board_name, "key": trello_api_key, "token": trello_token}
    response = requests.request("POST", url, params=querystring)
    board_id = response.json()["shortUrl"].split("/")[-1].strip()
    return board_id


def create_list(board_id, list_name):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    querystring = {"name": list_name, "key": trello_api_key, "token": trello_token}
    response = requests.request("POST", url, params=querystring)
    list_id = response.json()["id"]
    return list_id

def create_card(list_id, card_name, description):
    url = f"https://api.trello.com/1/cards"
    querystring = {"name": card_name, "desc": description,"idList": list_id, "key": trello_api_key, "token": trello_token}
    response = requests.request("POST", url, params=querystring)
    card_id = response.json()["id"]
    return card_id

# Define file paths for YAML configurations
files = {
    'agents': 'agents.yaml',
    'tasks': 'tasks.yaml'
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

# Assign loaded configurations to specific variables
agents_config = configs['agents']
tasks_config = configs['tasks']



from typing import List
from pydantic import BaseModel, Field
llm = LLM(
    #model="gemini/gemini-1.5-pro-latest",
    model="gemini/gemini-2.0-flash-exp",
    temperature=0.7,
    api_key="env"
)
class TaskEstimate(BaseModel):
    
    task_name: str = Field(..., description="Name of the task")
    estimated_time_hours: float = Field(..., description="Estimated time to complete the task in hours")
    required_resources: List[str] = Field(..., description="List of resources required to complete the task")
    duaration_days: List[str] = Field(..., description="estimated of number of day be precise")
    description: str = Field(..., description="description of the risks o details or any relevant inoformation")

class Milestone(BaseModel):
    milestone_name: str = Field(..., description="Name of the milestone")
    tasks: List[str] = Field(..., description="List of task IDs associated with this milestone")
    description: List[TaskEstimate] = Field(..., description="description of the risks o details or any relevant inoformation per each task")

    
class ProjectPlan(BaseModel):
    tasks: List[TaskEstimate] = Field(..., description="List of tasks with their estimates")
    milestones: List[Milestone] = Field(..., description="List of project milestones")
    project_name: str = Field(..., description="Name of the project")
    
    
# Creating Agents
project_planning_agent = Agent(
  config=agents_config['project_planning_agent'],
  llm=llm
)

estimation_agent = Agent(
  config=agents_config['estimation_agent'],
   llm=llm
)

resource_allocation_agent = Agent(
  config=agents_config['resource_allocation_agent'],
   llm=llm
)

# Creating Tasks
task_breakdown = Task(
  config=tasks_config['task_breakdown'],
  agent=project_planning_agent
)

time_resource_estimation = Task(
  config=tasks_config['time_resource_estimation'],
  agent=estimation_agent
)

resource_allocation = Task(
  config=tasks_config['resource_allocation'],
  agent=resource_allocation_agent,
  
)

# Creating Crew
crew = Crew(
  agents=[
    project_planning_agent,
    estimation_agent,
    resource_allocation_agent
  ],
  tasks=[
    task_breakdown,
    time_resource_estimation,
    resource_allocation
  ],
  verbose=True
)


# Creating Agents crew2
update_data_agent = Agent(
  config=agents_config['update_data_agent'],
  llm=llm
)
# Creating Tasks
task_update_data = Task(
  config=tasks_config['Regenerate_JSON'],
  agent=update_data_agent,
  output_pydantic=ProjectPlan # This is the structured output we want
)


crew2 = Crew(
  agents=[
    update_data_agent,
    
   
  ],
  tasks=[
    task_update_data,
    
  ],
  verbose=True
)

# Format the dictionary as Markdown for a better display in Jupyter Lab

@app.route("/inputs",methods=["GET", "POST"])
def inputs():
    data = request.get_json()
  # Extract values from the JSON data
    project = data.get('project-name')
    project_objectives = data.get('project-objectives')
    industry = data.get('industry')
    team_members = data.get('team-members')
    project_requirements = data.get('project-requirements')
    
    formatted_output = f"""
    **Project Type:** {project}

    **Project Objectives:** {project_objectives}

    **Industry:** {industry}

    **Team Members:**
    {team_members}
    **Project Requirements:**
    {project_requirements}
    """
    # Display the formatted output as Markdown
  

    # The given Python dictionary
    inputs = {
    'project_type': project,
    'project_objectives': project_objectives,
    'industry': industry,
    'team_members': team_members,
    'project_requirements': project_requirements
    }
    return start_job(inputs)

@app.route("/start_job", methods=["GET", "POST"])
def  start_job(inputs):
    
    result = crew.kickoff(
    inputs=inputs
      )
    print(time_resource_estimation.output)
    
    
    response =  time_resource_estimation.output
    print(type(response))
    return jsonify(str(response))



@app.route("/trelloboard",methods=["GET", "POST"])

def trelloboard():
    
    udata = request.get_json()
    updated_data=update_data(udata) #it return the pydantic class with updated by the user
    print(updated_data["project_name"])
    id_board=create_board(updated_data["project_name"])
    milestones =updated_data['milestones']
    print(milestones)
    for milestone in reversed(milestones):  # Reverse the order of milestones
      milestone_name = milestone['milestone_name']  # Access milestone name
      tasks = milestone['tasks']  # Access tasks
      description = milestone['description']  # Access task descriptions

      list_id = create_list(id_board, milestone_name)  # Create a list for the milestone

      for task, task_description in zip(tasks, description):  # Iterate over tasks and descriptions
          task_name = task  # Get task name
          task_detail = task_description['description'][0]  # Get the description for the task (first item in the list)
          create_card(list_id, task_name, task_detail)  # Create a card for each task
    return jsonify(str("hello world"))

def update_data(updated_data):

  inputs2 = {
    'udata': updated_data["editorContent"],
  
    }
  result = crew2.kickoff(
    inputs=inputs2
      )
  

  return result