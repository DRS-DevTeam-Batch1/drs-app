package edu.nu.drsui.utils

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import android.util.Log
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class CameraUtils(private val context: Context) {
    private var mediaRecorder: MediaRecorder? = null
    private var isRecording = false
    private var outputFile: File? = null

    fun startRecording(overNumber: Int, ballNumber: Int): String? {
        if (isRecording) {
            Log.w("CameraUtils", "Already recording")
            return null
        }

        try {
            createMediaRecorder()

            // Create output file
            val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
            val filename = "BALL_${overNumber}_${ballNumber}_$timestamp.mp4"
            val storageDir = context.getExternalFilesDir(null)
            outputFile = File(storageDir, filename)

            mediaRecorder?.apply {
                setOutputFile(outputFile?.absolutePath)
                prepare()
                start()
            }

            isRecording = true
            return outputFile?.absolutePath
        } catch (e: IOException) {
            Log.e("CameraUtils", "Failed to start recording", e)
            releaseMediaRecorder()
            return null
        }
    }

    fun stopRecording(): String? {
        if (!isRecording) {
            Log.w("CameraUtils", "Not recording")
            return null
        }

        try {
            mediaRecorder?.apply {
                stop()
                release()
            }
            mediaRecorder = null
            isRecording = false
            return outputFile?.absolutePath
        } catch (e: Exception) {
            Log.e("CameraUtils", "Failed to stop recording", e)
            return null
        }
    }

    private fun createMediaRecorder() {
        mediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            MediaRecorder(context)
        } else {
            @Suppress("DEPRECATION")
            MediaRecorder()
        }

        mediaRecorder?.apply {
            setVideoSource(MediaRecorder.VideoSource.CAMERA)
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setVideoEncoder(MediaRecorder.VideoEncoder.H264)
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            setVideoSize(1920, 1080)
            setVideoFrameRate(30)
            setVideoEncodingBitRate(10000000)
            setAudioEncodingBitRate(128000)
        }
    }

    private fun releaseMediaRecorder() {
        mediaRecorder?.release()
        mediaRecorder = null
        isRecording = false
    }

    fun cleanupOldVideos(maxVideos: Int) {
        val storageDir = context.getExternalFilesDir(null)
        val videoFiles = storageDir?.listFiles { file ->
            file.isFile && file.name.endsWith(".mp4") && file.name.startsWith("BALL_")
        }

        videoFiles?.sortByDescending { it.lastModified() }

        if (videoFiles != null && videoFiles.size > maxVideos) {
            for (i in maxVideos until videoFiles.size) {
                videoFiles[i].delete()
            }
        }
    }
}
