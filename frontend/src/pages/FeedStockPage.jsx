/**
 * Página del inventario de insumos (alimentos).
 *
 * Lista los tipos de alimento con su stock actual, costo por kilo y fecha
 * de última actualización. Permite buscar, agregar nuevos alimentos y, por
 * cada fila, editar, añadir stock (con opción de mismo/nuevo precio),
 * suspender/activar o eliminar.
 *
 * @returns {JSX.Element} Página del inventario de alimentos.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Modal from '../components/Modal.jsx'
import PageHeader from '../components/PageHeader.jsx'
import RowMenu from '../components/RowMenu.jsx'
import Toast from '../components/Toast.jsx'
import feedStockService from '../services/feedStockService.js'
import { getErrorMessage } from '../utils/errors.js'
import './FeedStockPage.css'

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

function CreateModal({ onClose, onSubmit }) {
  const [form, setForm] = useState({
    name: '',
    stock_kg: '',
    cost_per_kilo: '',
    min_stock_kg: '',
    entry_date: todayISO(),
  })
  const [errors, setErrors] = useState({})

  const setField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const validate = () => {
    const next = {}
    const stock = form.stock_kg === '' ? 0 : Number(form.stock_kg)
    const cost = form.cost_per_kilo === '' ? null : Number(form.cost_per_kilo)
    const minStock = form.min_stock_kg === '' ? 0 : Number(form.min_stock_kg)

    if (!form.name.trim()) next.name = 'Ingresa el nombre del alimento'
    if (!Number.isFinite(stock) || stock < 0) {
      next.stock_kg = 'Ingresa una cantidad mayor o igual a 0'
    }
    if (form.cost_per_kilo !== '' && (!Number.isFinite(cost) || cost <= 0)) {
      next.cost_per_kilo = 'Ingresa un costo mayor a 0'
    }
    if (!Number.isFinite(minStock) || minStock < 0) {
      next.min_stock_kg = 'Ingresa un valor mayor o igual a 0'
    }
    if (!form.entry_date) next.entry_date = 'La fecha es obligatoria'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!validate()) return
    onSubmit({
      name: form.name.trim(),
      stock_kg: form.stock_kg === '' ? 0 : Number(form.stock_kg),
      cost_per_kilo:
        form.cost_per_kilo === '' ? null : Number(form.cost_per_kilo),
      min_stock_kg: form.min_stock_kg === '' ? 0 : Number(form.min_stock_kg),
      entry_date: form.entry_date,
    })
  }

  return (
    <Modal
      open
      onClose={onClose}
      title="Agregar alimento"
      subtitle="Nuevo tipo de alimento en el inventario"
      footer={
        <div className="app-modal-actions">
          <button type="button" className="app-btn-secondary" onClick={onClose}>
            Cancelar
          </button>
          <button
            type="button"
            className="app-btn-primary"
            onClick={handleSubmit}
          >
            Agregar
          </button>
        </div>
      }
    >
      <form onSubmit={handleSubmit} noValidate className="app-form-stack">
        <div className="app-form-group">
          <label className="app-form-label" htmlFor="create-name">
            Nombre del alimento
          </label>
          <input
            id="create-name"
            className="app-form-control"
            maxLength={50}
            placeholder="Ej: Concentrado"
            value={form.name}
            onChange={(event) => setField('name', event.target.value)}
          />
          {errors.name && <p className="app-form-error">{errors.name}</p>}
        </div>

        <div className="feedstock-form-row">
          <div className="app-form-group">
            <label className="app-form-label" htmlFor="create-stock">
              Kilos iniciales
            </label>
            <input
              id="create-stock"
              className="app-form-control"
              type="number"
              min="0"
              step="0.01"
              placeholder="Ej: 500"
              value={form.stock_kg}
              onChange={(event) => setField('stock_kg', event.target.value)}
            />
            {errors.stock_kg && (
              <p className="app-form-error">{errors.stock_kg}</p>
            )}
          </div>
          <div className="app-form-group">
            <label className="app-form-label" htmlFor="create-cost">
              Costo por kilo
            </label>
            <input
              id="create-cost"
              className="app-form-control"
              type="number"
              min="0"
              step="0.01"
              placeholder="Ej: 2.5"
              value={form.cost_per_kilo}
              onChange={(event) =>
                setField('cost_per_kilo', event.target.value)
              }
            />
            {errors.cost_per_kilo && (
              <p className="app-form-error">{errors.cost_per_kilo}</p>
            )}
          </div>
        </div>

        <div className="feedstock-form-row">
          <div className="app-form-group">
            <label className="app-form-label" htmlFor="create-min">
              Stock mínimo
            </label>
            <input
              id="create-min"
              className="app-form-control"
              type="number"
              min="0"
              step="0.01"
              placeholder="Ej: 50"
              value={form.min_stock_kg}
              onChange={(event) => setField('min_stock_kg', event.target.value)}
            />
            {errors.min_stock_kg && (
              <p className="app-form-error">{errors.min_stock_kg}</p>
            )}
          </div>
          <div className="app-form-group">
            <label className="app-form-label" htmlFor="create-date">
              Fecha del ingreso
            </label>
            <input
              id="create-date"
              className="app-form-control"
              type="date"
              max={todayISO()}
              value={form.entry_date}
              onChange={(event) => setField('entry_date', event.target.value)}
            />
            {errors.entry_date && (
              <p className="app-form-error">{errors.entry_date}</p>
            )}
          </div>
        </div>
      </form>
    </Modal>
  )
}

function EditModal({ feed, onClose, onSubmit }) {
  const [form, setForm] = useState(() => ({
    name: feed.name,
    min_stock_kg: String(feed.min_stock_kg),
  }))
  const [errors, setErrors] = useState({})

  const setField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const validate = () => {
    const next = {}
    const minStock = Number(form.min_stock_kg)
    if (!form.name.trim()) next.name = 'Ingresa el nombre del alimento'
    if (!Number.isFinite(minStock) || minStock < 0) {
      next.min_stock_kg = 'Ingresa un valor mayor o igual a 0'
    }
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!validate()) return
    onSubmit({
      name: form.name.trim(),
      min_stock_kg: Number(form.min_stock_kg),
    })
  }

  return (
    <Modal
      open
      onClose={onClose}
      title={`Editar ${feed?.name || 'alimento'}`}
      subtitle="Cambiar el nombre y el stock mínimo"
      footer={
        <div className="app-modal-actions">
          <button type="button" className="app-btn-secondary" onClick={onClose}>
            Cancelar
          </button>
          <button
            type="button"
            className="app-btn-primary"
            onClick={handleSubmit}
          >
            Guardar
          </button>
        </div>
      }
    >
      <form onSubmit={handleSubmit} noValidate className="app-form-stack">
        <div className="app-form-group">
          <label className="app-form-label" htmlFor="edit-name">
            Nombre del alimento
          </label>
          <input
            id="edit-name"
            className="app-form-control"
            maxLength={50}
            value={form.name}
            onChange={(event) => setField('name', event.target.value)}
          />
          {errors.name && <p className="app-form-error">{errors.name}</p>}
        </div>
        <div className="app-form-group">
          <label className="app-form-label" htmlFor="edit-min">
            Stock mínimo (notificación de stock bajo)
          </label>
          <input
            id="edit-min"
            className="app-form-control"
            type="number"
            min="0"
            step="0.01"
            value={form.min_stock_kg}
            onChange={(event) => setField('min_stock_kg', event.target.value)}
          />
          {errors.min_stock_kg && (
            <p className="app-form-error">{errors.min_stock_kg}</p>
          )}
        </div>
      </form>
    </Modal>
  )
}

function AddStockModal({ feed, onClose, onSubmit }) {
  const [form, setForm] = useState({
    kilos_added: '',
    price_option: 'same',
    cost_per_kilo: '',
    entry_date: todayISO(),
  })
  const [errors, setErrors] = useState({})

  const setField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const validate = () => {
    const next = {}
    const kilos = Number(form.kilos_added)
    const cost = form.cost_per_kilo === '' ? null : Number(form.cost_per_kilo)
    if (!Number.isFinite(kilos) || kilos <= 0) {
      next.kilos_added = 'Ingresa una cantidad mayor a 0'
    }
    if (form.price_option === 'new' && (!Number.isFinite(cost) || cost <= 0)) {
      next.cost_per_kilo = 'Ingresa el nuevo costo por kilo'
    }
    if (!form.entry_date) next.entry_date = 'La fecha es obligatoria'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!validate()) return
    onSubmit({
      kilos_added: Number(form.kilos_added),
      price_option: form.price_option,
      cost_per_kilo:
        form.price_option === 'new' ? Number(form.cost_per_kilo) : null,
      entry_date: form.entry_date,
    })
  }

  return (
    <Modal
      open
      onClose={onClose}
      title={`Añadir stock — ${feed?.name || ''}`}
      subtitle={`Stock actual: ${formatKilos(feed?.stock_kg)}`}
      footer={
        <div className="app-modal-actions">
          <button type="button" className="app-btn-secondary" onClick={onClose}>
            Cancelar
          </button>
          <button
            type="button"
            className="app-btn-primary"
            onClick={handleSubmit}
          >
            Guardar ingreso
          </button>
        </div>
      }
    >
      <form onSubmit={handleSubmit} noValidate className="app-form-stack">
        <div className="app-form-group">
          <label className="app-form-label" htmlFor="addstock-kilos">
            Kilos a ingresar
          </label>
          <input
            id="addstock-kilos"
            className="app-form-control"
            type="number"
            min="0"
            step="0.01"
            placeholder="Ej: 200"
            value={form.kilos_added}
            onChange={(event) => setField('kilos_added', event.target.value)}
          />
          {errors.kilos_added && (
            <p className="app-form-error">{errors.kilos_added}</p>
          )}
        </div>

        <div className="app-form-group">
          <label className="app-form-label">
            Precio del kilo en este ingreso
          </label>
          <div className="feedstock-price-options">
            <label className="app-form-radio">
              <input
                type="radio"
                name="price-option"
                value="same"
                checked={form.price_option === 'same'}
                onChange={() => setField('price_option', 'same')}
              />
              <span>Costó lo mismo que la última vez</span>
              <small>{formatMoney(feed?.cost_per_kilo)}</small>
            </label>
            <label className="app-form-radio">
              <input
                type="radio"
                name="price-option"
                value="new"
                checked={form.price_option === 'new'}
                onChange={() => setField('price_option', 'new')}
              />
              <span>Cambió el precio</span>
            </label>
          </div>
        </div>

        {form.price_option === 'new' && (
          <div className="app-form-group">
            <label className="app-form-label" htmlFor="addstock-cost">
              Nuevo costo por kilo
            </label>
            <input
              id="addstock-cost"
              className="app-form-control"
              type="number"
              min="0"
              step="0.01"
              placeholder="Ej: 3.0"
              value={form.cost_per_kilo}
              onChange={(event) =>
                setField('cost_per_kilo', event.target.value)
              }
            />
            {errors.cost_per_kilo && (
              <p className="app-form-error">{errors.cost_per_kilo}</p>
            )}
          </div>
        )}

        <div className="app-form-group">
          <label className="app-form-label" htmlFor="addstock-date">
            Fecha del ingreso
          </label>
          <input
            id="addstock-date"
            className="app-form-control"
            type="date"
            max={todayISO()}
            value={form.entry_date}
            onChange={(event) => setField('entry_date', event.target.value)}
          />
          {errors.entry_date && (
            <p className="app-form-error">{errors.entry_date}</p>
          )}
        </div>
      </form>
    </Modal>
  )
}

function FeedStockPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const [editFeed, setEditFeed] = useState(null)
  const [addStockFeed, setAddStockFeed] = useState(null)
  const [deleteFeed, setDeleteFeed] = useState(null)
  const [busy, setBusy] = useState(false)
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

  const loadItems = useCallback(
    async (showToast = true) => {
      try {
        const data = await feedStockService.getFeedStock()
        setItems(data)
      } catch (error) {
        if (showToast) {
          pushToast(
            'error',
            getErrorMessage(error, 'No se pudo cargar el inventario'),
          )
        }
      } finally {
        setLoading(false)
      }
    },
    [pushToast],
  )

  useEffect(() => {
    let mounted = true
    feedStockService
      .getFeedStock()
      .then((data) => {
        if (mounted) setItems(data)
      })
      .catch((error) => {
        if (mounted) {
          pushToast(
            'error',
            getErrorMessage(error, 'No se pudo cargar el inventario'),
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

  const filteredItems = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return items
    return items.filter((item) => item.name.toLowerCase().includes(term))
  }, [items, search])

  const handleCreate = async (payload) => {
    setBusy(true)
    try {
      await feedStockService.createFeedType(payload)
      pushToast('success', 'Alimento agregado correctamente.')
      setCreateOpen(false)
      await loadItems(false)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo agregar el alimento'),
      )
    } finally {
      setBusy(false)
    }
  }

  const handleEdit = async (payload) => {
    if (!editFeed) return
    setBusy(true)
    try {
      await feedStockService.updateFeedType(editFeed.id, payload)
      pushToast('success', 'Alimento actualizado correctamente.')
      setEditFeed(null)
      await loadItems(false)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo actualizar el alimento'),
      )
    } finally {
      setBusy(false)
    }
  }

  const handleAddStock = async (payload) => {
    if (!addStockFeed) return
    setBusy(true)
    try {
      const updated = await feedStockService.addStock(addStockFeed.id, payload)
      pushToast(
        'success',
        `Stock actualizado a ${formatKilos(updated.stock_kg)}`,
      )
      setAddStockFeed(null)
      await loadItems(false)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo registrar el ingreso'),
      )
    } finally {
      setBusy(false)
    }
  }

  const handleToggleSuspend = async (feed) => {
    setBusy(true)
    try {
      const updated = await feedStockService.toggleSuspend(feed.id)
      pushToast(
        'success',
        updated.is_active
          ? `${feed.name} reactivado.`
          : `${feed.name} suspendido.`,
      )
      await loadItems(false)
    } catch (error) {
      pushToast('error', getErrorMessage(error, 'No se pudo cambiar el estado'))
    } finally {
      setBusy(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteFeed) return
    setBusy(true)
    try {
      await feedStockService.deleteFeedType(deleteFeed.id)
      pushToast('success', `${deleteFeed.name} eliminado del inventario.`)
      setDeleteFeed(null)
      await loadItems(false)
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo eliminar el alimento'),
      )
    } finally {
      setBusy(false)
    }
  }

  const handleClearSearch = () => setSearch('')

  return (
    <div className="feedstock-shell">
      <PageHeader
        eyebrow="Inventario de Alimentos"
        title="Gestión de insumos"
      />

      <div className="feedstock-toolbar">
        <div className="feedstock-search">
          <input
            type="search"
            placeholder="Buscar por nombre del alimento"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            aria-label="Buscar alimento"
          />
        </div>
        <button
          className="app-btn-secondary feedstock-clear-btn"
          onClick={handleClearSearch}
          disabled={!search}
        >
          Limpiar
        </button>
        <button
          className="app-btn-primary feedstock-create-btn"
          onClick={() => setCreateOpen(true)}
        >
          Agregar alimento
        </button>
      </div>

      <div className="feedstock-table-wrap">
        <table className="feedstock-table">
          <thead>
            <tr>
              <th>Alimento</th>
              <th className="col-desktop">Stock actual</th>
              <th className="col-desktop">Costo por kilo</th>
              <th>Última actualización</th>
              <th className="col-actions">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="table-empty">
                  Cargando...
                </td>
              </tr>
            ) : filteredItems.length === 0 ? (
              <tr>
                <td colSpan={5} className="table-empty">
                  No se encontraron alimentos
                </td>
              </tr>
            ) : (
              filteredItems.map((feed) => (
                <tr key={feed.id}>
                  <td>
                    <div className="feedstock-name-cell">
                      <span className="feedstock-name">{feed.name}</span>
                      <span
                        className={`feedstock-state estado estado-${
                          feed.is_active ? 'activo' : 'descartado'
                        }`}
                      >
                        {feed.is_active ? 'Activo' : 'Suspendido'}
                      </span>
                    </div>
                  </td>
                  <td className="col-desktop">
                    <div className="feedstock-stock-cell">
                      <span>{formatKilos(feed.stock_kg)}</span>
                      {feed.is_low_stock && (
                        <span className="feedstock-low">Stock bajo</span>
                      )}
                    </div>
                  </td>
                  <td className="col-desktop">
                    {formatMoney(feed.cost_per_kilo)}
                  </td>
                  <td>{formatShortDate(feed.last_stock_date)}</td>
                  <td className="col-actions">
                    <RowMenu
                      label={`Acciones de ${feed.name}`}
                      items={[
                        { label: 'Editar', onClick: () => setEditFeed(feed) },
                        {
                          label: 'Añadir stock',
                          onClick: () => setAddStockFeed(feed),
                        },
                        {
                          label: feed.is_active ? 'Suspender' : 'Activar',
                          onClick: () => handleToggleSuspend(feed),
                        },
                        {
                          label: 'Eliminar',
                          danger: true,
                          onClick: () => setDeleteFeed(feed),
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

      {createOpen && (
        <CreateModal
          onClose={() => setCreateOpen(false)}
          onSubmit={handleCreate}
        />
      )}
      {editFeed && (
        <EditModal
          key={editFeed.id}
          feed={editFeed}
          onClose={() => setEditFeed(null)}
          onSubmit={handleEdit}
        />
      )}
      {addStockFeed && (
        <AddStockModal
          key={addStockFeed.id}
          feed={addStockFeed}
          onClose={() => setAddStockFeed(null)}
          onSubmit={handleAddStock}
        />
      )}
      <Modal
        open={!!deleteFeed}
        onClose={() => setDeleteFeed(null)}
        title="Eliminar alimento"
        subtitle={
          deleteFeed ? `Se eliminará "${deleteFeed.name}" del inventario` : ''
        }
        footer={
          <div className="app-modal-actions">
            <button
              type="button"
              className="app-btn-secondary"
              onClick={() => setDeleteFeed(null)}
              disabled={busy}
            >
              Cancelar
            </button>
            <button
              type="button"
              className="app-btn-danger"
              onClick={handleDelete}
              disabled={busy}
            >
              {busy ? 'Eliminando...' : 'Eliminar'}
            </button>
          </div>
        }
      >
        <p className="feedstock-delete-warning">
          Los registros históricos de alimentación conservarán el nombre de este
          alimento. Esta acción no se puede deshacer.
        </p>
      </Modal>

      <Toast toasts={toasts} onDismiss={dismissToast} />
    </div>
  )
}

export default FeedStockPage
