import java.awt.BasicStroke
import java.awt.Color
import java.awt.Dimension
import java.awt.Font
import java.awt.Graphics
import java.awt.Graphics2D
import java.awt.RenderingHints
import javax.swing.JFrame
import javax.swing.JPanel
import javax.swing.SwingUtilities

class DrsDisplay(private var decision: String = "PENDING") : JPanel() {

    init {
        preferredSize = Dimension(300, 200)
        background = Color.BLACK
    }

    fun updateDecision(newDecision: String) {
        decision = newDecision
        repaint()
    }

    override fun paintComponent(g: Graphics) {
        super.paintComponent(g)
        val g2d = g as Graphics2D

        
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)
        g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON)

        g2d.color = Color(0, 0, 0, 220)
        g2d.fillRoundRect(10, 10, width - 20, height - 20, 15, 15)

        
        g2d.color = Color.WHITE
        g2d.stroke = BasicStroke(3f)
        g2d.drawRoundRect(10, 10, width - 20, height - 20, 15, 15)

        
        g2d.font = Font("Arial", Font.BOLD, 18)
        g2d.color = Color.WHITE
        val headerText = "DRS DECISION"
        val headerWidth = g2d.fontMetrics.stringWidth(headerText)
        g2d.drawString(headerText, (width - headerWidth) / 2, 40)

       
        g2d.drawLine(30, 50, width - 30, 50)

        
        g2d.color = when (decision.uppercase()) {
            "NOT OUT" -> Color.GREEN
            "PENDING" -> Color.YELLOW
            else -> Color.RED 
        }

       
        g2d.font = Font("Arial", Font.BOLD, 32)
        val displayText = decision.uppercase()
        val textWidth = g2d.fontMetrics.stringWidth(displayText)
        g2d.drawString(displayText, (width - textWidth) / 2, 120)
    }
}

class SimpleDrsApp {
    private val frame = JFrame("Cricket DRS")
    private val drsPanel = DrsDisplay()

    init {
        frame.defaultCloseOperation = JFrame.EXIT_ON_CLOSE
        frame.contentPane.add(drsPanel)
        frame.pack()
        frame.setLocationRelativeTo(null) // Center on screen
    }

    fun show() {
        frame.isVisible = true
    }

    fun displayDecision(decision: String) {
        drsPanel.updateDecision(decision)
    }
}


fun main() {
    
    val app = SimpleDrsApp()

    SwingUtilities.invokeLater {
        app.show()
    }

  
    Thread.sleep(2)
    app.displayDecision("OUT")

    Thread.sleep(2)
    app.displayDecision("NOT OUT")

    
}