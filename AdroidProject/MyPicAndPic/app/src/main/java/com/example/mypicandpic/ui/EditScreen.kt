package com.example.mypicandpic.ui

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil3.compose.AsyncImage
import coil3.request.ImageRequest

sealed interface FilterType {
    object None : FilterType
    object Grayscale : FilterType
    object Sepia : FilterType
    object Negative : FilterType
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EditScreen(
    photoUri: String,
    onNavigateBack: () -> Unit,
    onShare: (String, String?) -> Unit
) {
    var currentFilter by remember { mutableStateOf<FilterType>(FilterType.None) }
    var isCropMode by remember { mutableStateOf(false) }
    var cropRect by remember { mutableStateOf<Rect?>(null) }
    var cropEnd by remember { mutableStateOf(Offset.Zero) }

    val context = LocalContext.current
    val photoName = photoUri.substringAfterLast('/')

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(photoName, maxLines = 1, overflow = TextOverflow.Ellipsis) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "뒤로가기")
                      }
                  },
                actions = {
                    IconButton(onClick = {
                        onShare(photoUri, null)
                      }) {
                        Icon(Icons.Default.Share, contentDescription = "공유")
                      }
                  }
              )
          },
        bottomBar = {
            Surface(tonalElevation = 4.dp) {
                Column {
                    Row(
                        modifier = Modifier
                              .fillMaxWidth()
                              .padding(horizontal = 8.dp, vertical = 8.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                      ) {
                        FilterButton(
                            label = "원본",
                            isSelected = currentFilter == FilterType.None,
                            onClick = {
                                currentFilter = FilterType.None
                                isCropMode = false
                              }
                          )
                        FilterButton(
                            label = "흑백",
                            isSelected = currentFilter == FilterType.Grayscale,
                            onClick = { currentFilter = FilterType.Grayscale }
                          )
                        FilterButton(
                            label = "Sepia",
                            isSelected = currentFilter == FilterType.Sepia,
                            onClick = { currentFilter = FilterType.Sepia }
                          )
                        FilterButton(
                            label = "반전",
                            isSelected = currentFilter == FilterType.Negative,
                            onClick = { currentFilter = FilterType.Negative }
                          )
                        FilterButton(
                            label = "자르기",
                            isSelected = isCropMode,
                            onClick = { isCropMode = !isCropMode }
                          )
                      }

                    if (isCropMode && cropRect != null) {
                        Row(
                            modifier = Modifier
                                  .fillMaxWidth()
                                  .padding(8.dp),
                            horizontalArrangement = Arrangement.SpaceEvenly
                          ) {
                            TextButton(onClick = {
                                cropRect = null
                                isCropMode = false
                              }) {
                                Text("취소")
                              }
                            TextButton(onClick = {
                                cropRect = null
                                isCropMode = false
                              }) {
                                Text("확인")
                              }
                          }
                      }
                  }
              }
          },
        content = { padding ->
            Box(
                modifier = Modifier
                      .padding(padding)
                      .fillMaxSize()
                      .background(Color.Black),
                contentAlignment = Alignment.Center
              ) {
                if (isCropMode && cropRect != null) {
                    CropView(
                        cropEnd = cropEnd,
                        cropRect = cropRect!!,
                        onCropEnd = { cropEnd = it }
                      )
                  } else {
                    FilteredPhotoView(
                        photoUri = photoUri,
                        filter = currentFilter
                      )
                  }
              }
          }
      )
}

@Composable
fun FilterButton(
    label: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        colors = ButtonDefaults.buttonColors(
            containerColor = if (isSelected) MaterialTheme.colorScheme.primary
                          else MaterialTheme.colorScheme.surfaceVariant,
            contentColor = if (isSelected) MaterialTheme.colorScheme.onPrimary
                          else MaterialTheme.colorScheme.onSurfaceVariant
          ),
        shape = RoundedCornerShape(20.dp),
        modifier = Modifier.height(40.dp).padding(horizontal = 4.dp)
      ) {
        Text(label, maxLines = 1, overflow = TextOverflow.Ellipsis)
      }
}

@Composable
fun FilteredPhotoView(
    photoUri: String,
    filter: FilterType
) {
    val context = LocalContext.current

    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
      ) {
        AsyncImage(
            model = ImageRequest.Builder(context).data(photoUri).build(),
            contentDescription = null,
            contentScale = ContentScale.Fit,
            modifier = Modifier.fillMaxSize()
          )
        Canvas(modifier = Modifier.fillMaxSize()) {
            when (filter) {
                FilterType.Grayscale -> {
                    drawRect(
                        Color.Gray.copy(alpha = 0.5f),
                        blendMode = BlendMode.SrcAtop
                      )
                  }
                FilterType.Sepia -> {
                    drawRect(
                        Color(0.79f, 0.73f, 0.63f).copy(alpha = 0.4f),
                        blendMode = BlendMode.SrcAtop
                      )
                  }
                FilterType.Negative -> {
                    drawRect(Color.Black, blendMode = BlendMode.DstOut)
                  }
                FilterType.None -> {}
              }
          }
      }
}

@Composable
fun CropView(
    cropEnd: Offset,
    cropRect: Rect,
    onCropEnd: (Offset) -> Unit
) {
    Box(
        modifier = Modifier
              .fillMaxSize()
              .pointerInput(Unit) {
                detectDragGestures(
                    onDragEnd = {
                        onCropEnd(cropEnd)
                    }
                ) { _, _ -> }
              },
        contentAlignment = Alignment.Center
    ) {
                Canvas(modifier = Modifier.fillMaxSize()) {
                    if (cropRect.width > 10f && cropRect.height > 10f) {
                        drawRect(
                            Color.Black.copy(alpha = 0.7f),
                            topLeft = Offset(0f, 0f),
                            size = Size(size.width, cropRect.top.toFloat())
                        )
                        drawRect(
                            Color.Black.copy(alpha = 0.7f),
                            topLeft = Offset(0f, cropRect.bottom.toFloat()),
                            size = Size(size.width, size.height - cropRect.bottom.toFloat())
                        )
                        drawRect(
                            Color.Black.copy(alpha = 0.7f),
                            topLeft = Offset(0f, cropRect.top.toFloat()),
                            size = Size(cropRect.left.toFloat(), cropRect.height)
                        )
                        drawRect(
                            Color.Black.copy(alpha = 0.7f),
                            topLeft = Offset(cropRect.right.toFloat(), cropRect.top.toFloat()),
                            size = Size(size.width - cropRect.right.toFloat(), cropRect.height)
                        )

                        drawRect(
                            Color.White,
                            topLeft = cropRect.topLeft,
                            size = Size(cropRect.width, cropRect.height),
                            style = Stroke(width = 2f)
                        )
                    }
                }
    }
}
