package com.example.mypicandpic

import kotlinx.serialization.Serializable
import java.util.UUID

@Serializable
data class Photo(
    val id: String = UUID.randomUUID().toString(),
    val uri: String,
    val name: String,
    val date: Long,
    val size: Long
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as Photo
        return id == other.id
    }

    override fun hashCode(): Int {
        return id.hashCode()
    }
}
