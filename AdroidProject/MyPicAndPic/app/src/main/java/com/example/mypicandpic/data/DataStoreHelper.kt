package com.example.mypicandpic.data

import android.content.Context
import android.util.Log
import com.example.mypicandpic.Album
import com.example.mypicandpic.Photo
import kotlinx.serialization.json.Json
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import java.io.File

class DataStoreHelper(private val context: Context) {

    companion object {
        private const val TAG = "DataStoreHelper"
        private const val ALBUMS_FILE = "albums.json"
        private const val PHOTOS_FILE = "photos.json"
    }

    private val json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    }

    fun readAlbums(): List<Album> {
        return try {
            val file = File(context.filesDir, ALBUMS_FILE)
            if (file.exists()) {
                val content = file.readText()
                json.decodeFromString<List<Album>>(content)
            } else {
                emptyList()
            }
        } catch (e: Exception) {
            Log.e(TAG, "readAlbums error", e)
            emptyList()
        }
    }

    fun writeAlbums(albums: List<Album>) {
        try {
            val file = File(context.filesDir, ALBUMS_FILE)
            file.writeText(json.encodeToString(albums))
        } catch (e: Exception) {
            Log.e(TAG, "writeAlbums error", e)
        }
    }

    fun readPhotos(): List<Photo> {
        return try {
            val file = File(context.filesDir, PHOTOS_FILE)
            if (file.exists()) {
                val content = file.readText()
                json.decodeFromString<List<Photo>>(content)
            } else {
                emptyList()
            }
        } catch (e: Exception) {
            Log.e(TAG, "readPhotos error", e)
            emptyList()
        }
    }

    fun writePhotos(photos: List<Photo>) {
        try {
            val file = File(context.filesDir, PHOTOS_FILE)
            file.writeText(json.encodeToString(photos))
        } catch (e: Exception) {
            Log.e(TAG, "writePhotos error", e)
        }
    }

    fun addAlbum(name: String): Album {
        val albums = readAlbums().toMutableList()
        val newAlbum = Album(name = name)
        albums.add(newAlbum)
        writeAlbums(albums)
        return newAlbum
    }

    fun deleteAlbum(albumId: String) {
        val albums = readAlbums().filter { it.id != albumId }
        writeAlbums(albums)
    }

    fun renameAlbum(albumId: String, newName: String) {
        val albums = readAlbums().map {
            if (it.id == albumId) it.copy(name = newName) else it
        }
        writeAlbums(albums)
    }

    fun addPhotoToAlbum(albumId: String, photo: Photo) {
        val albums = readAlbums().map { album ->
            if (album.id == albumId) {
                album.copy(photoIds = album.photoIds + photo.id)
             } else album
          }.toMutableList()
        writeAlbums(albums)

        val photos = readPhotos().toMutableList()
        if (photos.none { it.id == photo.id }) {
            photos.add(photo)
            writePhotos(photos)
         }
     }

    fun removePhotoFromAlbum(albumId: String, photoId: String) {
        val albums = readAlbums().map { album ->
            if (album.id == albumId) {
                album.copy(photoIds = album.photoIds.filter { it != photoId })
            } else album
        }
        writeAlbums(albums)

        val photos = readPhotos().filter { it.id != photoId }
        if (photos.size < readPhotos().size) {
            writePhotos(photos)
        }
    }

    fun getAlbumWithPhotos(albumId: String): Album? {
        val albums = readAlbums()
        return albums.find { it.id == albumId }
    }

    fun getPhotoById(photoId: String): Photo? {
        return readPhotos().find { it.id == photoId }
    }
}
