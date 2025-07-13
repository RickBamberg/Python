import pandas as pd
import time
import pyautogui
import keyboard

# Função para registrar logs em um arquivo .txt
def log_to_file(message):
    with open("process_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Carrega a planilha
df = pd.read_excel('exemplo_buchas.xlsx')  # troque pelo nome correto

df = df.fillna(" ")
df.head()

# Início
print("Você tem 5 segundos para ir até a tela remota e posicionar o cursor no primeiro campo...")
log_to_file("Início do processo: Aguardando o usuário posicionar o cursor.")
time.sleep(5)

# Loop pelas linhas
for index, row in df.iterrows():
    print(f"\nDigitando linha {index+1} de {len(df)}...")
    #print(f"Linha: {row.iloc[0]} | {row.iloc[1]} | {row.iloc[2]} | {row.iloc[3]} | {row.iloc[4]} | {row.iloc[5]} | {row.iloc[6]} | {row.iloc[7]} | {row.iloc[8]} | {row.iloc[9]} | {row.iloc[10]} | {row.iloc[11]} | {row.iloc[12]} | {row.iloc[13]} | {row.iloc[14]} | {row.iloc[15]} | ")
    print(f"Linha: {row.iloc[0]} | {row.iloc[1]} | {row.iloc[2]} | {row.iloc[3]} | " \
          f"{row.iloc[4]} | {row.iloc[5]} | {row.iloc[6]} | {row.iloc[7]} | " \
          f"{row.iloc[8]} | {row.iloc[9]} | {row.iloc[10]} | {row.iloc[11]} | " \
          f"{row.iloc[12]} | {row.iloc[13]} | {row.iloc[14]} | {row.iloc[15]} |")
    log_to_file(f"Digitando linha {index+1} de {len(df)}...")
    log_to_file(f"Linha: {row.iloc[0]} | {row.iloc[1]} | {row.iloc[2]} | {row.iloc[3]} | " \
          f"{row.iloc[4]} | {row.iloc[5]} | {row.iloc[6]} | {row.iloc[7]} | " \
          f"{row.iloc[8]} | {row.iloc[9]} | {row.iloc[10]} | {row.iloc[11]} | " \
          f"{row.iloc[12]} | {row.iloc[13]} | {row.iloc[14]} | {row.iloc[15]} |")

    for cell in row:
        pyautogui.write(str(cell) if pd.notna(cell) else "")
        pyautogui.press('tab')
        time.sleep(0.05)  # pode ajustar para mais se estiver travando
    
    #print("Pressione TAB para submeter (Enter) e continuar...")
    #log_to_file("Aguardando F9 para submeter o formulário.")
    #keyboard.wait('tab')  # só continua quando você pressionar F9

    pyautogui.press('enter')  # envia o formulário
    time.sleep(0.5)  # pequena pausa antes da próxima linha

# Fim do processo
print("Processo concluído.")
log_to_file("Processo concluído.")
