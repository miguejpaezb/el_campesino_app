/**
 * Servicio de datos del dashboard.
 *
 * Obtiene y agrega la información de los lotes activos para alimentar las
 * tarjetas, el gráfico semanal y el resumen del panel de control.
 */
import apiClient from './apiClient.js'

const DAY_NAMES = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

const toISODate = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const formatShortDate = (d) => {
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const y = String(d.getFullYear()).slice(-2)
  return `${day}/${m}/${y}`
}

const buildWeekRange = () => {
  const to = new Date()
  const from = new Date(to)
  from.setDate(to.getDate() - 6)
  return { from, to }
}

const emptyDashboard = (from, to) => ({
  activeLots: 0,
  todayEggs: 0,
  weekTotal: 0,
  layingPercentage: 0,
  mortalityPercentage: 0,
  bestDay: null,
  daily: [],
  dailyBroken: [],
  dailyPercentage: [],
  dailyAverage: [],
  dailyLots: [],
  labels: [],
  dateRangeText: `${formatShortDate(from)} - ${formatShortDate(to)}`,
  hasData: false,
})

export const dashboardService = {
  async getActiveLots() {
    const { data } = await apiClient.get('/lots/', {
      params: { active: true },
    })
    return data
  },

  async getLotProduction(lotId, from, to) {
    const { data } = await apiClient.get(`/lots/${lotId}/production`, {
      params: { from: toISODate(from), to: toISODate(to) },
    })
    return data
  },

  async getLayingPercentage(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/production/percentage`)
    return data.laying_percentage
  },

  async getMortalityStats(lotId) {
    const { data } = await apiClient.get(`/lots/${lotId}/mortality/stats`)
    return data.mortality_percentage
  },

  async getDashboardData() {
    const { from, to } = buildWeekRange()
    let lots
    try {
      lots = await this.getActiveLots()
    } catch {
      return emptyDashboard(from, to)
    }

    if (!lots.length) {
      return emptyDashboard(from, to)
    }

    const todayISO = toISODate(to)

    const perLot = await Promise.all(
      lots.map(async (lot) => {
        let production, laying, mortality
        try {
          ;[production, laying, mortality] = await Promise.all([
            this.getLotProduction(lot.id, from, to),
            this.getLayingPercentage(lot.id),
            this.getMortalityStats(lot.id),
          ])
        } catch {
          return { lot, production: [], laying: 0, mortality: 0 }
        }
        return { lot, production, laying, mortality }
      }),
    )

    const daily = []
    const dailyBroken = []
    const dailyLots = []
    const labels = []
    const cursor = new Date(from)
    while (cursor <= to) {
      const iso = toISODate(cursor)
      labels.push(DAY_NAMES[cursor.getDay()])
      let eggs = 0
      let broken = 0
      let lotsWithRecords = 0
      for (const { production } of perLot) {
        const dayRecords = production.filter(
          (record) => record.collection_date === iso,
        )
        if (dayRecords.length) {
          lotsWithRecords += 1
          eggs += dayRecords.reduce((sum, record) => sum + record.egg_count, 0)
          broken += dayRecords.reduce(
            (sum, record) => sum + record.broken_eggs,
            0,
          )
        }
      }
      daily.push(eggs)
      dailyBroken.push(broken)
      dailyLots.push(lotsWithRecords)
      cursor.setDate(cursor.getDate() + 1)
    }

    const totalBirds = perLot.reduce(
      (acc, { lot }) => acc + (lot.current_quantity || 0),
      0,
    )
    const dailyPercentage = daily.map((eggs) =>
      totalBirds > 0 ? (eggs / totalBirds) * 100 : 0,
    )
    const dailyAverage = daily.map((eggs, index) =>
      dailyLots[index] ? eggs / dailyLots[index] : 0,
    )

    const todayEggs = perLot.reduce(
      (acc, { production }) =>
        acc +
        production
          .filter((record) => record.collection_date === todayISO)
          .reduce((sum, record) => sum + record.egg_count, 0),
      0,
    )

    const weekTotal = daily.reduce((acc, value) => acc + value, 0)
    const maxDaily = Math.max(...daily, 0)
    const bestDay = weekTotal > 0 ? labels[daily.indexOf(maxDaily)] : null
    const layingValues = perLot
      .map(({ laying }) => laying)
      .filter((value) => value > 0)
    const mortalityValues = perLot
      .map(({ mortality }) => mortality)
      .filter((value) => value > 0)

    const layingPercentage =
      layingValues.length > 0
        ? layingValues.reduce((a, b) => a + b, 0) / layingValues.length
        : 0
    const mortalityPercentage =
      mortalityValues.length > 0
        ? mortalityValues.reduce((a, b) => a + b, 0) / mortalityValues.length
        : 0

    return {
      activeLots: lots.length,
      todayEggs,
      weekTotal,
      layingPercentage,
      mortalityPercentage,
      bestDay,
      daily,
      dailyBroken,
      dailyPercentage,
      dailyAverage,
      dailyLots,
      labels,
      dateRangeText: `${formatShortDate(from)} - ${formatShortDate(to)}`,
      hasData: weekTotal > 0,
    }
  },
}

export default dashboardService
