# Required variables
export PROJECT_ID="ajmalaziz-814-20250326021733"
export APP_ID="pricing_agent_team_1752796033477"
export DISPLAY_NAME="Traffic Investigator Agent"
export DESCRIPTION="Supports with investigating traffic incidents"
export ICON_URI="https://i.pinimg.com/564x/b3/e0/94/b3e09489dcad03b0cd7c3547720c2573.jpg"
export TOOL_DESCRIPTION="This agent supports with investigating traffic incidents."



curl -X POST \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json" \
    -H "X-Goog-User-Project: ajmalaziz-814-20250326021733" \
    "https://discoveryengine.googleapis.com/v1alpha/projects/ajmalaziz-814-20250326021733/locations/global/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents" \
    -d '{
        "displayName": "'"${DISPLAY_NAME}"'",
        "description": "'"${DESCRIPTION}"'",
        "icon": {
            "uri": "'"${ICON_URI}"'"
        },
        "adk_agent_definition": {
            "tool_settings": {
                "tool_description": "'"${TOOL_DESCRIPTION}"'"
            },
            "provisioned_reasoning_engine": {
                "reasoning_engine": "..."
            }
        }
    }'