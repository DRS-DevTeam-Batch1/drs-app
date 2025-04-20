package edu.nu.drsui.model

data class Ball(
    val id: Int,
    val overNumber: Int,
    val ballNumber: Int,
    val captureAngle: CaptureAngle,
    val timestamp: Long,
    val videoPath: String? = null
)

enum class CaptureAngle(val displayName: String) {
    FRONT("Front"),
    LEGSIDE("Leg Side"),
}
