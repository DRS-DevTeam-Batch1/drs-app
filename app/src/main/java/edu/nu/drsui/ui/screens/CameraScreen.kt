package edu.nu.drsui.ui.screens

import android.content.Context
import android.util.Log
import androidx.camera.core.CameraSelector
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Lens
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import edu.nu.drsui.model.Ball
import edu.nu.drsui.model.CaptureAngle
import edu.nu.drsui.ui.components.BallList
import java.util.concurrent.Executor
import kotlin.coroutines.resume
import kotlin.coroutines.suspendCoroutine

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CameraScreen(
    hasCameraPermission: Boolean,
    onNavigateToSettings: () -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    var isRecording by remember { mutableStateOf(false) }
    var overNumber by remember { mutableStateOf(1) }
    var ballNumber by remember { mutableStateOf(1) }
    var selectedAngle by remember { mutableStateOf(CaptureAngle.FRONT) }
    var isAngleDropdownExpanded by remember { mutableStateOf(false) }

    // Simulate a list of recorded balls
    var recordedBalls by remember {
        mutableStateOf(listOf<Ball>())
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Top bar with settings
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

        // Camera preview
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
                    modifier = Modifier.fillMaxSize()
                )

                // Recording indicator
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

                // Capture button
                FloatingActionButton(
                    onClick = {
                        isRecording = !isRecording

                        // If stopping recording, add a new ball to the list
                        if (!isRecording) {
                            val newBall = Ball(
                                id = recordedBalls.size + 1,
                                overNumber = overNumber,
                                ballNumber = ballNumber,
                                captureAngle = selectedAngle,
                                timestamp = System.currentTimeMillis()
                            )

                            // Add to list and increment ball number
                            recordedBalls = (recordedBalls + newBall).takeLast(6)

                            // Increment ball number or reset and increment over
                            if (ballNumber < 6) {
                                ballNumber++
                            } else {
                                ballNumber = 1
                                overNumber++
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

        // Controls section
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

                // Over and ball number controls
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
                        value = ballNumber.toString(),
                        onValueChange = {
                            ballNumber = it.toIntOrNull()?.coerceIn(1, 6) ?: ballNumber
                        },
                        label = { Text("Ball") },
                        modifier = Modifier.weight(1f)
                    )
                }

                // Capture angle dropdown
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

                // Send to server button
                Button(
                    onClick = { /* TODO: Implement sending to server */ },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = recordedBalls.isNotEmpty()
                ) {
                    Text("Send Latest Ball to Server")
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Recorded balls list
        BallList(
            balls = recordedBalls,
            onBallSelected = { /* TODO: Implement ball selection */ }
        )
    }
}

@Composable
fun CameraPreview(
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    val previewView = remember { PreviewView(context) }

    LaunchedEffect(previewView) {
        val cameraProvider = context.getCameraProvider()
        val preview = Preview.Builder().build()

        val cameraSelector = CameraSelector.Builder()
            .requireLensFacing(CameraSelector.LENS_FACING_BACK)
            .build()

        preview.setSurfaceProvider(previewView.surfaceProvider)

        try {
            cameraProvider.unbindAll()
            cameraProvider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview
            )
        } catch (e: Exception) {
            Log.e("CameraPreview", "Use case binding failed", e)
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            // Clean up camera resources if needed
        }
    }

    AndroidView(
        factory = { previewView },
        modifier = modifier
    )
}

suspend fun Context.getCameraProvider(): ProcessCameraProvider = suspendCoroutine { continuation ->
    ProcessCameraProvider.getInstance(this).also { future ->
        future.addListener(
            {
                continuation.resume(future.get())
            },
            ContextCompat.getMainExecutor(this)
        )
    }
}
