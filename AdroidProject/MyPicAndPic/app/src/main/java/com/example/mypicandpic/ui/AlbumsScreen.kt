package com.example.mypicandpic.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import coil3.compose.AsyncImage
import coil3.request.ImageRequest
import com.example.mypicandpic.Album
import com.example.mypicandpic.Photo
import com.example.mypicandpic.viewmodel.AlbumViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AlbumsScreen(
    viewModel: AlbumViewModel,
    onNavigateToAlbumDetail: (albumId: String, albumName: String) -> Unit,
    onNavigateToEdit: (String) -> Unit,
    onNavigateBack: () -> Unit
) {
    val albums by viewModel.albums.collectAsState()
    val photos by viewModel.photos.collectAsState()

    var showAddAlbumDialog by remember { mutableStateOf(false) }
    var albumName by remember { mutableStateOf("") }

    if (showAddAlbumDialog) {
        AlertDialog(
            onDismissRequest = { showAddAlbumDialog = false },
            title = { Text("새 앨범 만들기") },
            text = {
                OutlinedTextField(
                    value = albumName,
                    onValueChange = { albumName = it },
                    placeholder = { Text("앨범 이름") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
            },
            confirmButton = {
                TextButton(
                    enabled = albumName.isNotBlank(),
                    onClick = {
                        viewModel.addAlbum(albumName.trim())
                        albumName = ""
                        showAddAlbumDialog = false
                    }
                ) {
                    Text("만들기")
                }
            },
            dismissButton = {
                TextButton(onClick = { showAddAlbumDialog = false }) {
                    Text("취소")
                }
            }
        )
    }

    Scaffold(
        floatingActionButton = {
            FloatingActionButton(
                onClick = { showAddAlbumDialog = true }
            ) {
                Icon(Icons.Default.Add, contentDescription = "새 앨범")
            }
        },
        content = { padding ->
            Column(modifier = Modifier.padding(padding)) {
                TopAppBar(
                    title = { Text("앨범 목록") },
                    navigationIcon = {
                        IconButton(onClick = onNavigateBack) {
                            Icon(Icons.Default.ArrowBack, contentDescription = "뒤로가기")
                        }
                    }
                )

                if (albums.isEmpty()) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(text = "앨범이 없습니다")
                    }
                } else {
                    LazyVerticalGrid(
                        columns = GridCells.Fixed(2),
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        contentPadding = PaddingValues(16.dp),
                        modifier = Modifier.fillMaxSize()
                    ) {
                        items(albums) { album ->
                            AlbumCard(
                                album = album,
                                photos = photos,
                                onClick = {
                                    onNavigateToAlbumDetail(album.id, album.name)
                                }
                            )
                        }
                    }
                }
            }
        }
    )
}

@Composable
fun AlbumCard(
    album: Album,
    photos: List<Photo>,
    onClick: () -> Unit
) {
    val albumPhotos = photos.filter { it.id in album.photoIds }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(0.8f)
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            Row(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(2.dp)
            ) {
                albumPhotos.take(3).forEach { photo ->
                    AsyncImage(
                        model = ImageRequest.Builder(LocalContext.current).data(photo.uri).build(),
                        contentDescription = photo.name,
                        contentScale = ContentScale.Crop,
                        modifier = Modifier.weight(1f).fillMaxHeight()
                    )
                }
            }

            Column(modifier = Modifier.padding(12.dp)) {
                Text(
                    text = album.name,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 1
                )
                Text(
                    text = "${albumPhotos.size}장의 사진",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
