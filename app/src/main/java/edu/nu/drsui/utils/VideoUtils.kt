package edu.nu.drsui.utils

import android.content.Context
import android.util.Base64
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.File
import java.io.FileInputStream
import java.net.HttpURLConnection
import java.net.URL

object VideoUtils {

    suspend fun sendVideoToServer(
        context: Context,
        videoPath: String,
        ballNumber: Int,
        overNumber: Int,
        captureAngle: String,
        serverUrl: String
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            val videoFile = File(videoPath)
            if (!videoFile.exists()) {
                Log.e("VideoUtils", "Video file does not exist: $videoPath")
                return@withContext false
            }

            // Read video file as bytes
            val videoBytes = FileInputStream(videoFile).use { it.readBytes() }

            // Encode to base64
            val base64Video = Base64.encodeToString(videoBytes, Base64.DEFAULT)

            // Create JSON payload
            val jsonPayload = JSONObject().apply {
                put("ballNumber", ballNumber)
                put("captureAngle", captureAngle)
                put("video", base64Video)
                put("cameraDetails", JSONObject().apply {
                    put("exposure", "1/60")
                    put("resolution", "1920x1080")
                    put("iso", 100)
                    put("whiteBalance", "auto")
                    put("focalLength", "35mm")
                    put("sensorSize", "full-frame")
                    put("frameRate", "30fps")
                    put("shutterSpeed", "1/500")
                })
                put("additionalMetadata", JSONObject().apply {
                    put("videoFormat", "MP4")
                    put("videoDuration", videoFile.length() / 1024000.0)
                    put("compression", "H.264")
                    put("fileSize", videoFile.length())
                })
            }

            // Send to server
            val url = URL(serverUrl)
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.doOutput = true

            connection.outputStream.use { os ->
                os.write(jsonPayload.toString().toByteArray())
            }

            val responseCode = connection.responseCode
            Log.d("VideoUtils", "Server response code: $responseCode")

            return@withContext responseCode == 200
        } catch (e: Exception) {
            Log.e("VideoUtils", "Error sending video to server", e)
            return@withContext false
        }
    }

    fun getVideoMetadata(videoPath: String): Map<String, Any> {
        // In a real app, you would use MediaMetadataRetriever to get actual metadata
        return mapOf(
            "duration" to "5.25",
            "resolution" to "1920x1080",
            "frameRate" to "30fps"
        )
    }
}
