from crewai import Agent,Task, Crew, LLM
import os

import yaml
import requests


#internal imports


##trello 

trello_api_key=""
trello_token=""
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

def create_card(list_id, card_name):
    url = f"https://api.trello.com/1/cards"
    querystring = {"name": card_name, "idList": list_id, "key": trello_api_key, "token": trello_token}
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
    api_key=""
)
class TaskEstimate(BaseModel):
    task_name: str = Field(..., description="Name of the task")
    estimated_time_hours: float = Field(..., description="Estimated time to complete the task in hours")
    required_resources: List[str] = Field(..., description="List of resources required to complete the task")
    duaration_days: List[str] = Field(..., description="List of duaration of each task in days")

class Milestone(BaseModel):
    milestone_name: str = Field(..., description="Name of the milestone")
    tasks: List[str] = Field(..., description="List of task IDs associated with this milestone")
    
class ProjectPlan(BaseModel):
    tasks: List[TaskEstimate] = Field(..., description="List of tasks with their estimates")
    milestones: List[Milestone] = Field(..., description="List of project milestones")
    
    
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
  output_pydantic=ProjectPlan # This is the structured output we want
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

from IPython.display import display, Markdown

project = 'Website'
industry = 'Technology'
project_objectives = 'Create a website for a small business'
team_members = """
- John Doe (Project Manager)
- Jane Doe (Software Engineer)
- Bob Smith (Designer)
- Alice Johnson (QA Engineer)
- Tom Brown (QA Engineer)
"""
project_requirements = """
- Create a responsive design that works well on desktop and mobile devices
- Implement a modern, visually appealing user interface with a clean look
- Develop a user-friendly navigation system with intuitive menu structure
- Include an "About Us" page highlighting the company's history and values
- Design a "Services" page showcasing the business's offerings with descriptions
- Create a "Contact Us" page with a form and integrated map for communication
- Implement a blog section for sharing industry news and company updates
- Ensure fast loading times and optimize for search engines (SEO)
- Integrate social media links and sharing capabilities
- Include a testimonials section to showcase customer feedback and build trust
"""

# Format the dictionary as Markdown for a better display in Jupyter Lab
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
display(Markdown(formatted_output))

# The given Python dictionary
inputs = {
  'project_type': project,
  'project_objectives': project_objectives,
  'industry': industry,
  'team_members': team_members,
  'project_requirements': project_requirements
}

# Run the crew
result = crew.kickoff(
  inputs=inputs
)

model_dict = result.pydantic.dict()['tasks']
model_dict = result.pydantic.dict()
print(model_dict)
milestones =result.pydantic.dict()['milestones']
#call the function to create the board and return the id
print(milestones)
name_board="test_2"
id_board = create_board(project)
"create a list of milestones"
# Gather the milestones





# Initialize a dictionary to store tasks per milestone
tasks_per_milestone = {}

# Iterate through each milestone to get tasks
for milestone in milestones:
    milestone_name = milestone['milestone_name']
    tasks = milestone['tasks']
    print(tasks)
    tasks_per_milestone[milestone_name] = tasks
    list_id=create_list(id_board,milestone_name)
    for task in tasks:
      create_card(list_id, task)
    

# Output the result
print("Milestones:", list(tasks_per_milestone.keys()))
print("Tasks per milestone:", tasks_per_milestone)


