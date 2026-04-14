# Install just the Python agent dependencies
pip install requests pyyaml

# Create a fake eve.json and write test events to it
touch tmp/eve.json

# Point config at the fake file
# edit config.yaml: eve_json_path: tmp/eve.json

# Run the agent directly (not as a service)
python agent.py

# In another terminal, append fake events to trigger the agent
echo '{"event_type":"alert","timestamp":"2024-11-12T14:30:01.000000+0000","flow_id":"123","src_ip":"192.168.1.44","src_port":54321,"dest_ip":"45.33.32.156","dest_port":4444,"proto":"TCP","alert":{"severity":1,"category":"Trojan Activity","signature":"ET MALWARE Test","signature_id":9999,"rev":1,"gid":1,"action":"allowed"}}' >> /tmp/eve.json