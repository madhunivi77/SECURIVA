# Payload Schema — Suricata Agent → Your API

Every POST to the SecuriVA API endpoint contains this JSON structure.

## Envelope

```json
{
  "schema_version": "1.0",
  "sent_at": "2024-11-12T14:32:01.123456+00:00",
  "sensor": {
    "id": "client-site-01",
    "hostname": "ids-box.internal",
    "location": "HQ - Server Room"
  },
  "event_count": 3,
  "api": "openai",
  "model": "gpt-3.5-turbo",
  "events": [ ...see below... ]
}
```

## Event Object

All event types share this base structure:

```json
{
  "event_id":   "1731421921.123456",
  "timestamp":  "2024-11-12T14:31:58.224034+0000",
  "event_type": "alert",
  "sensor_id":  "client-site-01",
  "src_ip":     "192.168.1.44",
  "src_port":   54321,
  "dest_ip":    "45.33.32.156",
  "dest_port":  80,
  "proto":      "TCP",
  "severity":   "high",
  "category":   "Attempted Information Leak",
  "summary":    "ET SCAN Nmap Scripting Engine User-Agent Detected",
  "raw": { ...type-specific fields... }
}
```

### severity values
| Value      | Meaning                              |
|------------|--------------------------------------|
| `critical` | Suricata priority 1                  |
| `high`     | Suricata priority 2                  |
| `medium`   | Suricata priority 3 / anomalies      |
| `low`      | Suricata priority 4                  |
| `info`     | DNS, HTTP, TLS, flow metadata        |

### event_type values and their raw fields

**alert**
```json
"raw": {
  "signature_id": 2024364,
  "rev": 4,
  "gid": 1,
  "action": "allowed"
}
```

**dns**
```json
"raw": {
  "type": "query",
  "rrname": "evil.example.com",
  "rdata": null,
  "rcode": null
}
```

**http**
```json
"raw": {
  "method": "GET",
  "hostname": "example.com",
  "url": "/path?q=1",
  "status": 200,
  "user_agent": "curl/7.68.0",
  "content_type": "text/html"
}
```

**tls**
```json
"raw": {
  "sni": "example.com",
  "version": "TLS 1.3",
  "issuer": "CN=Let's Encrypt Authority X3",
  "subject": "CN=example.com"
}
```

**anomaly**
```json
"raw": {
  "event": "INVALID_TCP_OPT_LEN",
  "layer": "proto"
}
```

**fileinfo**
```json
"raw": {
  "filename": "document.exe",
  "size": 204800,
  "magic": "PE32 executable",
  "md5": "abc123...",
  "sha256": "def456...",
  "stored": false
}
```

## Suggested AI Prompt (send with events)

```
You are a network security analyst. Below is a batch of normalized network 
events from a Suricata IDS sensor. 

Sensor: {{sensor.id}} at {{sensor.location}}
Time window: {{events[0].timestamp}} → {{events[-1].timestamp}}
Event count: {{event_count}}

Events:
{{events | json}}

Tasks:
1. Identify the most significant threats or anomalies.
2. Group related events that suggest a single attack or campaign.
3. For each finding, describe: what happened, affected hosts, likely intent, and recommended action.
4. Rate overall risk for this time window: Critical / High / Medium / Low.

Be concise. Prioritize actionable findings over noise.
```
