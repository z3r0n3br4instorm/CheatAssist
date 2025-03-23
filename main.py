import pyperclip
import keyboard
import os
import chromadb
from ollama import chat
from ollama import ChatResponse
from plyer import notification
from pypdf import PdfReader
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from pynput.mouse import Controller, Button

chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="rag_data")

mouse = Controller()

def load_pdf_to_chroma():
    """Loads a PDF file into ChromaDB for retrieval."""
    pdf_path = "RAG_DATA/data.pdf"
    if not os.path.exists(pdf_path):
        print("PDF file not found!")
        return
    
    reader = PdfReader(pdf_path)
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            collection.add(documents=[text], ids=[str(i)])
    
    print("PDF content loaded into ChromaDB.")

def retrieve_context(question):
    """Retrieves relevant information from ChromaDB based on the query."""
    results = collection.query(query_texts=[question], n_results=3)
    retrieved_text = "\n".join(results["documents"][0]) if results["documents"] else ""
    return retrieved_text

def ollama_call(question):
    """Calls Ollama AI to generate a response based on retrieved context."""
    context = retrieve_context(question)
    print(f"RAG_DATA---------\n{context}\n-------------")
    full_prompt = f"Relevant information:\n{context}\n\nQuestion: {question}\nAnswer:"
    
    response: ChatResponse = chat(model='CheatAssist', messages=[
        {'role': 'user', 'content': full_prompt}
    ])
    return response.message['content']

def copy_generate_notify():
    """Copies text, retrieves AI response, and sends notifications."""
    question = pyperclip.paste().strip()
    
    if not question:
        return
    
    os.system(f"sudo -u zerone DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus notify-send 'Assist' 'Copied: {" ".join(question.split()[:4])} ' --expire-time=3000")

    answer = ollama_call(question)
    pyperclip.copy(answer)
    
    print(answer)
    
    os.system(f"sudo -u zerone DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus notify-send 'Assist' '{answer.replace("'", "")}'")

def ctrl_c_click():
    """Detects Ctrl+C and emulates a left mouse click."""
    print("Ctrl+C detected! Emulating mouse left click...")
    mouse.click(Button.left, 1)

def main():
    """Main function to register hotkeys and start listening."""
    print("Listening for hotkeys...")
    keyboard.add_hotkey("ctrl+alt+c", copy_generate_notify)
    keyboard.add_hotkey("ctrl+c", ctrl_c_click)
    keyboard.wait()

if __name__ == "__main__":
    load_pdf_to_chroma()
    main()
