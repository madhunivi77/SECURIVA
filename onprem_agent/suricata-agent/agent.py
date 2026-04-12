#!/usr/bin/env python3
"""
Suricata EVE JSON Agent
Tails eve.json, normalizes events, batches them, and ships to your API.
"""

import json
import time
import logging
import os
import sys
import signal
from datetime import datetime, timezone
from pathlib import Path
from collections import deque

import requests
import yaml
from dotenv import load_dotenv

load_dotenv()
# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        # logging.FileHandler("tmp/agent.log") # dev
        logging.FileHandler("/var/log/suricata-agent/agent.log") # prod
    ],
)
log = logging.getLogger("suricata-agent")

# ── Config ─────────────────────────────────────────────────────────────────
CONFIG_PATH = os.environ.get("AGENT_CONFIG", "/etc/suricata-agent/config.yaml")

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

# ── Normalization ───────────────────────────────────────────────────────────
SEVERITY_MAP = {
    1: "critical",
    2: "high",
    3: "medium",
    4: "low",
}

EVENT_TYPE_PRIORITY = {
    "alert":    "high",
    "anomaly":  "medium",
    "dns":      "low",
    "http":     "low",
    "tls":      "low",
    "flow":     "low",
    "fileinfo": "low",
    "ssh":      "low",
    "smb":      "low",
    "stats":    "none",   # dropped by default
}

def normalize_event(raw: dict) -> dict | None:
    """Convert a raw EVE JSON event into a clean, consistent payload."""
    etype = raw.get("event_type", "unknown")

    # Drop noisy/irrelevant types
    if EVENT_TYPE_PRIORITY.get(etype) == "none":
        return None

    event = {
        "event_id":   raw.get("flow_id") or raw.get("pcap_cnt"),
        "timestamp":  raw.get("timestamp"),
        "event_type": etype,
        "sensor_id":  None,  # filled in by config at ship time
        "src_ip":     raw.get("src_ip"),
        "src_port":   raw.get("src_port"),
        "dest_ip":    raw.get("dest_ip"),
        "dest_port":  raw.get("dest_port"),
        "proto":      raw.get("proto"),
        "severity":   "info",
        "category":   etype,
        "summary":    "",
        "raw":        {},
    }

    if etype == "alert":
        alert = raw.get("alert", {})
        sev_num = alert.get("severity", 3)
        event["severity"] = SEVERITY_MAP.get(sev_num, "medium")
        event["category"] = alert.get("category", "Unknown")
        event["summary"]  = alert.get("signature", "Unknown signature")
        event["raw"] = {
            "signature_id": alert.get("signature_id"),
            "rev":          alert.get("rev"),
            "gid":          alert.get("gid"),
            "action":       alert.get("action"),
        }

    elif etype == "anomaly":
        anomaly = raw.get("anomaly", {})
        event["severity"] = "medium"
        event["summary"]  = anomaly.get("event", "Anomaly detected")
        event["raw"]      = anomaly

    elif etype == "dns":
        dns = raw.get("dns", {})
        event["summary"] = f"DNS {dns.get('type','query')} {dns.get('rrname','?')}"
        event["raw"] = {
            "type":   dns.get("type"),
            "rrname": dns.get("rrname"),
            "rdata":  dns.get("rdata"),
            "rcode":  dns.get("rcode"),
        }

    elif etype == "http":
        http = raw.get("http", {})
        event["summary"] = f"{http.get('http_method','?')} {http.get('hostname','?')}{http.get('url','')}"
        event["raw"] = {
            "method":      http.get("http_method"),
            "hostname":    http.get("hostname"),
            "url":         http.get("url"),
            "status":      http.get("status"),
            "user_agent":  http.get("http_user_agent"),
            "content_type":http.get("http_content_type"),
        }

    elif etype == "tls":
        tls = raw.get("tls", {})
        event["summary"] = f"TLS {tls.get('version','?')} → {tls.get('sni','?')}"
        event["raw"] = {
            "sni":     tls.get("sni"),
            "version": tls.get("version"),
            "issuer":  tls.get("issuerdn"),
            "subject": tls.get("subject"),
        }

    elif etype == "fileinfo":
        fi = raw.get("fileinfo", {})
        event["summary"] = f"File {fi.get('filename','?')} ({fi.get('magic','?')})"
        event["raw"] = {
            "filename": fi.get("filename"),
            "size":     fi.get("size"),
            "magic":    fi.get("magic"),
            "md5":      fi.get("md5"),
            "sha256":   fi.get("sha256"),
            "stored":   fi.get("stored"),
        }

    else:
        event["summary"] = f"{etype} event"
        event["raw"] = {k: v for k, v in raw.items() if k not in (
            "timestamp", "flow_id", "src_ip", "src_port",
            "dest_ip", "dest_port", "proto", "event_type"
        )}

    return event


