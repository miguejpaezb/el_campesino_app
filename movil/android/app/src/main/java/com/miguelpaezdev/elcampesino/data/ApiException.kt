package com.miguelpaezdev.elcampesino.data

class ApiException(
    val statusCode: Int,
    message: String,
) : Exception(message)
