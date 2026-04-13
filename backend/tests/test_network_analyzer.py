import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")

test_batch = {
    "api": "openai",
    "model": "gpt-3.5-turbo",
    "schema_version": "1.0",
    "sent_at": "2024-11-12T14:32:01.123456+00:00",
    "sensor": {
        "id": "client-site-01",
        "hostname": "ids-box.internal",
        "location": "HQ - Server Room"
    },
    "event_count": 8,
    "events": [
        {
            "event_id": "1731421921.111111",
            "timestamp": "2024-11-12T14:30:01.000000+0000",
            "event_type": "alert",
            "sensor_id": "client-site-01",
            "src_ip": "192.168.1.44",
            "src_port": 54321,
            "dest_ip": "45.33.32.156",
            "dest_port": 4444,
            "proto": "TCP",
            "severity": "critical",
            "category": "Trojan Activity",
            "summary": "ET MALWARE Metasploit Meterpreter Reverse TCP Shell",
            "raw": {"signature_id": 2019284, "rev": 4, "gid": 1, "action": "allowed"}
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
            "raw": {"signature_id": 2024220, "rev": 2, "gid": 1, "action": "allowed"}
        },
        {
            "event_id": "1731421921.333333",
            "timestamp": "2024-11-12T14:30:22.000000+0000",
            "event_type": "alert",
            "sensor_id": "client-site-01",
            "src_ip": "192.168.1.44",
            "src_port": 49201,
            "dest_ip": "192.168.1.22",
            "dest_port": 445,
            "proto": "TCP",
            "severity": "high",
            "category": "Attempted Administrator Privilege Gain",
            "summary": "ET EXPLOIT EternalBlue SMB MS17-010 Exploit Attempt",
            "raw": {"signature_id": 2024220, "rev": 2, "gid": 1, "action": "allowed"}
        },
        {
            "event_id": "1731421921.444444",
            "timestamp": "2024-11-12T14:30:45.000000+0000",
            "event_type": "alert",
            "sensor_id": "client-site-01",
            "src_ip": "203.0.113.99",
            "src_port": 61234,
            "dest_ip": "192.168.1.1",
            "dest_port": 22,
            "proto": "TCP",
            "severity": "medium",
            "category": "Attempted Information Leak",
            "summary": "ET SCAN SSH BruteForce Login Attempt",
            "raw": {"signature_id": 2001219, "rev": 20, "gid": 1, "action": "allowed"}
        },
        {
            "event_id": "1731421921.555555",
            "timestamp": "2024-11-12T14:31:02.000000+0000",
            "event_type": "alert",
            "sensor_id": "client-site-01",
            "src_ip": "192.168.1.44",
            "src_port": 52000,
            "dest_ip": "185.220.101.45",
            "dest_port": 443,
            "proto": "TCP",
            "severity": "high",
            "category": "Malware Command and Control",
            "summary": "ET MALWARE Known Tor Exit Node Traffic",
            "raw": {"signature_id": 2522690, "rev": 1, "gid": 1, "action": "allowed"}
        },
        {
            "event_id": "1731421921.666666",
            "timestamp": "2024-11-12T14:31:20.000000+0000",
            "event_type": "alert",
            "sensor_id": "client-site-01",
            "src_ip": "192.168.1.55",
            "src_port": 50100,
            "dest_ip": "8.8.8.8",
            "dest_port": 53,
            "proto": "UDP",
            "severity": "medium",
            "category": "Potentially Bad Traffic",
            "summary": "ET DNS Query for Known Malware Domain",
            "raw": {"signature_id": 2027863, "rev": 3, "gid": 1, "action": "allowed"}
        },
        {
            "event_id": "1731421921.777777",
            "timestamp": "2024-11-12T14:31:45.000000+0000",
            "event_type": "anomaly",
            "sensor_id": "client-site-01",
            "src_ip": "192.168.1.44",
            "src_port": 49300,
            "dest_ip": "192.168.1.33",
            "dest_port": 80,
            "proto": "TCP",
            "severity": "medium",
            "category": "anomaly",
            "summary": "INVALID_TCP_OPT_LEN",
            "raw": {"event": "INVALID_TCP_OPT_LEN", "layer": "proto"}
        },
        {
            "event_id": "1731421921.888888",
            "timestamp": "2024-11-12T14:31:58.000000+0000",
            "event_type": "alert",
            "sensor_id": "client-site-01",
            "src_ip": "192.168.1.44",
            "src_port": 53100,
            "dest_ip": "45.33.32.156",
            "dest_port": 4444,
            "proto": "TCP",
            "severity": "critical",
            "category": "Trojan Activity",
            "summary": "ET MALWARE Metasploit Meterpreter Reverse TCP Shell",
            "raw": {"signature_id": 2019284, "rev": 4, "gid": 1, "action": "allowed"}
        }
    ]
}

async def main():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://127.0.0.1:8000/security/firewall",
                json=test_batch,
                headers={"X-API-Key": api_key},
                timeout=30.0
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Analysis:\n{data['response']}")
        except Exception as e:
            print(f"error: Response failed: {e}")

asyncio.run(main())