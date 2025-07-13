import pandas as pd
import pywhatkit as pwk
import time
from datetime import datetime
import os

def criar_logs():
    """Cria os diretórios de logs se não existirem"""
    if not os.path.exists('logs'):
        os.makedirs('logs')

def salvar_log_envios(sucessos, erros, timestamp):
    """Salva log dos envios realizados"""
    try:
        # Log de sucessos
        if sucessos:
            df_sucessos = pd.DataFrame(sucessos)
            arquivo_sucesso = f'logs/envios_sucesso_{timestamp}.csv'
            df_sucessos.to_csv(arquivo_sucesso, index=False)
            print(f"✅ Log de sucessos salvo: {arquivo_sucesso}")
        
        # Log de erros
        if erros:
            df_erros = pd.DataFrame(erros)
            arquivo_erro = f'logs/envios_erro_{timestamp}.csv'
            df_erros.to_csv(arquivo_erro, index=False)
            print(f"❌ Log de erros salvo: {arquivo_erro}")
            
    except Exception as e:
        print(f"⚠️  Erro ao salvar logs: {str(e)}")

def criar_planilha_controle(numeros_enviados, timestamp):
    """Cria planilha para controle de confirmações"""
    try:
        dados_controle = []
        for numero in numeros_enviados:
            dados_controle.append({
                'numero': numero,
                'enviado_em': timestamp,
                'confirmou': 'NÃO',
                'data_confirmacao': '',
                'observacoes': ''
            })
        
        df_controle = pd.DataFrame(dados_controle)
        arquivo_controle = f'logs/controle_confirmacoes_{timestamp}.csv'
        df_controle.to_csv(arquivo_controle, index=False)
        
        print(f"📋 Planilha de controle criada: {arquivo_controle}")
        print(f"💡 Use esta planilha para marcar quem confirmou recebimento!")
        
    except Exception as e:
        print(f"⚠️  Erro ao criar planilha de controle: {str(e)}")

def enviar_mudanca_numero(arquivo_csv, coluna_numero, numero_antigo, numero_novo):
    """
    Envia notificação sobre mudança de número via WhatsApp
    """
    
    # Timestamp para os arquivos de log
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Cria diretório de logs
    criar_logs()
    
    # Mensagem sobre mudança de número
    mensagem = f"""📱 MUDANÇA DE NÚMERO

Olá! Este é meu novo número do WhatsApp.

❌ Número antigo: {numero_antigo}
✅ Número novo: {numero_novo}

Por favor, salve este novo número em sua agenda e delete o antigo.

Confirme com um 👍 para registrar.

Obrigado! 😊"""
    
    try:
        # Carrega o dataset (sem cabeçalho)
        print("📂 Carregando lista de números...")
        
        try:
            # Tenta carregar COM cabeçalho primeiro
            df_com_header = pd.read_csv(arquivo_csv)
            if coluna_numero in df_com_header.columns:
                df = df_com_header
                numeros = df[coluna_numero].dropna().astype(str).tolist()
                print(f"✅ Arquivo carregado com cabeçalho - usando coluna '{coluna_numero}'")
            else:
                raise ValueError("Coluna não encontrada")
                
        except:
            # Se falhar, carrega SEM cabeçalho
            print("📝 Tentando carregar sem cabeçalho...")
            df = pd.read_csv(arquivo_csv, header=None)
            
            if df.shape[1] >= 2:
                # Assume: Coluna 0 = Nome, Coluna 1 = Número
                numeros = df.iloc[:, 1].dropna().astype(str).tolist()
                print(f"✅ Arquivo sem cabeçalho carregado - usando coluna 1 (números)")
            else:
                print(f"❌ Erro: Arquivo deve ter pelo menos 2 colunas (nome, número)")
                return
        print(f"📊 Total de números encontrados: {len(numeros)}")
        
        # Confirmação antes de iniciar
        print(f"\n📝 Mensagem que será enviada:")
        print("-" * 50)
        print(mensagem)
        print("-" * 50)
        
        confirma = input(f"\n❓ Confirma envio para {len(numeros)} números? (s/n): ").lower()
        
        if confirma != 's':
            print("❌ Operação cancelada pelo usuário.")
            return
        
        print("\n🚀 Iniciando envios...")
        print("⚠️  NÃO MEXA NO COMPUTADOR DURANTE O PROCESSO!")
        
        # Aguarda 10 segundos para o usuário se preparar
        for i in range(10, 0, -1):
            print(f"Iniciando em {i} segundos...", end='\r')
            time.sleep(1)
        
        # Listas para logs
        sucessos = []
        erros = []
        contador_sucesso = 0
        contador_erro = 0
        
        for i, numero in enumerate(numeros, 1):
            try:
                # Limpa o número
                numero_limpo = ''.join(filter(str.isdigit, str(numero)))
                
                # Adiciona +55 se não tiver
                if len(numero_limpo) == 11 and numero_limpo.startswith(('11', '12', '13', '14', '15', '16', '17', '18', '19', '21', '22', '24', '27', '28')):
                    numero_formatado = '+55' + numero_limpo
                elif len(numero_limpo) == 71:
                    numero_formatado = '+55' + numero_limpo
                else:
                    numero_formatado = '+55' + numero_limpo
                
                print(f"📤 Enviando {i}/{len(numeros)} para {numero_formatado[-11:]}...")
                
                # Envia a mensagem
                pwk.sendwhatmsg_instantly(
                    phone_no=numero_formatado,
                    message=mensagem,
                    wait_time=8,     # Tempo para carregar WhatsApp Web
                    tab_close=True,  # Fecha a aba automaticamente
                    close_time=2     # Tempo para fechar
                )
                
                # Registra sucesso
                contador_sucesso += 1
                sucessos.append({
                    'numero_original': numero,
                    'numero_formatado': numero_formatado,
                    'status': 'ENVIADO',
                    'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'tentativa': i
                })
                
                print(f"✅ Enviado com sucesso!")
                
                # Pausa entre envios (importante para não ser bloqueado)
                if i < len(numeros):  # Não pausa no último
                    print("⏳ Aguardando 15 segundos...")
                    time.sleep(15)
                
            except Exception as e:
                # Registra erro
                contador_erro += 1
                erros.append({
                    'numero_original': numero,
                    'numero_formatado': numero_formatado if 'numero_formatado' in locals() else 'Erro na formatação',
                    'status': 'ERRO',
                    'erro': str(e),
                    'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'tentativa': i
                })
                
                print(f"❌ Erro ao enviar para {numero}: {str(e)}")
                time.sleep(5)  # Pausa menor em caso de erro
                continue
        
        # Salva logs dos envios
        salvar_log_envios(sucessos, erros, timestamp)
        
        # Cria planilha de controle para acompanhar confirmações
        numeros_enviados_sucesso = [item['numero_formatado'] for item in sucessos]
        if numeros_enviados_sucesso:
            criar_planilha_controle(numeros_enviados_sucesso, timestamp)
        
        # Relatório final
        print(f"\n{'='*50}")
        print(f"📊 RELATÓRIO FINAL")
        print(f"{'='*50}")
        print(f"✅ Enviados com sucesso: {contador_sucesso}")
        print(f"❌ Erros: {contador_erro}")
        print(f"📱 Total processado: {len(numeros)}")
        print(f"📁 Logs salvos na pasta 'logs/'")
        print(f"✨ Processo concluído!")
        
        # Instruções finais
        if contador_sucesso > 0:
            print(f"\n💡 PRÓXIMOS PASSOS:")
            print(f"1. Verifique os logs na pasta 'logs/'")
            print(f"2. Use a planilha 'controle_confirmacoes_{timestamp}.csv'")
            print(f"3. Marque 'SIM' na coluna 'confirmou' quando receber o 👍")
            print(f"4. ⚠️  IMPORTANTE: Confirmações que chegarem depois não aparecerão")
            print(f"   automaticamente no log - você deve atualizar manualmente!")
            print(f"5. A planilha é sua ferramenta de controle manual! 📋")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")

