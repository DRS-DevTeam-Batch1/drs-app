package edu.nu.drsui.utils

import android.content.Context
import android.util.Base64
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.File
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import android.widget.Toast
import java.io.FileInputStream
import java.net.HttpURLConnection
import java.net.URL
import okhttp3.*
object VideoUtils {

    suspend fun sendVideoToServer(
        context: Context,
        videoPath: String?,
        ballNumber: Int,
        overNumber: Int,
        captureAngle: String,
        serverUrl: String
    ): Boolean = withContext(Dispatchers.IO) {
        try {
            Toast.makeText(context, "sendVideoToServer called", Toast.LENGTH_SHORT).show()
            // Check if videoPath is null or empty
            if (videoPath.isNullOrEmpty()) {
                Log.e("VideoUtils", "Video path is null or empty")
                return@withContext false
            }
            Toast.makeText(context, "sendVideoToServer called", Toast.LENGTH_SHORT).show()
            val videoFile = File(videoPath)
            Log.e("DEBUG", "Selected file path: ${videoFile.absolutePath}")
            Log.d("DEBUG", "File exists: ${videoFile.exists()}")
            Log.d("DEBUG", "File name: ${videoFile.name}")
            Log.d("DEBUG", "File size: ${videoFile.length()} bytes")

            // Check if file exists
            if (!videoFile.exists()) {
                Log.e("VideoUtils", "Video file does not exist: $videoPath")
                return@withContext false
            }

            // Check if the file is a valid video file (optional but useful)
            if (!videoFile.canRead()) {
                Log.e("VideoUtils", "Cannot read the video file: $videoPath")
                return@withContext false
            }

            // Log the MIME type of the video file
            val mimeType = "video/*"  // Optionally, you could derive this dynamically based on the file type
            Log.d("DEBUG", "Sending file with MIME type: $mimeType")

            // Create RequestBody from video file
            val videoRequestBody = videoFile.asRequestBody(mimeType.toMediaTypeOrNull())
            if (videoRequestBody == null) {
                Log.e("VideoUtils", "Failed to create request body for video")
                return@withContext false
            }

            val videoPart = MultipartBody.Part.createFormData("video", videoFile.name, videoRequestBody)

            // Create metadata as JSON
            val metadataJson = JSONObject().apply {
                put("ballNumber", ballNumber)
                put("overNumber", overNumber)
                put("captureAngle", captureAngle)
            }

            // Create the request body containing video and metadata
            val metadataRequestBody = metadataJson.toString().toRequestBody("application/json".toMediaTypeOrNull())

            // Build the request using OkHttp
            val requestBody = MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("video", videoFile.name, videoRequestBody)
                .addFormDataPart("metadata", "metadata", metadataRequestBody) // Add metadata as another part
                .build()

            // Send the request to the server using OkHttp
            val request = Request.Builder()
                .url(serverUrl)
                .post(requestBody)
                .build()

            val client = OkHttpClient()
            val response = client.newCall(request).execute()

            val responseCode = response.code
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
