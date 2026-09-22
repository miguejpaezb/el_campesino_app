package com.miguelpaezdev.elcampesino.data

import com.google.gson.Gson
import com.miguelpaezdev.elcampesino.BuildConfig
import com.miguelpaezdev.elcampesino.data.dto.ErrorResponse
import java.io.IOException
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {

    private const val BASE_URL = "https://elcampesino.gvs.lat/api/v1/"

    private val gson = Gson()

    private val okHttpClient: OkHttpClient by lazy {
        val builder = OkHttpClient.Builder()
        if (BuildConfig.DEBUG) {
            val logging = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            builder.addInterceptor(logging)
        }
        builder.build()
    }

    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }

    val api: ApiService by lazy { retrofit.create(ApiService::class.java) }

    fun bearer(token: String): String = "Bearer $token"

    fun <T> unwrap(response: Response<T>): T {
        if (response.isSuccessful) {
            val body = response.body()
            if (body != null) return body
            throw IOException("Respuesta vacía del servidor")
        }
        val errorBody = response.errorBody()?.string()
        val detail = runCatching {
            gson.fromJson(errorBody, ErrorResponse::class.java)?.detail
        }.getOrNull().orEmpty().ifEmpty { "Error HTTP ${response.code()}" }
        throw IOException(detail)
    }
}