def criar_exemplo_csv():
    """Cria arquivo CSV de exemplo SEM cabeçalho"""
    dados = [
        ['João Silva', '11999999999'],
        ['Maria Santos', '21888888888'], 
        ['Pedro Oliveira', '11777777777'],
        ['Ana Costa', '11666666666']
    ]
    
    df = pd.DataFrame(dados)
    df.to_csv('numeros_mudanca.csv', index=False, header=False)
    print("✅ Arquivo 'numeros_mudanca.csv' criado SEM cabeçalho!")
    print("📝 Formato: Nome, Número (sem títulos nas colunas)")
    print("📂 Exemplo do conteúdo:")
    print("   João Silva,11999999999")
    print("   Maria Santos,21888888888")

def main():
    print("📱 NOTIFICAÇÃO DE MUDANÇA DE NÚMERO")
    print("="*50)
    
    print("1. Enviar notificações")
    print("2. Criar arquivo CSV exemplo")
    
    opcao = input("\nEscolha uma opção (1 ou 2): ").strip()
    
    if opcao == "1":
        # Configurações
        arquivo = input("Nome do arquivo CSV (ex: numeros.csv): ").strip()
        if not arquivo:
            arquivo = "numeros.csv"
        
        print("\n📝 FORMATO DO ARQUIVO:")
        print("✅ COM cabeçalho: nome,numero")
        print("✅ SEM cabeçalho: João Silva,11999999999")
        print("   O programa detecta automaticamente!")
        
        coluna = input("\nSe tem cabeçalho, nome da coluna dos números (ex: numero): ").strip()
        if not coluna:
            coluna = "numero"
        
        num_antigo = input("Seu número ANTIGO (ex: 11999999999): ").strip()
        num_novo = input("Seu número NOVO (ex: 11888888888): ").strip()
        
        if not num_antigo or not num_novo:
            print("❌ Números antigo e novo são obrigatórios!")
            return
        
        print(f"\n⚠️  INSTRUÇÕES:")
        print(f"1. Feche o WhatsApp Web se estiver aberto")
        print(f"2. O programa abrirá o navegador automaticamente")
        print(f"3. Escaneie o QR Code rapidamente quando aparecer")
        print(f"4. NÃO toque no computador durante o processo")
        
        input("\nPressione ENTER quando estiver pronto...")
        
        enviar_mudanca_numero(arquivo, coluna, num_antigo, num_novo)
        
    elif opcao == "2":
        criar_exemplo_csv()
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