# ── Shipper ─────────────────────────────────────────────────────────────────
def ship_batch(events: list, cfg: dict):
    if not events:
        return

    payload = {
        "api": cfg.get("llm-api"),
        "model": cfg.get("llm-model"),
        "schema_version": "1.0",
        "sent_at":        datetime.now(timezone.utc).isoformat(),
        "sensor": {
            "id":       cfg.get("sensor_id", "unknown"),
            "hostname": cfg.get("hostname", os.uname().nodename),
            "location": cfg.get("location", ""),
        },
        "event_count": len(events),
        "events":      events,
    }

    headers = {
        "Content-Type":  "application/json",
        "X-API-Key":     cfg["api_key"],
    }

    url = cfg["api_endpoint"]
    timeout = cfg.get("request_timeout_seconds", 10)

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=timeout)
        r.raise_for_status()
        log.info(f"Shipped {len(events)} events → {r.status_code}")
    except requests.exceptions.RequestException as e:
        log.error(f"Failed to ship batch: {e}")
        # Events are dropped on failure. For production, consider a dead-letter queue.


# ── Tailer ──────────────────────────────────────────────────────────────────
class EveTailer:
    """Tail eve.json, handling log rotation."""

    def __init__(self, path: str):
        self.path   = Path(path)
        self.file   = None
        self.inode  = None
        self._open()

    def _open(self):
        try:
            self.file  = open(self.path, "r")
            self.inode = self.path.stat().st_ino
            # Seek to end on first open so we don't replay history
            self.file.seek(0, 2)
            log.info(f"Tailing {self.path}")
        except FileNotFoundError:
            log.warning(f"{self.path} not found — will retry")
            self.file  = None
            self.inode = None

    def _check_rotate(self):
        try:
            new_inode = self.path.stat().st_ino
            if new_inode != self.inode:
                log.info("Log rotation detected — reopening")
                if self.file:
                    self.file.close()
                self.file  = open(self.path, "r")
                self.inode = new_inode
        except FileNotFoundError:
            pass

    def readlines(self):
        if self.file is None:
            self._open()
            return []

        self._check_rotate()
        lines = []
        while True:
            line = self.file.readline()
            if not line:
                break
            line = line.strip()
            if line:
                lines.append(line)
        return lines


# ── Main loop ───────────────────────────────────────────────────────────────
def run():
    cfg     = load_config()
    tailer  = EveTailer(cfg.get("eve_json_path", "/var/log/suricata/eve.json"))
    batch   = []
    max_batch_size  = cfg.get("max_batch_size", 100)
    batch_interval  = cfg.get("batch_interval_seconds", 60)
    flush_severities = set(cfg.get("immediate_flush_severities", ["critical"]))
    min_severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    min_rank = min_severity_rank.get(cfg.get("min_severity", "low"), 3)
    last_flush = time.monotonic()

    def flush(reason=""):
        nonlocal batch, last_flush
        if batch:
            log.info(f"Flushing {len(batch)} events ({reason})")
            ship_batch(batch, cfg)
        batch = []
        last_flush = time.monotonic()

    def handle_signal(sig, frame):
        log.info("Shutdown signal received — flushing and exiting")
        flush("shutdown")
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT,  handle_signal)

    log.info("Agent started")

    while True:
        cfg = load_config()  # reload config each cycle (live config updates)

        for line in tailer.readlines():
            try:
                raw   = json.loads(line)
                event = normalize_event(raw)
                if event is None:
                    continue

                # Apply sensor metadata
                event["sensor_id"] = cfg.get("sensor_id", os.uname().nodename)

                # Severity filter
                rank = min_severity_rank.get(event["severity"], 4)
                if rank > min_rank:
                    continue

                batch.append(event)

                # Immediate flush for critical/high events
                if event["severity"] in flush_severities:
                    flush(f"immediate ({event['severity']})")

                # Flush if batch is full
                if len(batch) >= max_batch_size:
                    flush("batch full")

            except json.JSONDecodeError:
                pass  # partial write — skip

        # Time-based flush
        if time.monotonic() - last_flush >= batch_interval and batch:
            flush("interval")

        time.sleep(1)


if __name__ == "__main__":
    # os.makedirs("tmp", exist_ok=True) # dev
    os.makedirs("/var/log/suricata-agent", exist_ok=True) # prod
    run()
