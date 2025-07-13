
class JogoDaVelha:
    def __init__(self):
        # Tabuleiro 3x3 representado como lista de listas
        # ' ' = vazio, 'X' = jogador 1, 'O' = jogador 2
        self.tabuleiro = [[' ' for _ in range(3)] for _ in range(3)]
        self.jogador_atual = 'X'  # X sempre começa
        self.jogo_ativo = True
        self.vencedor = None
    
    def exibir_tabuleiro(self):
        """Exibe o tabuleiro atual no console"""
        print("\n  0   1   2")
        for i in range(3):
            print(f"{i} {self.tabuleiro[i][0]} | {self.tabuleiro[i][1]} | {self.tabuleiro[i][2]}")
            if i < 2:
                print("  ---------")
    
    def posicao_valida(self, linha, coluna):
        """Verifica se a posição é válida e está vazia"""
        if linha < 0 or linha > 2 or coluna < 0 or coluna > 2:
            return False
        return self.tabuleiro[linha][coluna] == ' '
    
    def fazer_jogada(self, linha, coluna):
        """Executa uma jogada se for válida"""
        if not self.jogo_ativo:
            return False
        
        if not self.posicao_valida(linha, coluna):
            return False
        
        # Coloca o símbolo do jogador atual
        self.tabuleiro[linha][coluna] = self.jogador_atual
        
        # Verifica se há vencedor após a jogada
        if self.verificar_vitoria():
            self.vencedor = self.jogador_atual
            self.jogo_ativo = False
        elif self.tabuleiro_cheio():
            # Empate
            self.jogo_ativo = False
        else:
            # Troca o jogador
            self.trocar_jogador()
        
        return True
    
    def verificar_vitoria(self):
        """Verifica todas as condições de vitória"""
        return (self.verificar_linhas() or 
                self.verificar_colunas() or 
                self.verificar_diagonais())
    
    def verificar_linhas(self):
        """Verifica vitória nas linhas horizontais"""
        for linha in self.tabuleiro:
            if linha[0] == linha[1] == linha[2] != ' ':
                return True
        return False
    
    def verificar_colunas(self):
        """Verifica vitória nas colunas verticais"""
        for col in range(3):
            if (self.tabuleiro[0][col] == 
                self.tabuleiro[1][col] == 
                self.tabuleiro[2][col] != ' '):
                return True
        return False
    
    def verificar_diagonais(self):
        """Verifica vitória nas diagonais"""
        # Diagonal principal (top-left para bottom-right)
        if (self.tabuleiro[0][0] == 
            self.tabuleiro[1][1] == 
            self.tabuleiro[2][2] != ' '):
            return True
        
        # Diagonal secundária (top-right para bottom-left)
        if (self.tabuleiro[0][2] == 
            self.tabuleiro[1][1] == 
            self.tabuleiro[2][0] != ' '):
            return True
        
        return False
    
    def tabuleiro_cheio(self):
        """Verifica se o tabuleiro está completamente preenchido"""
        for linha in self.tabuleiro:
            for celula in linha:
                if celula == ' ':
                    return False
        return True
    
    def trocar_jogador(self):
        """Alterna entre os jogadores X e O"""
        self.jogador_atual = 'O' if self.jogador_atual == 'X' else 'X'
    
    def reiniciar_jogo(self):
        """Reinicia o jogo para o estado inicial"""
        self.tabuleiro = [[' ' for _ in range(3)] for _ in range(3)]
        self.jogador_atual = 'X'
        self.jogo_ativo = True
        self.vencedor = None
    
    def obter_estado_jogo(self):
        """Retorna o estado atual do jogo"""
        if not self.jogo_ativo:
            if self.vencedor:
                return f"Jogador {self.vencedor} venceu!"
            else:
                return "Empate!"
        else:
            return f"Vez do jogador {self.jogador_atual}"


# Exemplo de uso e teste da lógica
def main():
    jogo = JogoDaVelha()
    
    print("=== JOGO DA VELHA ===")
    print("Digite as coordenadas no formato: linha coluna (0-2)")
    print("Exemplo: 1 1 para o centro do tabuleiro")
    
    while jogo.jogo_ativo:
        jogo.exibir_tabuleiro()
        print(f"\n{jogo.obter_estado_jogo()}")
        
        try:
            entrada = input("Digite sua jogada (linha coluna): ").split()
            if len(entrada) != 2:
                print("Formato inválido! Use: linha coluna")
                continue
                
            linha = int(entrada[0])
            coluna = int(entrada[1])
            
            if jogo.fazer_jogada(linha, coluna):
                # Jogada válida executada
                pass
            else:
                print("Jogada inválida! Tente novamente.")
                
        except ValueError:
            print("Digite apenas números!")
        except KeyboardInterrupt:
            print("\nJogo interrompido!")
            break
    
    # Resultado final
    jogo.exibir_tabuleiro()
    print(f"\n{jogo.obter_estado_jogo()}")


if __name__ == "__main__":
    main()
    