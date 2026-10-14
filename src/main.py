import os
from dotenv import load_dotenv

def main() -> None:
    load_dotenv()
    anki_url = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
    debug_mode = os.getenv("DEBUG", "False")

    print("========================================")
    print("  Sentence Mining Anki - Inicializado   ")
    print("========================================")
    print(f"Anki Connect URL: {anki_url}")
    print(f"Debug Mode:       {debug_mode}")
    print("Proyecto listo para comenzar a codificar.")

if __name__ == "__main__":
    main()
