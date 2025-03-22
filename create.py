import ollama

ollama.create(model='CheatAssist', from_='llama3.2', system="You are a model designed to assist with questions. If the user provides a multiple-choice question, only return the correct answer's Value.")
