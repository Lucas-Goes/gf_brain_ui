from backend.scopes import SCOPES


def get_system_prompt(escopo):
    scope_config = SCOPES.get(escopo)
    if scope_config:
        return scope_config["system_prompt"]
    return SCOPES["documentacao"]["system_prompt"]


def get_tools_for_scope(escopo):
    scope_config = SCOPES.get(escopo)
    if scope_config:
        return scope_config.get("tools", [])
    return []


def get_kb_filter(escopo):
    scope_config = SCOPES.get(escopo)
    if scope_config:
        return scope_config.get("kb_filter")
    return {"type": "doc"}
