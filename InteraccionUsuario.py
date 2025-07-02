import os
import sys
import math
import csv
import re
import unicodedata
from collections import Counter
from functools import lru_cache
import numpy as np  # Necesario para cálculo de Zipf

# Limpiar la consola (Opcional)
def clear_screen():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        pass

# Normalización de texto
def normalize_text(text):
    """Normaliza acentos y caracteres especiales"""
    # Convertir a minúsculas y normalizar formas unicode
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    # Reemplazar caracteres acentuados
    text = re.sub(r'[áàäâ]', 'a', text)
    text = re.sub(r'[éèëê]', 'e', text)
    text = re.sub(r'[íìïî]', 'i', text)
    text = re.sub(r'[óòöô]', 'o', text)
    text = re.sub(r'[úùüû]', 'u', text)
    # Conservar ñ y eliminar otros caracteres
    text = re.sub(r'[^a-zñ]', '', text)
    return text

# Cálculo de parámetro alpha de Zipf
def zipf_alpha(frequencies):
    """Calcula el parámetro alpha de la ley de Zipf"""
    freqs = sorted(frequencies.values(), reverse=True)
    ranks = np.arange(1, len(freqs)+1)
    
    # Evitar log(0)
    valid = np.array(freqs) > 0
    log_ranks = np.log(ranks[valid])
    log_freqs = np.log(np.array(freqs)[valid])
    
    slope, _ = np.polyfit(log_ranks, log_freqs, 1)
    return -slope

@lru_cache(maxsize=None) # almacenar en memoria el contenido de cada archivo que se carga
# CARGAR Archivo
def load_corpus(path):
    #Comprobar que existe
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    
    # Leer texto - Convertir a minúsculas - Devolver cadena 
    with open(path, encoding='utf-8') as f:
        text = f.read()
    
    # Aplicar normalización de texto
    return normalize_text(text)


# Evitar re-computar los mismos n-gramas varias veces 
@lru_cache(maxsize=None)
def ngrams(text, n):
    # Counter => devolver un diccionario {ngrama: frecuencia}
    return Counter(text[i:i+n] for i in range(len(text)-n+1)) 


def relative_freq(counter):  # tomar un Counter
    # SUmar todas las ocurrencias
    total = sum(counter.values())

    # retornar nuevo dicc. con probablidades normalizadas
    return {k: v/total for k, v in counter.items()}


# Calcular la entropia
def entropy(freqs):
    return -sum(p * math.log2(p) for p in freqs.values() if p>0)


# Calcular la entropia Condicional
def conditional_entropy(joint_freqs, uni_freqs):
    return entropy(joint_freqs) - entropy(uni_freqs)


# Calcular la divergencia de Kullback-Leibler
def kl_divergence(p, q):
    return sum(p[k] * math.log2(p[k]/q.get(k, 1e-12)) for k in p)


# Calcular la divergencia de Jensen-Shannon
def js_divergence(p, q):
    m = {k: (p.get(k,0)+q.get(k,0))/2 for k in set(p) | set(q)}
    return (kl_divergence(p, m) + kl_divergence(q, m)) / 2


# GUARDAR en CSV
def save_csv(data, headers, filename):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"CSV guardado en {filename}")
    except Exception as e:
        print(f"Error al guardar CSV: {e}")


