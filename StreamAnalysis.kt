// === Data Models ===
open class Point3D(var x: Int, var y: Int, var z: Int)

class BallTrajectoryPoint(x: Int, y: Int, z: Int, var timeStamp: Double = 0.0) : Point3D(x, y, z)

class ImpactPoint(
    x: Int,
    y: Int,
    z: Int,
    var speed: Double = 0.0,
    var spinAxis: DoubleArray = doubleArrayOf(0.0, 0.0, 0.0),
    var surface: String? = null
) : Point3D(x, y, z)

class TrajectoryAnalysisResult {
    var label: String? = null        // OUT, NOT_OUT, LBW, CAUGHT, RUN_OUT, etc.
    var confidence: Double = 0.0
    var impactPoint: ImpactPoint? = null
    var predictedTrajectory: List<BallTrajectoryPoint>? = null
    var batCoordinates: List<Point3D>? = null
    var stumpCoordinates: List<Point3D>? = null
}

class VideoStreamConfig {
    var width: Int = 0
    var height: Int = 0
    var cameraId: String? = null
    var frameRate: Int = 30
    var outputPath: String? = null
}

// === Overlay Module Interface ===
interface StreamOverlayModule {
    fun initialize(config: VideoStreamConfig)
    fun receiveTrajectoryData(data: TrajectoryAnalysisResult)
    fun finalizeVideo(outputPath: String)
}

// === Decision Module Interface ===
interface DecisionModule {
    fun decide(data: TrajectoryAnalysisResult): TrajectoryAnalysisResult
}

// === LBW Decision Module ===
class LbwDecisionModule : DecisionModule {
    override fun decide(data: TrajectoryAnalysisResult): TrajectoryAnalysisResult {
        val impact = data.impactPoint
        val stumps = data.stumpCoordinates

        if (impact != null && stumps != null && impact.surface == "leg") {
            val inLineWithStumps = stumps.any { s -> s.x in (impact.x - 10)..(impact.x + 10) }
            if (inLineWithStumps && impact.y > 0) {
                data.label = "LBW"
                data.confidence = 0.92
                return data
            }
        }
        return data
    }
}

// === Caught Decision Module ===
class CaughtDecisionModule : DecisionModule {
    override fun decide(data: TrajectoryAnalysisResult): TrajectoryAnalysisResult {
        val batHit = !data.batCoordinates.isNullOrEmpty()
        val predicted = data.predictedTrajectory

        if (batHit && predicted != null) {
            val highZPoints = predicted.filter { it.z > 100 }
            if (highZPoints.isNotEmpty()) {
                data.label = "CAUGHT"
                data.confidence = 0.90
                return data
            }
        }
        return data
    }
}

// === Run-Out Decision Module ===
class RunOutDecisionModule : DecisionModule {
    override fun decide(data: TrajectoryAnalysisResult): TrajectoryAnalysisResult {
        val stumps = data.stumpCoordinates
        val predicted = data.predictedTrajectory

        if (stumps != null && predicted != null) {
            val lastFrame = predicted.lastOrNull()
            val nearStumps = stumps.any { s ->
                lastFrame != null && Math.abs(lastFrame.x - s.x) < 10 && Math.abs(lastFrame.y - s.y) < 10
            }
            if (nearStumps && data.label == null) {
                data.label = "RUN_OUT"
                data.confidence = 0.88
                return data
            }
        }
        return data
    }
}

// === Decision Maker ===
class DecisionMaker(private val modules: List<DecisionModule>) {
    fun makeDecision(data: TrajectoryAnalysisResult): TrajectoryAnalysisResult {
        for (module in modules) {
            val result = module.decide(data)
            if (result.label != null) return result
        }
        data.label = "NOT_OUT"
        data.confidence = 1.0
        return data
    }
}

// === Stream Analysis ===
class StreamAnalysis : StreamOverlayModule {
    private lateinit var config: VideoStreamConfig
    private val decisionMaker = DecisionMaker(
        listOf(
            LbwDecisionModule(),
            CaughtDecisionModule(),
            RunOutDecisionModule()
        )
    )

    override fun initialize(config: VideoStreamConfig) {
        this.config = config
        println("Overlay initialized with camera: ${config.cameraId}, resolution: ${config.width}x${config.height}")
    }

    override fun receiveTrajectoryData(data: TrajectoryAnalysisResult) {
        val decidedData = decisionMaker.makeDecision(data)
        println("🎯 Decision: ${decidedData.label}")
        println("📊 Confidence: ${decidedData.confidence}")
        println("🎬 Overlaying trajectory with ${data.predictedTrajectory?.size ?: 0} points...")
    }

    override fun finalizeVideo(outputPath: String) {
        println("Saving video to $outputPath with encoding settings...")
        println("✅ Video finalized successfully.")
    }
}
