/* Sincronización al reconectar (HIST-3.2). Envía la cola de operaciones a POST /api/sincronizacion en lotes de 200 como
   máximo, ordenadas por fecha local. El servidor es la fuente de verdad: devuelve un resultado por operación y, según
   él, la operación sale de la cola (APLICADA, DUPLICADA, CONFLICTO) o queda marcada como RECHAZADA para revisarla. */
window.Sync = (() => {
  const LOTE = 200;
  let enCurso = null;
  const emitir = (nombre, detalle) => document.dispatchEvent(new CustomEvent(nombre, { detail: detalle }));
  const usuario = () => document.getElementById("usuario")?.value || "";

  const aCuerpo = (o) => {
    const c = { id_operacion: o.id_operacion, tipo: o.tipo, id_dispositivo: o.id_dispositivo, fecha_local: o.fecha_local, datos: o.datos };
    if (o.id_cliente) c.id_cliente = o.id_cliente;
    if (o.nino_ref) c.nino_ref = o.nino_ref;
    return c;
  };
  const mensajeError = (r) => (r.errores?.length ? r.errores.map((e) => `${e.campo}: ${e.mensaje}`).join("; ") : r.mensaje) || "Operación rechazada.";

  async function enviarLote(lote) {
    const resp = await window.Auth.fetch("/api/sincronizacion", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Usuario": usuario() },
      body: JSON.stringify({ operaciones: lote.map(aCuerpo) }),
    });
    const cuerpo = resp.headers.get("content-type")?.includes("json") ? await resp.json() : null;
    if (!resp.ok) throw Object.assign(new Error(cuerpo?.mensaje || `Error ${resp.status}`), { estado: resp.status });
    return cuerpo;
  }

  async function ejecutar() {
    const resumen = { aplicadas: 0, duplicadas: 0, conflictos: 0, rechazadas: 0, mapeos: {}, error: null };
    try {
      const pendientes = (await window.Cola.listar()).filter((o) => o.estado === "PENDIENTE");
      for (let i = 0; i < pendientes.length && !resumen.error; i += LOTE) await procesarLote(pendientes.slice(i, i + LOTE), resumen);
      if (!resumen.error) await window.Cola.fijarMeta("ultima_sincronizacion", window.Cola.isoLocal());
    } catch (e) { resumen.error = e.message || "Error al sincronizar."; }
    return resumen;
  }

  async function procesarLote(lote, resumen) {
    let r;
    try { r = await enviarLote(lote); }
    catch (e) {
      const motivo = e instanceof TypeError ? "Sin conexión con el servidor." : e.message;
      for (const o of lote) await window.Cola.actualizar({ ...o, intentos: o.intentos + 1, ultimo_intento: window.Cola.isoLocal(), ultimo_error: motivo });
      resumen.error = motivo;
      return;
    }
    const porId = new Map(lote.map((o) => [o.id_operacion, o]));
    for (const x of r.resultados) {
      const o = porId.get(x.id_operacion);
      if (!o) continue;
      if (x.resultado === "RECHAZADA") {
        resumen.rechazadas++;
        await window.Cola.actualizar({ ...o, estado: "RECHAZADA", intentos: o.intentos + 1, ultimo_intento: window.Cola.isoLocal(), ultimo_error: mensajeError(x) });
        continue;
      }
      if (x.resultado === "CONFLICTO") resumen.conflictos++;
      else if (x.resultado === "DUPLICADA") resumen.duplicadas++;
      else resumen.aplicadas++;
      if (x.id_cliente && x.id_recurso && x.resultado !== "CONFLICTO") resumen.mapeos[x.id_cliente] = x.id_recurso;
      await window.Cola.quitar(o.id_operacion);
    }
  }

  /* Una sola sincronización a la vez; si ya hay una en curso se devuelve la misma promesa. Sin pendientes no hace nada. */
  async function sincronizar() {
    if (enCurso) return enCurso;
    if (!navigator.onLine) return null;
    if (!(await window.Cola.listar()).some((o) => o.estado === "PENDIENTE")) return null;
    if (enCurso) return enCurso;
    emitir("sync:inicio");
    enCurso = ejecutar().finally(() => { enCurso = null; });
    const resumen = await enCurso;
    emitir("sync:fin", resumen);
    return resumen;
  }
  return { sincronizar, get enCurso() { return enCurso !== null; } };
})();
