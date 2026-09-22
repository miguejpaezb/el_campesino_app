/**
 * Página del módulo de producción diaria.
 *
 * Permite seleccionar un lote, consultar sus indicadores (total, promedio
 * semanal, porcentaje de postura y producción del día), visualizar la
 * producción en un gráfico por rango de fechas y registrar recolecciones.
 * Si una recolección coincide en fecha y hora con una existente, se ofrece
 * sumar las cantidades (merge) previa confirmación.
 *
 * @returns {JSX.Element} Página de producción diaria.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Chart } from 'chart.js/auto'
import Modal from '../components/Modal.jsx'
import PageHeader from '../components/PageHeader.jsx'
import Toast from '../components/Toast.jsx'
import lotService from '../services/lotService.js'
import productionService from '../services/productionService.js'
import { getErrorMessage } from '../utils/errors.js'
import './ProductionPage.css'

const TOAST_DURATION = 4000
const COLORS = {
  line: '#9e6b34',
  bar: 'rgba(158, 107, 52, 0.75)',
  barHover: '#9e6b34',
  grid: 'rgba(0, 0, 0, 0.05)',
  text: '#666',
}

const pad = (n) => String(n).padStart(2, '0')

const toISODate = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const formatShortDate = (iso) => {
  if (!iso) return ''
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y.slice(-2)}`
}

const formatTime = (value) => {
  if (!value) return '—'
  return typeof value === 'string' ? value.slice(0, 5) : String(value)
}

const nowTime = () => {
  const d = new Date()
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const toApiTime = (value) => (value ? `${value}:00` : null)

const todayISO = () => toISODate(new Date())

const yesterdayISO = () => {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return toISODate(d)
}

const timeToMinutes = (value) => {
  if (!value) return null
  const [h, m] = value.split(':').map(Number)
  if (Number.isNaN(h) || Number.isNaN(m)) return null
  return h * 60 + m
}

const sortByTime = (a, b) => {
  const ta = timeToMinutes(a.collection_time)
  const tb = timeToMinutes(b.collection_time)
  if (ta === tb) return 0
  if (ta === null) return 1
  if (tb === null) return -1
  return ta - tb
}

function ProductionPage() {
  const [lots, setLots] = useState([])
  const [lotInput, setLotInput] = useState('')
  const [selectedLot, setSelectedLot] = useState(null)
  const [suggestionsOpen, setSuggestionsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const [loadingLots, setLoadingLots] = useState(true)
  const [metrics, setMetrics] = useState({
    total: 0,
    average: 0,
    percentage: 0,
  })
  const [todayEggs, setTodayEggs] = useState(0)
  const [records, setRecords] = useState(null)
  const [fromDate, setFromDate] = useState(todayISO())
  const [toDate, setToDate] = useState(todayISO())
  const [form, setForm] = useState({
    egg_count: '',
    broken_eggs: '',
    collection_date: todayISO(),
    collection_time: nowTime(),
    observations: '',
  })
  const [formErrors, setFormErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [mergeConflict, setMergeConflict] = useState(null)
  const [cardIndex, setCardIndex] = useState(0)
  const [toasts, setToasts] = useState([])
  const cardsRef = useRef(null)
  const canvasRef = useRef(null)
  const chartRef = useRef(null)
  const toastIdRef = useRef(0)
  const toastTimeoutsRef = useRef([])

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const pushToast = useCallback(
    (type, message) => {
      const id = ++toastIdRef.current
      setToasts((prev) => [...prev, { id, type, message }])
      const timeout = setTimeout(() => dismissToast(id), TOAST_DURATION)
      toastTimeoutsRef.current.push(timeout)
    },
    [dismissToast],
  )

  useEffect(() => {
    const timeouts = toastTimeoutsRef.current
    return () => timeouts.forEach((timeout) => clearTimeout(timeout))
  }, [])

  useEffect(() => {
    let mounted = true
    lotService
      .getLots()
      .then((data) => {
        if (!mounted) return
        setLots(data)
        const first = data[0]
        if (first) {
          setLotInput(first.lot_code)
          setSelectedLot(first)
        }
      })
      .catch((error) => {
        if (mounted) {
          pushToast(
            'error',
            getErrorMessage(error, 'No se pudieron cargar los lotes'),
          )
        }
      })
      .finally(() => {
        if (mounted) setLoadingLots(false)
      })
    return () => {
      mounted = false
    }
  }, [pushToast])

  const fetchProductionData = useCallback(async (lot, from, to) => {
    const [total, average, percentage, todayRecords, rangeRecords] =
      await Promise.all([
        productionService.getTotal(lot.id),
        productionService.getAverage(lot.id),
        productionService.getPercentage(lot.id),
        productionService.getProduction(lot.id, todayISO(), todayISO()),
        productionService.getProduction(lot.id, from, to),
      ])
    return {
      metrics: { total, average, percentage },
      todayEggs: todayRecords.reduce(
        (acc, record) => acc + record.egg_count,
        0,
      ),
      records: rangeRecords,
    }
  }, [])

  useEffect(() => {
    if (!selectedLot) return
    let active = true
    fetchProductionData(selectedLot, fromDate, toDate)
      .then((result) => {
        if (!active) return
        setMetrics(result.metrics)
        setTodayEggs(result.todayEggs)
        setRecords(result.records)
      })
      .catch((error) => {
        if (!active) return
        pushToast(
          'error',
          getErrorMessage(error, 'No se pudieron cargar los datos del lote'),
        )
        setRecords([])
      })
    return () => {
      active = false
    }
  }, [selectedLot, fromDate, toDate, fetchProductionData, pushToast])

  const refreshData = useCallback(async () => {
    if (!selectedLot) return
    try {
      const result = await fetchProductionData(selectedLot, fromDate, toDate)
      setMetrics(result.metrics)
      setTodayEggs(result.todayEggs)
      setRecords(result.records)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudieron actualizar los datos'),
      )
    }
  }, [selectedLot, fromDate, toDate, fetchProductionData, pushToast])

  const lotSuggestions = lots.filter((lot) =>
    lot.lot_code.toLowerCase().includes(lotInput.trim().toLowerCase()),
  )

  const clearLotData = () => {
    setSelectedLot(null)
    setMetrics({ total: 0, average: 0, percentage: 0 })
    setTodayEggs(0)
    setRecords([])
  }

  const selectLot = (lot) => {
    setLotInput(lot.lot_code)
    setSelectedLot(lot)
    setSuggestionsOpen(false)
    setActiveIndex(-1)
  }

  const handleLotInput = (event) => {
    const value = event.target.value
    setLotInput(value)
    setActiveIndex(-1)
    const lot = lots.find((item) => item.lot_code === value)
    if (lot) {
      setSelectedLot(lot)
      setSuggestionsOpen(true)
    } else {
      clearLotData()
    }
  }

  const handleLotFocus = () => {
    setSuggestionsOpen(true)
  }

  const handleLotBlur = () => {
    setTimeout(() => {
      setSuggestionsOpen(false)
      setActiveIndex(-1)
    }, 120)
  }

  const handleLotKeyDown = (event) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setSuggestionsOpen(true)
      setActiveIndex((prev) => Math.min(prev + 1, lotSuggestions.length - 1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((prev) => Math.max(prev - 1, -1))
    } else if (event.key === 'Enter') {
      if (suggestionsOpen && activeIndex >= 0 && lotSuggestions[activeIndex]) {
        event.preventDefault()
        selectLot(lotSuggestions[activeIndex])
      }
    } else if (event.key === 'Escape') {
      setSuggestionsOpen(false)
      setActiveIndex(-1)
    }
  }

  const setField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    setFormErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const validateForm = () => {
    const next = {}
    const egg = Number(form.egg_count)
    const broken = Number(form.broken_eggs)

    if (form.egg_count === '' || !Number.isInteger(egg) || egg < 0) {
      next.egg_count = 'Ingresa una cantidad mayor o igual a 0'
    }
    if (form.broken_eggs === '' || !Number.isInteger(broken) || broken < 0) {
      next.broken_eggs = 'Ingresa una cantidad mayor o igual a 0'
    }
    if (
      (egg === 0 || Number.isNaN(egg)) &&
      (broken === 0 || Number.isNaN(broken))
    ) {
      next.broken_eggs = 'Al menos una de las cantidades debe ser mayor a 0'
    }
    if (!form.collection_date) {
      next.collection_date = 'La fecha es obligatoria'
    } else if (form.collection_date > todayISO()) {
      next.collection_date = 'La fecha no puede ser futura'
    } else if (form.collection_date < yesterdayISO()) {
      next.collection_date = 'La fecha no puede ser anterior al día previo'
    }
    if (!form.collection_time) {
      next.collection_time = 'La hora es obligatoria'
    } else if (
      form.collection_date === todayISO() &&
      timeToMinutes(form.collection_time) > timeToMinutes(nowTime())
    ) {
      next.collection_time = 'La hora no puede ser futura'
    }
    setFormErrors(next)
    return Object.keys(next).length === 0
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!selectedLot) {
      pushToast('error', 'Selecciona un lote para registrar la producción.')
      return
    }
    if (!validateForm()) return
    setSubmitting(true)
    const payload = {
      egg_count: Number(form.egg_count),
      broken_eggs: Number(form.broken_eggs),
      collection_date: form.collection_date,
      collection_time: toApiTime(form.collection_time),
      observations: form.observations.trim() || null,
    }
    try {
      await productionService.registerProduction(selectedLot.id, payload)
      pushToast('success', 'Producción registrada correctamente.')
      resetForm()
      await refreshData()
    } catch (error) {
      if (error.response?.status === 409) {
        setMergeConflict({
          existing: error.response.data?.detail?.existing,
          payload,
        })
      } else {
        pushToast(
          'error',
          getErrorMessage(error, 'No se pudo registrar la producción'),
        )
      }
    } finally {
      setSubmitting(false)
    }
  }

  const handleMergeConfirm = async () => {
    if (!selectedLot || !mergeConflict) return
    setSubmitting(true)
    try {
      await productionService.mergeProduction(
        selectedLot.id,
        mergeConflict.payload,
      )
      pushToast('success', 'Cantidades sumadas al registro existente.')
      setMergeConflict(null)
      resetForm()
      await refreshData()
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo actualizar el registro'),
      )
    } finally {
      setSubmitting(false)
    }
  }

  const resetForm = () => {
    setForm({
      egg_count: '',
      broken_eggs: '',
      collection_date: todayISO(),
      collection_time: nowTime(),
      observations: '',
    })
    setFormErrors({})
  }

  const handleClear = () => {
    if (selectedLot) {
      setLotInput(selectedLot.lot_code)
    }
    resetForm()
  }

  const singleDay = fromDate === toDate

  const chartData = useMemo(() => {
    if (!selectedLot || !records) return null
    const maxPerDay = selectedLot.current_quantity || 0

    if (singleDay) {
      const dayRecords = records
        .filter((record) => record.collection_date === fromDate)
        .slice()
        .sort(sortByTime)
      let cumulative = 0
      const labels = []
      const data = []
      const meta = []
      for (const record of dayRecords) {
        cumulative += record.egg_count
        labels.push(formatTime(record.collection_time))
        data.push(cumulative)
        meta.push({
          ...record,
          before: cumulative - record.egg_count,
          total: cumulative,
        })
      }
      return {
        type: 'line',
        labels,
        data,
        meta,
        single: true,
        max: maxPerDay,
      }
    }

    const labels = []
    const data = []
    const meta = []
    const cursor = new Date(`${fromDate}T00:00:00`)
    const end = new Date(`${toDate}T00:00:00`)
    while (cursor <= end) {
      const iso = toISODate(cursor)
      const dayRecords = records.filter(
        (record) => record.collection_date === iso,
      )
      const eggs = dayRecords.reduce((acc, record) => acc + record.egg_count, 0)
      const broken = dayRecords.reduce(
        (acc, record) => acc + record.broken_eggs,
        0,
      )
      const sorted = dayRecords.slice().sort(sortByTime)
      const first = sorted[0]?.collection_time || null
      const last = sorted[sorted.length - 1]?.collection_time || null
      const percentage = maxPerDay ? (eggs / maxPerDay) * 100 : 0
      const average = dayRecords.length ? eggs / dayRecords.length : 0
      labels.push(formatShortDate(iso))
      data.push(eggs)
      meta.push({
        iso,
        eggs,
        broken,
        first,
        last,
        percentage,
        average,
        records: dayRecords.length,
      })
      cursor.setDate(cursor.getDate() + 1)
    }
    return { type: 'bar', labels, data, meta, single: false, max: maxPerDay }
  }, [records, fromDate, toDate, selectedLot, singleDay])

  useEffect(() => {
    if (!canvasRef.current || !chartData) return
    chartRef.current?.destroy()

    const tooltipLines = (ctx) => {
      const meta = chartData.meta[ctx.dataIndex]
      if (!meta) return ''
      if (chartData.single) {
        return [
          `Hora: ${formatTime(meta.collection_time)}`,
          `Antes: ${meta.before} huevos`,
          `Recolectados: ${meta.egg_count}`,
          `Total actual: ${meta.total}`,
          `No aptos: ${meta.broken_eggs}`,
          `Comentario: ${meta.observations || '—'}`,
        ]
      }
      return [
        `Primer registro: ${formatTime(meta.first)}`,
        `Último registro: ${formatTime(meta.last)}`,
        `Huevos recolectados: ${meta.eggs}`,
        `No aptos: ${meta.broken}`,
        `Postura del día: ${meta.percentage.toFixed(1)}%`,
        `Promedio de postura: ${meta.average.toFixed(1)}`,
      ]
    }

    chartRef.current = new Chart(canvasRef.current, {
      type: chartData.single ? 'line' : 'bar',
      data: {
        labels: chartData.labels,
        datasets: [
          {
            label: chartData.single ? 'Huevos acumulados' : 'Huevos por día',
            data: chartData.data,
            borderColor: COLORS.line,
            backgroundColor: chartData.single
              ? 'rgba(158, 107, 52, 0.08)'
              : COLORS.bar,
            borderWidth: 2,
            pointRadius: chartData.single ? 4 : 0,
            pointHoverRadius: 5,
            pointBackgroundColor: COLORS.line,
            borderRadius: 8,
            borderSkipped: false,
            maxBarThickness: 32,
            stepped: false,
            tension: chartData.single ? 0.4 : 0.2,
            cubicInterpolationMode: chartData.single ? 'monotone' : undefined,
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: {
          intersect: false,
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: { label: tooltipLines },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            suggestedMax: chartData.single ? chartData.max : undefined,
            grid: { color: COLORS.grid },
            ticks: { color: COLORS.text, maxTicksLimit: 6 },
          },
          x: {
            grid: { display: false },
            ticks: { color: COLORS.text, maxTicksLimit: 10 },
          },
        },
      },
    })

    return () => {
      chartRef.current?.destroy()
    }
  }, [chartData])

  const handleCardsScroll = (event) => {
    if (window.innerWidth > 768) return
    const next = Math.round(
      event.currentTarget.scrollLeft / event.currentTarget.offsetWidth,
    )
    if (next !== cardIndex) setCardIndex(next)
  }

  const goToCard = (index) => {
    if (!cardsRef.current) return
    cardsRef.current.scrollLeft = index * cardsRef.current.offsetWidth
    setCardIndex(index)
  }

  const cards = useMemo(
    () => [
      {
        label: 'Producción total del lote',
        value: metrics.total,
        sub: selectedLot?.lot_code || 'Sin lote',
        icon: 'PRODUCCION_DIARIA.svg',
        alt: 'Producción total',
        theme: 'primary',
      },
      {
        label: 'Promedio de postura semanal',
        value: metrics.average.toFixed(2),
        sub: 'Huevos por día',
        icon: 'TRAZABILIDAD.svg',
        alt: 'Promedio semanal',
        theme: 'success',
      },
      {
        label: 'Porcentaje de postura del lote',
        value: `${metrics.percentage.toFixed(1)}%`,
        sub: 'Del total registrado',
        icon: 'MONITOREO_IOT.svg',
        alt: 'Porcentaje de postura',
        theme: 'warning',
      },
      {
        label: 'Producción actual del día',
        value: todayEggs,
        sub: todayISO(),
        icon: 'INVENTARIO_AVES.svg',
        alt: 'Producción del día',
        theme: 'danger',
      },
    ],
    [metrics, todayEggs, selectedLot],
  )

  const mergeResult = mergeConflict
    ? {
        egg_count:
          (mergeConflict.existing?.egg_count || 0) +
          (mergeConflict.payload?.egg_count || 0),
        broken_eggs:
          (mergeConflict.existing?.broken_eggs || 0) +
          (mergeConflict.payload?.broken_eggs || 0),
      }
    : null

  return (
    <div className="production-shell">
      <div className="production-header-row">
        <PageHeader eyebrow="Producción Diaria" title="Registro de postura" />
        <div className="production-selector">
          <label htmlFor="production-lot-input">Lote</label>
          <div className="production-lot-autocomplete">
            <input
              id="production-lot-input"
              value={lotInput}
              onChange={handleLotInput}
              onFocus={handleLotFocus}
              onBlur={handleLotBlur}
              onKeyDown={handleLotKeyDown}
              placeholder={loadingLots ? 'Cargando lotes...' : 'Buscar lote'}
              autoComplete="off"
              role="combobox"
              aria-expanded={suggestionsOpen}
              aria-haspopup="listbox"
            />
            {suggestionsOpen && lotSuggestions.length > 0 && (
              <ul className="production-suggestions" role="listbox">
                {lotSuggestions.map((lot, index) => (
                  <li
                    key={lot.id}
                    role="option"
                    aria-selected={index === activeIndex}
                  >
                    <button
                      type="button"
                      className={index === activeIndex ? 'is-active' : ''}
                      onMouseDown={(event) => event.preventDefault()}
                      onClick={() => selectLot(lot)}
                    >
                      <span className="production-suggestion-code">
                        {lot.lot_code}
                      </span>
                      <span className="production-suggestion-meta">
                        {lot.breed} · Semana {lot.current_week} ·{' '}
                        {lot.current_quantity} aves
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <span className="production-date-chip">
            {formatShortDate(todayISO())}
          </span>
        </div>
      </div>

      {selectedLot && (
        <div className="production-lot-info">
          <span className="chip">
            {selectedLot.lot_code} · {selectedLot.breed}
          </span>
          <span className="production-lot-week">
            Semana {selectedLot.current_week} · {selectedLot.current_quantity}{' '}
            aves
          </span>
        </div>
      )}

      <div className="carousel-container">
        <section
          className="content-cards"
          ref={cardsRef}
          onScroll={handleCardsScroll}
        >
          {cards.map((card) => (
            <article key={card.label} className={`card card-${card.theme}`}>
              <div className="info">
                <span className="label">{card.label}</span>
                <strong className="count">{card.value}</strong>
                <small>{card.sub}</small>
              </div>
              <div className="icon">
                <img
                  src={`/icons/${card.icon}`}
                  alt={card.alt}
                  className="icon-card"
                />
              </div>
            </article>
          ))}
        </section>
        <div className="carousel-pagination">
          {cards.map((card, index) => (
            <button
              key={card.label}
              className={`pagination-dot ${index === cardIndex ? 'active' : ''}`}
              data-index={index}
              onClick={() => goToCard(index)}
              aria-label={`Ir a tarjeta ${index + 1}`}
            ></button>
          ))}
        </div>
      </div>

      <div className="production-grid">
        <section className="panel production-chart-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Producción</p>
              <h2>
                {singleDay ? 'Producción por hora' : 'Producción por día'}
              </h2>
            </div>
          </div>
          <div className="production-range">
            <div className="production-range-field">
              <label htmlFor="range-from">Desde</label>
              <input
                id="range-from"
                type="date"
                value={fromDate}
                max={todayISO()}
                onChange={(event) => setFromDate(event.target.value)}
              />
            </div>
            <span className="production-range-sep">—</span>
            <div className="production-range-field">
              <label htmlFor="range-to">Hasta</label>
              <input
                id="range-to"
                type="date"
                value={toDate}
                min={fromDate}
                max={todayISO()}
                onChange={(event) => setToDate(event.target.value)}
              />
            </div>
          </div>
          <div className="production-chart">
            {!records ? (
              <div className="chart-empty">Cargando...</div>
            ) : records.length === 0 ? (
              <div className="chart-empty">No hay registros en el rango</div>
            ) : (
              <canvas ref={canvasRef} id="productionChart"></canvas>
            )}
          </div>
        </section>

        <section className="panel production-form-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Registro</p>
              <h2>Registro de postura</h2>
            </div>
          </div>
          <form onSubmit={handleSubmit} noValidate>
            <div className="production-form-row">
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="form-egg-count">
                  Cantidad
                </label>
                <input
                  id="form-egg-count"
                  className="app-form-control"
                  type="number"
                  min="0"
                  step="1"
                  placeholder="Ej: 90"
                  value={form.egg_count}
                  onChange={(event) =>
                    setField('egg_count', event.target.value)
                  }
                />
                {formErrors.egg_count && (
                  <p className="app-form-error">{formErrors.egg_count}</p>
                )}
              </div>
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="form-broken-eggs">
                  No aptos
                </label>
                <input
                  id="form-broken-eggs"
                  className="app-form-control"
                  type="number"
                  min="0"
                  step="1"
                  placeholder="Ej: 2"
                  value={form.broken_eggs}
                  onChange={(event) =>
                    setField('broken_eggs', event.target.value)
                  }
                />
                {formErrors.broken_eggs && (
                  <p className="app-form-error">{formErrors.broken_eggs}</p>
                )}
              </div>
            </div>

            <div className="production-form-row">
              <div className="app-form-group">
                <label
                  className="app-form-label"
                  htmlFor="form-collection-date"
                >
                  Fecha
                </label>
                <input
                  id="form-collection-date"
                  className="app-form-control"
                  type="date"
                  min={yesterdayISO()}
                  max={todayISO()}
                  value={form.collection_date}
                  onChange={(event) =>
                    setField('collection_date', event.target.value)
                  }
                />
                {formErrors.collection_date && (
                  <p className="app-form-error">{formErrors.collection_date}</p>
                )}
              </div>
              <div className="app-form-group">
                <label
                  className="app-form-label"
                  htmlFor="form-collection-time"
                >
                  Hora
                </label>
                <input
                  id="form-collection-time"
                  className="app-form-control"
                  type="time"
                  value={form.collection_time}
                  onChange={(event) =>
                    setField('collection_time', event.target.value)
                  }
                />
                {formErrors.collection_time && (
                  <p className="app-form-error">{formErrors.collection_time}</p>
                )}
              </div>
            </div>

            <div className="app-form-group">
              <label className="app-form-label" htmlFor="form-observations">
                Comentario de registro
              </label>
              <textarea
                id="form-observations"
                className="app-form-control"
                rows={3}
                maxLength={300}
                placeholder="Notas de la recolección"
                value={form.observations}
                onChange={(event) =>
                  setField('observations', event.target.value)
                }
              />
            </div>

            <div className="production-form-actions">
              <button
                type="button"
                className="app-btn-secondary"
                onClick={handleClear}
                disabled={submitting}
              >
                Limpiar
              </button>
              <button
                type="submit"
                className="app-btn-primary"
                disabled={submitting || !selectedLot}
              >
                {submitting ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </form>
        </section>
      </div>

      <Modal
        open={!!mergeConflict}
        onClose={() => setMergeConflict(null)}
        title="Registro existente"
        subtitle="Se sumarán las cantidades al registro con la misma fecha y hora"
        footer={
          <div className="app-modal-actions">
            <button
              type="button"
              className="app-btn-secondary"
              onClick={() => setMergeConflict(null)}
              disabled={submitting}
            >
              Cancelar
            </button>
            <button
              type="button"
              className="app-btn-primary"
              onClick={handleMergeConfirm}
              disabled={submitting}
            >
              {submitting ? 'Sumando...' : 'Confirmar suma'}
            </button>
          </div>
        }
      >
        {mergeConflict && (
          <div className="merge-detail">
            <div className="summary-item">
              <span>Fecha y hora</span>
              <strong>
                {formatShortDate(mergeConflict.existing?.collection_date)} ·{' '}
                {formatTime(mergeConflict.existing?.collection_time)}
              </strong>
            </div>
            <div className="summary-item">
              <span>Registro existente</span>
              <strong>
                {mergeConflict.existing?.egg_count || 0} aptos ·{' '}
                {mergeConflict.existing?.broken_eggs || 0} no aptos
              </strong>
            </div>
            <div className="summary-item">
              <span>Nueva recolección</span>
              <strong>
                {mergeConflict.payload?.egg_count || 0} aptos ·{' '}
                {mergeConflict.payload?.broken_eggs || 0} no aptos
              </strong>
            </div>
            <div className="summary-item summary-item-total">
              <span>Resultado tras sumar</span>
              <strong>
                {mergeResult.egg_count} aptos · {mergeResult.broken_eggs} no
                aptos
              </strong>
            </div>
            {mergeConflict.existing?.observations && (
              <p className="merge-comment">
                Comentario actual: {mergeConflict.existing.observations}
              </p>
            )}
          </div>
        )}
      </Modal>

      <Toast toasts={toasts} onDismiss={dismissToast} />
    </div>
  )
}

export default ProductionPage
