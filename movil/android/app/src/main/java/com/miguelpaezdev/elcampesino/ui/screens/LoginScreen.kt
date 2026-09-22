package com.miguelpaezdev.elcampesino.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.miguelpaezdev.elcampesino.R
import com.miguelpaezdev.elcampesino.data.RetrofitClient
import com.miguelpaezdev.elcampesino.data.dto.LoginRequest
import com.miguelpaezdev.elcampesino.data.dto.UserDto
import com.miguelpaezdev.elcampesino.ui.theme.BrandBrown
import com.miguelpaezdev.elcampesino.ui.theme.BrandGreen
import com.miguelpaezdev.elcampesino.ui.theme.BrandYellow
import com.miguelpaezdev.elcampesino.ui.theme.DangerBackground
import com.miguelpaezdev.elcampesino.ui.theme.DangerBorder
import com.miguelpaezdev.elcampesino.ui.theme.DangerText
import com.miguelpaezdev.elcampesino.ui.theme.InputBorder
import com.miguelpaezdev.elcampesino.ui.theme.PlaceholderText
import com.miguelpaezdev.elcampesino.ui.theme.StatusIdle
import com.miguelpaezdev.elcampesino.ui.theme.StatusOffline
import com.miguelpaezdev.elcampesino.ui.theme.StatusOnline
import com.miguelpaezdev.elcampesino.ui.theme.StatusPillBackground
import java.io.IOException
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

private const val HEALTH_CHECK_INTERVAL_MS = 15000L

@Composable
fun LoginScreen(
    onLoggedIn: (String, UserDto) -> Unit,
    modifier: Modifier = Modifier,
) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var systemOnline by remember { mutableStateOf<Boolean?>(null) }

    val scope = rememberCoroutineScope()

    LaunchedEffect(Unit) {
        while (true) {
            systemOnline = try {
                RetrofitClient.api.health().isSuccessful
            } catch (e: Exception) {
                false
            }
            delay(HEALTH_CHECK_INTERVAL_MS)
        }
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .systemBarsPadding()
                .imePadding()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 28.dp, vertical = 24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Spacer(modifier = Modifier.height(40.dp))

            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Icon(
                    painter = painterResource(R.drawable.ic_pluma),
                    contentDescription = null,
                    tint = Color.Unspecified,
                    modifier = Modifier.size(56.dp),
                )
                Text(
                    text = "El Campesino",
                    color = BrandBrown,
                    fontSize = 32.sp,
                    fontWeight = FontWeight.SemiBold,
                )
            }

            Spacer(modifier = Modifier.height(40.dp))

            Column(
                modifier = Modifier
                    .widthIn(max = 420.dp)
                    .fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Text(
                    text = "Iniciar Sesión",
                    color = BrandBrown,
                    fontSize = 24.sp,
                    fontWeight = FontWeight.SemiBold,
                )

                if (error != null) {
                    ErrorAlert(message = error.orEmpty())
                }

                LoginField(
                    value = username,
                    onValueChange = { username = it },
                    placeholder = "Nombre de Usuario",
                    enabled = !loading,
                    keyboardType = KeyboardType.Text,
                    isPassword = false,
                )

                LoginField(
                    value = password,
                    onValueChange = { password = it },
                    placeholder = "Contraseña",
                    enabled = !loading,
                    keyboardType = KeyboardType.Password,
                    isPassword = true,
                )

                Button(
                    onClick = {
                        error = null
                        loading = true
                        scope.launch {
                            try {
                                val login = RetrofitClient.unwrap(
                                    RetrofitClient.api.login(
                                        LoginRequest(username.trim(), password),
                                    ),
                                )
                                val user = RetrofitClient.unwrap(
                                    RetrofitClient.api.getMe(
                                        RetrofitClient.bearer(login.accessToken),
                                    ),
                                )
                                onLoggedIn(login.accessToken, user)
                            } catch (e: Exception) {
                                error = when (e) {
                                    is IOException -> e.message
                                    else -> "No se pudo iniciar sesión"
                                }
                            } finally {
                                loading = false
                            }
                        }
                    },
                    enabled = !loading && username.isNotBlank() && password.isNotBlank(),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = BrandYellow,
                        contentColor = Color.Black,
                        disabledContainerColor = BrandYellow.copy(alpha = 0.65f),
                        disabledContentColor = Color.Black,
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                ) {
                    if (loading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(22.dp),
                            color = Color.Black,
                            strokeWidth = 2.dp,
                        )
                    } else {
                        Text(
                            text = "Ingresar",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                    }
                }

                Text(
                    text = "Olvidé mi contraseña",
                    color = Color.Black,
                    fontSize = 14.sp,
                    modifier = Modifier
                        .align(Alignment.CenterHorizontally)
                        .clickable { },
                )
            }

            Spacer(modifier = Modifier.height(32.dp))

            SystemStatusPill(systemOnline = systemOnline)
        }
    }
}

@Composable
private fun LoginField(
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    enabled: Boolean,
    keyboardType: KeyboardType,
    isPassword: Boolean,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        placeholder = {
            Text(
                text = placeholder,
                color = PlaceholderText,
                fontSize = 16.sp,
            )
        },
        singleLine = true,
        enabled = enabled,
        shape = RoundedCornerShape(10.dp),
        visualTransformation = if (isPassword) {
            PasswordVisualTransformation()
        } else {
            VisualTransformation.None
        },
        keyboardOptions = KeyboardOptions(keyboardType = keyboardType),
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = BrandGreen,
            unfocusedBorderColor = InputBorder,
            disabledBorderColor = InputBorder,
            focusedContainerColor = Color.White,
            unfocusedContainerColor = Color.White,
            disabledContainerColor = Color.White,
            cursorColor = BrandGreen,
        ),
        modifier = Modifier.fillMaxWidth(),
    )
}

@Composable
private fun ErrorAlert(message: String) {
    Text(
        text = message,
        color = DangerText,
        fontSize = 14.sp,
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(6.dp))
            .background(DangerBackground)
            .border(1.dp, DangerBorder, RoundedCornerShape(6.dp))
            .padding(horizontal = 16.dp, vertical = 12.dp),
    )
}

@Composable
private fun SystemStatusPill(systemOnline: Boolean?) {
    val dotColor = when (systemOnline) {
        null -> StatusIdle
        true -> StatusOnline
        false -> StatusOffline
    }
    val label = when (systemOnline) {
        null -> "Verificando..."
        true -> "Óptimo"
        false -> "Sin conexión"
    }

    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp),
        modifier = Modifier
            .clip(RoundedCornerShape(20.dp))
            .background(StatusPillBackground)
            .padding(horizontal = 10.dp, vertical = 6.dp),
    ) {
        Box(
            modifier = Modifier
                .size(10.dp)
                .clip(CircleShape)
                .background(dotColor),
        )
        Text(
            text = "Estado del sistema: $label",
            color = Color.Black,
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold,
        )
    }
}
