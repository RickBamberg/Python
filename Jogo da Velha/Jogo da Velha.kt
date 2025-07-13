
// MainActivity.kt
package com.exemplo.jogodavelha

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.gridlayout.widget.GridLayout

class MainActivity : AppCompatActivity() {
    
    private lateinit var gameLogic: JogoDaVelhaLogic
    private lateinit var statusText: TextView
    private lateinit var resetButton: Button
    private lateinit var gridLayout: GridLayout
    private val buttons = Array(3) { Array<Button?>(3) { null } }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initializeViews()
        initializeGame()
        setupClickListeners()
    }
    
    private fun initializeViews() {
        statusText = findViewById(R.id.statusText)
        resetButton = findViewById(R.id.resetButton)
        gridLayout = findViewById(R.id.gridLayout)
        
        // Inicializa os botões do tabuleiro
        for (i in 0..2) {
            for (j in 0..2) {
                val buttonId = resources.getIdentifier("btn_${i}_${j}", "id", packageName)
                buttons[i][j] = findViewById(buttonId)
            }
        }
    }
    
    private fun initializeGame() {
        gameLogic = JogoDaVelhaLogic()
        updateUI()
    }
    
    private fun setupClickListeners() {
        // Listener para cada botão do tabuleiro
        for (i in 0..2) {
            for (j in 0..2) {
                buttons[i][j]?.setOnClickListener {
                    onCellClicked(i, j)
                }
            }
        }
        
        // Listener para botão de reset
        resetButton.setOnClickListener {
            resetGame()
        }
    }
    
    private fun onCellClicked(linha: Int, coluna: Int) {
        if (gameLogic.fazerJogada(linha, coluna)) {
            updateUI()
            
            when (gameLogic.obterEstadoJogo()) {
                is EstadoJogo.Vencedor -> {
                    showWinnerMessage(gameLogic.obterEstadoJogo() as EstadoJogo.Vencedor)
                }
                is EstadoJogo.Empate -> {
                    showDrawMessage()
                }
                else -> {
                    // Jogo continua
                }
            }
        } else {
            Toast.makeText(this, "Jogada inválida!", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun updateUI() {
        // Atualiza o tabuleiro visual
        for (i in 0..2) {
            for (j in 0..2) {
                val cellValue = gameLogic.obterCelula(i, j)
                buttons[i][j]?.text = when (cellValue) {
                    Jogador.X -> "X"
                    Jogador.O -> "O"
                    else -> ""
                }
                
                // Desabilita botão se célula ocupada ou jogo terminado
                buttons[i][j]?.isEnabled = cellValue == null && gameLogic.jogoAtivo
            }
        }
        
        // Atualiza texto de status
        statusText.text = when (val estadoJogo = gameLogic.obterEstadoJogo()) {
            is EstadoJogo.JogadorAtual -> "Vez do jogador ${estadoJogo.jogador.symbol}"
            is EstadoJogo.Vencedor -> "Jogador ${estadoJogo.jogador.symbol} venceu!"
            is EstadoJogo.Empate -> "Empate!"
        }
    }
    
    private fun showWinnerMessage(vencedor: EstadoJogo.Vencedor) {
        Toast.makeText(
            this, 
            "🎉 Jogador ${vencedor.jogador.symbol} venceu!", 
            Toast.LENGTH_LONG
        ).show()
    }
    
    private fun showDrawMessage() {
        Toast.makeText(this, "🤝 Empate!", Toast.LENGTH_LONG).show()
    }
    
    private fun resetGame() {
        gameLogic.reiniciarJogo()
        updateUI()
    }
}

// JogoDaVelhaLogic.kt - Lógica do jogo adaptada para Kotlin
enum class Jogador(val symbol: String) {
    X("X"),
    O("O");
    
    fun outro(): Jogador = if (this == X) O else X
}

sealed class EstadoJogo {
    data class JogadorAtual(val jogador: Jogador) : EstadoJogo()
    data class Vencedor(val jogador: Jogador) : EstadoJogo()
    object Empate : EstadoJogo()
}

class JogoDaVelhaLogic {
    private val tabuleiro = Array(3) { Array<Jogador?>(3) { null } }
    private var jogadorAtual = Jogador.X
    var jogoAtivo = true
        private set
    private var vencedor: Jogador? = null
    
    fun fazerJogada(linha: Int, coluna: Int): Boolean {
        if (!jogoAtivo || !posicaoValida(linha, coluna)) {
            return false
        }
        
        // Faz a jogada
        tabuleiro[linha][coluna] = jogadorAtual
        
        // Verifica resultado
        when {
            verificarVitoria() -> {
                vencedor = jogadorAtual
                jogoAtivo = false
            }
            tabuleiroCompleto() -> {
                jogoAtivo = false
            }
            else -> {
                jogadorAtual = jogadorAtual.outro()
            }
        }
        
        return true
    }
    
    fun obterCelula(linha: Int, coluna: Int): Jogador? {
        return if (linha in 0..2 && coluna in 0..2) {
            tabuleiro[linha][coluna]
        } else null
    }
    
    fun obterEstadoJogo(): EstadoJogo {
        return when {
            vencedor != null -> EstadoJogo.Vencedor(vencedor!!)
            !jogoAtivo -> EstadoJogo.Empate
            else -> EstadoJogo.JogadorAtual(jogadorAtual)
        }
    }
    
    fun reiniciarJogo() {
        for (i in 0..2) {
            for (j in 0..2) {
                tabuleiro[i][j] = null
            }
        }
        jogadorAtual = Jogador.X
        jogoAtivo = true
        vencedor = null
    }
    
    private fun posicaoValida(linha: Int, coluna: Int): Boolean {
        return linha in 0..2 && 
               coluna in 0..2 && 
               tabuleiro[linha][coluna] == null
    }
    
    private fun verificarVitoria(): Boolean {
        return verificarLinhas() || verificarColunas() || verificarDiagonais()
    }
    
    private fun verificarLinhas(): Boolean {
        for (linha in 0..2) {
            if (tabuleiro[linha][0] != null &&
                tabuleiro[linha][0] == tabuleiro[linha][1] &&
                tabuleiro[linha][1] == tabuleiro[linha][2]) {
                return true
            }
        }
        return false
    }
    
    private fun verificarColunas(): Boolean {
        for (coluna in 0..2) {
            if (tabuleiro[0][coluna] != null &&
                tabuleiro[0][coluna] == tabuleiro[1][coluna] &&
                tabuleiro[1][coluna] == tabuleiro[2][coluna]) {
                return true
            }
        }
        return false
    }
    
    private fun verificarDiagonais(): Boolean {
        // Diagonal principal
        if (tabuleiro[0][0] != null &&
            tabuleiro[0][0] == tabuleiro[1][1] &&
            tabuleiro[1][1] == tabuleiro[2][2]) {
            return true
        }
        
        // Diagonal secundária
        if (tabuleiro[0][2] != null &&
            tabuleiro[0][2] == tabuleiro[1][1] &&
            tabuleiro[1][1] == tabuleiro[2][0]) {
            return true
        }
        
        return false
    }
    
    private fun tabuleiroCompleto(): Boolean {
        for (linha in 0..2) {
            for (coluna in 0..2) {
                if (tabuleiro[linha][coluna] == null) {
                    return false
                }
            }
        }
        return true
    }
}
