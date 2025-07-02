import os
import re
from collections import Counter
import matplotlib.pyplot as plt

def plot_freq_corpus(file_path, output_png, title):
    # 0) Comprobación de que el archivo existe
    print(f"🔍 Comprobando existencia de «{file_path}» ...", end=" ")
    if not os.path.isfile(file_path):
        print("❌ NO encontrado.")
        return
    print("✅ encontrado.")

    # 1) carga y limpieza
    print(f"📖 Leyendo «{file_path}» ...")
    with open(file_path, encoding='utf-8') as f:
        text = f.read().lower()

    print("✂️  Limpiando texto (solo a–z y ñ) ...")
    cleaned = re.sub(r'[^a-zñ]', '', text)
    print(f"   – Total original: {len(text)} caracteres")
    print(f"   – Total limpiado: {len(cleaned)} símbolos")

    # 2) conteo
    counts = Counter(cleaned)
    total = sum(counts.values())
    print(f"🔢 Hay {len(counts)} símbolos distintos; {total} en total.")

    # 3) orden de mayor a menor
    items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    symbols, freqs_abs = zip(*items)
    freqs_rel = [f/total for f in freqs_abs]

    # Muestra los 5 símbolos más frecuentes:
    print("🏆 Top 5 símbolos:")
    for s, c in items[:5]:
        print(f"    '{s}': {c} apariciones ({c/total:.2%})")

    # 4) gráfico
    print(f"📊 Generando gráfico y guardando en «{output_png}» ...")
    plt.figure()
    plt.bar(symbols, freqs_rel)
    plt.xlabel('Símbolo')
    plt.ylabel('Frecuencia relativa')
    plt.title(title)
    plt.tight_layout()

    # 5) guardado
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Imagen creada.\n")

if __name__ == "__main__":
    # Ajusta las rutas a donde de verdad estén tus archivos
    plot_freq_corpus(
        file_path='esp.txt',
        output_png='frecuencia_esp.png',
        title='Frecuencia de símbolos en español'
    )
    plot_freq_corpus(
        file_path='eng.txt',
        output_png='frecuencia_eng.png',
        title='Frecuencia de símbolos en inglés'
    )