# Menú e interacción
def main():
    # Mensaje inicial
    print("🛠️  Iniciando EntropiaCheck…")
    paths = {'1': 'esp.txt', '2': 'eng.txt'}
    current_lang = None
    current_n = 1

    while True:
        # clear_screen()  # Comentar para debugging si oculta la interfaz
        print("\n=== CORPUS ANALYZER: Entropía y Probabilidades ===")
        print(f"Idioma actual: {current_lang if current_lang else 'No seleccionado'}")
        print(f"Análisis: {current_n}-gramas")
        print("1) Seleccionar idioma (1=Español, 2=Inglés)")
        print("2) Elegir n-gramas (1,2,3)")
        print("3) Ver resultados")
        print("4) Exportar CSV")
        print("5) Salir")
        opt = input("Elige una opción [1-5]: ").strip()

        if opt == '1':
            lang = input("Selecciona idioma (1=Español, 2=Inglés): ").strip()
            if lang in paths:
                try:
                    load_corpus(paths[lang])
                    current_lang = paths[lang]
                    print(f"Idioma cargado: {current_lang}")
                except FileNotFoundError as e:
                    print(e)
            else:
                print("Opción inválida.")
            input("Enter para continuar...")

        elif opt == '2':
            n = input("Selecciona n para n-gramas (1,2,3): ").strip()
            if n in ('1','2','3'):
                current_n = int(n)
                print(f"Análisis configurado a {current_n}-gramas.")
            else:
                print("Opción inválida.")
            input("Enter para continuar...")

        elif opt == '3':
            if not current_lang:
                print("Primero selecciona un idioma.")
                input("Enter para continuar...")
                continue
            try:
                text = load_corpus(current_lang)
            except FileNotFoundError as e:
                print(e)
                input("Enter para continuar...")
                continue
            cnt = ngrams(text, current_n)
            rel = relative_freq(cnt)
            top = sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:20]

            print(f"\nTop 20 de {current_n}-gramas en {current_lang}:")
            print(f"{'Rank':<5}{'N-grama':<10}{'Conteo':<10}{'FrecRel':<10}")
            for i, (gram, c) in enumerate(top, 1):
                print(f"{i:<5}{gram:<10}{c:<10}{rel[gram]*100:6.2f}%")

            H = entropy(rel)
            print(f"\nEntropía H{current_n}: {H:.4f} bits")
            
            # NUEVO: Entropía teórica uniforme
            alphabet_size = 27 if 'esp' in current_lang else 26
            H_uniform = math.log2(alphabet_size)
            print(f"Entropía teórica (uniforme): {H_uniform:.4f} bits")
            print(f"Redundancia: {H_uniform - H:.4f} bits")
            
            # NUEVO: Ley de Zipf (solo para unigramas)
            if current_n == 1:
                try:
                    alpha = zipf_alpha(rel)
                    print(f"Parámetro alpha (Zipf): {alpha:.4f}")
                except Exception as e:
                    print(f"Error calculando Zipf: {str(e)}")
            
            if current_n > 1:
                uni = relative_freq(ngrams(text,1))
                Hcond = conditional_entropy(relative_freq(cnt), uni)
                print(f"Entropía condicionada práctica: {Hcond:.4f} bits")
                
                # NUEVO: Entropía condicionada teórica
                H_cond_theoretical = entropy(uni)
                print(f"Entropía condicionada teórica: {H_cond_theoretical:.4f} bits")
                print(f"Redundancia en bigramas: {H_cond_theoretical - Hcond:.4f} bits")

            if current_n == 1:
                other = 'eng.txt' if current_lang == 'esp.txt' else 'esp.txt'
                try:
                    other_text = load_corpus(other)
                    other_uni = relative_freq(ngrams(other_text,1))
                    print(f"\nComparación entre idiomas:")
                    print(f"- {current_lang}: {H:.4f} bits")
                    print(f"- {other}: {entropy(other_uni):.4f} bits")
                except Exception as e:
                    print(f"\nNo se pudo cargar el otro idioma: {str(e)}")

            input("\nEnter para continuar...")

        elif opt == '4':
            if not current_lang:
                print("Selecciona un idioma primero.")
                input("Enter para continuar...")
                continue
            try:
                text = load_corpus(current_lang)
            except FileNotFoundError as e:
                print(e)
                input("Enter para continuar...")
                continue
            cnt = ngrams(text, current_n)
            rel = relative_freq(cnt)
            data = [(gram, cnt[gram], rel[gram]) for gram in sorted(cnt, key=cnt.get, reverse=True)]
            filename = input("Nombre de archivo CSV de salida (p.ej. out.csv): ").strip()
            save_csv(data, ['ngram', 'count', 'freq'], filename)
            input("Enter para continuar...")

        elif opt == '5':
            print("Adiós!")
            sys.exit(0)

        else:
            print("Opción inválida.")
            input("Enter para continuar...")

if __name__ == '__main__':
    main()