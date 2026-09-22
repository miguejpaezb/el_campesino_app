package com.miguelpaezdev.elcampesino

import android.app.Application
import com.miguelpaezdev.elcampesino.data.session.SessionManager

class ElCampesinoApp : Application() {

    lateinit var session: SessionManager
        private set

    override fun onCreate() {
        super.onCreate()
        session = SessionManager(this)
    }
}
