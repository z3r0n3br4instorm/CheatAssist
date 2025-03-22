import pyperclip
import keyboard
import os
import chromadb
from ollama import chat
from ollama import ChatResponse
from plyer import notification
from pypdf import PdfReader
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="rag_data")

def load_pdf_to_chroma():
    pdf_path = "RAG_DATA/data.pdf"
    if not os.path.exists(pdf_path):
        print("PDF file not found!")
        return
    
    reader = PdfReader(pdf_path)
    text_chunks = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            collection.add(documents=[text], ids=[str(i)])
    
    print("PDF content loaded into ChromaDB.")
def retrieve_context(question):
    results = collection.query(query_texts=[question], n_results=3)
    retrieved_text = "\n".join(results["documents"][0]) if results["documents"] else ""
    return retrieved_text

def ollama_call(question):
    context = retrieve_context(question)
    print(f"RAG_DATA---------\n{context}\n-------------")
    full_prompt = f"Relevant information:\n{context}\n\nQuestion: {question}\nAnswer:"
    
    response: ChatResponse = chat(model='CheatAssist', messages=[
        {'role': 'user', 'content': full_prompt}
    ])
    return response.message['content']

def copy_generate_notify():
    question = pyperclip.paste()
    os.system(f"sudo -u zerone DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus notify-send 'Assist' 'Copied: {question.replace("'", "")} ' --expire-time=3000")
    if question.strip():
        answer = ollama_call(question)
        pyperclip.copy(answer)
        print(answer)
        os.system(f"sudo -u zerone DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus notify-send 'Assist' '{answer.replace("'", "")}'")
load_pdf_to_chroma()

def main():
    print("Listening for Ctrl + Alt + C...")
    keyboard.add_hotkey("ctrl+alt+c", copy_generate_notify)
    keyboard.wait()

if __name__ == "__main__":
    main()
