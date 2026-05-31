package com.example.mypicandpic.data

import android.content.Context
import com.example.mypicandpic.Album
import com.example.mypicandpic.Photo
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.io.File

class JsonFileManager(private val context: Context) {
    private val json = Json { ignoreUnknownKeys = true; prettyPrint = true }
    private val albumsFile = File(context.filesDir, "albums.json")
    private val photosFile = File(context.filesDir, "photos.json")

    fun saveAlbums(albums: List<Album>) {
        albumsFile.writeText(json.encodeToString(albums))
    }

    fun loadAlbums(): List<Album> {
        if (!albumsFile.exists()) return emptyList()
        return try {
            json.decodeFromString<List<Album>>(albumsFile.readText())
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun savePhotos(photos: List<Photo>) {
        photosFile.writeText(json.encodeToString(photos))
    }

    fun loadPhotos(): List<Photo> {
        if (!photosFile.exists()) return emptyList()
        return try {
            json.decodeFromString<List<Photo>>(photosFile.readText())
        } catch (e: Exception) {
            emptyList()
        }
    }
}
