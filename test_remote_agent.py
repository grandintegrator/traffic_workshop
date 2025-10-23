from vertexai import agent_engines


# Get the remote agent engine from the RESOURCE_ID
RESOURCE_ID = "projects/812402096883/locations/us-central1/reasoningEngines/4485783140954013696"
remote_app = agent_engines.get(RESOURCE_ID)

session = remote_app.create_session(user_id="u1234")
print(f"Session details: {session}")

for event in remote_app.stream_query(
    user_id="u1234",
    session_id=session["id"],
    # message="I love the colour purple. From now on, all examples should reference the colour purple."
    message="There was incident yesterday on Monash Freeway at 10am, help me investigate it please. The incident occurred on  2025-10-19 between 8am and 8pm and the number plate was: QMX-921",
):
    print(f">>> {event}")
    # if event.is_final_response():
    #       if event.content and event.content.parts:
    #          # Assuming text response in the first part
    #          final_response_text = event.content.parts[0].text
    # print(f"<<< Agent Response: {final_response_text}")
