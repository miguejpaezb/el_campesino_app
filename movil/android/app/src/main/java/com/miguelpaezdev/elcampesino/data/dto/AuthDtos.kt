package com.miguelpaezdev.elcampesino.data.dto

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    val username: String,
    val password: String,
)

data class LoginResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("token_type")
    val tokenType: String,
)

data class UserDto(
    val id: Int,
    val username: String,
    val email: String,
    @SerializedName("full_name")
    val fullName: String,
    val role: String,
    @SerializedName("is_active")
    val isActive: Boolean,
)

data class ErrorResponse(
    val detail: String? = null,
)
