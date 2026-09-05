/**
 * Página del módulo de sanidad.
 *
 * Permite seleccionar un lote y consultar su estado sanitario mediante
 * tarjetas indicadoras (aves actuales, mortalidad, supervivencia y
 * enfermedades activas). En pestañas se administran las vacunas, la
 * mortalidad y las enfermedades: listados, registro de eventos, edición de
 * tratamiento y resolución de enfermedades.
 *
 * @returns {JSX.Element} Página de sanidad.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Modal from '../components/Modal.jsx'
import PageHeader from '../components/PageHeader.jsx'
import RowMenu from '../components/RowMenu.jsx'
import Toast from '../components/Toast.jsx'
import lotService from '../services/lotService.js'
import sanidadService from '../services/sanidadService.js'
import { getErrorMessage } from '../utils/errors.js'
import './SanidadPage.css'

const TOAST_DURATION = 4000

const toISODate = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const todayISO = () => toISODate(new Date())

const formatShortDate = (iso) => {
  if (!iso) return '—'
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y.slice(-2)}`
}

const formatNumber = (value) => {
  const num = Number(value)
  if (Number.isNaN(num)) return '—'
  return num.toLocaleString('es-CO')
}

const emptyToNull = (value) => (value && value.trim() ? value.trim() : null)

const initialVaccineForm = (week) => ({
  vaccine_name: '',
  dosage: '',
  application_date: todayISO(),
  week: String(week ?? ''),
  batch_number: '',
  next_application_date: '',
})

const initialMortalityForm = (week) => ({
  quantity: '',
  cause: '',
  event_date: todayISO(),
  week: String(week ?? ''),
  observations: '',
})

const initialDiseaseForm = () => ({
  diagnosis_date: todayISO(),
  disease_name: '',
  affected_quantity: '',
  symptoms: '',
  treatment: '',
})

function SanidadPage() {
  const [lots, setLots] = useState([])
  const [lotInput, setLotInput] = useState('')
  const [selectedLot, setSelectedLot] = useState(null)
  const [suggestionsOpen, setSuggestionsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const [loadingLots, setLoadingLots] = useState(true)
  const [tab, setTab] = useState('vaccines')
  const [vaccinations, setVaccinations] = useState([])
  const [mortalityRecords, setMortalityRecords] = useState([])
  const [diseases, setDiseases] = useState([])
  const [stats, setStats] = useState(null)
  const [loadingHealth, setLoadingHealth] = useState(true)
  const [cardIndex, setCardIndex] = useState(0)

  const [vaccineOpen, setVaccineOpen] = useState(false)
  const [vaccineForm, setVaccineForm] = useState(initialVaccineForm())
  const [vaccineErrors, setVaccineErrors] = useState({})

  const [mortalityOpen, setMortalityOpen] = useState(false)
  const [mortalityForm, setMortalityForm] = useState(initialMortalityForm())
  const [mortalityErrors, setMortalityErrors] = useState({})

  const [diseaseOpen, setDiseaseOpen] = useState(false)
  const [diseaseForm, setDiseaseForm] = useState(initialDiseaseForm())
  const [diseaseErrors, setDiseaseErrors] = useState({})

  const [editTarget, setEditTarget] = useState(null)
  const [editForm, setEditForm] = useState({})

  const [resolveTarget, setResolveTarget] = useState(null)
  const [busy, setBusy] = useState('')
  const [toasts, setToasts] = useState([])

  const cardsRef = useRef(null)
  const toastIdRef = useRef(0)
  const toastTimeoutsRef = useRef([])
  const healthReqRef = useRef(0)

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

  const fetchHealthData = useCallback(async (lot) => {
    const [vaccinationsData, mortalityData, diseasesData, statsData] =
      await Promise.all([
        sanidadService.listVaccinations(lot.id),
        sanidadService.listMortality(lot.id),
        sanidadService.listDiseases(lot.id),
        sanidadService.mortalityStats(lot.id),
      ])
    return {
      vaccinations: vaccinationsData,
      mortality: mortalityData,
      diseases: diseasesData,
      stats: statsData,
    }
  }, [])

  const applyHealthData = useCallback((data) => {
    setVaccinations(data.vaccinations)
    setMortalityRecords(data.mortality)
    setDiseases(data.diseases)
    setStats(data.stats)
  }, [])

  const reloadHealth = useCallback(
    async (lot) => {
      const requestId = ++healthReqRef.current
      try {
        const data = await fetchHealthData(lot)
        if (requestId !== healthReqRef.current) return
        applyHealthData(data)
      } catch (error) {
        if (requestId === healthReqRef.current) {
          pushToast(
            'error',
            getErrorMessage(error, 'No se pudieron cargar los datos del lote'),
          )
          applyHealthData({
            vaccinations: [],
            mortality: [],
            diseases: [],
            stats: null,
          })
        }
      } finally {
        if (requestId === healthReqRef.current) setLoadingHealth(false)
      }
    },
    [fetchHealthData, applyHealthData, pushToast],
  )

  useEffect(() => {
    if (!selectedLot) return
    let active = true
    fetchHealthData(selectedLot)
      .then((data) => {
        if (!active) return
        applyHealthData(data)
      })
      .catch((error) => {
        if (!active) return
        pushToast(
          'error',
          getErrorMessage(error, 'No se pudieron cargar los datos del lote'),
        )
        applyHealthData({
          vaccinations: [],
          mortality: [],
          diseases: [],
          stats: null,
        })
      })
      .finally(() => {
        if (active) setLoadingHealth(false)
      })
    return () => {
      active = false
    }
  }, [selectedLot, fetchHealthData, applyHealthData, pushToast])

  const updateLotInState = useCallback((fresh) => {
    setSelectedLot(fresh)
    setLotInput(fresh.lot_code)
    setLots((prev) => prev.map((lot) => (lot.id === fresh.id ? fresh : lot)))
  }, [])

  const lotSuggestions = lots.filter((lot) =>
    lot.lot_code.toLowerCase().includes(lotInput.trim().toLowerCase()),
  )

  const clearLotData = () => {
    setSelectedLot(null)
    setVaccinations([])
    setMortalityRecords([])
    setDiseases([])
    setStats(null)
  }

  const selectLot = (lot) => {
    setLotInput(lot.lot_code)
    if (selectedLot?.id !== lot.id) {
      setSelectedLot(lot)
      setLoadingHealth(true)
      setTab('vaccines')
    }
    setSuggestionsOpen(false)
    setActiveIndex(-1)
  }

  const handleLotInput = (event) => {
    const value = event.target.value
    setLotInput(value)
    setActiveIndex(-1)
    const lot = lots.find((item) => item.lot_code === value)
    if (lot) {
      if (selectedLot?.id !== lot.id) {
        setSelectedLot(lot)
        setLoadingHealth(true)
      }
      setSuggestionsOpen(true)
    } else {
      clearLotData()
    }
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

  // ============================ Tarjetas ============================

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

  const totalMortality = mortalityRecords.reduce(
    (acc, record) => acc + record.quantity,
    0,
  )
  const activeDiseases = diseases.filter((disease) => !disease.is_resolved)

  const cards = useMemo(() => {
    if (!selectedLot) return []
    return [
      {
        label: 'Aves actuales',
        value: formatNumber(selectedLot.current_quantity),
        sub: `de ${formatNumber(selectedLot.initial_quantity)} iniciales`,
        icon: 'INVENTARIO_AVES.svg',
        alt: 'Aves actuales',
      },
      {
        label: 'Mortalidad',
        value: stats ? `${stats.mortality_percentage.toFixed(1)}%` : '—',
        sub: `${formatNumber(totalMortality)} aves perdidas`,
        icon: 'SANIDAD.svg',
        alt: 'Porcentaje de mortalidad',
      },
      {
        label: 'Supervivencia',
        value: stats ? `${stats.survival_percentage.toFixed(1)}%` : '—',
        sub: 'Aves actuales vs iniciales',
        icon: 'MONITOREO_IOT.svg',
        alt: 'Porcentaje de supervivencia',
      },
      {
        label: 'Enfermedades activas',
        value: activeDiseases.length,
        sub: `${diseases.length} registradas en total`,
        icon: 'PRODUCCION_DIARIA.svg',
        alt: 'Enfermedades activas',
      },
    ]
  }, [selectedLot, stats, totalMortality, activeDiseases, diseases])

  // ============================ Vacunas ============================

  const openVaccineModal = () => {
    if (!selectedLot) return
    setVaccineForm(initialVaccineForm(selectedLot.current_week))
    setVaccineErrors({})
    setVaccineOpen(true)
  }

  const setVaccineField = (field, value) => {
    setVaccineForm((prev) => ({ ...prev, [field]: value }))
    setVaccineErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const validateVaccine = () => {
    const next = {}
    if (!vaccineForm.vaccine_name.trim()) {
      next.vaccine_name = 'El nombre de la vacuna es obligatorio'
    }
    if (!vaccineForm.dosage.trim()) {
      next.dosage = 'La dosis es obligatoria'
    }
    if (!vaccineForm.application_date) {
      next.application_date = 'La fecha de aplicación es obligatoria'
    }
    const week = Number(vaccineForm.week)
    if (vaccineForm.week === '' || !Number.isInteger(week) || week <= 0) {
      next.week = 'La semana debe ser un número mayor a 0'
    }
    setVaccineErrors(next)
    return Object.keys(next).length === 0
  }

  const handleVaccineSubmit = async (event) => {
    event.preventDefault()
    if (!selectedLot) return
    if (!validateVaccine()) return
    setBusy('vaccine')
    const payload = {
      vaccine_name: vaccineForm.vaccine_name.trim(),
      dosage: vaccineForm.dosage.trim(),
      application_date: vaccineForm.application_date,
      week: Number(vaccineForm.week),
      batch_number: emptyToNull(vaccineForm.batch_number),
      next_application_date:
        emptyToNull(vaccineForm.next_application_date) || null,
    }
    try {
      await sanidadService.registerVaccination(selectedLot.id, payload)
      pushToast('success', 'Vacuna registrada correctamente.')
      setVaccineOpen(false)
      setLoadingHealth(true)
      await reloadHealth(selectedLot)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo registrar la vacuna'),
      )
    } finally {
      setBusy('')
    }
  }

  // ============================ Mortalidad ============================

  const openMortalityModal = () => {
    if (!selectedLot) return
    setMortalityForm(initialMortalityForm(selectedLot.current_week))
    setMortalityErrors({})
    setMortalityOpen(true)
  }

  const setMortalityField = (field, value) => {
    setMortalityForm((prev) => ({ ...prev, [field]: value }))
    setMortalityErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const validateMortality = () => {
    const next = {}
    const quantity = Number(mortalityForm.quantity)
    if (
      mortalityForm.quantity === '' ||
      !Number.isInteger(quantity) ||
      quantity <= 0
    ) {
      next.quantity = 'La cantidad debe ser mayor a 0'
    } else if (selectedLot && quantity > selectedLot.current_quantity) {
      next.quantity = `No puede exceder las ${selectedLot.current_quantity} aves actuales`
    }
    if (!mortalityForm.cause.trim()) {
      next.cause = 'La causa es obligatoria'
    }
    if (!mortalityForm.event_date) {
      next.event_date = 'La fecha es obligatoria'
    }
    const week = Number(mortalityForm.week)
    if (mortalityForm.week === '' || !Number.isInteger(week) || week <= 0) {
      next.week = 'La semana debe ser un número mayor a 0'
    }
    setMortalityErrors(next)
    return Object.keys(next).length === 0
  }

  const handleMortalitySubmit = async (event) => {
    event.preventDefault()
    if (!selectedLot) return
    if (!validateMortality()) return
    setBusy('mortality')
    const payload = {
      quantity: Number(mortalityForm.quantity),
      cause: mortalityForm.cause.trim(),
      event_date: mortalityForm.event_date,
      week: Number(mortalityForm.week),
      observations: emptyToNull(mortalityForm.observations),
    }
    const wasActive = selectedLot.is_active
    try {
      await sanidadService.registerMortality(selectedLot.id, payload)
      pushToast('success', 'Mortalidad registrada correctamente.')
      setMortalityOpen(false)
      const fresh = await lotService.getLot(selectedLot.id)
      setLoadingHealth(true)
      updateLotInState(fresh)
      if (wasActive && !fresh.is_active) {
        pushToast(
          'info',
          'El lote quedó sin aves y fue desactivado automáticamente.',
        )
      }
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo registrar la mortalidad'),
      )
    } finally {
      setBusy('')
    }
  }

  // ============================ Enfermedades ============================

  const openDiseaseModal = () => {
    setDiseaseForm(initialDiseaseForm())
    setDiseaseErrors({})
    setDiseaseOpen(true)
  }

  const setDiseaseField = (field, value) => {
    setDiseaseForm((prev) => ({ ...prev, [field]: value }))
    setDiseaseErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const validateDisease = () => {
    const next = {}
    if (!diseaseForm.disease_name.trim()) {
      next.disease_name = 'El nombre de la enfermedad es obligatorio'
    }
    const affected = Number(diseaseForm.affected_quantity)
    if (
      diseaseForm.affected_quantity === '' ||
      !Number.isInteger(affected) ||
      affected <= 0
    ) {
      next.affected_quantity = 'La cantidad debe ser mayor a 0'
    }
    if (!diseaseForm.diagnosis_date) {
      next.diagnosis_date = 'La fecha de diagnóstico es obligatoria'
    }
    setDiseaseErrors(next)
    return Object.keys(next).length === 0
  }

  const handleDiseaseSubmit = async (event) => {
    event.preventDefault()
    if (!selectedLot) return
    if (!validateDisease()) return
    setBusy('disease')
    const payload = {
      diagnosis_date: diseaseForm.diagnosis_date,
      disease_name: diseaseForm.disease_name.trim(),
      affected_quantity: Number(diseaseForm.affected_quantity),
      symptoms: emptyToNull(diseaseForm.symptoms),
      treatment: emptyToNull(diseaseForm.treatment),
    }
    try {
      await sanidadService.registerDisease(selectedLot.id, payload)
      pushToast('success', 'Enfermedad registrada correctamente.')
      setDiseaseOpen(false)
      setLoadingHealth(true)
      await reloadHealth(selectedLot)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo registrar la enfermedad'),
      )
    } finally {
      setBusy('')
    }
  }

  const openEditDisease = (disease) => {
    setEditTarget(disease)
    setEditForm({
      symptoms: disease.symptoms || '',
      treatment: disease.treatment || '',
      treatment_start_date: disease.treatment_start_date || '',
      treatment_end_date: disease.treatment_end_date || '',
    })
  }

  const setEditField = (field, value) => {
    setEditForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleEditSubmit = async (event) => {
    event.preventDefault()
    if (!selectedLot || !editTarget) return
    setBusy('edit')
    const payload = {
      symptoms: emptyToNull(editForm.symptoms),
      treatment: emptyToNull(editForm.treatment),
      treatment_start_date: emptyToNull(editForm.treatment_start_date),
      treatment_end_date: emptyToNull(editForm.treatment_end_date),
    }
    try {
      await sanidadService.updateDisease(selectedLot.id, editTarget.id, payload)
      pushToast('success', 'Tratamiento actualizado correctamente.')
      setEditTarget(null)
      setLoadingHealth(true)
      await reloadHealth(selectedLot)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo actualizar el tratamiento'),
      )
    } finally {
      setBusy('')
    }
  }

  const handleResolveConfirm = async () => {
    if (!selectedLot || !resolveTarget) return
    setBusy('resolve')
    try {
      await sanidadService.resolveDisease(selectedLot.id, resolveTarget.id)
      pushToast('success', 'Enfermedad marcada como resuelta.')
      setResolveTarget(null)
      setLoadingHealth(true)
      await reloadHealth(selectedLot)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo resolver la enfermedad'),
      )
    } finally {
      setBusy('')
    }
  }

  const isEmpty = (list) => list.length === 0

  const EmptyRow = ({ colSpan, children }) => (
    <tr>
      <td className="table-empty" colSpan={colSpan}>
        {children}
      </td>
    </tr>
  )

  const renderVaccineTable = () => (
    <div className="table-wrap">
      <table className="sanidad-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Semana</th>
            <th>Vacuna</th>
            <th>Dosis</th>
            <th className="col-desktop">Lote biológico</th>
            <th className="col-desktop">Próxima aplicación</th>
          </tr>
        </thead>
        <tbody>
          {loadingHealth ? (
            <EmptyRow colSpan={6}>Cargando...</EmptyRow>
          ) : isEmpty(vaccinations) ? (
            <EmptyRow colSpan={6}>No hay vacunas registradas</EmptyRow>
          ) : (
            vaccinations.map((record) => (
              <tr key={record.id}>
                <td>{formatShortDate(record.application_date)}</td>
                <td>Semana {record.week}</td>
                <td className="truncate">{record.vaccine_name}</td>
                <td>{record.dosage}</td>
                <td className="col-desktop">{record.batch_number || '—'}</td>
                <td className="col-desktop">
                  {formatShortDate(record.next_application_date)}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )

  const renderMortalityTable = () => (
    <div className="table-wrap">
      <table className="sanidad-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Semana</th>
            <th>Cantidad</th>
            <th>Causa</th>
            <th className="col-desktop">Observaciones</th>
          </tr>
        </thead>
        <tbody>
          {loadingHealth ? (
            <EmptyRow colSpan={5}>Cargando...</EmptyRow>
          ) : isEmpty(mortalityRecords) ? (
            <EmptyRow colSpan={5}>No se han registrado mortalidades</EmptyRow>
          ) : (
            mortalityRecords.map((record) => (
              <tr key={record.id}>
                <td>{formatShortDate(record.event_date)}</td>
                <td>Semana {record.week}</td>
                <td>{record.quantity}</td>
                <td className="truncate">{record.cause}</td>
                <td className="col-desktop truncate">
                  {record.observations || '—'}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )

  const renderDiseasesTable = () => (
    <div className="table-wrap">
      <table className="sanidad-table">
        <thead>
          <tr>
            <th className="col-desktop">Diagnóstico</th>
            <th>Enfermedad</th>
            <th>Afectadas</th>
            <th className="col-desktop">Tratamiento</th>
            <th>Estado</th>
            <th className="col-actions">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {loadingHealth ? (
            <EmptyRow colSpan={6}>Cargando...</EmptyRow>
          ) : isEmpty(diseases) ? (
            <EmptyRow colSpan={6}>No hay enfermedades registradas</EmptyRow>
          ) : (
            diseases.map((disease) => (
              <tr key={disease.id}>
                <td className="col-desktop">
                  {formatShortDate(disease.diagnosis_date)}
                </td>
                <td className="truncate">{disease.disease_name}</td>
                <td>{disease.affected_quantity}</td>
                <td className="col-desktop truncate">
                  {disease.treatment || '—'}
                </td>
                <td>
                  <span
                    className={`sanidad-pill ${
                      disease.is_resolved
                        ? 'sanidad-pill-green'
                        : 'sanidad-pill-red'
                    }`}
                  >
                    {disease.is_resolved ? 'Resuelta' : 'Activa'}
                  </span>
                </td>
                <td className="col-actions">
                  <RowMenu
                    label="Acciones de enfermedad"
                    items={[
                      {
                        label: 'Editar tratamiento',
                        onClick: () => openEditDisease(disease),
                      },
                      ...(disease.is_resolved
                        ? []
                        : [
                            {
                              label: 'Marcar como resuelta',
                              onClick: () => setResolveTarget(disease),
                            },
                          ]),
                    ]}
                  />
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )

  const lotStatePill =
    selectedLot &&
    (selectedLot.is_active ? (
      <span className="sanidad-pill sanidad-pill-green">Activo</span>
    ) : (
      <span className="sanidad-pill sanidad-pill-gray">Descartado</span>
    ))

  return (
    <div className="sanidad-shell">
      <div className="sanidad-header-row">
        <PageHeader eyebrow="Sanidad" title="Panel de sanidad" />
        <div className="sanidad-selector">
          <label htmlFor="sanidad-lot-input">Lote</label>
          <div className="sanidad-autocomplete">
            <input
              id="sanidad-lot-input"
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
              <ul className="sanidad-suggestions" role="listbox">
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
                      <span className="sanidad-suggestion-code">
                        {lot.lot_code}
                      </span>
                      <span className="sanidad-suggestion-meta">
                        {lot.breed} · Semana {lot.current_week} ·{' '}
                        {lot.current_quantity} aves
                        {!lot.is_active ? ' · Inactivo' : ''}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <span className="sanidad-date-chip">
            {formatShortDate(todayISO())}
          </span>
        </div>
      </div>

      {selectedLot && (
        <>
          <div className="sanidad-lot-info">
            <span className="chip">
              {selectedLot.lot_code} · {selectedLot.breed}
            </span>
            <span className="sanidad-lot-week">
              Semana {selectedLot.current_week} · {selectedLot.current_quantity}{' '}
              aves
            </span>
            {lotStatePill}
          </div>

          {!selectedLot.is_active && (
            <p className="sanidad-inactive-note">
              <strong>Lote inactivo:</strong>
              {selectedLot.discard_reason
                ? ` ${selectedLot.discard_reason}.`
                : ' Este lote fue descartado.'}{' '}
              Solo se permite consultar su historial y registrar enfermedades.
            </p>
          )}

          <div className="carousel-container">
            <section
              className="content-cards"
              ref={cardsRef}
              onScroll={handleCardsScroll}
            >
              {cards.map((card) => (
                <article key={card.label} className="card">
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
                  className={`pagination-dot ${
                    index === cardIndex ? 'active' : ''
                  }`}
                  onClick={() => goToCard(index)}
                  aria-label={`Ir a tarjeta ${index + 1}`}
                ></button>
              ))}
            </div>
          </div>

          <div className="sanidad-tabs" role="tablist" aria-label="Secciones">
            {[
              { key: 'vaccines', label: 'Vacunas', count: vaccinations.length },
              {
                key: 'mortality',
                label: 'Mortalidad',
                count: mortalityRecords.length,
              },
              {
                key: 'diseases',
                label: 'Enfermedades',
                count: diseases.length,
              },
            ].map((item) => (
              <button
                key={item.key}
                type="button"
                role="tab"
                aria-selected={tab === item.key}
                className={`sanidad-tab ${tab === item.key ? 'is-active' : ''}`}
                onClick={() => setTab(item.key)}
              >
                {item.label}
                <span className="sanidad-tab-count">{item.count}</span>
              </button>
            ))}
          </div>

          {tab === 'vaccines' && (
            <section className="panel sanidad-panel">
              <div className="panel-header">
                <div>
                  <p className="eyebrow">Vacunación</p>
                  <h2>Vacunas aplicadas</h2>
                </div>
                {selectedLot.is_active && (
                  <div className="sanidad-panel-actions">
                    <button
                      type="button"
                      className="app-btn-primary"
                      onClick={openVaccineModal}
                      disabled={!!busy}
                    >
                      Registrar vacuna
                    </button>
                  </div>
                )}
              </div>
              {renderVaccineTable()}
            </section>
          )}

          {tab === 'mortality' && (
            <section className="panel sanidad-panel">
              <div className="panel-header">
                <div>
                  <p className="eyebrow">Mortalidad</p>
                  <h2>Registro de mortalidad</h2>
                </div>
                {selectedLot.is_active && (
                  <div className="sanidad-panel-actions">
                    <button
                      type="button"
                      className="app-btn-primary"
                      onClick={openMortalityModal}
                      disabled={!!busy}
                    >
                      Registrar mortalidad
                    </button>
                  </div>
                )}
              </div>
              {renderMortalityTable()}
            </section>
          )}

          {tab === 'diseases' && (
            <section className="panel sanidad-panel">
              <div className="panel-header">
                <div>
                  <p className="eyebrow">Enfermedades</p>
                  <h2>Registro de enfermedades</h2>
                </div>
                <div className="sanidad-panel-actions">
                  <button
                    type="button"
                    className="app-btn-primary"
                    onClick={openDiseaseModal}
                    disabled={!!busy}
                  >
                    Registrar enfermedad
                  </button>
                </div>
              </div>
              {renderDiseasesTable()}
            </section>
          )}
        </>
      )}

      <Modal
        open={vaccineOpen}
        onClose={() => setVaccineOpen(false)}
        title="Registrar vacuna"
        subtitle={
          selectedLot
            ? `Lote ${selectedLot.lot_code} · Semana ${selectedLot.current_week}`
            : undefined
        }
      >
        <form onSubmit={handleVaccineSubmit} noValidate>
          <div className="app-form-stack">
            <div className="sanidad-form-row">
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="vac-vaccine-name">
                  Nombre de la vacuna
                </label>
                <input
                  id="vac-vaccine-name"
                  className="app-form-control"
                  type="text"
                  maxLength={100}
                  placeholder="Ej: Newcastle"
                  value={vaccineForm.vaccine_name}
                  onChange={(event) =>
                    setVaccineField('vaccine_name', event.target.value)
                  }
                />
                {vaccineErrors.vaccine_name && (
                  <p className="app-form-error">{vaccineErrors.vaccine_name}</p>
                )}
              </div>
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="vac-dosage">
                  Dosis
                </label>
                <input
                  id="vac-dosage"
                  className="app-form-control"
                  type="text"
                  maxLength={50}
                  placeholder="Ej: 0.5 ml"
                  value={vaccineForm.dosage}
                  onChange={(event) =>
                    setVaccineField('dosage', event.target.value)
                  }
                />
                {vaccineErrors.dosage && (
                  <p className="app-form-error">{vaccineErrors.dosage}</p>
                )}
              </div>
            </div>

            <div className="sanidad-form-row">
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="vac-date">
                  Fecha de aplicación
                </label>
                <input
                  id="vac-date"
                  className="app-form-control"
                  type="date"
                  value={vaccineForm.application_date}
                  onChange={(event) =>
                    setVaccineField('application_date', event.target.value)
                  }
                />
                {vaccineErrors.application_date && (
                  <p className="app-form-error">
                    {vaccineErrors.application_date}
                  </p>
                )}
              </div>
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="vac-week">
                  Semana del ciclo
                </label>
                <input
                  id="vac-week"
                  className="app-form-control"
                  type="number"
                  min="1"
                  step="1"
                  value={vaccineForm.week}
                  onChange={(event) =>
                    setVaccineField('week', event.target.value)
                  }
                />
                {vaccineErrors.week && (
                  <p className="app-form-error">{vaccineErrors.week}</p>
                )}
              </div>
            </div>

            <div className="sanidad-form-row">
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="vac-batch">
                  Lote del biológico
                </label>
                <input
                  id="vac-batch"
                  className="app-form-control"
                  type="text"
                  maxLength={50}
                  placeholder="Opcional"
                  value={vaccineForm.batch_number}
                  onChange={(event) =>
                    setVaccineField('batch_number', event.target.value)
                  }
                />
              </div>
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="vac-next">
                  Próxima aplicación
                </label>
                <input
                  id="vac-next"
                  className="app-form-control"
                  type="date"
                  value={vaccineForm.next_application_date}
                  onChange={(event) =>
                    setVaccineField('next_application_date', event.target.value)
                  }
                />
              </div>
            </div>
          </div>

          <div className="app-modal-actions">
            <button
              type="button"
              className="app-btn-secondary"
              onClick={() => setVaccineOpen(false)}
              disabled={!!busy}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="app-btn-primary"
              disabled={busy === 'vaccine'}
            >
              {busy === 'vaccine' ? 'Guardando...' : 'Registrar vacuna'}
            </button>
          </div>
        </form>
      </Modal>

      <Modal
        open={mortalityOpen}
        onClose={() => setMortalityOpen(false)}
        title="Registrar mortalidad"
        subtitle={
          selectedLot
            ? `Lote ${selectedLot.lot_code} · ${selectedLot.current_quantity} aves actuales`
            : undefined
        }
      >
        <form onSubmit={handleMortalitySubmit} noValidate>
          <div className="app-form-stack">
            <div className="sanidad-form-row">
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="mor-quantity">
                  Cantidad de aves
                </label>
                <input
                  id="mor-quantity"
                  className="app-form-control"
                  type="number"
                  min="1"
                  max={selectedLot?.current_quantity}
                  step="1"
                  placeholder="Ej: 5"
                  value={mortalityForm.quantity}
                  onChange={(event) =>
                    setMortalityField('quantity', event.target.value)
                  }
                />
                {mortalityErrors.quantity && (
                  <p className="app-form-error">{mortalityErrors.quantity}</p>
                )}
              </div>
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="mor-week">
                  Semana del ciclo
                </label>
                <input
                  id="mor-week"
                  className="app-form-control"
                  type="number"
                  min="1"
                  step="1"
                  value={mortalityForm.week}
                  onChange={(event) =>
                    setMortalityField('week', event.target.value)
                  }
                />
                {mortalityErrors.week && (
                  <p className="app-form-error">{mortalityErrors.week}</p>
                )}
              </div>
            </div>

            <div className="app-form-group">
              <label className="app-form-label" htmlFor="mor-cause">
                Causa
              </label>
              <input
                id="mor-cause"
                className="app-form-control"
                type="text"
                maxLength={200}
                placeholder="Ej: Enfermedad respiratoria"
                value={mortalityForm.cause}
                onChange={(event) =>
                  setMortalityField('cause', event.target.value)
                }
              />
              {mortalityErrors.cause && (
                <p className="app-form-error">{mortalityErrors.cause}</p>
              )}
            </div>

            <div className="app-form-group">
              <label className="app-form-label" htmlFor="mor-date">
                Fecha del evento
              </label>
              <input
                id="mor-date"
                className="app-form-control"
                type="date"
                value={mortalityForm.event_date}
                onChange={(event) =>
                  setMortalityField('event_date', event.target.value)
                }
              />
              {mortalityErrors.event_date && (
                <p className="app-form-error">{mortalityErrors.event_date}</p>
              )}
            </div>

            <div className="app-form-group">
              <label className="app-form-label" htmlFor="mor-observations">
                Observaciones
              </label>
              <textarea
                id="mor-observations"
                className="app-form-control"
                rows={3}
                maxLength={500}
                placeholder="Detalles del evento"
                value={mortalityForm.observations}
                onChange={(event) =>
                  setMortalityField('observations', event.target.value)
                }
              />
            </div>
          </div>

          <div className="app-modal-actions">
            <button
              type="button"
              className="app-btn-secondary"
              onClick={() => setMortalityOpen(false)}
              disabled={!!busy}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="app-btn-primary"
              disabled={busy === 'mortality'}
            >
              {busy === 'mortality' ? 'Guardando...' : 'Registrar mortalidad'}
            </button>
          </div>
        </form>
      </Modal>

      <Modal
        open={diseaseOpen}
        onClose={() => setDiseaseOpen(false)}
        title="Registrar enfermedad"
        subtitle={selectedLot ? `Lote ${selectedLot.lot_code}` : undefined}
      >
        <form onSubmit={handleDiseaseSubmit} noValidate>
          <div className="app-form-stack">
            <div className="sanidad-form-row">
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="dis-date">
                  Fecha de diagnóstico
                </label>
                <input
                  id="dis-date"
                  className="app-form-control"
                  type="date"
                  value={diseaseForm.diagnosis_date}
                  onChange={(event) =>
                    setDiseaseField('diagnosis_date', event.target.value)
                  }
                />
                {diseaseErrors.diagnosis_date && (
                  <p className="app-form-error">
                    {diseaseErrors.diagnosis_date}
                  </p>
                )}
              </div>
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="dis-affected">
                  Aves afectadas
                </label>
                <input
                  id="dis-affected"
                  className="app-form-control"
                  type="number"
                  min="1"
                  step="1"
                  placeholder="Ej: 12"
                  value={diseaseForm.affected_quantity}
                  onChange={(event) =>
                    setDiseaseField('affected_quantity', event.target.value)
                  }
                />
                {diseaseErrors.affected_quantity && (
                  <p className="app-form-error">
                    {diseaseErrors.affected_quantity}
                  </p>
                )}
              </div>
            </div>

            <div className="app-form-group">
              <label className="app-form-label" htmlFor="dis-name">
                Nombre de la enfermedad
              </label>
              <input
                id="dis-name"
                className="app-form-control"
                type="text"
                maxLength={100}
                placeholder="Ej: New Castle"
                value={diseaseForm.disease_name}
                onChange={(event) =>
                  setDiseaseField('disease_name', event.target.value)
                }
              />
              {diseaseErrors.disease_name && (
                <p className="app-form-error">{diseaseErrors.disease_name}</p>
              )}
            </div>

            <div className="app-form-group">
              <label className="app-form-label" htmlFor="dis-symptoms">
                Síntomas observados
              </label>
              <textarea
                id="dis-symptoms"
                className="app-form-control"
                rows={3}
                maxLength={500}
                placeholder="Síntomas detectados"
                value={diseaseForm.symptoms}
                onChange={(event) =>
                  setDiseaseField('symptoms', event.target.value)
                }
              />
            </div>

            <div className="app-form-group">
              <label className="app-form-label" htmlFor="dis-treatment">
                Tratamiento aplicado
              </label>
              <textarea
                id="dis-treatment"
                className="app-form-control"
                rows={3}
                maxLength={500}
                placeholder="Tratamiento y medicación"
                value={diseaseForm.treatment}
                onChange={(event) =>
                  setDiseaseField('treatment', event.target.value)
                }
              />
            </div>
          </div>

          <div className="app-modal-actions">
            <button
              type="button"
              className="app-btn-secondary"
              onClick={() => setDiseaseOpen(false)}
              disabled={!!busy}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="app-btn-primary"
              disabled={busy === 'disease'}
            >
              {busy === 'disease' ? 'Guardando...' : 'Registrar enfermedad'}
            </button>
          </div>
        </form>
      </Modal>

      <Modal
        open={!!editTarget}
        onClose={() => setEditTarget(null)}
        title="Editar tratamiento"
        subtitle={
          editTarget
            ? `${editTarget.disease_name} · Lote ${selectedLot?.lot_code}`
            : undefined
        }
      >
        <form onSubmit={handleEditSubmit} noValidate>
          <div className="app-form-stack">
            <div className="app-form-group">
              <label className="app-form-label" htmlFor="edit-symptoms">
                Síntomas observados
              </label>
              <textarea
                id="edit-symptoms"
                className="app-form-control"
                rows={3}
                maxLength={500}
                value={editForm.symptoms || ''}
                onChange={(event) =>
                  setEditField('symptoms', event.target.value)
                }
              />
            </div>

            <div className="app-form-group">
              <label className="app-form-label" htmlFor="edit-treatment">
                Tratamiento aplicado
              </label>
              <textarea
                id="edit-treatment"
                className="app-form-control"
                rows={3}
                maxLength={500}
                value={editForm.treatment || ''}
                onChange={(event) =>
                  setEditField('treatment', event.target.value)
                }
              />
            </div>

            <div className="sanidad-form-row">
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="edit-start">
                  Inicio del tratamiento
                </label>
                <input
                  id="edit-start"
                  className="app-form-control"
                  type="date"
                  value={editForm.treatment_start_date || ''}
                  onChange={(event) =>
                    setEditField('treatment_start_date', event.target.value)
                  }
                />
              </div>
              <div className="app-form-group">
                <label className="app-form-label" htmlFor="edit-end">
                  Fin del tratamiento
                </label>
                <input
                  id="edit-end"
                  className="app-form-control"
                  type="date"
                  value={editForm.treatment_end_date || ''}
                  onChange={(event) =>
                    setEditField('treatment_end_date', event.target.value)
                  }
                />
              </div>
            </div>
          </div>

          <div className="app-modal-actions">
            <button
              type="button"
              className="app-btn-secondary"
              onClick={() => setEditTarget(null)}
              disabled={!!busy}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="app-btn-primary"
              disabled={busy === 'edit'}
            >
              {busy === 'edit' ? 'Guardando...' : 'Guardar cambios'}
            </button>
          </div>
        </form>
      </Modal>

      <Modal
        open={!!resolveTarget}
        onClose={() => setResolveTarget(null)}
        title="Marcar enfermedad como resuelta"
        subtitle="Esta acción no se puede deshacer desde el módulo"
        footer={
          <div className="app-modal-actions">
            <button
              type="button"
              className="app-btn-secondary"
              onClick={() => setResolveTarget(null)}
              disabled={!!busy}
            >
              Cancelar
            </button>
            <button
              type="button"
              className="app-btn-primary"
              onClick={handleResolveConfirm}
              disabled={busy === 'resolve'}
            >
              {busy === 'resolve' ? 'Guardando...' : 'Confirmar'}
            </button>
          </div>
        }
      >
        {resolveTarget && (
          <div className="merge-detail">
            <div className="summary-item">
              <span>Enfermedad</span>
              <strong>{resolveTarget.disease_name}</strong>
            </div>
            <div className="summary-item">
              <span>Diagnóstico</span>
              <strong>{formatShortDate(resolveTarget.diagnosis_date)}</strong>
            </div>
            <div className="summary-item">
              <span>Aves afectadas</span>
              <strong>{resolveTarget.affected_quantity}</strong>
            </div>
          </div>
        )}
      </Modal>

      <Toast toasts={toasts} onDismiss={dismissToast} />
    </div>
  )
}

export default SanidadPage
