package com.example.mypicandpic

import kotlinx.serialization.Serializable
import java.util.UUID

@Serializable
data class Album(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val photoIds: List<String> = emptyList(),
    val createdAt: Long = System.currentTimeMillis()
)
