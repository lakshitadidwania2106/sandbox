from proxy.scrubber import scrub_input
from proxy.guardrails import check_output
from proxy.canary import detect_leak
from agent.agent import run_agent


def process_request(user_input):
    clean = scrub_input(user_input)

    if clean is None:
        return "🚨 Prompt Injection Blocked"

    try:
        response = run_agent(clean)
    except Exception as e:
        return f"Error: {str(e)}"

    if detect_leak(response):
        return "🚨 Canary Leak Detected"

    if not check_output(response):
        return "🚨 Data Leak Prevented"

    return response
