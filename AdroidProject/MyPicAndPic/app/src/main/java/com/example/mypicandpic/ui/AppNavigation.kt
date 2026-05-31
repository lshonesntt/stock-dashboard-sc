package com.example.mypicandpic.ui

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Face
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.mypicandpic.Photo
import com.example.mypicandpic.viewmodel.AlbumViewModel
import kotlinx.coroutines.launch

@Composable
fun AppNavigation(
    viewModel: AlbumViewModel = viewModel()
) {
    var currentDest by rememberSaveable { mutableStateOf<AppDest>(AppDest.Home) }
    val snackbarState = remember { SnackbarHostState() }
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    val permLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { perms ->
        if (!perms.all { it.value }) {
            scope.launch { snackbarState.showSnackbar("Permission denied") }
        }
    }

    val imagePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.PickMultipleVisualMedia(10)
    ) { uris ->
        if (uris != null && uris.isNotEmpty()) {
            uris.forEach { uri ->
                try {
                    context.contentResolver.takePersistableUriPermission(
                        uri,
                        android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION
                    )
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
            if (currentDest is AppDest.AlbumDetail) {
                val albumId = (currentDest as AppDest.AlbumDetail).albumId
                uris.forEach { uri ->
                    val fileName = uri.lastPathSegment ?: "photo_${System.currentTimeMillis()}"
                    viewModel.addPhotoToAlbum(
                        albumId = albumId,
                        photoUri = uri.toString(),
                        photoName = fileName
                    )
                }
                scope.launch { snackbarState.showSnackbar("Added ${uris.size} photos") }
            }
        }
    }

    LaunchedEffect(Unit) {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            permLauncher.launch(arrayOf(android.Manifest.permission.READ_MEDIA_IMAGES))
        } else {
            permLauncher.launch(arrayOf(android.Manifest.permission.READ_EXTERNAL_STORAGE))
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(hostState = snackbarState) },
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Home, "Home") },
                    label = { Text("홈") },
                    selected = currentDest is AppDest.Home,
                    onClick = { currentDest = AppDest.Home }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Face, "Albums") },
                    label = { Text("앨범") },
                    selected = currentDest is AppDest.Albums,
                    onClick = { currentDest = AppDest.Albums }
                )
            }
        }
    ) { padding ->
            Box(modifier = Modifier.padding(padding)) {
                when (val dest = currentDest) {
                    is AppDest.Home -> {
                        HomeScreen(
                            viewModel = viewModel,
                            onNavigateToAlbums = { currentDest = AppDest.Albums },
                            onNavigateToEdit = { currentDest = AppDest.Edit(it) }
                        )
                    }
                    is AppDest.Albums -> {
                        AlbumsScreen(
                            viewModel = viewModel,
                            onNavigateToAlbumDetail = { id, name -> currentDest = AppDest.AlbumDetail(id, name) },
                            onNavigateToEdit = { currentDest = AppDest.Edit(it) },
                            onNavigateBack = {}
                        )
                    }
                    is AppDest.AlbumDetail -> {
                        AlbumDetailScreen(
                            albumId = dest.albumId,
                            albumName = dest.albumName,
                            viewModel = viewModel,
                            onNavigateBack = { currentDest = AppDest.Albums },
                            onNavigateToEdit = { currentDest = AppDest.Edit(it) },
                            onAddPhotos = { 
                                imagePickerLauncher.launch(
                                    PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
                                )
                            }
                        )
                    }
                    is AppDest.Edit -> {
                        EditScreen(
                            photoUri = dest.photoUri,
                            onNavigateBack = { currentDest = AppDest.Home },
                            onShare = { uriStr, _ ->
                                val shareIntent = android.content.Intent(android.content.Intent.ACTION_SEND).apply {
                                    type = "image/*"
                                    putExtra(android.content.Intent.EXTRA_STREAM, android.net.Uri.parse(uriStr))
                                    addFlags(android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION)
                                }
                                context.startActivity(android.content.Intent.createChooser(shareIntent, "공유할 앱 선택"))
                            }
                        )
                    }
                }
            }
    }
}

sealed interface AppDest : java.io.Serializable {
    data object Home : AppDest
    data object Albums : AppDest
    data class AlbumDetail(val albumId: String, val albumName: String) : AppDest
    data class Edit(val photoUri: String) : AppDest
}
