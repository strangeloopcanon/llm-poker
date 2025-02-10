import llm
m = llm.get_model("gpt-4o")
resp = m.prompt("Return valid JSON: {\"action\": \"call\", \"raise_amount\": null}")
print(resp.text())
