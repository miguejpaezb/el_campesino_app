/**
 * Página principal del módulo de alimentación.
 *
 * Muestra un buscador y una tabla de lotes. Cada lote tiene un menú que
 * permite registrar alimentación (modal con autocompletado de alimentos del
 * inventario y descuento de stock) o navegar al resumen de alimentación.
 * La cabecera incluye un botón para la gestión del inventario de alimentos.
 *
 * @returns {JSX.Element} Página principal de alimentación.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Modal from '../components/Modal.jsx'
import PageHeader from '../components/PageHeader.jsx'
import RowMenu from '../components/RowMenu.jsx'
import Toast from '../components/Toast.jsx'
import feedStockService from '../services/feedStockService.js'
import feedingService from '../services/feedingService.js'
import lotService from '../services/lotService.js'
import { getErrorMessage } from '../utils/errors.js'
import './FeedingPage.css'

const TOAST_DURATION = 4000

const toISODate = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const todayISO = () => toISODate(new Date())

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

function RegisterFeedingModal({ lot, feeds, onClose, onSubmit, submitting }) {
  const [feedInput, setFeedInput] = useState('')
  const [selectedFeed, setSelectedFeed] = useState(null)
  const [suggestionsOpen, setSuggestionsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const [form, setForm] = useState(() => ({
    kilos: '',
    feed_date: todayISO(),
    week: String(lot.current_week),
    observations: '',
  }))
  const [errors, setErrors] = useState({})

  const suggestions = feeds.filter((feed) =>
    feed.name.toLowerCase().includes(feedInput.trim().toLowerCase()),
  )

  const selectFeed = (feed) => {
    setFeedInput(feed.name)
    setSelectedFeed(feed)
    setSuggestionsOpen(false)
    setActiveIndex(-1)
  }

  const handleFeedInput = (event) => {
    const value = event.target.value
    setFeedInput(value)
    setActiveIndex(-1)
    const feed = feeds.find((item) => item.name === value)
    if (feed) {
      setSelectedFeed(feed)
      setSuggestionsOpen(true)
    } else {
      setSelectedFeed(null)
    }
  }

  const handleFeedFocus = () => setSuggestionsOpen(true)

  const handleFeedBlur = () => {
    setTimeout(() => {
      setSuggestionsOpen(false)
      setActiveIndex(-1)
    }, 120)
  }

  const handleFeedKeyDown = (event) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setSuggestionsOpen(true)
      setActiveIndex((prev) => Math.min(prev + 1, suggestions.length - 1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((prev) => Math.max(prev - 1, -1))
    } else if (event.key === 'Enter') {
      if (suggestionsOpen && activeIndex >= 0 && suggestions[activeIndex]) {
        event.preventDefault()
        selectFeed(suggestions[activeIndex])
      }
    } else if (event.key === 'Escape') {
      setSuggestionsOpen(false)
      setActiveIndex(-1)
    }
  }

  const setField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const validate = () => {
    const next = {}
    const kilos = Number(form.kilos)
    if (!selectedFeed) next.feedInput = 'Selecciona un tipo de alimento'
    if (form.kilos === '' || !Number.isFinite(kilos) || kilos <= 0) {
      next.kilos = 'Ingresa una cantidad mayor a 0'
    } else if (selectedFeed && kilos > selectedFeed.stock_kg) {
      next.kilos = `Solo hay ${formatKilos(selectedFeed.stock_kg)} en stock`
    }
    if (!form.feed_date) {
      next.feed_date = 'La fecha es obligatoria'
    } else if (form.feed_date > todayISO()) {
      next.feed_date = 'La fecha no puede ser futura'
    }
    if (form.week !== '') {
      const week = Number(form.week)
      if (!Number.isInteger(week) || week < 0) {
        next.week = 'La semana debe ser un entero mayor o igual a 0'
      }
    }
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!validate()) return
    onSubmit({
      feed_type_id: selectedFeed.id,
      kilos: Number(form.kilos),
      feed_date: form.feed_date,
      week: form.week === '' ? null : Number(form.week),
      observations: form.observations.trim() || null,
    })
  }

  const totalCost =
    selectedFeed && form.kilos !== ''
      ? Number(form.kilos) * (selectedFeed.cost_per_kilo || 0)
      : 0

  return (
    <Modal
      open
      onClose={onClose}
      title={`Registrar alimentación — ${lot?.lot_code || ''}`}
      subtitle={
        lot
          ? `${lot.breed} · Semana ${lot.current_week} · ${lot.current_quantity} aves`
          : ''
      }
      footer={
        <div className="app-modal-actions">
          <button
            type="button"
            className="app-btn-secondary"
            onClick={onClose}
            disabled={submitting}
          >
            Cancelar
          </button>
          <button
            type="button"
            className="app-btn-primary"
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? 'Guardando...' : 'Guardar'}
          </button>
        </div>
      }
    >
      <form onSubmit={handleSubmit} noValidate className="app-form-stack">
        <div className="app-form-group">
          <label className="app-form-label" htmlFor="feeding-feed-input">
            Tipo de alimento
          </label>
          <div className="feeding-modal-autocomplete">
            <input
              id="feeding-feed-input"
              className="app-form-control"
              value={feedInput}
              onChange={handleFeedInput}
              onFocus={handleFeedFocus}
              onBlur={handleFeedBlur}
              onKeyDown={handleFeedKeyDown}
              placeholder="Buscar alimento del inventario"
              autoComplete="off"
              role="combobox"
              aria-expanded={suggestionsOpen}
              aria-haspopup="listbox"
            />
            {suggestionsOpen && suggestions.length > 0 && (
              <ul className="feeding-modal-suggestions" role="listbox">
                {suggestions.map((feed, index) => (
                  <li
                    key={feed.id}
                    role="option"
                    aria-selected={index === activeIndex}
                  >
                    <button
                      type="button"
                      className={index === activeIndex ? 'is-active' : ''}
                      onMouseDown={(event) => event.preventDefault()}
                      onClick={() => selectFeed(feed)}
                    >
                      <span className="feeding-modal-suggestion-name">
                        {feed.name}
                      </span>
                      <span className="feeding-modal-suggestion-meta">
                        {formatKilos(feed.stock_kg)} ·{' '}
                        {formatMoney(feed.cost_per_kilo)}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          {errors.feedInput && (
            <p className="app-form-error">{errors.feedInput}</p>
          )}
        </div>

        {selectedFeed && (
          <div className="feeding-selected-feed">
            <div className="feeding-selected-feed-item">
              <span>Stock actual</span>
              <strong>{formatKilos(selectedFeed.stock_kg)}</strong>
            </div>
            <div className="feeding-selected-feed-item">
              <span>Costo por kilo</span>
              <strong>{formatMoney(selectedFeed.cost_per_kilo)}</strong>
            </div>
            <div className="feeding-selected-feed-item">
              <span>Estado</span>
              <strong>
                {selectedFeed.is_active ? 'Activo' : 'Suspendido'}
              </strong>
            </div>
            {selectedFeed.is_low_stock && (
              <div className="feeding-selected-feed-item">
                <span>Alerta</span>
                <strong className="feeding-selected-feed-alert">
                  Stock bajo
                </strong>
              </div>
            )}
          </div>
        )}

        <div className="feeding-form-row">
          <div className="app-form-group">
            <label className="app-form-label" htmlFor="feeding-kilos">
              Kilos
            </label>
            <input
              id="feeding-kilos"
              className="app-form-control"
              type="number"
              min="0"
              step="0.01"
              placeholder="Ej: 100"
              value={form.kilos}
              onChange={(event) => setField('kilos', event.target.value)}
            />
            {errors.kilos && <p className="app-form-error">{errors.kilos}</p>}
          </div>
          <div className="app-form-group">
            <label className="app-form-label" htmlFor="feeding-week">
              Semana del ciclo
            </label>
            <input
              id="feeding-week"
              className="app-form-control"
              type="number"
              min="0"
              step="1"
              value={form.week}
              onChange={(event) => setField('week', event.target.value)}
            />
            {errors.week && <p className="app-form-error">{errors.week}</p>}
          </div>
        </div>

        <div className="feeding-form-row">
          <div className="app-form-group">
            <label className="app-form-label" htmlFor="feeding-date">
              Fecha
            </label>
            <input
              id="feeding-date"
              className="app-form-control"
              type="date"
              max={todayISO()}
              value={form.feed_date}
              onChange={(event) => setField('feed_date', event.target.value)}
            />
            {errors.feed_date && (
              <p className="app-form-error">{errors.feed_date}</p>
            )}
          </div>
          <div className="app-form-group">
            <label className="app-form-label" htmlFor="feeding-observations">
              Observaciones
            </label>
            <input
              id="feeding-observations"
              className="app-form-control"
              maxLength={300}
              placeholder="Notas del suministro"
              value={form.observations}
              onChange={(event) => setField('observations', event.target.value)}
            />
          </div>
        </div>

        {selectedFeed && Number(form.kilos) > 0 && (
          <div className="feeding-value-spent">
            <span>Valor del suministro</span>
            <strong>{formatMoney(totalCost)}</strong>
          </div>
        )}
      </form>
    </Modal>
  )
}

function FeedingPage() {
  const navigate = useNavigate()
  const [lots, setLots] = useState([])
  const [feeds, setFeeds] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [registerLot, setRegisterLot] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [toasts, setToasts] = useState([])
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
    Promise.all([lotService.getLots(), feedStockService.getFeedStock()])
      .then(([lotsData, feedsData]) => {
        if (!mounted) return
        setLots(lotsData)
        setFeeds(feedsData.filter((feed) => feed.is_active))
      })
      .catch((error) => {
        if (mounted) {
          pushToast(
            'error',
            getErrorMessage(error, 'No se pudieron cargar los datos'),
          )
        }
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [pushToast])

  const filteredLots = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return lots
    return lots.filter(
      (lot) =>
        String(lot.id).includes(term) ||
        lot.lot_code.toLowerCase().includes(term),
    )
  }, [lots, search])

  const handleRegister = async (payload) => {
    if (!registerLot) return
    setSubmitting(true)
    try {
      await feedingService.registerFeeding(registerLot.id, payload)
      pushToast('success', 'Alimentación registrada correctamente.')
      setRegisterLot(null)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo registrar la alimentación'),
      )
    } finally {
      setSubmitting(false)
    }
  }

  const handleClearSearch = () => setSearch('')

  const estadoLabel = (isActive) => (isActive ? 'Activo' : 'Descartado')

  return (
    <div className="feeding-shell">
      <div className="feeding-header-row">
        <PageHeader eyebrow="Alimentación" title="Registro de suministro" />
        <button
          className="app-btn-primary feeding-stock-btn"
          onClick={() => navigate('/alimentacion/insumos')}
        >
          Gestión de alimento
        </button>
      </div>

      <div className="feeding-toolbar">
        <div className="feeding-search">
          <input
            type="search"
            placeholder="Buscar por ID o código de lote"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            aria-label="Buscar lote"
          />
        </div>
        <button
          className="app-btn-secondary feeding-clear-btn"
          onClick={handleClearSearch}
          disabled={!search}
        >
          Limpiar
        </button>
      </div>

      <div className="feeding-table-wrap">
        <table className="feeding-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Lote</th>
              <th className="col-desktop">Aves actuales</th>
              <th className="col-desktop">Semana actual</th>
              <th className="col-estado">Estado</th>
              <th className="col-actions">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="table-empty">
                  Cargando...
                </td>
              </tr>
            ) : filteredLots.length === 0 ? (
              <tr>
                <td colSpan={6} className="table-empty">
                  No se encontraron lotes
                </td>
              </tr>
            ) : (
              filteredLots.map((lot) => (
                <tr key={lot.id}>
                  <td className="cell-id">{String(lot.id).padStart(2, '0')}</td>
                  <td>
                    <div className="feeding-lot-cell">
                      <span className="feeding-lot-code">{lot.lot_code}</span>
                      <small>{lot.breed}</small>
                    </div>
                  </td>
                  <td className="col-desktop">{lot.current_quantity}</td>
                  <td className="col-desktop">{lot.current_week}</td>
                  <td className="col-estado">
                    <span
                      className={`estado estado-${
                        lot.is_active ? 'activo' : 'descartado'
                      }`}
                    >
                      {estadoLabel(lot.is_active)}
                    </span>
                  </td>
                  <td className="col-actions">
                    <RowMenu
                      label={`Acciones del lote ${lot.lot_code}`}
                      items={[
                        {
                          label: 'Registrar alimentación',
                          onClick: () => setRegisterLot(lot),
                        },
                        {
                          label: 'Ver resumen de alimentación',
                          onClick: () =>
                            navigate(`/alimentacion/resumen/${lot.id}`),
                        },
                      ]}
                    />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {registerLot && (
        <RegisterFeedingModal
          lot={registerLot}
          feeds={feeds}
          onClose={() => setRegisterLot(null)}
          onSubmit={handleRegister}
          submitting={submitting}
        />
      )}

      <Toast toasts={toasts} onDismiss={dismissToast} />
    </div>
  )
}

export default FeedingPage
