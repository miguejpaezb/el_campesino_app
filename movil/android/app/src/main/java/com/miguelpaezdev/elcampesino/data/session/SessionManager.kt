package com.miguelpaezdev.elcampesino.data.session

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.google.gson.Gson
import com.miguelpaezdev.elcampesino.data.dto.UserDto
import kotlinx.coroutines.flow.first

private val Context.sessionDataStore: DataStore<Preferences> by preferencesDataStore(
    name = "session",
)

class SessionManager(context: Context) {

    private val dataStore = context.applicationContext.sessionDataStore
    private val gson = Gson()

    suspend fun getToken(): String? = dataStore.data.first()[TOKEN_KEY]

    suspend fun getUser(): UserDto? {
        val json = dataStore.data.first()[USER_KEY] ?: return null
        return runCatching { gson.fromJson(json, UserDto::class.java) }.getOrNull()
    }

    suspend fun save(token: String, user: UserDto) {
        dataStore.edit { prefs ->
            prefs[TOKEN_KEY] = token
            prefs[USER_KEY] = gson.toJson(user)
        }
    }

    suspend fun clear() {
        dataStore.edit { prefs -> prefs.clear() }
    }

    private companion object {
        val TOKEN_KEY = stringPreferencesKey("access_token")
        val USER_KEY = stringPreferencesKey("user_json")
    }
}
