import os
calls = 0
def decide(request, config):
    global calls
    calls += 1
    assert "HOME" not in os.environ
    assert "seed" not in request
    return {"asks": [], "memory": {"calls": calls}}
