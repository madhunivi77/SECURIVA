from starlette.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from .api_key_manager import validate_api_key
from starlette.applications import Starlette
from starlette.routing import Route
from collections import Counter
from.chat_handler import get_llm_client
import json

def verify_auth(request):
    try:
        api_key = request.cookies.get("api_key")

        if not api_key:
            return JSONResponse(
                {"error": "Not authenticated. Please login first."},
                status_code=401
            )

        user_id = validate_api_key(api_key)

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

async def firewall_get(request):
    # fetch from aws

    # placeholder data
    data = {
        "alerts": 
            [
                {
                    "event_id": "1731421921.222222",
                    "timestamp": "2024-11-12T14:30:15.000000+0000",
                    "event_type": "alert",
                    "sensor_id": "client-site-01",
                    "src_ip": "192.168.1.44",
                    "src_port": 49200,
                    "dest_ip": "192.168.1.10",
                    "dest_port": 445,
                    "proto": "TCP",
                    "severity": "high",
                    "category": "Attempted Administrator Privilege Gain",
                    "summary": "ET EXPLOIT EternalBlue SMB MS17-010 Exploit Attempt",
                    "raw": {
                    "signature_id": 2024220,
                    "rev": 2,
                    "gid": 1,
                    "action": "allowed"
                    },
                    "analysis": "This alert indicates an active EternalBlue (MS17-010) exploitation attempt from internal host 192.168.1.44 targeting SMB port 445 on 192.168.1.10. The source IP appears to be a compromised internal machine conducting lateral movement — isolate it immediately and audit the destination host for signs of successful exploitation."
                },
                {
                    "event_id": "1731421921.222222",
                    "timestamp": "2024-11-12T14:30:15.000000+0000",
                    "event_type": "alert",
                    "sensor_id": "client-site-01",
                    "src_ip": "192.168.1.44",
                    "src_port": 49200,
                    "dest_ip": "192.168.1.10",
                    "dest_port": 445,
                    "proto": "TCP",
                    "severity": "high",
                    "category": "Attempted Administrator Privilege Gain",
                    "summary": "ET EXPLOIT EternalBlue SMB MS17-010 Exploit Attempt",
                    "raw": {
                    "signature_id": 2024220,
                    "rev": 2,
                    "gid": 1,
                    "action": "allowed"
                    },
                    "analysis": "This alert indicates an active EternalBlue (MS17-010) exploitation attempt from internal host 192.168.1.44 targeting SMB port 445 on 192.168.1.10. The source IP appears to be a compromised internal machine conducting lateral movement — isolate it immediately and audit the destination host for signs of successful exploitation."
                }
            ]
    }
    return JSONResponse({"status": "ok", "response": data})


security_app = Starlette(
    routes=[
        Route("/firewall", firewall, methods=["POST"]),
        Route("/firewall", firewall_get, methods=["GET"]),
    ]
)