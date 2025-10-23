import sys
import os

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from traffic_agents.agent import root_agent
import logging
import os
from dotenv import set_key, load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GOOGLE_CLOUD_PROJECT = "ajmalaziz-814-20250326021733"
GOOGLE_CLOUD_LOCATION = "us-central1"
STAGING_BUCKET = "gs://transport-agent"

ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

vertexai.init(
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# Function to update the .env file
def update_env_file(agent_engine_id, env_file_path):
    """Updates the .env file with the agent engine ID."""
    try:
        set_key(env_file_path, "AGENT_ENGINE_ID", agent_engine_id)
        print(f"Updated AGENT_ENGINE_ID in {env_file_path} to {agent_engine_id}")
    except Exception as e:
        print(f"Error updating .env file: {e}")

logger.info("deploying safety investigation agent...")

app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

logging.debug("deploying agent to agent engine:")

remote_app = agent_engines.create(
    app,
    display_name="traffic_investigation_agent",
    requirements=[
        "google-cloud-aiplatform[adk,agent-engines]>=1.100.0,<2.0.0",
        "google-adk>=1.7.0,<2.0.0",
        "python-dotenv",
        "absl-py>=2.3.1",
        "db-dtypes>=1.4.3",
        "python-dotenv>=1.1.1",
        "google-cloud-secret-manager",
        "pandas>=2.3.1"
    ],
    extra_packages=[
        "./traffic_agents",
    ],
)

# log remote_app
logging.info(f"Deployed incident investigation agent to Vertex AI Agent Engine successfully, resource name: {remote_app.resource_name}")

# Update the .env file with the new Agent Engine ID
update_env_file(remote_app.resource_name, ENV_FILE_PATH)
