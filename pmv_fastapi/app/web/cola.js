/* Cola de operaciones sin conexión (HIST-3.1). Las operaciones se guardan en el dispositivo (IndexedDB, almacén
   «pendientes») con un id_operacion UUID, el id del dispositivo y la fecha local, y se envían al reconectar (sync.js).
   Si IndexedDB no está disponible (p. ej. navegación privada) se usa memoria: la app funciona, pero lo pendiente se
   pierde al cerrar la pestaña, y la interfaz lo avisa. */
window.Cola = (() => {
  const NOMBRE = "anemia-junin", VERSION = 1;
  const memoria = { pendientes: new Map(), meta: new Map() };
  let abierta = null, persistente = true;

  const pedir = (r) => new Promise((ok, fallo) => { r.onsuccess = () => ok(r.result); r.onerror = () => fallo(r.error); });
  function abrir() {
    if (!abierta) {
      abierta = new Promise((ok, fallo) => {
        try {
          const r = indexedDB.open(NOMBRE, VERSION);
          r.onupgradeneeded = () => {
            r.result.createObjectStore("pendientes", { keyPath: "id_operacion" });
            r.result.createObjectStore("meta", { keyPath: "clave" });
          };
          r.onsuccess = () => ok(r.result);
          r.onerror = () => fallo(r.error);
          r.onblocked = () => fallo(new Error("IndexedDB bloqueada"));
        } catch (e) { fallo(e); }
      }).catch(() => { persistente = false; return null; });
    }
    return abierta;
  }
  /* Acceso uniforme a un almacén: IndexedDB o, si no existe, el mapa en memoria. */
  async function almacen(nombre, modo = "readonly") {
    const db = await abrir();
    const clave = nombre === "meta" ? "clave" : "id_operacion";
    if (!db) {
      const m = memoria[nombre];
      return {
        get: async (k) => m.get(k), getAll: async () => [...m.values()],
        put: async (v) => { m.set(v[clave], v); }, delete: async (k) => { m.delete(k); },
      };
    }
    const a = db.transaction(nombre, modo).objectStore(nombre);
    return { get: (k) => pedir(a.get(k)), getAll: () => pedir(a.getAll()), put: (v) => pedir(a.put(v)), delete: (k) => pedir(a.delete(k)) };
  }
  const avisar = () => document.dispatchEvent(new CustomEvent("cola:cambio"));

  const uuid = () => {
    if (crypto.randomUUID) return crypto.randomUUID();
    const b = crypto.getRandomValues(new Uint8Array(16));
    b[6] = (b[6] & 0x0f) | 0x40; b[8] = (b[8] & 0x3f) | 0x80;
    const h = [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
    return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
  };
  /* Fecha y hora local con su desfase (p. ej. 2026-09-27T08:15:00-05:00). */
  const isoLocal = (d = new Date()) => {
    const p = (n) => String(n).padStart(2, "0"), desfase = -d.getTimezoneOffset(), a = Math.abs(desfase);
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
      + `${desfase >= 0 ? "+" : "-"}${p(Math.floor(a / 60))}:${p(a % 60)}`;
  };

  async function meta(clave) { return (await (await almacen("meta")).get(clave))?.valor ?? null; }
  async function fijarMeta(clave, valor) { await (await almacen("meta", "readwrite")).put({ clave, valor }); }
  async function idDispositivo() {
    let id = await meta("id_dispositivo");
    if (!id) { id = uuid(); await fijarMeta("id_dispositivo", id); }
    return id;
  }

  /* Guarda una operación pendiente. ``opciones``: id_cliente (REGISTRAR_NINO), nino_ref ({id} o {id_cliente}) y
     resumen (texto sin datos sensibles innecesarios para el panel de pendientes). */
  async function encolar(tipo, datos, opciones = {}) {
    const op = {
      id_operacion: uuid(), tipo, id_dispositivo: await idDispositivo(), fecha_local: isoLocal(), datos,
      id_cliente: opciones.id_cliente ?? null, nino_ref: opciones.nino_ref ?? null, resumen: opciones.resumen ?? tipo,
      estado: "PENDIENTE", intentos: 0, ultimo_intento: null, ultimo_error: null, creado_en: Date.now(),
    };
    await (await almacen("pendientes", "readwrite")).put(op);
    avisar();
    return op;
  }
  async function listar() {
    const todas = await (await almacen("pendientes")).getAll();
    return todas.sort((a, b) => (a.fecha_local < b.fecha_local ? -1 : a.fecha_local > b.fecha_local ? 1 : a.creado_en - b.creado_en));
  }
  async function actualizar(op) { await (await almacen("pendientes", "readwrite")).put(op); avisar(); }
  async function quitar(id) { await (await almacen("pendientes", "readwrite")).delete(id); avisar(); }

  return { uuid, isoLocal, meta, fijarMeta, idDispositivo, encolar, listar, actualizar, quitar, get persistente() { return persistente; }, abrir };
})();
