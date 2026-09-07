/**
 * Página del módulo de trazabilidad (auditoría con blockchain simulado).
 *
 * Permite elegir una entidad auditada (lote, producción, alimentación,
 * sanidad o insumos) y consultar su cadena de hash encadenado: historial de
 * eventos con su autor, los cambios registrados y la verificación de
 * integridad de la cadena.
 *
 * @returns {JSX.Element} Página de trazabilidad.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import Toast from '../components/Toast.jsx'
import { useAuth } from '../hooks/useAuth.js'
import { authService } from '../services/authService.js'
import feedStockService from '../services/feedStockService.js'
import feedingService from '../services/feedingService.js'
import lotService from '../services/lotService.js'
import productionService from '../services/productionService.js'
import sanidadService from '../services/sanidadService.js'
import traceabilityService from '../services/traceabilityService.js'
import { getErrorMessage } from '../utils/errors.js'
import './TraceabilityPage.css'

const TOAST_DURATION = 4000

const ENTITY_DEFS = [
  {
    key: 'lot',
    label: 'Lote',
    type: 'BirdLot',
    needsLot: false,
    recordNoun: '',
  },
  {
    key: 'production',
    label: 'Producción',
    type: 'EggProduction',
    needsLot: true,
    recordNoun: 'Registro',
  },
  {
    key: 'feeding',
    label: 'Alimentación',
    type: 'FeedingRecord',
    needsLot: true,
    recordNoun: 'Suministro',
  },
  {
    key: 'vaccination',
    label: 'Vacuna',
    type: 'Vaccination',
    needsLot: true,
    recordNoun: 'Vacuna',
  },
  {
    key: 'mortality',
    label: 'Mortalidad',
    type: 'Mortality',
    needsLot: true,
    recordNoun: 'Evento',
  },
  {
    key: 'disease',
    label: 'Enfermedad',
    type: 'Disease',
    needsLot: true,
    recordNoun: 'Enfermedad',
  },
  {
    key: 'feedtype',
    label: 'Insumo',
    type: 'FeedType',
    needsLot: false,
    recordNoun: 'Insumo',
  },
]

const RECORD_LOADERS = {
  production: (lotId) => productionService.getProduction(lotId),
  feeding: (lotId) => feedingService.getFeeding(lotId),
  vaccination: (lotId) => sanidadService.listVaccinations(lotId),
  mortality: (lotId) => sanidadService.listMortality(lotId),
  disease: (lotId) => sanidadService.listDiseases(lotId),
}

const pad = (n) => String(n).padStart(2, '0')

const fmtDate = (value) => {
  if (!value) return '—'
  const [y, m, d] = String(value).slice(0, 10).split('-')
  if (!y || !m || !d) return String(value)
  return `${d}/${m}/${y.slice(-2)}`
}

const fmtTime = (value) => {
  if (!value) return ''
  const [h, m] = String(value).split(':')
  return m ? `${pad(h)}:${m}` : ''
}

const fmtDateTime = (value) => {
  if (!value) return '—'
  const text = String(value).slice(0, 19).replace('T', ' ')
  const [date, time] = text.split(' ')
  return `${fmtDate(date)}${time ? ` ${time.slice(0, 5)}` : ''}`
}

const fmtNumber = (value) => {
  const num = Number(value)
  if (Number.isNaN(num)) return '—'
  return num.toLocaleString('es-CO')
}

const sameInstance = (a, b) =>
  Boolean(a && b && a.module === b.module && a.type === b.type && a.id === b.id)

const makeLotInstance = (lot) => ({
  module: 'lot',
  type: 'BirdLot',
  id: lot.id,
  label: `${lot.lot_code} · ${lot.breed}`,
  meta: `Semana ${lot.current_week} · ${fmtNumber(lot.current_quantity)} aves · ${
    lot.is_active ? 'Activo' : 'Descartado'
  }`,
})

const makeFeedInstance = (feed) => ({
  module: 'feedtype',
  type: 'FeedType',
  id: feed.id,
  label: feed.name,
  meta: `Stock ${fmtNumber(feed.stock_kg)} kg${feed.is_low_stock ? ' · Stock bajo' : ''}${
    feed.is_active ? '' : ' · Suspendido'
  }`,
})

const buildRecordInstance = (moduleKey, record) => {
  const def = ENTITY_DEFS.find((item) => item.key === moduleKey)
  const base = { module: moduleKey, type: def.type, id: record.id }
  switch (moduleKey) {
    case 'production':
      return {
        ...base,
        label: `${fmtDate(record.collection_date)} ${fmtTime(
          record.collection_time,
        )} · ${fmtNumber(record.egg_count)} huevos`,
        meta: `Semana ${record.week} · ${fmtNumber(record.broken_eggs)} no aptos`,
      }
    case 'feeding':
      return {
        ...base,
        label: `${fmtDate(record.feed_date)} · ${record.feed_type} · ${fmtNumber(
          record.kilos,
        )} kg`,
        meta: `Semana ${record.week}`,
      }
    case 'vaccination':
      return {
        ...base,
        label: `${fmtDate(record.application_date)} · ${record.vaccine_name}`,
        meta: `Semana ${record.week} · Dosis ${record.dosage}`,
      }
    case 'mortality':
      return {
        ...base,
        label: `${fmtDate(record.event_date)} · ${record.quantity} aves`,
        meta: `Semana ${record.week} · ${record.cause || 'Sin causa registrada'}`,
      }
    case 'disease':
      return {
        ...base,
        label: `${fmtDate(record.diagnosis_date)} · ${record.disease_name}`,
        meta: `${record.affected_quantity} aves afectadas`,
      }
    default:
      return { ...base, label: `#${record.id}`, meta: '' }
  }
}

const fmtChangeValue = (value) => {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'boolean') return value ? 'Sí' : 'No'
  if (typeof value === 'number') return fmtNumber(value)
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

const parseChangesRows = (changes) => {
  if (!changes) return { rows: [], raw: null }
  let parsed
  try {
    parsed = JSON.parse(changes)
  } catch {
    return { rows: [], raw: changes }
  }
  if (parsed === null || parsed === undefined) return { rows: [], raw: null }
  if (typeof parsed !== 'object' || Array.isArray(parsed)) {
    return { rows: [], raw: JSON.stringify(parsed) }
  }
  return { rows: Object.entries(parsed), raw: null }
}

function TraceBlock({
  entry,
  index,
  open,
  tampered,
  prevMatches,
  authorName,
  onToggle,
  onCopy,
}) {
  const { rows, raw } = parseChangesRows(entry.changes)
  const isGenesis = index === 0
  const prevOk = isGenesis || prevMatches
  return (
    <article className={`trace-block ${open ? 'is-open' : ''}`}>
      <button
        type="button"
        className="trace-block-head"
        onClick={onToggle}
        aria-expanded={open}
      >
        <span className="trace-block-index">#{index + 1}</span>
        <span
          className={`trace-action trace-action-${entry.action.toLowerCase()}`}
        >
          {entry.action}
        </span>
        <span className="trace-block-meta">
          <time>{fmtDateTime(entry.timestamp)}</time>
          <span className="trace-author">
            Usuario {entry.user_id}
            {authorName ? ` · ${authorName}` : ''}
          </span>
        </span>
        <span
          className={`trace-chevron ${open ? 'is-open' : ''}`}
          aria-hidden="true"
        />
      </button>

      {open && (
        <div className={`trace-block-body ${tampered ? 'is-tampered' : ''}`}>
          <div className="trace-changes">
            <span className="trace-body-label">Cambios registrados</span>
            {rows.length > 0 ? (
              <dl className="trace-changes-list">
                {rows.map(([field, value]) => (
                  <div className="trace-change-row" key={field}>
                    <dt>{field}</dt>
                    <dd>{fmtChangeValue(value)}</dd>
                  </div>
                ))}
              </dl>
            ) : raw ? (
              <p className="trace-code">{raw}</p>
            ) : (
              <p className="trace-muted trace-muted-inline">
                Sin detalle de cambios
              </p>
            )}
          </div>

          <div className="trace-hashes">
            <div className="trace-hash-row">
              <div className="trace-hash-info">
                <span className="trace-body-label">Hash anterior</span>
                <code className="trace-hash-code">
                  {entry.previous_hash}
                  {prevOk && (
                    <span className="trace-hash-ok">
                      {isGenesis ? ' · Bloque génesis' : ' · Coincide'}
                    </span>
                  )}
                  {!prevOk && (
                    <span className="trace-hash-bad"> · No coincide</span>
                  )}
                </code>
              </div>
              <button
                type="button"
                className="trace-copy-btn"
                onClick={() => onCopy(entry.previous_hash, 'Hash anterior')}
              >
                Copiar
              </button>
            </div>
            <div className="trace-hash-row">
              <div className="trace-hash-info">
                <span className="trace-body-label">Hash actual</span>
                <code className="trace-hash-code">{entry.current_hash}</code>
              </div>
              <button
                type="button"
                className="trace-copy-btn"
                onClick={() => onCopy(entry.current_hash, 'Hash actual')}
              >
                Copiar
              </button>
            </div>
          </div>
        </div>
      )}
    </article>
  )
}

function TraceChain({ instance, def, usersById, pushToast }) {
  const [chain, setChain] = useState([])
  const [chainLoading, setChainLoading] = useState(true)
  const [verifyResult, setVerifyResult] = useState(null)
  const [verifying, setVerifying] = useState(false)
  const [expandedIds, setExpandedIds] = useState([])

  useEffect(() => {
    let mounted = true
    traceabilityService
      .getHistory(instance.type, instance.id)
      .then((data) => {
        if (!mounted) return
        setChain(data)
        setExpandedIds(data.length ? [data[0].id] : [])
      })
      .catch((error) => {
        if (mounted) {
          pushToast(
            'error',
            getErrorMessage(error, 'No se pudo cargar la cadena de auditoría'),
          )
        }
      })
      .finally(() => {
        if (mounted) setChainLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [instance.type, instance.id, pushToast])

  const copyHash = async (text, what) => {
    try {
      await navigator.clipboard.writeText(text)
      pushToast('success', `${what} copiado al portapapeles.`)
    } catch {
      pushToast('error', `No se pudo copiar el ${what.toLowerCase()}.`)
    }
  }

  const toggleBlock = (id) => {
    setExpandedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id],
    )
  }

  const handleVerify = async () => {
    setVerifying(true)
    try {
      const result = await traceabilityService.verify(
        instance.type,
        instance.id,
      )
      setVerifyResult(result)
      if (result.valid) pushToast('success', result.detail)
      else pushToast('error', result.detail)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo verificar la cadena'),
      )
    } finally {
      setVerifying(false)
    }
  }

  const tamperedMatch = verifyResult?.detail?.match(/#(\d+)/)
  const tamperedIndex =
    verifyResult && !verifyResult.valid && tamperedMatch
      ? Number(tamperedMatch[1]) - 1
      : null

  return (
    <>
      <section className="panel trace-summary">
        <div className="trace-summary-info">
          <p className="eyebrow">Cadena de auditoría</p>
          <h2>{instance.label}</h2>
          <p className="trace-summary-meta">
            {instance.type} #{instance.id}
            {instance.meta ? ` · ${instance.meta}` : ''}
          </p>
        </div>
        <div className="trace-summary-side">
          <div className="trace-chain-badge">
            <strong>{fmtNumber(chain.length)}</strong>
            <span>bloques</span>
          </div>
          <button
            type="button"
            className="app-btn-primary trace-verify-btn"
            onClick={handleVerify}
            disabled={verifying || chainLoading || chain.length === 0}
          >
            {verifying ? 'Verificando...' : 'Verificar integridad'}
          </button>
        </div>
      </section>

      {verifyResult && (
        <div
          className={`trace-verify trace-verify-${verifyResult.valid ? 'ok' : 'bad'}`}
          role="status"
        >
          <span className="trace-verify-icon" aria-hidden="true">
            {verifyResult.valid ? '✔' : '✖'}
          </span>
          <div className="trace-verify-text">
            <strong>
              {verifyResult.valid
                ? 'Cadena íntegra'
                : 'Alerta: posible alteración de la cadena'}
            </strong>
            <p>{verifyResult.detail}</p>
          </div>
          <button
            type="button"
            className="trace-verify-close"
            onClick={() => setVerifyResult(null)}
            aria-label="Cerrar resultado de verificación"
          >
            ×
          </button>
        </div>
      )}

      <section className="panel trace-blocks">
        <div className="trace-blocks-head">
          <div>
            <p className="eyebrow">Bloques</p>
            <h2>Cadena de {def.label.toLowerCase()}</h2>
          </div>
          {chain.length > 0 && (
            <span className="trace-blocks-range">
              {fmtDateTime(chain[0].timestamp)} →{' '}
              {fmtDateTime(chain[chain.length - 1].timestamp)}
            </span>
          )}
        </div>

        <div className="trace-chain">
          {chainLoading ? (
            <p className="trace-muted">Cargando cadena de auditoría...</p>
          ) : chain.length === 0 ? (
            <p className="trace-muted">
              Esta entidad no tiene eventos de auditoría registrados.
            </p>
          ) : (
            chain.map((entry, index) => {
              const author = usersById[entry.user_id]?.username
              return (
                <TraceBlock
                  key={entry.id}
                  entry={entry}
                  index={index}
                  open={expandedIds.includes(entry.id)}
                  tampered={tamperedIndex === index}
                  prevMatches={
                    index === 0 ||
                    entry.previous_hash === chain[index - 1].current_hash
                  }
                  authorName={author}
                  onToggle={() => toggleBlock(entry.id)}
                  onCopy={copyHash}
                />
              )
            })
          )}
        </div>
      </section>
    </>
  )
}

function InstanceSelect({
  entityKey,
  def,
  lotId,
  selectedId,
  onPick,
  onError,
}) {
  const [status, setStatus] = useState('loading')
  const [instances, setInstances] = useState([])

  useEffect(() => {
    let mounted = true
    const build = (record) =>
      entityKey === 'feedtype'
        ? makeFeedInstance(record)
        : buildRecordInstance(entityKey, record)
    const load =
      entityKey === 'feedtype'
        ? () => feedStockService.getFeedStock()
        : () => RECORD_LOADERS[entityKey](lotId)

    load()
      .then((list) => {
        if (!mounted) return
        const next = list.map(build)
        setInstances(next)
        if (next.length > 0) onPick(next[0])
      })
      .catch((error) => {
        if (mounted) {
          onError(
            getErrorMessage(
              error,
              `No se pudieron cargar los registros de ${def.label.toLowerCase()}`,
            ),
          )
        }
      })
      .finally(() => {
        if (mounted) setStatus('ready')
      })
    return () => {
      mounted = false
    }
  }, [entityKey, def, lotId, onPick, onError])

  const handleChange = (event) => {
    const instance = instances.find(
      (item) => String(item.id) === event.target.value,
    )
    if (instance) onPick(instance)
  }

  const fieldLabel = entityKey === 'feedtype' ? 'Insumo' : def.recordNoun

  return (
    <div className="trace-instance-select">
      <label className="trace-field-label" htmlFor="trace-instance-select">
        {fieldLabel}
      </label>
      <div className="trace-select-wrap">
        {status === 'loading' ? (
          <div className="trace-select-loading">Cargando registros...</div>
        ) : instances.length === 0 ? (
          <div className="trace-select-empty">
            {entityKey === 'feedtype'
              ? 'No hay insumos registrados'
              : `No hay ${def.recordNoun.toLowerCase()}s para este lote`}
          </div>
        ) : (
          <select
            id="trace-instance-select"
            className="trace-select"
            value={selectedId ?? ''}
            onChange={handleChange}
          >
            {instances.map((instance) => (
              <option key={instance.id} value={instance.id}>
                #{instance.id} · {instance.label}
              </option>
            ))}
          </select>
        )}
      </div>
    </div>
  )
}

function TraceabilityPage() {
  const { user } = useAuth()
  const [entityKey, setEntityKey] = useState('lot')

  const [lots, setLots] = useState([])
  const [lotsLoading, setLotsLoading] = useState(true)
  const [lotInput, setLotInput] = useState('')
  const [selectedLot, setSelectedLot] = useState(null)
  const [suggestionsOpen, setSuggestionsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)

  const [activeInstance, setActiveInstance] = useState(null)
  const [usersById, setUsersById] = useState({})
  const [toasts, setToasts] = useState([])

  const toastIdRef = useRef(0)
  const toastTimeoutsRef = useRef([])

  const activeDef = useMemo(
    () => ENTITY_DEFS.find((item) => item.key === entityKey),
    [entityKey],
  )

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
          setActiveInstance((prev) =>
            sameInstance(prev, makeLotInstance(first))
              ? prev
              : makeLotInstance(first),
          )
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
        if (mounted) setLotsLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [pushToast])

  useEffect(() => {
    if (user?.role !== 'admin') return
    let mounted = true
    authService
      .listUsers()
      .then((list) => {
        if (!mounted) return
        setUsersById(Object.fromEntries(list.map((item) => [item.id, item])))
      })
      .catch(() => {})
    return () => {
      mounted = false
    }
  }, [user?.role])

  const setActiveInstanceSmart = useCallback((next) => {
    setActiveInstance((prev) => (sameInstance(prev, next) ? prev : next))
  }, [])

  const setLotSelection = (lot) => {
    const changed = (selectedLot?.id ?? null) !== (lot?.id ?? null)
    setSelectedLot(lot)
    if (entityKey === 'lot') {
      setActiveInstanceSmart(lot ? makeLotInstance(lot) : null)
    } else if (changed) {
      setActiveInstanceSmart(null)
    }
  }

  const lotSuggestions = lots.filter((lot) =>
    lot.lot_code.toLowerCase().includes(lotInput.trim().toLowerCase()),
  )

  const selectLot = (lot) => {
    setLotInput(lot.lot_code)
    setLotSelection(lot)
    setSuggestionsOpen(false)
    setActiveIndex(-1)
  }

  const handleLotInput = (event) => {
    const value = event.target.value
    setLotInput(value)
    setActiveIndex(-1)
    const lot = lots.find((item) => item.lot_code === value) || null
    setLotSelection(lot)
  }

  const handleLotFocus = () => setSuggestionsOpen(true)

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

  const changeEntity = (key) => {
    if (key === entityKey) return
    setEntityKey(key)
    setSuggestionsOpen(false)
    setActiveIndex(-1)
    if (key === 'lot') {
      setActiveInstanceSmart(selectedLot ? makeLotInstance(selectedLot) : null)
    } else {
      setActiveInstanceSmart(null)
    }
  }

  const pickInstance = useCallback((instance) => {
    setActiveInstance((prev) =>
      sameInstance(prev, instance) ? prev : instance,
    )
  }, [])

  const isFeedModule = entityKey === 'feedtype'
  const isLotModule = entityKey === 'lot'
  const isChildModule = !isLotModule && !isFeedModule

  const instanceSelectKey = isFeedModule
    ? 'feedtype'
    : `${entityKey}:${selectedLot ? selectedLot.id : 'none'}`

  const instanceSelectId =
    activeInstance && activeInstance.module === entityKey
      ? activeInstance.id
      : null

  const chainKey = activeInstance
    ? `${activeInstance.module}:${activeInstance.type}:${activeInstance.id}`
    : 'empty'

  return (
    <div className="trace-shell">
      <div className="trace-header-row">
        <PageHeader eyebrow="Trazabilidad" title="Trazabilidad y auditoría" />
      </div>

      <section className="panel trace-filters">
        <div className="trace-filters-top">
          <span className="trace-filters-label">Entidad auditada</span>
          <div
            className="trace-pills"
            role="tablist"
            aria-label="Tipo de entidad"
          >
            {ENTITY_DEFS.map((def) => (
              <button
                key={def.key}
                type="button"
                role="tab"
                aria-selected={entityKey === def.key}
                className={`trace-pill ${entityKey === def.key ? 'is-active' : ''}`}
                onClick={() => changeEntity(def.key)}
              >
                {def.label}
              </button>
            ))}
          </div>
        </div>

        <div className="trace-filters-controls">
          {!isFeedModule && (
            <div className="trace-lot-selector">
              <label className="trace-field-label" htmlFor="trace-lot-input">
                Lote
              </label>
              <div className="trace-autocomplete">
                <input
                  id="trace-lot-input"
                  value={lotInput}
                  onChange={handleLotInput}
                  onFocus={handleLotFocus}
                  onBlur={handleLotBlur}
                  onKeyDown={handleLotKeyDown}
                  placeholder={
                    lotsLoading ? 'Cargando lotes...' : 'Buscar lote por código'
                  }
                  autoComplete="off"
                  role="combobox"
                  aria-expanded={suggestionsOpen}
                  aria-haspopup="listbox"
                />
                {suggestionsOpen && lotSuggestions.length > 0 && (
                  <ul className="trace-suggestions" role="listbox">
                    {lotSuggestions.map((lot, index) => (
                      <li key={lot.id} role="option">
                        <button
                          type="button"
                          className={index === activeIndex ? 'is-active' : ''}
                          onMouseDown={(event) => event.preventDefault()}
                          onClick={() => selectLot(lot)}
                        >
                          <span className="trace-suggestion-code">
                            {lot.lot_code}
                          </span>
                          <span className="trace-suggestion-meta">
                            {lot.breed} · Semana {lot.current_week} ·{' '}
                            {fmtNumber(lot.current_quantity)} aves
                            {!lot.is_active ? ' · Inactivo' : ''}
                          </span>
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}

          {isFeedModule || (isChildModule && selectedLot) ? (
            <InstanceSelect
              key={instanceSelectKey}
              entityKey={entityKey}
              def={activeDef}
              lotId={selectedLot ? selectedLot.id : null}
              selectedId={instanceSelectId}
              onPick={pickInstance}
              onError={pushToast}
            />
          ) : null}

          {isChildModule && !selectedLot && (
            <p className="trace-hint">
              Primero selecciona un lote para ver sus registros.
            </p>
          )}
        </div>
      </section>

      {activeInstance ? (
        <TraceChain
          key={chainKey}
          instance={activeInstance}
          def={activeDef}
          usersById={usersById}
          pushToast={pushToast}
        />
      ) : (
        <section className="panel trace-blocks">
          <p className="trace-muted">
            Selecciona una entidad para consultar su trazabilidad.
          </p>
        </section>
      )}

      <Toast toasts={toasts} onDismiss={dismissToast} />
    </div>
  )
}

export default TraceabilityPage
