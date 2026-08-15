/**
 * Página de inicio del panel de control.
 *
 * Muestra las tarjetas de producción, el gráfico de huevos por día, el
 * resumen semanal y el historial de acciones, alimentados por el backend.
 *
 * @returns {JSX.Element} Dashboard de producción semanal.
 */
import { useEffect, useRef, useState } from 'react'
import { Chart } from 'chart.js/auto'
import PageHeader from '../components/PageHeader.jsx'
import { dashboardService } from '../services/dashboardService.js'
import './DashboardPage.css'

const EMPTY = {
  activeLots: 0,
  todayEggs: 0,
  weekTotal: 0,
  layingPercentage: 0,
  mortalityPercentage: 0,
  bestDay: null,
  daily: [],
  labels: [],
  dateRangeText: '',
  hasData: false,
}

function DashboardPage() {
  const [data, setData] = useState(EMPTY)
  const [loading, setLoading] = useState(true)
  const [cardIndex, setCardIndex] = useState(0)
  const cardsRef = useRef(null)
  const canvasRef = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    let mounted = true
    dashboardService
      .getDashboardData()
      .then((result) => {
        if (mounted) setData(result)
      })
      .catch(() => {
        if (mounted) setData(EMPTY)
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    if (!canvasRef.current) return

    chartRef.current?.destroy()
    chartRef.current = new Chart(canvasRef.current, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Huevos producidos',
            data: data.daily,
            backgroundColor: '#d9b15a',
            borderRadius: 8,
            borderSkipped: false,
            maxBarThickness: 28,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            enabled: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            display: false,
            grid: {
              display: false,
            },
          },
          x: {
            grid: {
              display: false,
            },
            ticks: {
              color: '#666',
              maxTicksLimit: 7,
            },
          },
        },
      },
    })

    return () => {
      chartRef.current?.destroy()
    }
  }, [data])

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

  const yesterday =
    data.daily.length > 1 ? data.daily[data.daily.length - 2] : 0
  const today = data.daily.length > 0 ? data.daily[data.daily.length - 1] : 0
  const vsYesterday =
    yesterday > 0 ? Math.round(((today - yesterday) / yesterday) * 100) : null

  const cards = [
    {
      label: 'Producción hoy',
      value: data.todayEggs,
      sub:
        vsYesterday !== null
          ? `${vsYesterday > 0 ? '+' : ''}${vsYesterday}% vs ayer`
          : 'Sin registros hoy',
      icon: 'PRODUCCION_DIARIA.svg',
      alt: 'Producción diaria',
      theme: 'primary',
    },
    {
      label: 'Lotes activos',
      value: data.activeLots,
      sub: 'Activos actualmente',
      icon: 'INVENTARIO_AVES.svg',
      alt: 'Inventario',
      theme: 'success',
    },
    {
      label: 'Tasa de postura',
      value: `${data.layingPercentage.toFixed(1)}%`,
      sub: 'Promedio semanal',
      icon: 'TRAZABILIDAD.svg',
      alt: 'Trazabilidad',
      theme: 'warning',
    },
    {
      label: 'Mortalidad',
      value: `${data.mortalityPercentage.toFixed(1)}%`,
      sub: 'Promedio semanal',
      icon: 'SANIDAD.svg',
      alt: 'Sanidad',
      theme: 'danger',
    },
  ]

  return (
    <div className="dashboard-shell">
      <PageHeader eyebrow="Panel de control" title="Producción semanal" />

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

      <section className="panel-grid">
        <article className="panel panel-chart">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Producción</p>
              <h2>Huevos por día</h2>
            </div>
            <span className="chip">{data.dateRangeText}</span>
          </div>
          <div className="chart">
            {data.hasData ? (
              <canvas ref={canvasRef} id="weeklyChart"></canvas>
            ) : (
              <div className="chart-empty">
                {loading ? 'Cargando...' : 'No hay registros'}
              </div>
            )}
          </div>
        </article>

        <article className="panel summary-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Resumen</p>
              <h2>Semana actual</h2>
            </div>
          </div>
          <ul className="summary-list">
            <li>
              <span>Total de huevos</span>
              <strong>{data.weekTotal}</strong>
            </li>
            <li>
              <span>Mejor día</span>
              <strong>{data.bestDay || '—'}</strong>
            </li>
            <li>
              <span>Tasa de postura</span>
              <strong>{data.layingPercentage.toFixed(1)}%</strong>
            </li>
            <li>
              <span>Mortalidad</span>
              <strong>{data.mortalityPercentage.toFixed(1)}%</strong>
            </li>
          </ul>
        </article>
      </section>

      <section className="panel actions-panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Seguimiento</p>
            <h2>Historial de acciones</h2>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Fecha</th>
                <th>Hora</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan="4" className="table-empty">
                  No hay registros
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

export default DashboardPage
