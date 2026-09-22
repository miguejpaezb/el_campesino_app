package com.miguelpaezdev.elcampesino.data

import com.miguelpaezdev.elcampesino.data.dto.EvaluateResultDto
import com.miguelpaezdev.elcampesino.data.dto.HealthDto
import com.miguelpaezdev.elcampesino.data.dto.LoginRequest
import com.miguelpaezdev.elcampesino.data.dto.LoginResponse
import com.miguelpaezdev.elcampesino.data.dto.LotCreateRequest
import com.miguelpaezdev.elcampesino.data.dto.LotDiscardRequest
import com.miguelpaezdev.elcampesino.data.dto.LotDto
import com.miguelpaezdev.elcampesino.data.dto.LotSummaryDto
import com.miguelpaezdev.elcampesino.data.dto.LotUpdateRequest
import com.miguelpaezdev.elcampesino.data.dto.UserDto
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.HTTP
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path

interface ApiService {

    @GET("health")
    suspend fun health(): Response<HealthDto>

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @GET("auth/me")
    suspend fun getMe(@Header("Authorization") bearerToken: String): Response<UserDto>

    @GET("lots/")
    suspend fun getLots(): Response<List<LotDto>>

    @POST("lots/")
    suspend fun createLot(@Body request: LotCreateRequest): Response<LotDto>

    @PUT("lots/{id}")
    suspend fun updateLot(
        @Path("id") id: Int,
        @Body request: LotUpdateRequest,
    ): Response<LotDto>

    @HTTP(method = "DELETE", path = "lots/{id}", hasBody = true)
    suspend fun discardLot(
        @Path("id") id: Int,
        @Body request: LotDiscardRequest,
    ): Response<LotDto>

    @POST("lots/{id}/advance-week")
    suspend fun advanceWeek(@Path("id") id: Int): Response<LotDto>

    @POST("lots/{id}/evaluate")
    suspend fun evaluateLot(@Path("id") id: Int): Response<EvaluateResultDto>

    @GET("lots/{id}/summary")
    suspend fun getLotSummary(@Path("id") id: Int): Response<LotSummaryDto>
}
