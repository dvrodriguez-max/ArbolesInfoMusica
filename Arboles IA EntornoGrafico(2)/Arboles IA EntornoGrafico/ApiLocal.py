import json
import ollama  # 1. Cambiamos groq por ollama

def explorar():
    try:
        with open("EstructurasDeDatos.json", encoding="utf-8") as f:
            nodo = json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'EstructurasDeDatos.json'")
        return

    camino = []
    
    
    while True:
        camino.append(nodo["valor"])
        hijos = nodo.get("hijos", [])
        
        print(f"\n" + "="*30)
        print(f" UBICACIÓN: {' > '.join(camino)}")
        print("="*30)
        
        if not hijos:
            prompt = f"Explícame qué es {nodo['valor']} en el contexto de {camino[0]}."
            print(f"\n[Ollama] Generando explicación local...")
            try:
                # 2. Usamos el cliente de ollama local
                response = ollama.chat(
                    model='llama3.2:1b', # Asegúrate de tenerlo descargado con 'ollama run llama3'
                    messages=[
                        {"role": "system", "content": "Eres un experto en algoritmos. Da respuestas claras y breves."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": 0.5}
                )
                print("\nEXPLICACIÓN:")
                print(response['message']['content'])
            except Exception as e:
                print(f"\nError al conectar con Ollama: {e}")
            
            break

        print(f"Selecciona una categoría:")
        for i, h in enumerate(hijos, 1):
            print(f"{i}. {h['valor']}")

        while True:
            idx = input("\nNúmero > ")
            if idx.isdigit() and 1 <= int(idx) <= len(hijos):
                nodo = hijos[int(idx) - 1]
                break
            print("Opción inválida.")

if __name__ == "__main__":
    explorar()