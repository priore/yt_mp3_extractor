import csv
import subprocess
import os
import argparse

# Configurazione standard per l'alta qualità MP3
AUDIO_FORMAT = "mp3"
AUDIO_QUALITY = "320K" # Usa "320K" per la massima qualità

# Prerequisiti:
#
# Prima di eseguire lo script, devi assicurarti che sul tuo sistema siano installati:
# Python 3: (Generalmente preinstallato su macOS).
#
# yt-dlp: Lo strumento per il download.
# Installazione (tramite Homebrew su macOS): brew install yt-dlp
#
# FFmpeg: Necessario a yt-dlp per l'estrazione e la conversione in MP3.
# Installazione (tramite Homebrew su macOS): brew install ffmpeg
#
# Esecuzione:
# python3 audio_extractor.py ~/Desktop/lista_brani.csv ~/Desktop/MP3

def process_csv(csv_path: str, output_dir: str):
    """
    Legge un file CSV (Titolo, Autore), cerca il video su YouTube, 
    scarica l'audio del primo risultato e lo converte in MP3.
    """
    print(f"Inizio elaborazione del CSV: {csv_path}")

    # 1. Creazione della cartella di output se non esiste
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            # Puoi saltare l'intestazione se presente (es. next(reader))
            
            for i, row in enumerate(reader):
                if len(row) < 2:
                    print(f"Riga {i+1} ignorata: Formato non valido. Richiesti Titolo e Autore.")
                    continue
                
                # Assumiamo Titolo nella colonna 1 e Autore nella colonna 2
                title = row[0].strip()
                author = row[1].strip()
                
                # Combina titolo e autore per una ricerca più precisa
                search_query = f"{title} {author}"
                
                # Usa il prefisso 'ytsearch1:' per cercare e selezionare SOLO il primo risultato
                yt_dlp_search_term = f"ytsearch1:{search_query}"

                # Pulisce il titolo per usarlo nel nome del file
                # Rimuove caratteri non validi nei nomi file
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
                
                print(f"\n--- Elaborazione {i+1}: '{search_query}' ---")
                
                # 2. Preparazione del comando yt-dlp
                # -x: Estrai solo l'audio
                # --audio-format/quality: Imposta il formato/bitrate
                # -o: Template per il nome del file
                
                output_template = os.path.join(output_dir, f"{safe_title}.%(ext)s")
                
                command = [
                    "yt-dlp",
                    "-x",
                    "--audio-format", AUDIO_FORMAT,
                    "--audio-quality", AUDIO_QUALITY,
                    "--embed-metadata",
                    "-o", output_template,
                    yt_dlp_search_term # Qui usiamo la stringa di ricerca
                ]

                # 3. Esecuzione del comando
                try:
                    # check=True solleverà un errore se yt-dlp fallisce
                    subprocess.run(command, check=True, capture_output=True, text=True)
                    print(f"✅ Ricerca, download e conversione completati per: {title}")
                    
                except subprocess.CalledProcessError as e:
                    print(f"❌ Errore durante l'elaborazione di {title} ({search_query}):")
                    print(f"   Dettaglio errore: {e.stderr.strip().splitlines()[-1]}")
                except FileNotFoundError:
                    print("❌ ERRORE CRITICO: Il comando 'yt-dlp' non è stato trovato. Assicurati che sia installato e nel tuo PATH.")
                    return
                    
    except FileNotFoundError:
        print(f"❌ ERRORE: File CSV non trovato al percorso specificato: {csv_path}")
        
    print("\n*** Elaborazione completata. ***")


def main():
    parser = argparse.ArgumentParser(
        description="Cerca, scarica l'audio e converte da una lista di brani (Titolo, Autore) specificati in un CSV."
    )
    parser.add_argument(
        "csv_file",
        help="Il percorso del file CSV. Formato richiesto: Titolo,Autore"
    )
    parser.add_argument(
        "output_directory",
        help="La cartella dove salvare i file MP3 risultanti."
    )
    
    args = parser.parse_args()
    
    process_csv(args.csv_file, args.output_directory)


if __name__ == "__main__":
    main()