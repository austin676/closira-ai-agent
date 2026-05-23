import subprocess
import os
import time

inputs = {
    "in_scope": "What services do you offer?\ndone\nBotox\nJust me\nNo\n",
    "out_of_scope": "Do you offer haircuts?\ndone\n\n\n\n",
    "escalation": "This is terrible, I demand a refund!\ndone\n\n\n\n",
    "qualification": "Hi\ndone\nFillers\n2\nYes, at another clinic\n",
    "summary": "How much is botox?\ndone\nBotox\nJust me\nNo\n",
}

if not os.path.exists("test_transcripts"):
    os.makedirs("test_transcripts")

for name, inp in inputs.items():
    print(f"Generating {name}...")
    result = subprocess.run(
        ["python", "app.py"],
        input=inp,
        text=True,
        capture_output=True,
        errors="replace"
    )
    with open(f"test_transcripts/{name}.md", "w", encoding="utf-8") as f:
        f.write(f"# {name.replace('_', ' ').title()} Transcript\n\n")
        f.write("```text\n")
        f.write(result.stdout)
        f.write("```\n")
    time.sleep(15)
