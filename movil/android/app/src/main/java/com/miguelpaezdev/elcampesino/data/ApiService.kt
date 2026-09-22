package com.miguelpaezdev.elcampesino.data

import com.miguelpaezdev.elcampesino.data.dto.LoginRequest
import com.miguelpaezdev.elcampesino.data.dto.LoginResponse
import com.miguelpaezdev.elcampesino.data.dto.UserDto
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST

interface ApiService {

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @GET("auth/me")
    suspend fun getMe(@Header("Authorization") bearerToken: String): Response<UserDto>
}
