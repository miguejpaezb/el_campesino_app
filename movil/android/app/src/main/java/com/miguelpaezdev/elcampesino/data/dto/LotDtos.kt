package com.miguelpaezdev.elcampesino.data.dto

import com.google.gson.annotations.SerializedName

data class LotDto(
    val id: Int,
    @SerializedName("lot_code") val lotCode: String,
    val breed: String,
    @SerializedName("initial_quantity") val initialQuantity: Int,
    @SerializedName("current_quantity") val currentQuantity: Int,
    @SerializedName("current_week") val currentWeek: Int,
    @SerializedName("entry_date") val entryDate: String,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("discard_reason") val discardReason: String?,
    val observations: String?,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String,
)

data class LotCreateRequest(
    @SerializedName("lot_code") val lotCode: String,
    val breed: String,
    @SerializedName("initial_quantity") val initialQuantity: Int,
    @SerializedName("entry_date") val entryDate: String?,
    val observations: String?,
)

data class LotUpdateRequest(
    val breed: String,
    val observations: String?,
)

data class LotDiscardRequest(
    val reason: String,
)

data class EvaluateResultDto(
    val message: String,
    @SerializedName("is_active") val isActive: Boolean,
)

data class LotSummaryDto(
    val id: Int,
    @SerializedName("lot_code") val lotCode: String,
    val breed: String,
    @SerializedName("current_week") val currentWeek: Int,
    @SerializedName("initial_quantity") val initialQuantity: Int,
    @SerializedName("current_quantity") val currentQuantity: Int,
    @SerializedName("total_eggs") val totalEggs: Int,
    @SerializedName("average_weekly_production") val averageWeeklyProduction: Double,
    @SerializedName("laying_percentage") val layingPercentage: Double,
    @SerializedName("total_feed") val totalFeed: Double,
    @SerializedName("total_mortality") val totalMortality: Int,
    @SerializedName("mortality_percentage") val mortalityPercentage: Double,
    @SerializedName("survival_percentage") val survivalPercentage: Double,
    @SerializedName("vaccination_count") val vaccinationCount: Int,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("discard_reason") val discardReason: String?,
)
