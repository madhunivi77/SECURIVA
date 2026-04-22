from starlette.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from .api_key_manager import validate_api_key
from starlette.applications import Starlette
from starlette.routing import Route
from collections import Counter
from .llm_client import get_llm_client
from pathlib import Path
import json

def verify_auth(request):
    try:
        api_key = request.cookies.get("api_key")

        if not api_key:
            return JSONResponse(
                {"error": "Not authenticated. Please login first."},
                status_code=401
            )

        oauth_file = Path(__file__).parent / "oauth.json"
        user_id = validate_api_key(api_key, oauth_file)

        if not user_id:
            return JSONResponse(
                {"error": "Invalid or expired API key. Please login again."},
                status_code=401
            )
    except Exception as e:
        print(f"Internal error: {str(e)}")
        return JSONResponse(
            {"error": "An internal error occurred"},
            status_code=500
        )
    

async def firewall(request):
    """Receives batched network logs from on prem agent"""
    verify_auth(request)

    data = await request.json()
    schema_version = data.get("schema_version")
    sent_at = data.get("sent_at")
    sensor = data.get("sensor", {})
    event_count = data.get("event_count")
    events = data.get("events", [])
    api = data.get("api")
    model = data.get("model")

    # Pre-aggregate to reduce tokens
    summary = {
        "by_severity": dict(Counter(e["severity"] for e in events)),
        "by_category": dict(Counter(e["category"] for e in events)),
        "unique_src_ips": list(set(e["src_ip"] for e in events if e.get("src_ip"))),
        "unique_dest_ips": list(set(e["dest_ip"] for e in events if e.get("dest_ip"))),
    }

    prompt = f'''
    You are a network security analyst. Below is a batch of normalized network 
    events from a Suricata IDS sensor. 

    Sensor: {sensor} at {sensor["location"]}
    Time window: {events[0]["timestamp"]} → {events[-1]["timestamp"]}
    Event count: {event_count}
    Summary: {json.dumps(summary, indent=2)}

    Events:
    {json.dumps(events, indent=2)}

    Tasks:
    1. Identify the most significant threats or anomalies.
    2. Group related events that suggest a single attack or campaign.
    3. For each finding, describe: what happened, affected hosts, likely intent, and recommended action.
    4. Rate overall risk for this time window: Critical / High / Medium / Low.

    Be concise. Prioritize actionable findings over noise.'''

    # get response from agent
    llm_client = get_llm_client(api, model)
    response = await llm_client.ainvoke(prompt)
    insight = response.content
    print(f"Network Analysis:\n{insight}\n")
    # post to database
    return JSONResponse({"status": "ok","response": insight})


security_app = Starlette(
    routes=[
        Route("/firewall", firewall, methods=["POST"]),
    ]
)