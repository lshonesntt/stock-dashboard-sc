package com.example.mypicandpic.viewmodel

import android.app.Application
import android.content.ContentUris
import android.provider.MediaStore
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.mypicandpic.Album
import com.example.mypicandpic.Photo
import com.example.mypicandpic.data.DataStoreHelper
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class AlbumViewModel(application: Application) : AndroidViewModel(application) {

    private val helper = DataStoreHelper(application)
    private val _albums = MutableStateFlow(emptyList<Album>())
    private val _photos = MutableStateFlow(emptyList<Photo>())
    private val _selectedPhotos = MutableStateFlow(emptyList<Photo>())

    val albums: StateFlow<List<Album>> = _albums.asStateFlow()
    val photos: StateFlow<List<Photo>> = _photos.asStateFlow()
    val selectedPhotos: StateFlow<List<Photo>> = _selectedPhotos.asStateFlow()

    init {
        loadAlbums()
        loadPhotos()
    }

    fun loadAlbums() {
        viewModelScope.launch {
            _albums.value = helper.readAlbums()
        }
    }

    fun loadPhotos() {
        viewModelScope.launch {
            _photos.value = helper.readPhotos()
        }
    }

    fun addAlbum(name: String) {
        viewModelScope.launch {
            helper.addAlbum(name)
            loadAlbums()
        }
    }

    fun deleteAlbum(albumId: String) {
        viewModelScope.launch {
            helper.deleteAlbum(albumId)
            loadAlbums()
        }
    }

    fun renameAlbum(albumId: String, newName: String) {
        viewModelScope.launch {
            helper.renameAlbum(albumId, newName)
            loadAlbums()
        }
    }

    fun addPhotoToAlbum(albumId: String, photoUri: String, photoName: String, photoSize: Long = 0L) {
        viewModelScope.launch {
            val photo = Photo(
                uri = photoUri,
                name = photoName,
                date = System.currentTimeMillis(),
                size = photoSize
             )
            helper.addPhotoToAlbum(albumId, photo)
            loadPhotos()
            loadAlbums()
           }
       }

    fun removePhotoFromAlbum(albumId: String, photoId: String) {
        viewModelScope.launch {
            helper.removePhotoFromAlbum(albumId, photoId)
            loadAlbums()
            loadPhotos()
         }
      }

    fun selectPhoto(photo: Photo) {
        viewModelScope.launch {
            val current = _selectedPhotos.value.toMutableList()
            if (current.contains(photo)) {
                current.remove(photo)
             } else {
                current.add(photo)
             }
            _selectedPhotos.value = current
        }
    }

    fun clearSelected() {
        viewModelScope.launch {
            _selectedPhotos.value = emptyList()
        }
    }

    fun getPhotosByAlbum(albumId: String): List<Photo> {
        val album = helper.getAlbumWithPhotos(albumId)
        return if (album != null) {
            _photos.value.filter { it.id in album.photoIds }
         } else emptyList()
    }

    fun scanDevicePhotos(): List<Photo> {
        val app = getApplication<Application>()
        val resolver = app.contentResolver
        val collection = MediaStore.Images.Media.EXTERNAL_CONTENT_URI
        val projection = arrayOf(
            MediaStore.Images.Media._ID,
            MediaStore.Images.Media.DISPLAY_NAME,
            MediaStore.Images.Media.DATE_ADDED,
            MediaStore.Images.Media.SIZE
         )
        val photos = mutableListOf<Photo>()

        try {
            resolver.query(collection, projection, null, null, "${MediaStore.Images.Media.DATE_ADDED} DESC LIMIT 100")?.use { cursor ->
                val idCol = cursor.getColumnIndex(MediaStore.Images.Media._ID)
                val nameCol = cursor.getColumnIndex(MediaStore.Images.Media.DISPLAY_NAME)
                val dateCol = cursor.getColumnIndex(MediaStore.Images.Media.DATE_ADDED)
                val sizeCol = cursor.getColumnIndex(MediaStore.Images.Media.SIZE)

                while (cursor.moveToNext()) {
                    val id = cursor.getLong(idCol)
                    val name = cursor.getString(nameCol) ?: ""
                    val date = cursor.getLong(dateCol) * 1000
                    val size = cursor.getLong(sizeCol)

                    val uri = ContentUris.withAppendedId(collection, id)
                    photos.add(Photo(
                        uri = uri.toString(),
                        name = name,
                        date = date,
                        size = size
                     ))
                 }
             }
         } catch (e: Exception) {
            e.printStackTrace()
         }

        return photos
    }
}
