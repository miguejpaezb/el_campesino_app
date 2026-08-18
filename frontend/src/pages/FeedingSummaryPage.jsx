/**
 * Página de resumen de alimentación de un lote.
 *
 * Muestra los indicadores globales (total consumido, costo, registros y
 * último suministro), el gráfico de kilos por día en una ventana de 7 días
 * seleccionable, un resumen del lapso y el historial de registros paginado.
 *
 * @returns {JSX.Element} Página de resumen de alimentación.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Chart } from 'chart.js/auto'
import PageHeader from '../components/PageHeader.jsx'
import Toast from '../components/Toast.jsx'
import feedingService from '../services/feedingService.js'
import lotService from '../services/lotService.js'
import { getErrorMessage } from '../utils/errors.js'
import './FeedingSummaryPage.css'

const TOAST_DURATION = 4000
const PAGE_SIZE = 10
const COLORS = {
  bar: 'rgba(158, 107, 52, 0.75)',
  barHover: '#9e6b34',
  grid: 'rgba(0, 0, 0, 0.05)',
  text: '#666',
}

const toISODate = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const todayISO = () => toISODate(new Date())

const addDaysISO = (iso, days) => {
  const d = new Date(`${iso}T00:00:00`)
  d.setDate(d.getDate() + days)
  return toISODate(d)
}

const formatShortDate = (iso) => {
  if (!iso) return ''
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y.slice(-2)}`
}

const formatKilos = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '—'
  }
  return `${Number(value).toLocaleString('es-CO', {
    maximumFractionDigits: 2,
  })} kg`
}

const formatMoney = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '—'
  }
  return Number(value).toLocaleString('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 2,
  })
}

function FeedingSummaryPage() {
  const { lotId } = useParams()
  const navigate = useNavigate()
  const [lot, setLot] = useState(null)
  const [records, setRecords] = useState(null)
  const [metrics, setMetrics] = useState({ totalKg: 0, totalCost: 0 })
  const [page, setPage] = useState(1)
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
    const id = Number(lotId)
    if (!Number.isInteger(id)) {
      pushToast('error', 'Lote no válido')
      navigate('/alimentacion')
      return () => {
        mounted = false
      }
    }
    Promise.all([
      lotService.getLot(id),
      feedingService.getTotalKg(id),
      feedingService.getTotalCost(id),
      feedingService.getFeeding(id),
    ])
      .then(([lotData, totalKg, totalCost, recordsData]) => {
        if (!mounted) return
        setLot(lotData)
        setMetrics({ totalKg, totalCost })
        setRecords(recordsData)
      })
      .catch((error) => {
        if (!mounted) return
        pushToast(
          'error',
          getErrorMessage(error, 'No se pudieron cargar los datos del lote'),
        )
      })
    return () => {
      mounted = false
    }
  }, [lotId, navigate, pushToast])

  const today = todayISO()

  const windowRange = useMemo(() => {
    const from = addDaysISO(today, -6)
    const to = today
    return { from, to }
  }, [today])

  const windowRecords = useMemo(() => {
    if (!records) return []
    return records
      .filter(
        (record) =>
          record.feed_date >= windowRange.from &&
          record.feed_date <= windowRange.to,
      )
      .slice()
      .sort((a, b) => {
        if (a.feed_date === b.feed_date) {
          return new Date(b.created_at) - new Date(a.created_at)
        }
        return a.feed_date < b.feed_date ? 1 : -1
      })
  }, [records, windowRange])

  const lastRecord = useMemo(() => {
    if (!records || records.length === 0) return null
    return records.slice().sort((a, b) => {
      if (a.feed_date === b.feed_date) {
        return new Date(b.created_at) - new Date(a.created_at)
      }
      return a.feed_date < b.feed_date ? 1 : -1
    })[0]
  }, [records])

  const chartData = useMemo(() => {
    if (!lot || !records) return null
    const labels = []
    const data = []
    const meta = []
    const cursor = new Date(`${windowRange.from}T00:00:00`)
    const end = new Date(`${windowRange.to}T00:00:00`)
    while (cursor <= end) {
      const iso = toISODate(cursor)
      const dayRecords = windowRecords.filter(
        (record) => record.feed_date === iso,
      )
      const kilos = dayRecords.reduce((acc, record) => acc + record.kilos, 0)
      const cost = dayRecords.reduce((acc, record) => {
        if (record.total_cost === null || record.total_cost === undefined) {
          return acc
        }
        return acc + record.total_cost
      }, 0)
      const types = dayRecords.map((record) => record.feed_type)
      labels.push(formatShortDate(iso))
      data.push(Number(kilos.toFixed(2)))
      meta.push({
        iso,
        kilos,
        cost,
        types: types.filter((value, index) => types.indexOf(value) === index),
        records: dayRecords.length,
      })
      cursor.setDate(cursor.getDate() + 1)
    }
    return { labels, data, meta }
  }, [lot, records, windowRecords, windowRange])

  useEffect(() => {
    if (!canvasRef.current || !chartData) return
    chartRef.current?.destroy()

    const tooltipLines = (ctx) => {
      const meta = chartData.meta[ctx.dataIndex]
      if (!meta) return ''
      return [
        `Tipo: ${meta.types.join(', ') || '—'}`,
        `Kilos: ${formatKilos(meta.kilos)}`,
        `Costo total: ${formatMoney(meta.cost)}`,
        `Registros: ${meta.records}`,
      ]
    }

    chartRef.current = new Chart(canvasRef.current, {
      type: 'bar',
      data: {
        labels: chartData.labels,
        datasets: [
          {
            label: 'Kilos por día',
            data: chartData.data,
            backgroundColor: COLORS.bar,
            hoverBackgroundColor: COLORS.barHover,
            borderRadius: 8,
            borderSkipped: false,
            maxBarThickness: 32,
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

  const summary = useMemo(() => {
    if (windowRecords.length === 0) {
      return {
        kilos: 0,
        cost: 0,
        count: 0,
        average: 0,
        topType: '—',
      }
    }
    const kilos = windowRecords.reduce((acc, record) => acc + record.kilos, 0)
    const cost = windowRecords.reduce((acc, record) => {
      if (record.total_cost === null || record.total_cost === undefined) {
        return acc
      }
      return acc + record.total_cost
    }, 0)
    const typeCounts = {}
    for (const record of windowRecords) {
      typeCounts[record.feed_type] = (typeCounts[record.feed_type] || 0) + 1
    }
    const topType = Object.entries(typeCounts).sort(
      (a, b) => b[1] - a[1],
    )[0]?.[0]
    return {
      kilos,
      cost,
      count: windowRecords.length,
      average: kilos / 7,
      topType,
    }
  }, [windowRecords])

  const sortedAll = useMemo(() => {
    if (!records) return []
    return records.slice().sort((a, b) => {
      if (a.feed_date === b.feed_date) {
        return new Date(b.created_at) - new Date(a.created_at)
      }
      return a.feed_date < b.feed_date ? 1 : -1
    })
  }, [records])

  const pageCount = Math.max(1, Math.ceil(sortedAll.length / PAGE_SIZE))
  const safePage = Math.min(page, pageCount)
  const pageRecords = sortedAll.slice(
    (safePage - 1) * PAGE_SIZE,
    safePage * PAGE_SIZE,
  )

  const cards = useMemo(
    () => [
      {
        label: 'Total de alimento consumido',
        value: formatKilos(metrics.totalKg),
        sub: lot?.lot_code || '—',
        icon: 'ALIMENTO.svg',
        alt: 'Total de alimento',
        theme: 'primary',
      },
      {
        label: 'Costo total de alimentación',
        value: formatMoney(metrics.totalCost),
        sub: 'Kilos × costo por kilo',
        icon: 'PRODUCCION_DIARIA.svg',
        alt: 'Costo total',
        theme: 'success',
      },
      {
        label: 'Registros de alimentación',
        value: records ? records.length : 0,
        sub: 'Suministros registrados',
        icon: 'INVENTARIO_AVES.svg',
        alt: 'Registros',
        theme: 'warning',
      },
      {
        label: 'Último suministro',
        value: lastRecord ? formatShortDate(lastRecord.feed_date) : '—',
        sub: lastRecord
          ? `${lastRecord.feed_type} · ${formatKilos(lastRecord.kilos)}`
          : 'Sin registros',
        icon: 'MONITOREO_IOT.svg',
        alt: 'Último suministro',
        theme: 'danger',
      },
    ],
    [metrics, records, lot, lastRecord],
  )

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

  return (
    <div className="feedingsummary-shell">
      <div className="feedingsummary-header-row">
        <PageHeader
          eyebrow="Alimentación · Resumen"
          title={`Lote ${lot?.lot_code || ''}`}
        />
        <button
          className="feedingsummary-back-btn"
          onClick={() => navigate('/alimentacion')}
          aria-label="Volver a alimentación"
        >
          <img src="/icons/arrow.svg" alt="Volver" />
        </button>
      </div>

      {lot && (
        <div className="feedingsummary-lot-info">
          <span className="chip">
            {lot.lot_code} · {lot.breed}
          </span>
          <span className="feedingsummary-lot-week">
            Semana {lot.current_week} · {lot.current_quantity} aves
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

      <div className="feedingsummary-grid">
        <section className="panel feedingsummary-chart-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Consumo</p>
              <h2>Kilos de alimento por día</h2>
            </div>
          </div>
          <div className="feedingsummary-chart">
            {!records ? (
              <div className="chart-empty">Cargando...</div>
            ) : windowRecords.length === 0 ? (
              <div className="chart-empty">No hay registros en este lapso</div>
            ) : (
              <canvas ref={canvasRef} id="feedingSummaryChart"></canvas>
            )}
          </div>
        </section>

        <section className="panel feedingsummary-summary-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Resumen</p>
              <h2>Últimos 7 días</h2>
            </div>
          </div>
          <ul className="summary-list">
            <li>
              <span>Total consumido</span>
              <strong>{formatKilos(summary.kilos)}</strong>
            </li>
            <li>
              <span>Costo del lapso</span>
              <strong>{formatMoney(summary.cost)}</strong>
            </li>
            <li>
              <span>Registros</span>
              <strong>{summary.count}</strong>
            </li>
            <li>
              <span>Promedio por día</span>
              <strong>{formatKilos(summary.average)}</strong>
            </li>
            <li>
              <span>Tipo más usado</span>
              <strong>{summary.topType}</strong>
            </li>
          </ul>
        </section>
      </div>

      <section className="panel feedingsummary-history-panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Historial</p>
            <h2>Registros de alimentación</h2>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Semana</th>
                <th>Tipo de alimento</th>
                <th>Kilos</th>
                <th>Costo total</th>
              </tr>
            </thead>
            <tbody>
              {!records ? (
                <tr>
                  <td className="table-empty" colSpan={5}>
                    Cargando...
                  </td>
                </tr>
              ) : pageRecords.length === 0 ? (
                <tr>
                  <td className="table-empty" colSpan={5}>
                    No hay registros de alimentación
                  </td>
                </tr>
              ) : (
                pageRecords.map((record) => (
                  <tr key={record.id}>
                    <td>{formatShortDate(record.feed_date)}</td>
                    <td>{record.week}</td>
                    <td>{record.feed_type}</td>
                    <td>{formatKilos(record.kilos)}</td>
                    <td>{formatMoney(record.total_cost)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {records && records.length > PAGE_SIZE && (
          <div className="feedingsummary-pagination">
            <button
              type="button"
              className="app-btn-secondary"
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              disabled={safePage <= 1}
            >
              ← Anterior
            </button>
            <span>
              Página {safePage} de {pageCount}
            </span>
            <button
              type="button"
              className="app-btn-secondary"
              onClick={() => setPage((prev) => Math.min(pageCount, prev + 1))}
              disabled={safePage >= pageCount}
            >
              Siguiente →
            </button>
          </div>
        )}
      </section>

      <Toast toasts={toasts} onDismiss={dismissToast} />
    </div>
  )
}

export default FeedingSummaryPage
