package com.example.mypicandpic

import android.Manifest
import android.content.Context
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.example.mypicandpic.ui.AlbumDetailScreen
import com.example.mypicandpic.ui.AlbumsScreen
import com.example.mypicandpic.ui.EditScreen
import com.example.mypicandpic.ui.HomeScreen
import com.example.mypicandpic.ui.theme.MyPicAndPicTheme
import com.example.mypicandpic.viewmodel.AlbumViewModel
import androidx.annotation.Keep
import java.io.Serializable

private const val REQUEST_CODE_PERMISSIONS = 100

@Keep
class MainActivity : ComponentActivity() {
    private val viewModel: AlbumViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        requestGalleryPermissions()
        setContent {
            MyPicAndPicTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MyApp(viewModel)
                }
            }
        }
    }

    private fun requestGalleryPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (shouldShowRequestPermissionRationale(Manifest.permission.READ_MEDIA_IMAGES)) {
                Toast.makeText(this, "갤러리 접근 권한이 필요합니다", Toast.LENGTH_LONG).show()
             }
            requestPermissions(arrayOf(Manifest.permission.READ_MEDIA_IMAGES), REQUEST_CODE_PERMISSIONS)
         } else {
            requestPermissions(arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE), REQUEST_CODE_PERMISSIONS)
         }
     }
}

private fun showShareToast(context: Context, uri: String) {
    Toast.makeText(context, "공유 기능: ${uri.take(50)}", Toast.LENGTH_SHORT).show()
}

@Composable
fun MyApp(viewModel: AlbumViewModel) {
    var screen by rememberSaveable { mutableStateOf<Screen>(Screen.Home) }
    val context = LocalContext.current

    when (val current = screen) {
        is Screen.Home -> HomeScreen(
            viewModel = viewModel,
            onNavigateToAlbums = { screen = Screen.Albums },
            onNavigateToEdit = { uri -> screen = Screen.Edit(uri) }
         )
        is Screen.Albums -> AlbumsScreen(
            viewModel = viewModel,
            onNavigateToAlbumDetail = { id, name ->
                screen = Screen.AlbumDetail(id, name)
             },
            onNavigateToEdit = { uri -> screen = Screen.Edit(uri) },
            onNavigateBack = { screen = Screen.Home }
         )
        is Screen.AlbumDetail -> AlbumDetailScreen(
            albumId = current.albumId,
            albumName = current.albumName,
            viewModel = viewModel,
            onNavigateBack = { screen = Screen.Albums },
            onNavigateToEdit = { uri -> screen = Screen.Edit(uri) },
            onAddPhotos = { }
         )
        is Screen.Edit -> {
            EditScreen(
                photoUri = current.photoUri,
                onNavigateBack = { screen = Screen.Home },
                onShare = { uri, _ -> showShareToast(context, uri) }
             )
         }
     }
}

sealed interface Screen : Serializable {
    data object Home : Screen
    data object Albums : Screen
    data class AlbumDetail(val albumId: String, val albumName: String) : Screen
    data class Edit(val photoUri: String) : Screen
}
