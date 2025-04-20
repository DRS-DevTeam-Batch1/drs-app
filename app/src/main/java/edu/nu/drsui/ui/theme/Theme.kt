package edu.nu.drsui.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// Define colors
val Green40 = Color(0xFF4CAF50)
val Green80 = Color(0xFFA5D6A7)
val Green90 = Color(0xFFC8E6C9)
val Green20 = Color(0xFF1B5E20)

val Blue40 = Color(0xFF03A9F4)
val Blue80 = Color(0xFF81D4FA)
val Blue90 = Color(0xFFB3E5FC)
val Blue20 = Color(0xFF01579B)

val Orange40 = Color(0xFFFF9800)
val Orange80 = Color(0xFFFFCC80)
val Orange90 = Color(0xFFFFE0B2)
val Orange20 = Color(0xFFE65100)

val ErrorRed40 = Color(0xFFF44336)
val ErrorRed80 = Color(0xFFEF9A9A)

// Light color scheme
private val LightColorScheme = lightColorScheme(
    primary = Green40,
    onPrimary = Color.White,
    primaryContainer = Green90,
    onPrimaryContainer = Color(0xFF0C3B0F),
    secondary = Blue40,
    onSecondary = Color.White,
    secondaryContainer = Blue90,
    onSecondaryContainer = Blue20,
    tertiary = Orange40,
    onTertiary = Color.White,
    tertiaryContainer = Orange90,
    onTertiaryContainer = Orange20,
    error = ErrorRed40,
    onError = Color.White,
    background = Color(0xFFF8F8F8),
    onBackground = Color.Black,
    surface = Color.White,
    onSurface = Color.Black,
    surfaceVariant = Color(0xFFF5F5F5),
    onSurfaceVariant = Color(0xFF757575)
)

// Dark color scheme
private val DarkColorScheme = darkColorScheme(
    primary = Green80,
    onPrimary = Color.Black,
    primaryContainer = Green20,
    onPrimaryContainer = Green90,
    secondary = Blue80,
    onSecondary = Color.Black,
    secondaryContainer = Blue20,
    onSecondaryContainer = Blue90,
    tertiary = Orange80,
    onTertiary = Color.Black,
    tertiaryContainer = Orange20,
    onTertiaryContainer = Orange90,
    error = ErrorRed80,
    onError = Color.Black,
    background = Color(0xFF121212),
    onBackground = Color.White,
    surface = Color(0xFF212121),
    onSurface = Color.White,
    surfaceVariant = Color(0xFF424242),
    onSurfaceVariant = Color(0xFFE0E0E0)
)

@Composable
fun DRSTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color is available on Android 12+
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
