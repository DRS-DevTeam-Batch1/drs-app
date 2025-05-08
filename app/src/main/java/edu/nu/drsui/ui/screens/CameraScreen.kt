package edu.nu.drsui.ui.screenscmab

import androidx.camera.video.Quality
import androidx.camera.video.Recorder
import androidx.camera.video.VideoCapture
import androidx.camera.video.FileOutputOptions
import androidx.camera.video.QualitySelector
import androidx.camera.video.VideoRecordEvent
import androidx.camera.video.Recording


// Your Imports
import android.widget.Toast
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.ui.platform.LocalContext
import edu.nu.drsui.network.RetrofitClient
import edu.nu.drsui.network.VideoUploadApi
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.launch
import androidx.compose.runtime.rememberCoroutineScope
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.HttpException
import java.io.File

// Other Android & Jetpack Compose Imports
import android.content.Context
import android.util.Log
import androidx.camera.core.CameraSelector
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Lens
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import edu.nu.drsui.model.Ball
import edu.nu.drsui.model.CaptureAngle
import edu.nu.drsui.ui.components.BallList
import okhttp3.RequestBody.Companion.asRequestBody
import kotlin.coroutines.resume
import kotlin.coroutines.suspendCoroutine

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CameraScreen(
    hasCameraPermission: Boolean,
    onNavigateToSettings: () -> Unit
) {
    var videoCapture by remember { mutableStateOf<VideoCapture<Recorder>?>(null) }
    var recording by remember { mutableStateOf<Recording?>(null) }
    var isUploading by remember { mutableStateOf(false) }
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val coroutineScope = rememberCoroutineScope()

    var isRecording by remember { mutableStateOf(false) }
    var overNumber by remember { mutableStateOf(1) }
    var ballNumberText by remember { mutableStateOf("1") }
    var ballNumber by remember { mutableStateOf(1) }
    var selectedAngle by remember { mutableStateOf(CaptureAngle.FRONT) }
    var isAngleDropdownExpanded by remember { mutableStateOf(false) }

    var recordedBalls by remember {
        mutableStateOf(listOf<Ball>())
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Top Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "DRS App",
                style = MaterialTheme.typography.titleLarge
            )

            IconButton(onClick = onNavigateToSettings) {
                Icon(
                    imageVector = Icons.Default.Settings,
                    contentDescription = "Settings"
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Camera Preview
        if (hasCameraPermission) {
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .border(
                        width = 2.dp,
                        color = if (isRecording) Color.Red else MaterialTheme.colorScheme.primary,
                        shape = RoundedCornerShape(12.dp)
                    )
            ) {
                CameraPreview(
                    modifier = Modifier.fillMaxSize(),
                    onVideoCaptureReady = { capture ->
                        videoCapture = capture
                    }
                )

                if (isRecording) {
                    Row(
                        modifier = Modifier
                            .align(Alignment.TopStart)
                            .padding(16.dp)
                            .background(
                                color = Color.Black.copy(alpha = 0.6f),
                                shape = RoundedCornerShape(16.dp)
                            )
                            .padding(horizontal = 12.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(12.dp)
                                .background(Color.Red, CircleShape)
                        )
                        Text(
                            text = "REC",
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                FloatingActionButton(
                    onClick = {
                        val vc = videoCapture
                        if (vc != null) {
                            if (recording != null) {
                                recording?.stop()
                                recording = null
                                isRecording = false
                            } else {
                                val videoDir = File(context.filesDir, "Videos")
                                if (!videoDir.exists()) {
                                    videoDir.mkdirs()
                                }

                                val outputFile = File(videoDir, "ball_${recordedBalls.size + 1}.mp4")
                                val outputOptions = FileOutputOptions.Builder(outputFile).build()

                                val newRecording = vc.output
                                    .prepareRecording(context, outputOptions) // Only if you want audio
                                    .start(ContextCompat.getMainExecutor(context)) { recordEvent ->
                                        when (recordEvent) {
                                            is VideoRecordEvent.Start -> {
                                                isRecording = true
                                            }
                                            is VideoRecordEvent.Finalize -> {
                                                if (!recordEvent.hasError()) {
                                                    Log.d("Recording", "Video saved successfully: ${outputFile.absolutePath}")
                                                } else {
                                                    Log.e("Recording", "Video capture failed: ${recordEvent.error}")
                                                }
                                                recording = null
                                                isRecording = false
                                            }
                                        }
                                    }

                                recording = newRecording

                                val newBall = Ball(
                                    id = recordedBalls.size + 1,
                                    overNumber = overNumber,
                                    ballNumber = ballNumber,
                                    captureAngle = selectedAngle,
                                    timestamp = System.currentTimeMillis()
                                )

                                recordedBalls = (recordedBalls + newBall).takeLast(6)

                                if (ballNumber < 6) {
                                    ballNumber++
                                } else {
                                    ballNumber = 1
                                    overNumber++
                                }
                            }
                        }
                    },
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(bottom = 16.dp),
                    containerColor = if (isRecording) Color.Red else MaterialTheme.colorScheme.primary
                ) {
                    Icon(
                        imageVector = Icons.Default.Lens,
                        contentDescription = if (isRecording) "Stop Recording" else "Start Recording",
                        tint = Color.White
                    )
                }
            }
        } else {
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(Color.Black),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "Camera permission required",
                    color = Color.White
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Controls and Upload Button
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "Recording Controls",
                    style = MaterialTheme.typography.titleMedium
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedTextField(
                        value = overNumber.toString(),
                        onValueChange = {
                            overNumber = it.toIntOrNull() ?: overNumber
                        },
                        label = { Text("Over") },
                        modifier = Modifier.weight(1f)
                    )

                    OutlinedTextField(
                        value = ballNumberText,
                        onValueChange = { newText ->
                            // Allow only digits
                            if (newText.all { it.isDigit() }) {
                                val number = newText.toIntOrNull()
                                if (number != null && number in 1..6) {
                                    ballNumberText = newText
                                    ballNumber = number
                                } else if (newText.isEmpty()) {
                                    ballNumberText = ""
                                }
                                // Else do nothing (if >6 or invalid)
                            }
                            // Else ignore the non-digit typing
                        },
                        label = { Text("Ball") },
                        modifier = Modifier.weight(1f)
                    )
                }

                Box {
                    OutlinedTextField(
                        value = selectedAngle.displayName,
                        onValueChange = {},
                        label = { Text("Capture Angle") },
                        modifier = Modifier.fillMaxWidth(),
                        readOnly = true,
                        trailingIcon = {
                            IconButton(onClick = { isAngleDropdownExpanded = true }) {
                                Icon(
                                    imageVector = Icons.Default.Settings,
                                    contentDescription = "Select Angle"
                                )
                            }
                        }
                    )

                    DropdownMenu(
                        expanded = isAngleDropdownExpanded,
                        onDismissRequest = { isAngleDropdownExpanded = false }
                    ) {
                        CaptureAngle.values().forEach { angle ->
                            DropdownMenuItem(
                                text = { Text(angle.displayName) },
                                onClick = {
                                    selectedAngle = angle
                                    isAngleDropdownExpanded = false
                                }
                            )
                        }
                    }
                }

                Button(
                    onClick = {
                        if (recordedBalls.isNotEmpty()) {
                            val latestBall = recordedBalls.last()
                            val videoFilePath = context.filesDir.absolutePath + "/Videos/ball_${latestBall.id}.mp4"

                            coroutineScope.launch {
                                isUploading = true
                                uploadVideo(videoFilePath, context) {
                                    isUploading = false
                                }
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = recordedBalls.isNotEmpty() && !isUploading
                ) {
                    Text(if (isUploading) "Uploading..." else "Send Latest Ball to Server")
                }

                if (isUploading) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Box(
                        modifier = Modifier.fillMaxWidth(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        BallList(
            balls = recordedBalls,
            onBallSelected = { /* Optional */ }
        )
    }
}

@Composable
fun CameraPreview(
    modifier: Modifier = Modifier,
    onVideoCaptureReady: (VideoCapture<Recorder>) -> Unit // ⭐ New
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    val previewView = remember { PreviewView(context) }

    LaunchedEffect(previewView) {
        val cameraProvider = context.getCameraProvider()
        val preview = Preview.Builder().build()

        val recorder = Recorder.Builder()
            .setQualitySelector(QualitySelector.from(Quality.HIGHEST))
            .build()

        val videoCapture = VideoCapture.withOutput(recorder)

        val cameraSelector = CameraSelector.Builder()
            .requireLensFacing(CameraSelector.LENS_FACING_BACK)
            .build()

        try {
            cameraProvider.unbindAll()
            cameraProvider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview,
                videoCapture
            )

            preview.setSurfaceProvider(previewView.surfaceProvider)

            onVideoCaptureReady(videoCapture) // ⭐ Pass it back
        } catch (e: Exception) {
            Log.e("CameraPreview", "Use case binding failed", e)
        }
    }

    DisposableEffect(Unit) {
        onDispose { }
    }

    AndroidView(
        factory = { previewView },
        modifier = modifier
    )
}

suspend fun Context.getCameraProvider(): ProcessCameraProvider = suspendCoroutine { continuation ->
    ProcessCameraProvider.getInstance(this).also { future ->
        future.addListener(
            { continuation.resume(future.get()) },
            ContextCompat.getMainExecutor(this)
        )
    }
}
suspend fun uploadVideo(filePath: String, context: Context, onComplete: () -> Unit) {
    try {
        val file = File(filePath)
        if (!file.exists()) {
            Toast.makeText(context, "File does not exist: $filePath", Toast.LENGTH_SHORT).show()
            return
        }

        val requestFile = file.asRequestBody("video/mp4".toMediaTypeOrNull())
        val body = MultipartBody.Part.createFormData("file", file.name, requestFile)

        // Log the file being uploaded
        Log.d("Upload", "Uploading video from: $filePath")

        val api = RetrofitClient.retrofit.create(VideoUploadApi::class.java)

        val response = withContext(Dispatchers.IO) {
            api.uploadVideo(body)
        }

        if (response.isSuccessful) {
            withContext(Dispatchers.Main) {
                Toast.makeText(context, "Video uploaded successfully!", Toast.LENGTH_SHORT).show()
            }
        } else {
            withContext(Dispatchers.Main) {
                Toast.makeText(context, "Upload failed: ${response.code()}", Toast.LENGTH_SHORT).show()
            }
        }
    } catch (e: Exception) {
        e.printStackTrace()
        if (e is HttpException) {
            withContext(Dispatchers.Main) {
                Toast.makeText(context, "Server error: ${e.code()}", Toast.LENGTH_SHORT).show()
            }
        } else {
            withContext(Dispatchers.Main) {
                Toast.makeText(context, "Upload failed: ${e.localizedMessage}", Toast.LENGTH_SHORT).show()
            }
        }
    } finally {
        onComplete()
    }
}
