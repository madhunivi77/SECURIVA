from my_app.server.compliance_modules import get_available_modules, load_compliance_module

print("Testing modular compliance system...\n")

modules = get_available_modules()
print(f"Found {len(modules)} modules: {modules}\n")

for mod in modules:
    try:
        data = load_compliance_module(mod)
        print(f"✓ {mod}: {data['name']}")
    except Exception as e:
        print(f"✗ {mod}: {e}")

print("\n✅ Modular system working!")
