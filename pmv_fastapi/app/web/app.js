/* Cliente web (PWA). Consume la API REST: Incremento 1 (PMV), Incremento 2 (agenda, alertas, asistencia) e Incremento 3
   (registro sin conexión con cola en el dispositivo, sincronización, conflictos y visitas domiciliarias priorizadas). */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const ETIQUETA = { SIN_ANEMIA: "Sin anemia", LEVE: "Anemia leve", MODERADA: "Anemia moderada", SEVERA: "Anemia severa", NO_APLICA: "No aplica (< 6 m)" };
const COLOR = { SIN_ANEMIA: "#1F7A3D", LEVE: "#C99200", MODERADA: "#D26A1B", SEVERA: "#B0222B", NO_APLICA: "#8C99A6" };
const CLAVE_BORRADOR = "anemia-junin:borrador-registro";
const CAMPOS_NINO = ["dni", "nombres", "apellidos", "sexo", "fecha_nacimiento", "establecimiento", "distrito", "comunidad", "altitud_m", "tutor_nombre", "tutor_celular"];
const CAMPOS_EVAL = ["fecha", "hemoglobina_observada", "peso_kg", "talla_cm"];
const NUMERICOS = ["altitud_m", "hemoglobina_observada", "peso_kg", "talla_cm"];
const hoyISO = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
/* «Hoy» del sistema: lo fija el servidor (con FECHA_REFERENCIA es el corte del dataset); mientras responde se usa el del navegador. */
let HOY = hoyISO();
const SEVERIDAD_HIS = { LEV: "Leve", MOD: "Moderada", SEV: "Severa" };

async function api(ruta, opciones = {}) {
  const r = await window.Auth.fetch(ruta, {
    ...opciones,
    headers: { "Content-Type": "application/json", "X-Usuario": $("#usuario").value, ...(opciones.headers || {}) },
  });
  if (!opciones.method || opciones.method === "GET") $("#aviso-cache").hidden = !r.headers.get("X-Desde-Cache");
  const cuerpo = r.headers.get("content-type")?.includes("json") ? await r.json() : null;
  if (!r.ok) throw { estado: r.status, ...(cuerpo || { mensaje: "Error de comunicación." }) };
  return cuerpo;
}

/* Una falla de red (no una respuesta del servidor): el registro se guarda en el dispositivo. */
const sinConexion = (e) => !navigator.onLine || e instanceof TypeError;

function toast(texto, ok = true) {
  const t = $("#toast");
  t.textContent = texto; t.className = "toast" + (ok ? " ok" : ""); t.hidden = false;
  clearTimeout(t._t); t._t = setTimeout(() => (t.hidden = true), 3200);
}

const badge = (c) => c ? `<span class="badge ${c}">${ETIQUETA[c]}</span>` : `<span class="badge NO_APLICA">Sin control</span>`;
const edad = (m) => (m < 12 ? `${m} m` : `${Math.floor(m / 12)} a ${m % 12} m`);
const fecha = (iso) => (iso ? iso.split("-").reverse().join("/") : "—");
/* Iniciales en la lista de pendientes: identifica el registro sin repetir datos personales completos. */
const etiquetaNino = (nombre) => (/\s/.test(nombre) ? nombre.split(/\s+/).filter(Boolean).map((p) => p[0].toUpperCase() + ".").join(" ") : nombre);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* ---------- navegación ---------- */
function mostrar(vista) {
  $$(".pestana").forEach((b) => b.classList.toggle("activa", b.dataset.vista === vista));
  $$(".vista").forEach((v) => v.classList.toggle("activa", v.id === "vista-" + vista));
  if (vista === "seguimiento") cargarSeguimiento();
  if (vista === "alertas") cargarAlertas();
  if (vista === "agenda") cargarAgendaPersonal();
  if (vista === "visitas") cargarVisitas();
  if (vista === "recordatorios") cargarRecordatorios();
  if (vista === "sincronizacion") cargarSincronizacion();
  if (vista !== "expediente") expedienteActual = null;
  actualizarInsignia();
}
$$(".pestana").forEach((b) => b.addEventListener("click", () => mostrar(b.dataset.vista)));

/* ---------- conectividad ---------- */
let expedienteActual = null; // {id} del servidor o {id_cliente} de un niño registrado sin conexión
function estadoRed() { $("#red").classList.toggle("fuera", !navigator.onLine); $("#red").title = navigator.onLine ? "En línea" : "Sin conexión: los registros se guardan en este dispositivo"; }
addEventListener("online", () => { estadoRed(); window.Sync.sincronizar(); });
addEventListener("offline", () => { estadoRed(); actualizarSync(); });

/* ---------- HU-01 / HU-03: registro ---------- */
const form = $("#form-registro");
function leerFormulario() {
  const d = {};
  [...CAMPOS_NINO, ...CAMPOS_EVAL].forEach((c) => {
    const v = form.elements[c].value.trim();
    d[c] = NUMERICOS.includes(c) ? (v === "" ? null : Number(v)) : (v === "" ? null : v);
  });
  return d;
}
function limpiarErrores() {
  $$(".campo", form).forEach((c) => c.classList.remove("invalido"));
  $$(".error", form).forEach((e) => (e.textContent = ""));
  $("#alerta-registro").hidden = true;
}
function pintarErrores(errores, contenedor = form) {
  errores.forEach(({ campo, mensaje }) => {
    const input = contenedor.querySelector(`[name="${campo}"]`);
    if (!input) return;
    input.closest(".campo").classList.add("invalido");
    input.closest(".campo").querySelector(".error").textContent = mensaje;
  });
}
function guardarBorrador() {
  if (window.Auth.modo !== "demo") return;
  try { localStorage.setItem(CLAVE_BORRADOR, JSON.stringify(leerFormulario())); $("#borrador").hidden = false; } catch (_) { /* almacenamiento no disponible */ }
}
function restaurarBorrador() {
  if (window.Auth.modo !== "demo") return;
  try {
    const b = JSON.parse(localStorage.getItem(CLAVE_BORRADOR) || "null");
    if (!b) return;
    Object.entries(b).forEach(([k, v]) => { if (v !== null && form.elements[k]) form.elements[k].value = v; });
    $("#borrador").hidden = false;
  } catch (_) { /* sin borrador */ }
}
function borrarBorrador() { try { localStorage.removeItem(CLAVE_BORRADOR); } catch (_) {} $("#borrador").hidden = true; }

let temporizadorPrevia;
async function vistaPrevia() {
  const d = leerFormulario();
  const caja = $("#vista-previa");
  if (!d.fecha_nacimiento || d.altitud_m === null || d.hemoglobina_observada === null || !d.fecha) {
    caja.innerHTML = '<span class="previa-vacia">Complete fecha de nacimiento, altitud y hemoglobina para ver la clasificación.</span>';
    return;
  }
  try {
    const r = await api("/api/validaciones/evaluacion", { method: "POST", body: JSON.stringify({
      fecha_nacimiento: d.fecha_nacimiento, altitud_m: d.altitud_m,
      evaluacion: { fecha: d.fecha, hemoglobina_observada: d.hemoglobina_observada, peso_kg: d.peso_kg ?? 10, talla_cm: d.talla_cm ?? 75 },
    }) });
    caja.innerHTML = `<strong>Validación clínica (vista previa)</strong>
      <div class="kv"><span>Edad al control</span><strong>${edad(r.edad_meses)}</strong>
      <span>Ajuste por altitud (${r.altitud_m} m)</span><strong>−${(r.hemoglobina_observada - r.hemoglobina_ajustada).toFixed(1)} g/dL</strong>
      <span>Hemoglobina ajustada</span><strong data-testid="hb-ajustada">${r.hemoglobina_ajustada.toFixed(1)} g/dL</strong>
      <span>Clasificación</span><span data-testid="clasificacion-previa">${badge(r.clasificacion)}</span></div>`;
  } catch (e) {
    if (sinConexion(e)) { caja.innerHTML = '<span class="previa-vacia" data-testid="previa-sin-conexion">Sin conexión: la clasificación se calculará al sincronizar.</span>'; return; }
    const relevantes = (e.errores || []).filter((x) => x.campo !== "peso_kg" && x.campo !== "talla_cm");
    caja.innerHTML = relevantes.length ? `<span class="previa-error">${esc(relevantes[0].mensaje)}</span>` : '<span class="previa-vacia">Revise los datos.</span>';
  }
}
form.addEventListener("input", (ev) => {
  const campo = ev.target.closest(".campo");
  if (campo) { campo.classList.remove("invalido"); campo.querySelector(".error").textContent = ""; }
  if (!form.querySelector(".campo.invalido")) $("#alerta-registro").hidden = true;
  guardarBorrador(); clearTimeout(temporizadorPrevia); temporizadorPrevia = setTimeout(vistaPrevia, 350); });

form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  limpiarErrores();
  const d = leerFormulario();
  const nino = Object.fromEntries(CAMPOS_NINO.map((c) => [c, d[c]]));
  const evaluacion_inicial = Object.fromEntries(CAMPOS_EVAL.map((c) => [c, d[c]]));
  try {
    const exp = await api("/api/ninos", { method: "POST", body: JSON.stringify({ nino, evaluacion_inicial }) });
    borrarBorrador();
    form.reset(); valoresPorDefecto(); vistaPrevia();
    toast(`Registro guardado: ${exp.nombres} ${exp.apellidos}`);
    abrirExpediente(exp.id);
  } catch (e) {
    if (sinConexion(e)) { await guardarNinoSinConexion(nino, evaluacion_inicial); return; }
    pintarErrores(e.errores || []);
    const alerta = $("#alerta-registro");
    alerta.textContent = e.estado === 409 ? e.mensaje : (e.mensaje || "No se pudo guardar.");
    alerta.hidden = false;
  }
});
/* HIST-3.1: sin conexión el registro queda en la cola del dispositivo con un id_cliente temporal. */
const OBLIGATORIOS_LOCALES = { nombres: "Ingrese los nombres.", apellidos: "Ingrese los apellidos.", fecha_nacimiento: "Ingrese la fecha de nacimiento.",
  comunidad: "Ingrese la comunidad.", fecha: "Ingrese la fecha del control.", hemoglobina_observada: "Ingrese la hemoglobina.",
  peso_kg: "Ingrese el peso.", talla_cm: "Ingrese la talla." };
async function guardarNinoSinConexion(nino, evaluacion_inicial) {
  const faltan = Object.entries(OBLIGATORIOS_LOCALES).filter(([c]) => (c in nino ? nino[c] : evaluacion_inicial[c]) === null)
    .map(([campo, mensaje]) => ({ campo, mensaje }));
  if (faltan.length) {
    pintarErrores(faltan);
    const alerta = $("#alerta-registro");
    alerta.textContent = "Sin conexión: complete los datos indicados para guardar el registro en el dispositivo."; alerta.hidden = false;
    return;
  }
  const id_cliente = window.Cola.uuid();
  await window.Cola.encolar("REGISTRAR_NINO", { nino, evaluacion_inicial }, { id_cliente,
    resumen: `Registro de niño ${etiquetaNino(`${nino.nombres} ${nino.apellidos}`)} y evaluación inicial del ${fecha(evaluacion_inicial.fecha)}` });
  borrarBorrador();
  form.reset(); valoresPorDefecto(); vistaPrevia();
  toast("Guardado en el dispositivo: se sincronizará al reconectar");
  abrirExpediente("local:" + id_cliente);
}
function valoresPorDefecto() {
  form.elements.establecimiento.value = "P. S. Chongos Alto";
  form.elements.distrito.value = "Chongos Alto";
  form.elements.altitud_m.value = 3550;
  form.elements.fecha.value = HOY;
}
$("#limpiar").addEventListener("click", () => { form.reset(); borrarBorrador(); limpiarErrores(); valoresPorDefecto(); vistaPrevia(); });

/* ---------- HU-04: seguimiento ---------- */
let temporizadorBusqueda;
async function cargarSeguimiento() {
  const p = new URLSearchParams({ estado: $("#filtro-estado").value });
  if ($("#buscar").value.trim()) p.set("q", $("#buscar").value.trim());
  if ($("#filtro-clasificacion").value) p.set("clasificacion", $("#filtro-clasificacion").value);
  let filas = [];
  try { filas = await api("/api/ninos?" + p); }
  catch (e) { if (!sinConexion(e)) throw e; toast("Sin conexión: esta lista aún no se consultó en este dispositivo", false); }
  const locales = await ninosLocales($("#buscar").value.trim(), $("#filtro-estado").value, $("#filtro-clasificacion").value);
  $("#total-seguimiento").textContent = `${filas.length + locales.length} niño(s)`;
  $("#sin-resultados").hidden = filas.length + locales.length > 0;
  $("#cuerpo-seguimiento").innerHTML = locales.map((o) => {
    const n = o.datos.nino, ev = o.datos.evaluacion_inicial;
    return `<tr class="click" data-id="local:${o.id_cliente}" data-testid="fila-pendiente">
      <td><strong>${esc(n.nombres)} ${esc(n.apellidos)}</strong></td><td>${esc(n.dni || "—")}</td><td>${edad(mesesEntre(n.fecha_nacimiento, HOY))}</td><td>${esc(n.comunidad)}</td>
      <td>${fecha(ev.fecha)}</td><td>—</td><td><span class="ctrl ctrl-LOCAL">Pendiente de sincronizar</span></td></tr>`;
  }).join("") + filas.map((f) => `
    <tr class="click" data-id="${f.id}">
      <td><strong>${esc(f.nombre_completo)}</strong></td><td>${esc(f.dni || f.codigo_origen || "—")}</td><td>${edad(f.edad_meses)}</td><td>${esc(f.comunidad)}</td>
      <td class="${f.control_atrasado ? "atrasado" : ""}">${fecha(f.ultima_fecha_control)}${f.dias_desde_ultimo_control !== null ? ` · ${f.dias_desde_ultimo_control} d` : ""}${f.controles_vencidos ? ` <span class="ctrl ctrl-VENCIDO" data-testid="vencidos-fila">${f.controles_vencidos} vencido(s)</span>` : ""}</td>
      <td>${f.ultima_hb_ajustada !== null ? f.ultima_hb_ajustada.toFixed(1) : "—"}</td><td>${badge(f.ultima_clasificacion)}</td>
    </tr>`).join("");
  $$("#cuerpo-seguimiento tr").forEach((tr) => tr.addEventListener("click", () => abrirExpediente(tr.dataset.id)));
}
/* Niños registrados sin conexión que todavía no llegaron al servidor, según los filtros de la lista. */
const mesesEntre = (nac, hoy) => {
  const [a1, m1, d1] = nac.split("-").map(Number), [a2, m2, d2] = hoy.split("-").map(Number);
  return Math.max(0, (a2 - a1) * 12 + (m2 - m1) - (d2 < d1 ? 1 : 0));
};
async function ninosLocales(texto = "", estado = "ACTIVO", clasificacion = "") {
  if (clasificacion || (estado && estado !== "ACTIVO")) return []; // aún no se conoce su clasificación; un niño nuevo está activo
  const t = texto.toLowerCase();
  return (await window.Cola.listar()).filter((o) => o.tipo === "REGISTRAR_NINO" && o.id_cliente).filter((o) => {
    const n = o.datos.nino;
    return !t || [`${n.nombres} ${n.apellidos}`, n.dni || "", n.comunidad || ""].some((c) => c.toLowerCase().includes(t));
  });
}
$("#buscar").addEventListener("input", () => { clearTimeout(temporizadorBusqueda); temporizadorBusqueda = setTimeout(cargarSeguimiento, 250); });
$("#filtro-clasificacion").addEventListener("change", cargarSeguimiento);
$("#filtro-estado").addEventListener("change", cargarSeguimiento);

/* ---------- HU-02: expediente ---------- */
function grafico(evals) {
  const puntos = [...evals].reverse();
  if (puntos.length < 2) return "";
  const w = 320, h = 110, pad = 22;
  const ys = puntos.map((e) => e.hemoglobina_ajustada);
  const min = Math.min(...ys, 9) - 0.5, max = Math.max(...ys, 12) + 0.5;
  const x = (i) => pad + (i * (w - 2 * pad)) / (puntos.length - 1);
  const y = (v) => h - pad + 6 - ((v - min) / (max - min)) * (h - 2 * pad);
  const linea = puntos.map((e, i) => `${x(i)},${y(e.hemoglobina_ajustada)}`).join(" ");
  const umbral = puntos[puntos.length - 1].edad_meses >= 24 ? 11 : 10.5;
  return `<svg viewBox="0 0 ${w} ${h}" width="100%" role="img" aria-label="Evolución de hemoglobina ajustada">
    <line x1="${pad}" x2="${w - pad}" y1="${y(umbral)}" y2="${y(umbral)}" stroke="#B0222B" stroke-dasharray="4 4"/>
    <text x="${w - pad}" y="${y(umbral) - 4}" font-size="10" text-anchor="end" fill="#B0222B">umbral ${umbral}</text>
    <polyline points="${linea}" fill="none" stroke="#1F4E79" stroke-width="2.5"/>
    ${puntos.map((e, i) => `<circle cx="${x(i)}" cy="${y(e.hemoglobina_ajustada)}" r="4" fill="${COLOR[e.clasificacion]}"/>
      <text x="${x(i)}" y="${h - 4}" font-size="9.5" text-anchor="middle" fill="#5E6E7E">${fecha(e.fecha).slice(0, 5)}</text>`).join("")}
  </svg>`;
}

async function abrirExpediente(id) {
  if (String(id).startsWith("local:")) return abrirExpedienteLocal(id.slice(6));
  mostrar("expediente");
  let exp;
  try { exp = await api("/api/ninos/" + id); }
  catch (e) {
    if (!sinConexion(e)) throw e;
    toast("Sin conexión: este expediente aún no se consultó en este dispositivo", false);
    return;
  }
  expedienteActual = { id };
  const pendientes = (await window.Cola.listar()).filter((o) => o.tipo === "REGISTRAR_EVALUACION" && o.nino_ref?.id === id);
  const u = exp.evaluaciones[0];
  $("#expediente").innerHTML = `
    <div class="tarjeta">
      <div class="cabecera-exp">
        <div><h2 style="font-size:19px;margin:0" data-testid="expediente-nombre">${esc(exp.nombre_completo)}</h2>
          <span class="chip">${exp.estado === "ACTIVO" ? "Seguimiento activo" : "Alta"}</span> ${u ? badge(u.clasificacion) : ""}</div>
        <div><button class="secundario" id="btn-editar">Editar datos</button></div>
      </div>
      <div class="datos">
        <div><span>DNI</span><strong>${exp.dni || "No registrado"}</strong></div>
        <div><span>Edad</span><strong>${edad(exp.edad_meses)}</strong></div>
        <div><span>Nacimiento</span><strong>${fecha(exp.fecha_nacimiento)}</strong></div>
        <div><span>Sexo</span><strong>${exp.sexo || "No registrado"}</strong></div>
        <div><span>Comunidad / distrito</span><strong>${esc(exp.comunidad)} · ${esc(exp.distrito)}</strong></div>
        <div><span>Altitud</span><strong>${exp.altitud_m} m s. n. m.</strong></div>
        <div><span>Madre / tutor</span><strong>${exp.tutor_nombre ? esc(exp.tutor_nombre) : "No registrado"}</strong></div>
        <div><span>Celular</span><strong>${exp.tutor_celular || "—"}</strong></div>
        <div><span>Establecimiento</span><strong>${esc(exp.establecimiento)}</strong></div>
        ${exp.origen !== "SISTEMA" ? `<div data-testid="expediente-origen"><span>Origen de los datos</span><strong>Dataset DIRESA Junín (anonimizado)</strong></div>
        <div><span>Código</span><strong data-testid="expediente-codigo">${esc(exp.codigo_origen)}</strong></div>
        <div><span>Provincia · red · microred</span><strong>${esc(exp.provincia || "—")} · ${esc(exp.red || "—")} · ${esc(exp.microred || "—")}</strong></div>` : ""}
      </div>
      <form id="form-editar" class="grid" style="margin-top:12px" hidden novalidate>
        ${[["comunidad","Comunidad"],["altitud_m","Altitud (m)"],["tutor_nombre","Madre / tutor"],["tutor_celular","Celular"]].map(([c,l]) =>
          `<div class="campo"><label>${l}</label><input name="${c}" value="${esc(exp[c] ?? "")}"><small class="error"></small></div>`).join("")}
        <div class="campo"><label>Estado</label><select name="estado"><option value="ACTIVO" ${exp.estado==="ACTIVO"?"selected":""}>Seguimiento activo</option><option value="ALTA" ${exp.estado==="ALTA"?"selected":""}>Alta</option></select><small class="error"></small></div>
        <div class="acciones" style="align-self:end"><button class="primario">Guardar cambios</button></div>
      </form>
    </div>
    <div class="bloques">
      <div class="tarjeta tabla-envoltura">
        <table class="tabla" data-testid="tabla-evaluaciones"><thead><tr><th>Fecha</th><th>Edad</th><th>Hb obs.</th><th>Hb ajust.</th><th>Clasificación</th><th>Peso / talla</th></tr></thead>
        <tbody>${pendientes.map(filaEvaluacionPendiente).join("")}${exp.evaluaciones.map((e) => `<tr><td>${fecha(e.fecha)}</td><td>${edad(e.edad_meses)}</td><td>${e.hemoglobina_observada.toFixed(1)}</td>
          <td><strong>${e.hemoglobina_ajustada.toFixed(1)}</strong></td><td>${badge(e.clasificacion)}${e.clasificacion_origen ? `<br><small data-testid="clasificacion-his">HIS: ${SEVERIDAD_HIS[e.clasificacion_origen] || esc(e.clasificacion_origen)}</small>` : ""}</td>
          <td>${e.peso_kg === null || e.talla_cm === null ? '<span data-testid="sin-antropometria">no registrado</span>' : `${e.peso_kg} kg · ${e.talla_cm} cm`}</td></tr>`).join("")}</tbody></table>
      </div>
      <div class="tarjeta">
        <h2>Evolución de hemoglobina ajustada</h2>${grafico(exp.evaluaciones) || '<p class="vacio" style="padding:0">Se mostrará con dos o más controles.</p>'}
        <h2 style="margin-top:14px">Registrar nuevo control</h2>
        <form id="form-control" novalidate>
          <div class="fila2"><div class="campo"><label>Fecha</label><input type="date" name="fecha" value="${HOY}"><small class="error"></small></div>
          <div class="campo"><label>Hb observada (g/dL)</label><input type="number" step="0.1" name="hemoglobina_observada"><small class="error"></small></div></div>
          <div class="fila2"><div class="campo"><label>Peso (kg)</label><input type="number" step="0.1" name="peso_kg"><small class="error"></small></div>
          <div class="campo"><label>Talla (cm)</label><input type="number" step="0.1" name="talla_cm"><small class="error"></small></div></div>
          <div class="acciones"><button class="primario" data-testid="guardar-control">Guardar control</button></div>
        </form>
      </div>
    </div>
    <div class="tarjeta" style="margin-top:14px" data-testid="agenda-seccion">
      <h2>Agenda de controles</h2>
      <div id="agenda-contenido"><p class="vacio" style="padding:0">Calculando agenda…</p></div>
    </div>
    ${seccionVisitas()}
    ${seccionBarreras()}`;
  cargarAgenda(id);
  cargarVisitasNino({ id }, exp.nombre_completo);
  cargarBarrerasNino({ id }, exp.nombre_completo);
  $("#btn-barrera-nino").addEventListener("click", () => abrirModalBarrera({ ref: { id }, nombre: exp.nombre_completo, alTerminar: () => cargarBarrerasNino({ id }, exp.nombre_completo) }));
  $("#btn-editar").addEventListener("click", () => ($("#form-editar").hidden = !$("#form-editar").hidden));
  $("#form-editar").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const f = ev.target; const cambios = {};
    ["comunidad", "tutor_nombre", "tutor_celular", "estado"].forEach((c) => (cambios[c] = f.elements[c].value.trim()));
    cambios.altitud_m = Number(f.elements.altitud_m.value);
    try { await api("/api/ninos/" + id, { method: "PATCH", body: JSON.stringify(cambios) }); toast("Expediente actualizado"); abrirExpediente(id); }
    catch (e) {
      if (sinConexion(e)) { toast("Sin conexión: editar los datos del expediente requiere conexión", false); return; }
      pintarErrores(e.errores || [], f);
    }
  });
  $("#form-control").addEventListener("submit", (ev) => { ev.preventDefault(); registrarControl(ev.target, { id }, exp.nombre_completo, () => abrirExpediente(id)); });
  $("#btn-visita-nino").addEventListener("click", () => abrirModalVisita({ ref: { id }, nombre: exp.nombre_completo, alTerminar: () => cargarVisitasNino({ id }, exp.nombre_completo) }));
}
const filaEvaluacionPendiente = (o) => `<tr class="atenuado" data-testid="evaluacion-pendiente"><td>${fecha(o.datos.fecha)}</td><td>—</td><td>${o.datos.hemoglobina_observada.toFixed(1)}</td>
  <td>—</td><td><span class="ctrl ctrl-LOCAL">Pendiente de sincronizar</span></td>
  <td>${o.datos.peso_kg === null || o.datos.talla_cm === null ? "no registrado" : `${o.datos.peso_kg} kg · ${o.datos.talla_cm} cm`}</td></tr>`;

/* HIST-3.1: un control nuevo se envía en línea; sin conexión (o con un niño aún no sincronizado) queda en la cola. */
async function registrarControl(f, ref, nombre, recargar) {
  $$(".campo", f).forEach((c) => c.classList.remove("invalido")); $$(".error", f).forEach((x) => (x.textContent = ""));
  const datos = { fecha: f.elements.fecha.value || null };
  ["hemoglobina_observada", "peso_kg", "talla_cm"].forEach((c) => (datos[c] = f.elements[c].value === "" ? null : Number(f.elements[c].value)));
  if (ref.id) {
    try { await api(`/api/ninos/${ref.id}/evaluaciones`, { method: "POST", body: JSON.stringify(datos) }); toast("Control registrado"); recargar(); return; }
    catch (e) { if (!sinConexion(e)) { pintarErrores(e.errores || [], f); return; } }
  }
  const faltan = [["fecha", "Ingrese la fecha del control."], ["hemoglobina_observada", "Ingrese la hemoglobina."], ["peso_kg", "Ingrese el peso."], ["talla_cm", "Ingrese la talla."]].filter(([c]) => datos[c] === null);
  if (faltan.length) { pintarErrores(faltan.map(([campo, mensaje]) => ({ campo, mensaje })), f); return; }
  await window.Cola.encolar("REGISTRAR_EVALUACION", datos, { nino_ref: ref, resumen: `Control de hemoglobina de ${etiquetaNino(nombre)} del ${fecha(datos.fecha)}` });
  toast("Guardado en el dispositivo: se sincronizará al reconectar");
  recargar();
}

/* HIST-3.1: expediente provisional de un niño registrado sin conexión (todavía no existe en el servidor). */
async function abrirExpedienteLocal(idCliente) {
  mostrar("expediente");
  const cola = await window.Cola.listar();
  const op = cola.find((o) => o.tipo === "REGISTRAR_NINO" && o.id_cliente === idCliente);
  if (!op) { toast("Ese registro ya se sincronizó: búsquelo en Seguimiento"); mostrar("seguimiento"); return; }
  expedienteActual = { id_cliente: idCliente };
  const n = op.datos.nino, ev = op.datos.evaluacion_inicial, nombre = `${n.nombres} ${n.apellidos}`;
  const nuevos = cola.filter((o) => o.tipo === "REGISTRAR_EVALUACION" && o.nino_ref?.id_cliente === idCliente);
  const fila = (e, etiqueta) => `<tr class="atenuado" data-testid="evaluacion-pendiente"><td>${fecha(e.fecha)}</td><td>—</td><td>${e.hemoglobina_observada.toFixed(1)}</td><td>—</td>
    <td><span class="ctrl ctrl-LOCAL">${etiqueta}</span></td><td>${e.peso_kg === null || e.talla_cm === null ? "no registrado" : `${e.peso_kg} kg · ${e.talla_cm} cm`}</td></tr>`;
  $("#expediente").innerHTML = `
    <div class="tarjeta">
      <div class="cabecera-exp">
        <div><h2 style="font-size:19px;margin:0" data-testid="expediente-nombre">${esc(nombre)}</h2>
          <span class="chip" data-testid="expediente-pendiente">Pendiente de sincronizar</span></div>
      </div>
      <p class="nota">Este niño se registró sin conexión y está guardado solo en este dispositivo. El servidor validará los datos y calculará la clasificación y la agenda al sincronizar.</p>
      <div class="datos">
        <div><span>DNI</span><strong>${esc(n.dni || "No registrado")}</strong></div>
        <div><span>Edad</span><strong>${edad(mesesEntre(n.fecha_nacimiento, HOY))}</strong></div>
        <div><span>Nacimiento</span><strong>${fecha(n.fecha_nacimiento)}</strong></div>
        <div><span>Sexo</span><strong>${esc(n.sexo || "No registrado")}</strong></div>
        <div><span>Comunidad / distrito</span><strong>${esc(n.comunidad)} · ${esc(n.distrito)}</strong></div>
        <div><span>Altitud</span><strong>${esc(n.altitud_m)} m s. n. m.</strong></div>
        <div><span>Madre / tutor</span><strong>${esc(n.tutor_nombre || "No registrado")}</strong></div>
        <div><span>Establecimiento</span><strong>${esc(n.establecimiento)}</strong></div>
      </div>
    </div>
    <div class="bloques">
      <div class="tarjeta tabla-envoltura">
        <table class="tabla" data-testid="tabla-evaluaciones"><thead><tr><th>Fecha</th><th>Edad</th><th>Hb obs.</th><th>Hb ajust.</th><th>Clasificación</th><th>Peso / talla</th></tr></thead>
        <tbody>${nuevos.map((o) => fila(o.datos, "Control pendiente")).join("")}${fila(ev, "Evaluación inicial pendiente")}</tbody></table>
      </div>
      <div class="tarjeta">
        <h2>Registrar nuevo control</h2>
        <form id="form-control" novalidate>
          <div class="fila2"><div class="campo"><label>Fecha</label><input type="date" name="fecha" value="${HOY}"><small class="error"></small></div>
          <div class="campo"><label>Hb observada (g/dL)</label><input type="number" step="0.1" name="hemoglobina_observada"><small class="error"></small></div></div>
          <div class="fila2"><div class="campo"><label>Peso (kg)</label><input type="number" step="0.1" name="peso_kg"><small class="error"></small></div>
          <div class="campo"><label>Talla (cm)</label><input type="number" step="0.1" name="talla_cm"><small class="error"></small></div></div>
          <div class="acciones"><button class="primario" data-testid="guardar-control">Guardar control</button></div>
        </form>
      </div>
    </div>
    ${seccionVisitas()}
    ${seccionBarreras()}`;
  const ref = { id_cliente: idCliente };
  cargarVisitasNino(ref, nombre);
  cargarBarrerasNino(ref, nombre);
  $("#btn-barrera-nino").addEventListener("click", () => abrirModalBarrera({ ref, nombre, alTerminar: () => cargarBarrerasNino(ref, nombre) }));
  $("#form-control").addEventListener("submit", (ev) => { ev.preventDefault(); registrarControl(ev.target, ref, nombre, () => abrirExpediente("local:" + idCliente)); });
  $("#btn-visita-nino").addEventListener("click", () => abrirModalVisita({ ref, nombre, alTerminar: () => cargarVisitasNino(ref, nombre) }));
}
/* ---------- HIST-2.1: agenda de controles ---------- */
const ESTADO_CTRL = { CUMPLIDO: "Cumplido", PENDIENTE: "Pendiente", PROXIMO: "Próximo a vencer", VENCIDO: "Vencido", CERRADO_RECUPERADO: "Cerrado por recuperación" };
const estadoVisual = (c) => (c.estado === "PENDIENTE" && c.proximo ? "PROXIMO" : c.estado);
const chipControl = (c) => {
  const v = estadoVisual(c);
  const extra = c.estado === "VENCIDO" ? ` · ${c.dias_vencido} d` : "";
  const asistio = c.cumplido_por_asistencia ? " (asistió)" : "";
  const marca = c.inasistencia_registrada
    ? ` <span class="ctrl ctrl-INASISTENCIA" data-testid="marca-inasistencia" title="${esc(c.motivo_inasistencia)}">Inasistencia registrada</span>` : "";
  return `<span class="ctrl ctrl-${v}" data-testid="estado-control" data-estado="${v}">${ESTADO_CTRL[v]}${extra}${asistio}</span>${marca}`;
};
/* HIST-2.4: solo se registra la asistencia de controles ya programados (fecha <= hoy) y todavía sin cumplir ni marcar. */
const puedeRegistrarAsistencia = (c) => (c.estado === "PENDIENTE" || c.estado === "VENCIDO") && !c.inasistencia_registrada && c.fecha_programada <= HOY;
/* Asistencias guardadas en el dispositivo y aún sin sincronizar: «nino|codigo|fecha_programada». */
let asistenciasPendientes = new Set();
async function refrescarAsistenciasPendientes() {
  asistenciasPendientes = new Set((await window.Cola.listar()).filter((o) => o.tipo === "REGISTRAR_ASISTENCIA" && o.nino_ref?.id)
    .map((o) => `${o.nino_ref.id}|${o.datos.codigo}|${o.datos.fecha_programada}`));
}
const botonesAsistencia = (c, ninoId) => asistenciasPendientes.has(`${ninoId}|${c.codigo}|${c.fecha_programada}`)
  ? '<span class="ctrl ctrl-LOCAL" data-testid="asistencia-pendiente">Pendiente de sincronizar</span>'
  : puedeRegistrarAsistencia(c)
  ? `<button type="button" class="mini" data-accion="ASISTIO" data-testid="btn-asistio">Asistió</button><button type="button" class="mini no" data-accion="NO_ASISTIO" data-testid="btn-no-asistio">No asistió</button>` : "";

async function cargarAgenda(id) {
  actualizarInsignia(); // un control nuevo o un cambio de estado modifica el total de vencidos de la cabecera
  const caja = $("#agenda-contenido");
  try {
    const a = await api(`/api/ninos/${id}/agenda`);
    await refrescarAsistenciasPendientes();
    if (!a.aplica) { caja.innerHTML = `<p class="vacio" style="padding:0" data-testid="agenda-sin-agenda">${esc(a.motivo)}</p>`; return; }
    const r = a.resumen;
    caja.innerHTML = `
      <div class="resumen-agenda" data-testid="agenda-resumen">
        <span class="chip" data-testid="agenda-total">${r.total} controles</span>
        <span class="ctrl ctrl-CUMPLIDO" data-testid="agenda-cumplidos">${r.cumplidos} cumplidos</span>
        <span class="ctrl ctrl-PENDIENTE" data-testid="agenda-pendientes">${r.pendientes} pendientes</span>
        <span class="ctrl ctrl-PROXIMO" data-testid="agenda-proximos">${r.proximos} por vencer</span>
        <span class="ctrl ctrl-VENCIDO" data-testid="agenda-vencidos">${r.vencidos} vencidos</span>
        ${r.cerrados ? `<span class="ctrl ctrl-CERRADO_RECUPERADO">${r.cerrados} cerrados por recuperación</span>` : ""}
        ${r.inasistencias ? `<span class="ctrl ctrl-INASISTENCIA" data-testid="agenda-inasistencias">${r.inasistencias} con inasistencia</span>` : ""}
        <span class="proximo" data-testid="agenda-proximo-control">${r.proximo_control ? `Próximo control: ${esc(r.proximo_control.codigo)} el ${fecha(r.proximo_control.fecha_programada)}` : "Sin controles pendientes"}</span>
      </div>
      <div class="agenda-scroll tabla-envoltura"><table class="tabla completa" data-testid="agenda-tabla">
        <thead><tr><th>Fecha programada</th><th>Control</th><th>Tipo</th><th>Ventana de cumplimiento</th><th>Estado</th><th>Asistencia</th></tr></thead>
        <tbody>${a.controles.map((c) => `<tr data-estado="${estadoVisual(c)}" data-codigo="${c.codigo}" data-programada="${c.fecha_programada}" data-nino="${id}" data-desc="${esc(c.descripcion)}">
          <td>${fecha(c.fecha_programada)}</td><td>${esc(c.descripcion)}</td>
          <td>${c.tipo === "CONTROL_TRATAMIENTO" ? "Tratamiento" : "Por edad"}</td>
          <td>${fecha(c.fecha_inicio_ventana)} – ${fecha(c.fecha_limite)}</td><td>${chipControl(c)}</td>
          <td class="celda-acciones">${botonesAsistencia(c, id)}</td></tr>`).join("")}</tbody></table></div>
      <p class="nota">Agenda referencial calculada con el esquema ${esc(a.version_esquema)} al ${fecha(a.fecha_referencia)}; la confirma la microred. No es un diagnóstico.</p>`;
    $$("[data-accion]", caja).forEach((b) => b.addEventListener("click", () => abrirModalAsistencia(b.closest("tr"), b.dataset.accion, () => { cargarAgenda(id); if ($("#barreras-nino")) cargarBarrerasNino({ id }); })));
  } catch (e) { caja.innerHTML = `<p class="alerta">${esc(sinConexion(e) ? "Sin conexión: la agenda de este niño aún no se consultó en este dispositivo." : e.mensaje || "No se pudo calcular la agenda.")}</p>`; }
}

/* ---------- HIST-2.3: agenda del personal ---------- */
const DIAS = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];
const diaSemana = (iso) => DIAS[new Date(iso + "T12:00:00").getDay()];
const sumarDias = (iso, n) => { const d = new Date(iso + "T12:00:00"); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); };
const diasEntre = (a, b) => Math.round((new Date(b + "T12:00:00") - new Date(a + "T12:00:00")) / 86400000);
let secuenciaAgenda = 0;

function llenarSelect(sel, opciones, vacio, actual) {
  sel.innerHTML = `<option value="">${vacio}</option>` + opciones.map((o) => `<option value="${esc(o)}">${esc(o)}</option>`).join("");
  sel.value = opciones.includes(actual) ? actual : "";
}

async function cargarAgendaPersonal() {
  const mia = ++secuenciaAgenda;
  const enviado = { desde: $("#agenda-desde").value, hasta: $("#agenda-hasta").value };
  const p = new URLSearchParams();
  [["desde", "#agenda-desde"], ["hasta", "#agenda-hasta"], ["establecimiento", "#filtro-agenda-establecimiento"], ["comunidad", "#filtro-agenda-comunidad"]]
    .forEach(([k, id]) => { if ($(id).value) p.set(k, $(id).value); });
  const aviso = $("#agenda-error");
  let a;
  try { a = await api("/api/agenda?" + p); await refrescarAsistenciasPendientes(); }
  catch (e) {
    if (mia !== secuenciaAgenda) return;
    aviso.textContent = (e.errores?.[0] || e).mensaje || "No se pudo consultar la agenda."; aviso.hidden = false;
    return;
  }
  if (mia !== secuenciaAgenda) return; // llegó la respuesta de una consulta anterior: se descarta
  aviso.hidden = true;
  // Solo se completa lo que la persona no tocó mientras llegaba la respuesta (DEF-09): lo escrito después se respeta.
  if ($("#agenda-desde").value === enviado.desde) $("#agenda-desde").value = a.desde;
  if ($("#agenda-hasta").value === enviado.hasta) $("#agenda-hasta").value = a.hasta;
  llenarSelect($("#filtro-agenda-establecimiento"), a.establecimientos_disponibles, "Todos", a.establecimiento);
  llenarSelect($("#filtro-agenda-comunidad"), a.comunidades_disponibles, "Todas", a.comunidad);
  const r = a.resumen;
  $("#total-agenda").textContent = `${r.total} control(es) · ${r.ninos} niño(s)`;
  $("#agenda-personal-resumen").innerHTML = `
    <span class="chip" data-testid="agenda-personal-total">${r.total} programados</span>
    <span class="ctrl ctrl-CUMPLIDO" data-testid="agenda-personal-cumplidos">${r.cumplidos} cumplidos</span>
    <span class="ctrl ctrl-PENDIENTE" data-testid="agenda-personal-pendientes">${r.pendientes} pendientes</span>
    <span class="ctrl ctrl-VENCIDO" data-testid="agenda-personal-vencidos">${r.vencidos} vencidos</span>
    <span class="ctrl ctrl-INASISTENCIA" data-testid="agenda-personal-inasistencias">${r.con_inasistencia} con inasistencia</span>
    <span class="proximo">Del ${fecha(a.desde)} al ${fecha(a.hasta)} · fecha de referencia ${fecha(a.fecha_referencia)}</span>`;
  $("#cuerpo-agenda-personal").innerHTML = a.dias.map((d) => `
    <tr class="dia${d.total ? "" : " sin-controles"}" data-fecha="${d.fecha}" data-testid="agenda-personal-dia">
      <td colspan="6">${diaSemana(d.fecha)} ${fecha(d.fecha)}<small data-testid="agenda-personal-dia-total">${d.total} control(es)${d.total ? ` · ${d.cumplidos} cumplidos · ${d.pendientes} pendientes · ${d.vencidos} vencidos` : ""}</small></td>
    </tr>` + d.items.map((i) => {
      const c = i.control, v = estadoVisual(c);
      return `<tr class="${c.estado === "CUMPLIDO" ? "atenuado" : ""}" data-estado="${v}" data-codigo="${c.codigo}" data-programada="${c.fecha_programada}" data-nino="${i.nino.id}" data-nombre="${esc(i.nino.nombre_completo)}" data-desc="${esc(c.descripcion)}">
        <td><a href="#" class="enlace-nino" data-testid="agenda-personal-nino">${esc(i.nino.nombre_completo)}</a><br><small>${i.nino.dni ? "DNI " + i.nino.dni : esc(i.nino.codigo_origen || "")}</small></td>
        <td>${esc(c.descripcion)}</td><td>${c.tipo === "CONTROL_TRATAMIENTO" ? "Tratamiento" : "Por edad"}</td>
        <td>${esc(i.nino.establecimiento)}<br><small>${esc(i.nino.comunidad)}</small></td>
        <td>${chipControl(c)}${i.prioridad ? ` <span class="badge prio-${i.prioridad}" data-testid="prioridad">${i.prioridad}</span>` : ""}</td>
        <td class="celda-acciones">${botonesAsistencia(c, i.nino.id)}</td></tr>`;
    }).join("")).join("");
  $$("#cuerpo-agenda-personal .enlace-nino").forEach((x) => x.addEventListener("click", (ev) => { ev.preventDefault(); abrirExpediente(x.closest("tr").dataset.nino); }));
  $$("#cuerpo-agenda-personal [data-accion]").forEach((b) => b.addEventListener("click", () => abrirModalAsistencia(b.closest("tr"), b.dataset.accion, cargarAgendaPersonal)));
}
$("#agenda-consultar").addEventListener("click", cargarAgendaPersonal);
$("#filtro-agenda-establecimiento").addEventListener("change", cargarAgendaPersonal);
$("#filtro-agenda-comunidad").addEventListener("change", cargarAgendaPersonal);
function moverRango(signo) {
  const desde = $("#agenda-desde").value, hasta = $("#agenda-hasta").value;
  if (!desde || !hasta) return;
  const paso = diasEntre(desde, hasta) + 1;
  $("#agenda-desde").value = sumarDias(desde, signo * paso); $("#agenda-hasta").value = sumarDias(hasta, signo * paso);
  cargarAgendaPersonal();
}
$("#agenda-anterior").addEventListener("click", () => moverRango(-1));
$("#agenda-siguiente").addEventListener("click", () => moverRango(1));

/* ---------- HIST-2.4: registrar asistencia a un control ---------- */
const modal = { fila: null, accion: null, alTerminar: null };
function cerrarModalAsistencia() { $("#modal-asistencia").hidden = true; modal.fila = null; }
async function abrirModalAsistencia(fila, accion, alTerminar) {
  modal.fila = fila; modal.accion = accion; modal.alTerminar = alTerminar;
  const nombre = fila.dataset.nombre || $("[data-testid=expediente-nombre]")?.textContent || "";
  const asistio = accion === "ASISTIO";
  $("#modal-titulo").textContent = asistio ? "Registrar asistencia" : "Registrar inasistencia";
  $("#modal-detalle").textContent = `${nombre} · ${fila.dataset.desc} · programado el ${fecha(fila.dataset.programada)}`;
  $("#campo-motivo").hidden = asistio; $("#campo-evaluacion").hidden = !asistio;
  $("#asistencia-motivo").value = ""; $("#asistencia-detalle").value = ""; $("#asistencia-barrera").value = ""; $("#asistencia-error").textContent = "";
  $("#asistencia-evaluacion").innerHTML = '<option value="">Sin evaluación vinculada</option>';
  $("#asistencia-confirmar").textContent = asistio ? "Registrar asistencia" : "Registrar inasistencia";
  $("#modal-asistencia").hidden = false;
  (asistio ? $("#asistencia-evaluacion") : $("#asistencia-motivo")).focus();
  if (asistio) {
    try {
      const exp = await api("/api/ninos/" + fila.dataset.nino);
      if (modal.fila !== fila) return;
      $("#asistencia-evaluacion").innerHTML += exp.evaluaciones.map((e) => `<option value="${e.id}">${fecha(e.fecha)} · Hb ajustada ${e.hemoglobina_ajustada.toFixed(1)} g/dL</option>`).join("");
    } catch (_) { /* sin evaluaciones para vincular: se registra la asistencia sin vínculo */ }
  }
}
$("#asistencia-cancelar").addEventListener("click", cerrarModalAsistencia);
$("#modal-asistencia").addEventListener("click", (ev) => { if (ev.target.id === "modal-asistencia") cerrarModalAsistencia(); });
addEventListener("keydown", (ev) => { if (ev.key === "Escape" && !$("#modal-asistencia").hidden) cerrarModalAsistencia(); });
$("#form-asistencia").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const { fila, accion } = modal;
  const cuerpo = { fecha_programada: fila.dataset.programada, estado: accion };
  if (accion === "NO_ASISTIO") {
    const opcion = $("#asistencia-motivo").value, detalle = $("#asistencia-detalle").value.trim();
    if (!opcion) { $("#asistencia-error").textContent = "Seleccione el motivo de la inasistencia."; return; }
    cuerpo.motivo = (detalle ? `${opcion}: ${detalle}` : opcion).slice(0, 200);
  } else if ($("#asistencia-evaluacion").value) cuerpo.evaluacion_id = $("#asistencia-evaluacion").value;
  const alTerminar = modal.alTerminar;
  /* HIST-4.3: la barrera que el personal asocia a la inasistencia se registra aparte, con la fuente INASISTENCIA. */
  const barrera = accion === "NO_ASISTIO" ? { tipo: $("#asistencia-barrera").value, detalle: $("#asistencia-detalle").value.trim() || null } : { tipo: "" };
  if (barrera.tipo === "OTRA" && !barrera.detalle) { $("#asistencia-error").textContent = "Con «Otra» barrera, describa la barrera en el detalle."; return; }
  const nombreNino = fila.dataset.nombre || $("[data-testid=expediente-nombre]")?.textContent || "";
  const registrarBarreraAsociada = () => (barrera.tipo
    ? barreraAsociada({ id: fila.dataset.nino }, { tipo: barrera.tipo, detalle: barrera.detalle, fuente: "INASISTENCIA", fecha: HOY }, nombreNino)
    : Promise.resolve());
  try {
    await api(`/api/ninos/${fila.dataset.nino}/controles/${encodeURIComponent(fila.dataset.codigo)}/asistencia`, { method: "POST", body: JSON.stringify(cuerpo) });
    await registrarBarreraAsociada();
    cerrarModalAsistencia();
    toast(accion === "ASISTIO" ? "Asistencia registrada" : "Inasistencia registrada");
    if (alTerminar) alTerminar();
    actualizarInsignia();
  } catch (e) {
    if (!sinConexion(e)) { $("#asistencia-error").textContent = (e.errores?.[0] || e).mensaje || "No se pudo registrar."; return; }
    const nombre = fila.dataset.nombre || $("[data-testid=expediente-nombre]")?.textContent || "";
    await window.Cola.encolar("REGISTRAR_ASISTENCIA", { codigo: fila.dataset.codigo, ...cuerpo }, { nino_ref: { id: fila.dataset.nino },
      resumen: `${accion === "ASISTIO" ? "Asistencia" : "Inasistencia"} de ${etiquetaNino(nombre)} al control ${fila.dataset.desc} (${fecha(fila.dataset.programada)})` });
    await registrarBarreraAsociada();
    cerrarModalAsistencia();
    toast("Guardado en el dispositivo: se sincronizará al reconectar");
    if (alTerminar) alTerminar();
  }
});

/* ---------- HIST-2.2: alertas de controles vencidos ---------- */
const comunidadesAlerta = new Set();
async function actualizarInsignia() {
  try {
    const r = await api("/api/alertas/resumen");
    const ins = $("#insignia-alertas");
    ins.textContent = r.total_vencidos;
    ins.classList.toggle("cero", r.total_vencidos === 0);
    ins.title = `${r.total_vencidos} control(es) vencido(s) en ${r.ninos_con_vencidos} niño(s)`;
  } catch (_) { /* sin conexión: se conserva el último valor */ }
}
$("#insignia-alertas").addEventListener("click", (ev) => { ev.preventDefault(); mostrar("alertas"); });

let secuenciaAlertas = 0;
async function cargarAlertas() {
  const mia = ++secuenciaAlertas;
  const p = new URLSearchParams();
  if ($("#filtro-alerta-comunidad").value) p.set("comunidad", $("#filtro-alerta-comunidad").value);
  if ($("#filtro-alerta-prioridad").value) p.set("prioridad", $("#filtro-alerta-prioridad").value);
  const [r, filas] = await Promise.all([api("/api/alertas/resumen"), api("/api/alertas/controles-vencidos?" + p)]);
  if (mia !== secuenciaAlertas) return; // llegó una respuesta de un filtro anterior: se descarta
  $("#total-alertas").textContent = `${filas.length} alerta(s)`;
  $("#alertas-resumen").innerHTML = `
    <div class="tarjeta kpi"><strong data-testid="kpi-vencidos">${r.total_vencidos}</strong><span>controles vencidos</span></div>
    <div class="tarjeta kpi"><strong data-testid="kpi-ninos-vencidos">${r.ninos_con_vencidos}</strong><span>niños con controles vencidos</span></div>
    <div class="tarjeta kpi"><strong data-testid="kpi-alta">${r.por_prioridad.ALTA}</strong><span>prioridad alta</span></div>
    <div class="tarjeta kpi"><strong data-testid="kpi-media">${r.por_prioridad.MEDIA}</strong><span>prioridad media</span></div>
    <div class="tarjeta kpi"><strong data-testid="kpi-baja">${r.por_prioridad.BAJA}</strong><span>prioridad baja</span></div>
    <div class="tarjeta kpi"><strong data-testid="kpi-proximos">${r.proximos_7_dias}</strong><span>controles por vencer en 7 días</span></div>`;
  if (!$("#filtro-alerta-comunidad").value) {
    filas.forEach((f) => comunidadesAlerta.add(f.nino.comunidad));
    const sel = $("#filtro-alerta-comunidad"), actual = sel.value;
    sel.innerHTML = '<option value="">Todas</option>' + [...comunidadesAlerta].sort().map((c) => `<option value="${esc(c)}">${esc(c)}</option>`).join("");
    sel.value = actual;
  }
  $("#sin-alertas").hidden = filas.length > 0;
  $("#cuerpo-alertas").innerHTML = filas.map((f) => `
    <tr class="click" data-id="${f.nino.id}" data-prioridad="${f.prioridad}" data-codigo="${f.control.codigo}">
      <td><span class="badge prio-${f.prioridad}" data-testid="prioridad">${f.prioridad}</span></td>
      <td><strong>${esc(f.nino.nombre_completo)}</strong><br><small>${f.nino.dni ? "DNI " + f.nino.dni : esc(f.nino.codigo_origen || "")}</small></td>
      <td>${esc(f.control.descripcion)}${f.control.inasistencia_registrada ? ` <span class="ctrl ctrl-INASISTENCIA" data-testid="marca-inasistencia" title="${esc(f.control.motivo_inasistencia)}">Inasistencia registrada</span>` : ""}</td><td>${fecha(f.control.fecha_programada)}</td>
      <td class="atrasado">${f.control.dias_vencido} d</td><td>${esc(f.nino.comunidad)}</td>
      <td>${f.nino.tutor_celular || "—"}</td><td>${badge(f.ultima_clasificacion)}</td></tr>`).join("");
  $$("#cuerpo-alertas tr").forEach((tr) => tr.addEventListener("click", () => abrirExpediente(tr.dataset.id)));
  cargarAlertasBarreras();
}
/* HIST-4.4: niños con barreras críticas (mismo filtro de comunidad y de prioridad que los controles vencidos). */
let secuenciaAlertasBarreras = 0;
async function cargarAlertasBarreras() {
  const mia = ++secuenciaAlertasBarreras;
  const p = new URLSearchParams();
  if ($("#filtro-alerta-comunidad").value) p.set("comunidad", $("#filtro-alerta-comunidad").value);
  if (["ALTA", "MEDIA"].includes($("#filtro-alerta-prioridad").value)) p.set("prioridad", $("#filtro-alerta-prioridad").value);
  const aviso = $("#alertas-barreras-error");
  let filas;
  try { filas = await api("/api/alertas/barreras?" + p); }
  catch (e) {
    if (mia !== secuenciaAlertasBarreras) return;
    aviso.textContent = sinConexion(e) ? "Sin conexión: las barreras críticas aún no se consultaron en este dispositivo." : (e.errores?.[0] || e).mensaje || "No se pudieron consultar las barreras críticas.";
    aviso.hidden = false;
    return;
  }
  if (mia !== secuenciaAlertasBarreras) return;
  aviso.hidden = true;
  $("#total-alertas-barreras").textContent = `${filas.length} niño(s)`;
  $("#sin-alertas-barreras").hidden = filas.length > 0;
  $("#cuerpo-alertas-barreras").innerHTML = filas.map((f) => `
    <tr class="click" data-id="${f.nino.id}" data-prioridad="${f.prioridad}" data-testid="alerta-barrera">
      <td><span class="badge prio-${f.prioridad}" data-testid="prioridad-barrera">${f.prioridad}</span></td>
      <td><strong>${esc(f.nino.nombre_completo)}</strong><br><small>${f.nino.dni ? "DNI " + esc(f.nino.dni) : esc(f.nino.codigo_origen || "")}</small></td>
      <td><ul class="lista-barreras" data-testid="razones-barrera">${f.razones.map((r) => `<li>${esc(r.descripcion)}</li>`).join("")}</ul></td>
      <td><ul class="lista-barreras">${f.barreras.slice(0, 3).map((b) => `<li>${esc(TIPOS_BARRERA[b.tipo] || b.tipo)} · ${fecha(b.fecha)}</li>`).join("")}</ul></td>
      <td>${esc(f.nino.comunidad)}</td><td>${esc(f.nino.tutor_celular || "—")}</td><td>${badge(f.ultima_clasificacion)}</td></tr>`).join("");
  $$("#cuerpo-alertas-barreras tr").forEach((tr) => tr.addEventListener("click", () => abrirExpediente(tr.dataset.id)));
}
$("#filtro-alerta-comunidad").addEventListener("change", cargarAlertas);
$("#filtro-alerta-prioridad").addEventListener("change", cargarAlertas);

async function buscarExpediente() {
  const valor = $("#buscar-dni").value.trim();
  try {
    if (/^[0-9]{8}$/.test(valor)) { abrirExpediente((await api("/api/ninos/dni/" + valor)).id); return; }
    // Los registros del dataset no tienen DNI: se buscan por su código seudónimo (todos los estados).
    const filas = await api("/api/ninos?" + new URLSearchParams({ estado: "", q: valor }));
    const exacto = filas.find((f) => (f.codigo_origen || "").toLowerCase() === valor.toLowerCase());
    if (!exacto) throw { mensaje: "No existe un niño con ese DNI o código." };
    abrirExpediente(exacto.id);
  } catch (e) { toast(e.mensaje || "No encontrado", false); }
}
$("#btn-buscar-dni").addEventListener("click", buscarExpediente);
$("#buscar-dni").addEventListener("keydown", (ev) => { if (ev.key === "Enter") buscarExpediente(); });

/* ---------- HU-05: reporte ---------- */
async function generarReporte() {
  const desde = $("#desde").value, hasta = $("#hasta").value;
  $("#btn-csv").href = `/api/reportes/periodo?desde=${desde}&hasta=${hasta}&formato=csv`;
  try {
    const r = await api(`/api/reportes/periodo?desde=${desde}&hasta=${hasta}`);
    const total = Math.max(1, r.evaluaciones_realizadas);
    const pct = r.ninos_evaluados ? Math.round((100 * r.ninos_con_anemia) / r.ninos_evaluados) : 0;
    $("#reporte").innerHTML = `
      <div class="kpis">
        <div class="tarjeta kpi"><strong data-testid="kpi-registrados">${r.ninos_registrados}</strong><span>niños registrados en el periodo</span></div>
        <div class="tarjeta kpi"><strong>${r.evaluaciones_realizadas}</strong><span>evaluaciones de hemoglobina</span></div>
        <div class="tarjeta kpi"><strong>${r.ninos_evaluados}</strong><span>niños evaluados</span></div>
        <div class="tarjeta kpi"><strong>${pct}%</strong><span>evaluados con anemia (${r.ninos_con_anemia})</span></div>
      </div>
      <div class="bloques">
        <div class="tarjeta barras"><h2>Evaluaciones por clasificación</h2>
          ${["SIN_ANEMIA", "LEVE", "MODERADA", "SEVERA"].map((c) => `<div class="fila"><span>${ETIQUETA[c]}</span>
            <div class="pista"><div class="relleno" style="width:${(100 * r.por_clasificacion[c]) / total}%;background:${COLOR[c]}"></div></div><strong>${r.por_clasificacion[c]}</strong></div>`).join("")}
        </div>
        <div class="tarjeta tabla-envoltura"><table class="tabla"><thead><tr><th>Comunidad</th><th>Evaluaciones</th><th>Con anemia</th></tr></thead>
          <tbody>${r.por_comunidad.map((c) => `<tr><td>${esc(c.comunidad)}</td><td>${c.evaluaciones}</td><td>${c.con_anemia}</td></tr>`).join("") || '<tr><td colspan="3">Sin datos</td></tr>'}</tbody></table></div>
      </div>`;
  } catch (e) { $("#reporte").innerHTML = `<p class="alerta">${esc((e.errores?.[0] || e).mensaje)}</p>`; }
}
$("#btn-reporte").addEventListener("click", generarReporte);

/* ---------- VIS-3.5: visitas domiciliarias ---------- */
const RESULTADO_VISITA = { REALIZADA: "Realizada", NO_ENCONTRADO: "No se encontró a la familia", RECHAZADA: "La familia rechazó la visita" };
const SUPLEMENTO = { SI: "Sí", NO: "No", DESCONOCIDO: "No se sabe" };
const seccionVisitas = () => `
    <div class="tarjeta" style="margin-top:14px" data-testid="visitas-seccion">
      <div class="cabecera-exp"><h2>Visitas domiciliarias</h2>
        <button type="button" class="secundario" id="btn-visita-nino" data-testid="btn-visita-nino">Registrar visita</button></div>
      <div id="visitas-nino"><p class="vacio" style="padding:0">Cargando visitas…</p></div>
    </div>`;
const mismaRef = (a, b) => (a?.id && a.id === b?.id) || (a?.id_cliente && a.id_cliente === b?.id_cliente);

async function cargarVisitasNino(ref, nombre) {
  const caja = $("#visitas-nino");
  let hechas = [], aviso = "";
  if (ref.id) {
    try { hechas = await api(`/api/ninos/${ref.id}/visitas`); }
    catch (e) { if (!sinConexion(e)) { caja.innerHTML = `<p class="alerta">${esc(e.mensaje || "No se pudieron consultar las visitas.")}</p>`; return; } aviso = "Sin conexión: las visitas ya sincronizadas aún no se consultaron en este dispositivo."; }
  }
  const pendientes = (await window.Cola.listar()).filter((o) => o.tipo === "REGISTRAR_VISITA" && mismaRef(o.nino_ref, ref));
  if (!caja.isConnected) return;
  const filas = pendientes.map((o) => `<tr class="atenuado" data-testid="visita-pendiente"><td>${fecha(o.datos.fecha)}</td><td>${RESULTADO_VISITA[o.datos.resultado]}</td>
      <td>${SUPLEMENTO[o.datos.consume_suplemento]}</td><td>${esc(o.datos.observaciones || "—")}</td><td><span class="ctrl ctrl-LOCAL">Pendiente de sincronizar</span></td></tr>`)
    .concat(hechas.map((v) => `<tr data-testid="visita-fila"><td>${fecha(v.fecha)}</td><td>${RESULTADO_VISITA[v.resultado] || esc(v.resultado)}</td><td>${SUPLEMENTO[v.consume_suplemento] || esc(v.consume_suplemento)}</td>
      <td>${esc(v.observaciones || "—")}</td><td>${esc(v.registrado_por)}</td></tr>`));
  caja.innerHTML = (aviso ? `<p class="nota">${esc(aviso)}</p>` : "") + (filas.length
    ? `<div class="tabla-envoltura"><table class="tabla completa" data-testid="visitas-nino-tabla"><thead><tr><th>Fecha</th><th>Resultado</th><th>Consume el suplemento</th><th>Observaciones</th><th>Registrada por</th></tr></thead><tbody>${filas.join("")}</tbody></table></div>`
    : '<p class="vacio" style="padding:0" data-testid="visitas-nino-vacio">Aún no se registraron visitas a este niño.</p>');
}

const modalVisita = { ref: null, nombre: "", alTerminar: null };
function cerrarModalVisita() { $("#modal-visita").hidden = true; }
function abrirModalVisita({ ref, nombre, alTerminar }) {
  Object.assign(modalVisita, { ref, nombre, alTerminar });
  $("#visita-detalle").textContent = nombre;
  $("#visita-fecha").value = HOY; $("#visita-fecha").max = HOY;
  $("#visita-resultado").value = "REALIZADA"; $("#visita-suplemento").value = "DESCONOCIDO"; $("#visita-suplemento").disabled = false;
  $("#visita-observaciones").value = ""; $("#visita-error").textContent = "";
  $("#visita-barrera").value = ""; $("#campo-visita-barrera").hidden = true;
  $("#modal-visita").hidden = false;
  $("#visita-resultado").focus();
}
/* Solo una visita realizada informa si el niño consume el suplemento. */
$("#visita-resultado").addEventListener("change", () => {
  const realizada = $("#visita-resultado").value === "REALIZADA";
  $("#visita-suplemento").disabled = !realizada;
  if (!realizada) $("#visita-suplemento").value = "DESCONOCIDO";
  $("#campo-visita-barrera").hidden = realizada; // HIST-4.3: una visita no lograda puede dejar una barrera
  if (realizada) $("#visita-barrera").value = "";
});
$("#visita-cancelar").addEventListener("click", cerrarModalVisita);
$("#modal-visita").addEventListener("click", (ev) => { if (ev.target.id === "modal-visita") cerrarModalVisita(); });
addEventListener("keydown", (ev) => { if (ev.key === "Escape" && !$("#modal-visita").hidden) cerrarModalVisita(); });
$("#form-visita").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const { ref, nombre, alTerminar } = modalVisita;
  const datos = { fecha: $("#visita-fecha").value, resultado: $("#visita-resultado").value, consume_suplemento: $("#visita-suplemento").value,
    observaciones: $("#visita-observaciones").value.trim() || null };
  if (!datos.fecha) { $("#visita-error").textContent = "Ingrese la fecha de la visita."; return; }
  if (datos.fecha > HOY) { $("#visita-error").textContent = "La fecha de la visita no puede ser futura."; return; }
  const barrera = datos.resultado === "REALIZADA" ? "" : $("#visita-barrera").value;
  if (barrera === "OTRA" && !datos.observaciones) { $("#visita-error").textContent = "Con «Otra» barrera, descríbala en las observaciones."; return; }
  const registrarBarreraAsociada = () => (barrera
    ? barreraAsociada(ref, { tipo: barrera, detalle: datos.observaciones && datos.observaciones.slice(0, 200), fuente: "VISITA", fecha: datos.fecha }, nombre)
    : Promise.resolve());
  const terminar = (texto) => { cerrarModalVisita(); toast(texto); if (alTerminar) alTerminar(); };
  if (ref.id) {
    try { await api(`/api/ninos/${ref.id}/visitas`, { method: "POST", body: JSON.stringify(datos) }); await registrarBarreraAsociada(); terminar("Visita registrada"); return; }
    catch (e) { if (!sinConexion(e)) { $("#visita-error").textContent = (e.errores?.[0] || e).mensaje || "No se pudo registrar la visita."; return; } }
  }
  await window.Cola.encolar("REGISTRAR_VISITA", datos, { nino_ref: ref, resumen: `Visita domiciliaria a ${etiquetaNino(nombre)} del ${fecha(datos.fecha)}` });
  await registrarBarreraAsociada();
  terminar("Guardado en el dispositivo: se sincronizará al reconectar");
});

const establecimientosVisitas = new Set();
let secuenciaVisitas = 0;
async function cargarVisitas() {
  const mia = ++secuenciaVisitas;
  const p = new URLSearchParams({ limite: $("#filtro-visitas-limite").value });
  if ($("#filtro-visitas-establecimiento").value) p.set("establecimiento", $("#filtro-visitas-establecimiento").value);
  const aviso = $("#visitas-error");
  let filas;
  try { filas = await api("/api/visitas/priorizadas?" + p); }
  catch (e) {
    if (mia !== secuenciaVisitas) return;
    aviso.textContent = sinConexion(e) ? "Sin conexión: la lista priorizada aún no se consultó en este dispositivo." : (e.errores?.[0] || e).mensaje || "No se pudo consultar la lista.";
    aviso.hidden = false;
    return;
  }
  if (mia !== secuenciaVisitas) return;
  aviso.hidden = true;
  if (!$("#filtro-visitas-establecimiento").value) {
    filas.forEach((f) => establecimientosVisitas.add(f.establecimiento));
    const sel = $("#filtro-visitas-establecimiento"), actual = sel.value;
    sel.innerHTML = '<option value="">Todos</option>' + [...establecimientosVisitas].sort().map((x) => `<option value="${esc(x)}">${esc(x)}</option>`).join("");
    sel.value = actual;
  }
  const pendientes = new Set((await window.Cola.listar()).filter((o) => o.tipo === "REGISTRAR_VISITA" && o.nino_ref?.id).map((o) => o.nino_ref.id));
  $("#total-visitas").textContent = `${filas.length} niño(s)`;
  $("#sin-visitas").hidden = filas.length > 0;
  $("#cuerpo-visitas").innerHTML = filas.map((f) => `
    <tr data-nino="${f.nino.id}" data-nombre="${esc(f.nino.nombre_completo)}" data-testid="visita-priorizada">
      <td><strong>${f.posicion}</strong></td>
      <td><a href="#" class="enlace-nino">${esc(f.nino.nombre_completo)}</a><br><small>${f.nino.dni ? "DNI " + esc(f.nino.dni) : esc(f.nino.codigo_origen || "")}</small></td>
      <td>${esc(f.nino.comunidad)}</td><td>${badge(f.ultima_clasificacion)}</td>
      <td class="${f.dias_control_vencido ? "atrasado" : ""}">${f.dias_control_vencido ? f.dias_control_vencido + " d" : "—"}${f.inasistencias_recientes ? ` <span class="ctrl ctrl-INASISTENCIA">${f.inasistencias_recientes} inasist.</span>` : ""}</td>
      <td>${f.ultima_visita ? `${fecha(f.ultima_visita)} · ${f.dias_desde_ultima_visita} d` : "Sin visitas"}</td>
      <td><button type="button" class="puntaje" data-testid="puntaje" title="Ver cómo se calculó">${f.puntaje.toFixed(1)}</button></td>
      <td class="celda-acciones">${pendientes.has(f.nino.id) ? '<span class="ctrl ctrl-LOCAL" data-testid="visita-pendiente-fila">Pendiente de sincronizar</span> ' : ""}<button type="button" class="mini" data-testid="btn-visitar">Registrar visita</button></td>
    </tr>
    <tr class="desglose" hidden data-testid="desglose"><td colspan="8"><ul>${f.componentes.map((c) =>
      `<li><strong>${esc(c.descripcion)}</strong>: ${esc(c.valor)} → ${c.puntos.toFixed(1)} de ${c.maximo.toFixed(0)} puntos</li>`).join("")}</ul></td></tr>`).join("");
  $$("#cuerpo-visitas .puntaje").forEach((b) => b.addEventListener("click", () => { const d = b.closest("tr").nextElementSibling; d.hidden = !d.hidden; }));
  $$("#cuerpo-visitas .enlace-nino").forEach((x) => x.addEventListener("click", (ev) => { ev.preventDefault(); abrirExpediente(x.closest("tr").dataset.nino); }));
  $$("#cuerpo-visitas [data-testid=btn-visitar]").forEach((b) => b.addEventListener("click", () => {
    const tr = b.closest("tr");
    abrirModalVisita({ ref: { id: tr.dataset.nino }, nombre: tr.dataset.nombre, alTerminar: cargarVisitas });
  }));
}
$("#visitas-consultar").addEventListener("click", cargarVisitas);
$("#filtro-visitas-establecimiento").addEventListener("change", cargarVisitas);
$("#filtro-visitas-limite").addEventListener("change", cargarVisitas);

/* ---------- HIST-4.3: barreras de acceso al tratamiento ---------- */
const TIPOS_BARRERA = {
  TRANSPORTE: "Falta de transporte", ECONOMICA: "Falta de dinero", OLVIDO: "Olvido de la cita", TRABAJO_CUIDADOR: "Trabajo de la madre o cuidador",
  DISTANCIA_CLIMA: "Distancia o clima", EFECTOS_ADVERSOS_SUPLEMENTO: "Efectos adversos del suplemento", RECHAZO_TRATAMIENTO: "Rechazo del tratamiento", OTRA: "Otra (describir)",
};
const FUENTE_BARRERA = { PERSONAL: "Personal de salud", RESPUESTA_RECORDATORIO: "Respuesta a un recordatorio", INASISTENCIA: "Inasistencia a un control", VISITA: "Visita domiciliaria" };
/* Los selectores de barrera comparten el catálogo; la primera opción (vacía) depende de cada uno. */
$$(".select-barrera").forEach((s) => {
  s.innerHTML = `<option value="">${esc(s.dataset.vacio)}</option>` + Object.entries(TIPOS_BARRERA).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join("");
});

/* Registra una barrera: en línea si el niño ya está en el servidor; si no, queda en la cola del dispositivo (REGISTRAR_BARRERA). */
async function registrarBarrera(ref, datos, nombre) {
  if (ref.id) {
    try { await api(`/api/ninos/${ref.id}/barreras`, { method: "POST", body: JSON.stringify(datos) }); return "enviada"; }
    catch (e) {
      if (e.estado === 409) return "existente"; // el niño ya tenía esa barrera: no se duplica
      if (!sinConexion(e)) throw e;
    }
  }
  await window.Cola.encolar("REGISTRAR_BARRERA", datos, { nino_ref: ref, resumen: `Barrera «${TIPOS_BARRERA[datos.tipo]}» de ${etiquetaNino(nombre)} del ${fecha(datos.fecha)}` });
  return "en cola";
}

/* La barrera asociada a una inasistencia o a una visita no debe impedir que estas queden registradas: si falla, se avisa. */
async function barreraAsociada(ref, datos, nombre) {
  try { await registrarBarrera(ref, datos, nombre); }
  catch (e) { toast("Se registró, pero la barrera no se pudo guardar: " + ((e.errores?.[0] || e).mensaje || "inténtelo desde el expediente"), false); }
}

const seccionBarreras = () => `
    <div class="tarjeta" style="margin-top:14px" data-testid="barreras-seccion">
      <div class="cabecera-exp"><h2>Barreras de acceso</h2>
        <button type="button" class="secundario" id="btn-barrera-nino" data-testid="btn-barrera-nino">Registrar barrera</button></div>
      <div id="barreras-nino"><p class="vacio" style="padding:0">Cargando barreras…</p></div>
    </div>`;

async function cargarBarrerasNino(ref) {
  const caja = $("#barreras-nino");
  let hechas = [], aviso = "";
  if (ref.id) {
    try { hechas = await api(`/api/ninos/${ref.id}/barreras`); }
    catch (e) { if (!sinConexion(e)) { caja.innerHTML = `<p class="alerta">${esc(e.mensaje || "No se pudieron consultar las barreras.")}</p>`; return; } aviso = "Sin conexión: las barreras ya sincronizadas aún no se consultaron en este dispositivo."; }
  }
  const pendientes = (await window.Cola.listar()).filter((o) => o.tipo === "REGISTRAR_BARRERA" && mismaRef(o.nino_ref, ref));
  if (!caja.isConnected) return;
  const filas = pendientes.map((o) => `<tr class="atenuado" data-testid="barrera-pendiente"><td>${fecha(o.datos.fecha)}</td><td>${esc(TIPOS_BARRERA[o.datos.tipo] || o.datos.tipo)}</td>
      <td>${esc(o.datos.detalle || "—")}</td><td>${esc(FUENTE_BARRERA[o.datos.fuente] || o.datos.fuente)}</td><td><span class="ctrl ctrl-LOCAL">Pendiente de sincronizar</span></td></tr>`)
    .concat(hechas.map((b) => `<tr data-testid="barrera-fila"><td>${fecha(b.fecha)}</td><td>${esc(TIPOS_BARRERA[b.tipo] || b.tipo)}</td><td>${esc(b.detalle || "—")}</td>
      <td>${esc(FUENTE_BARRERA[b.fuente] || b.fuente)}</td><td>${esc(b.registrado_por)}</td></tr>`));
  caja.innerHTML = (aviso ? `<p class="nota">${esc(aviso)}</p>` : "") + (filas.length
    ? `<div class="tabla-envoltura"><table class="tabla completa" data-testid="barreras-nino-tabla"><thead><tr><th>Fecha</th><th>Barrera</th><th>Detalle</th><th>Origen</th><th>Registrada por</th></tr></thead><tbody>${filas.join("")}</tbody></table></div>`
    : '<p class="vacio" style="padding:0" data-testid="barreras-nino-vacio">No se registraron barreras de acceso para este niño.</p>');
}

const modalBarrera = { ref: null, nombre: "", alTerminar: null };
function cerrarModalBarrera() { $("#modal-barrera").hidden = true; }
function abrirModalBarrera({ ref, nombre, alTerminar }) {
  Object.assign(modalBarrera, { ref, nombre, alTerminar });
  $("#barrera-detalle-nino").textContent = nombre;
  $("#barrera-tipo").value = ""; $("#barrera-detalle").value = ""; $("#barrera-error").textContent = "";
  $("#barrera-fecha").value = HOY; $("#barrera-fecha").max = HOY;
  $("#modal-barrera").hidden = false;
  $("#barrera-tipo").focus();
}
$("#barrera-cancelar").addEventListener("click", cerrarModalBarrera);
$("#modal-barrera").addEventListener("click", (ev) => { if (ev.target.id === "modal-barrera") cerrarModalBarrera(); });
addEventListener("keydown", (ev) => { if (ev.key === "Escape" && !$("#modal-barrera").hidden) cerrarModalBarrera(); });
$("#form-barrera").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const { ref, nombre, alTerminar } = modalBarrera;
  const datos = { tipo: $("#barrera-tipo").value, detalle: $("#barrera-detalle").value.trim() || null, fuente: "PERSONAL", fecha: $("#barrera-fecha").value };
  if (!datos.tipo) { $("#barrera-error").textContent = "Seleccione una barrera."; return; }
  if (datos.tipo === "OTRA" && !datos.detalle) { $("#barrera-error").textContent = "Con «Otra» describa la barrera en el detalle."; return; }
  if (!datos.fecha) { $("#barrera-error").textContent = "Ingrese la fecha de la barrera."; return; }
  if (datos.fecha > HOY) { $("#barrera-error").textContent = "La fecha de la barrera no puede ser futura."; return; }
  try {
    const resultado = await registrarBarrera(ref, datos, nombre);
    cerrarModalBarrera();
    toast(resultado === "en cola" ? "Guardado en el dispositivo: se sincronizará al reconectar" : resultado === "existente" ? "El niño ya tenía registrada esa barrera" : "Barrera registrada");
    if (alTerminar) alTerminar();
  } catch (e) { $("#barrera-error").textContent = (e.errores?.[0] || e).mensaje || "No se pudo registrar la barrera."; }
});

/* ---------- HIST-4.1 y HIST-4.2: recordatorios y respuesta del tutor ---------- */
const ESTADO_RECORDATORIO = { ENVIADO_SIMULADO: "Simulado (no se envió)", ENVIADO: "Enviado", ENTREGADO: "Entregado", LEIDO: "Leído", FALLIDO: "Fallido" };
const TIPO_RECORDATORIO = { PROXIMO: "Próximo", CITA_DEL_DIA: "Cita de hoy", VENCIDO: "Vencido" };
const CANAL = { SIMULADO: "Simulado", WHATSAPP: "WhatsApp", SMS: "SMS" };
const pct = (v) => (v === null || v === undefined ? "—" : `${Math.round(v * 100)} %`);
const textoRespuesta = (r) => (!r.respuesta ? "" : r.respuesta === "CONFIRMA" ? "Confirma" : r.respuesta === "NO_PUEDE" ? "No puede asistir"
  : `Reprograma${r.fecha_reprogramada ? " para el " + fecha(r.fecha_reprogramada) : ""}`);

function pintarMetricasRecordatorios(m) {
  $("#recordatorios-metricas").innerHTML = `
    <div class="tarjeta kpi"><strong data-testid="kpi-rec-total">${m.total}</strong><span>recordatorios generados</span></div>
    <div class="tarjeta kpi"><strong data-testid="kpi-rec-enviados">${m.enviados}</strong><span>enviados (${m.simulados} simulados)</span></div>
    <div class="tarjeta kpi"><strong data-testid="kpi-rec-fallidos">${m.fallidos}</strong><span>fallidos</span></div>
    <div class="tarjeta kpi"><strong data-testid="kpi-rec-entrega">${pct(m.tasa_entrega)}</strong><span>tasa de entrega (envíos reales)</span></div>
    <div class="tarjeta kpi"><strong data-testid="kpi-rec-respuestas">${m.con_respuesta}</strong><span>con respuesta del tutor</span></div>
    <div class="tarjeta kpi"><strong data-testid="kpi-rec-confirmacion">${pct(m.tasa_confirmacion)}</strong><span>tasa de confirmación</span></div>`;
}

let secuenciaRecordatorios = 0;
async function cargarRecordatorios() {
  const mia = ++secuenciaRecordatorios;
  const p = new URLSearchParams();
  if ($("#filtro-recordatorio-estado").value) p.set("estado", $("#filtro-recordatorio-estado").value);
  const aviso = $("#recordatorios-error");
  let filas, metricas;
  try { [filas, metricas] = await Promise.all([api("/api/recordatorios?" + p), api("/api/recordatorios/metricas")]); }
  catch (e) {
    if (mia !== secuenciaRecordatorios) return;
    aviso.textContent = sinConexion(e) ? "Sin conexión: los recordatorios aún no se consultaron en este dispositivo." : (e.errores?.[0] || e).mensaje || "No se pudieron consultar los recordatorios.";
    aviso.hidden = false;
    return;
  }
  if (mia !== secuenciaRecordatorios) return;
  aviso.hidden = true;
  pintarMetricasRecordatorios(metricas);
  $("#total-recordatorios").textContent = `${filas.length} recordatorio(s)`;
  $("#sin-recordatorios").hidden = filas.length > 0;
  $("#cuerpo-recordatorios").innerHTML = filas.map((r) => `
    <tr data-id="${r.id}" data-nombre="${esc(r.nino.nombre_completo)}" data-control="${esc(r.codigo_control)}" data-programada="${r.fecha_programada}" data-testid="recordatorio">
      <td><a href="#" class="enlace-nino" data-nino="${r.nino.id}">${esc(r.nino.nombre_completo)}</a><br><small>${esc(r.nino.comunidad)}</small></td>
      <td>${esc(r.codigo_control)}<br><small>${fecha(r.fecha_programada)}</small></td>
      <td>${esc(TIPO_RECORDATORIO[r.tipo] || r.tipo)}</td>
      <td>${r.simulado ? '<span class="ctrl ctrl-SIMULADO" data-testid="marca-simulado" title="No salió ningún mensaje real">SIMULADO</span> ' : `<span class="ctrl ctrl-${r.estado}">${esc(CANAL[r.canal] || r.canal)}</span> `}
        <span data-testid="estado-recordatorio">${esc(ESTADO_RECORDATORIO[r.estado] || r.estado)}</span>${r.detalle ? `<br><small>${esc(r.detalle)}</small>` : ""}</td>
      <td>${esc(r.destino)}</td>
      <td data-testid="respuesta-recordatorio">${r.respuesta ? `${esc(textoRespuesta(r))}<br><small>${r.origen_respuesta === "WHATSAPP" ? "por WhatsApp" : "registrada por " + esc(r.respondido_por || "")}</small>` : '<span class="nota">Sin respuesta</span>'}</td>
      <td class="celda-acciones">${r.respuesta || r.estado === "FALLIDO" ? "" : '<button type="button" class="mini" data-testid="btn-responder">Registrar respuesta</button>'}</td>
    </tr>`).join("");
  $$("#cuerpo-recordatorios .enlace-nino").forEach((x) => x.addEventListener("click", (ev) => { ev.preventDefault(); abrirExpediente(x.dataset.nino); }));
  $$("#cuerpo-recordatorios [data-testid=btn-responder]").forEach((b) => b.addEventListener("click", () => abrirModalRespuesta(b.closest("tr"))));
}
$("#filtro-recordatorio-estado").addEventListener("change", cargarRecordatorios);
$("#recordatorios-actualizar").addEventListener("click", cargarRecordatorios);

$("#recordatorios-generar").addEventListener("click", async () => {
  const boton = $("#recordatorios-generar"), caja = $("#recordatorios-resultado");
  if (!navigator.onLine) { toast("Generar los recordatorios requiere conexión", false); return; }
  boton.disabled = true;
  try {
    const r = await api("/api/recordatorios/generar", { method: "POST", body: JSON.stringify({}) });
    const simulados = r.recordatorios.some((x) => x.simulado);
    caja.textContent = `Recordatorios de hoy: ${r.enviados} enviado(s), ${r.fallidos} fallido(s), ${r.omitidos_sin_contacto} sin contacto y ${r.omitidos_ya_enviado} ya enviado(s) antes.`
      + (simulados ? " Modo simulado: no salió ningún mensaje real." : "");
    caja.hidden = false;
    await cargarRecordatorios();
  } catch (e) {
    toast(sinConexion(e) ? "Sin conexión: no se pudieron generar los recordatorios" : (e.errores?.[0] || e).mensaje || "No se pudieron generar los recordatorios", false);
  } finally { boton.disabled = false; }
});

const modalRespuesta = { fila: null };
function cerrarModalRespuesta() { $("#modal-respuesta").hidden = true; modalRespuesta.fila = null; }
function actualizarCamposRespuesta() {
  const opcion = $("#respuesta-opcion").value;
  $("#campo-respuesta-fecha").hidden = opcion !== "REPROGRAMAR";
  $("#campo-respuesta-barrera").hidden = opcion !== "NO_PUEDE";
}
function abrirModalRespuesta(fila) {
  modalRespuesta.fila = fila;
  $("#respuesta-detalle").textContent = `${fila.dataset.nombre} · control ${fila.dataset.control} · programado el ${fecha(fila.dataset.programada)}`;
  $("#respuesta-opcion").value = "CONFIRMA"; $("#respuesta-fecha").value = ""; $("#respuesta-fecha").min = HOY;
  $("#respuesta-barrera").value = ""; $("#respuesta-barrera-detalle").value = ""; $("#respuesta-error").textContent = "";
  actualizarCamposRespuesta();
  $("#modal-respuesta").hidden = false;
  $("#respuesta-opcion").focus();
}
$("#respuesta-opcion").addEventListener("change", actualizarCamposRespuesta);
$("#respuesta-cancelar").addEventListener("click", cerrarModalRespuesta);
$("#modal-respuesta").addEventListener("click", (ev) => { if (ev.target.id === "modal-respuesta") cerrarModalRespuesta(); });
addEventListener("keydown", (ev) => { if (ev.key === "Escape" && !$("#modal-respuesta").hidden) cerrarModalRespuesta(); });
$("#form-respuesta").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const fila = modalRespuesta.fila, opcion = $("#respuesta-opcion").value;
  const cuerpo = { respuesta: opcion };
  if (opcion === "REPROGRAMAR") {
    cuerpo.fecha_reprogramada = $("#respuesta-fecha").value;
    if (!cuerpo.fecha_reprogramada) { $("#respuesta-error").textContent = "Indique la nueva fecha."; return; }
  }
  if (opcion === "NO_PUEDE" && $("#respuesta-barrera").value) {
    cuerpo.barrera = { tipo: $("#respuesta-barrera").value, detalle: $("#respuesta-barrera-detalle").value.trim() || null };
    if (cuerpo.barrera.tipo === "OTRA" && !cuerpo.barrera.detalle) { $("#respuesta-error").textContent = "Con «Otra» describa la barrera en el detalle."; return; }
  }
  try {
    const r = await api(`/api/recordatorios/${fila.dataset.id}/respuesta`, { method: "POST", body: JSON.stringify(cuerpo) });
    cerrarModalRespuesta();
    toast(r.barrera_sugerida ? "Respuesta registrada. Conviene registrar el motivo como barrera en el expediente" : "Respuesta registrada");
    await cargarRecordatorios();
    actualizarInsignia();
  } catch (e) {
    $("#respuesta-error").textContent = sinConexion(e) ? "Sin conexión: la respuesta del tutor se registra cuando haya conexión." : (e.errores?.[0] || e).mensaje || "No se pudo registrar la respuesta.";
  }
});

/* ---------- HIST-3.2 a 3.4: indicador, pendientes y conflictos ---------- */
const TIPO_OPERACION = { REGISTRAR_NINO: "Registro de niño", REGISTRAR_EVALUACION: "Control de hemoglobina", REGISTRAR_ASISTENCIA: "Asistencia a control", REGISTRAR_VISITA: "Visita domiciliaria", REGISTRAR_BARRERA: "Barrera de acceso" };
const horaLocal = (iso) => (iso ? `${fecha(iso.slice(0, 10))} ${iso.slice(11, 16)}` : "—");
let conflictosPendientes = 0;
async function actualizarSync() {
  const cola = await window.Cola.listar();
  const n = cola.length, ind = $("#sync-indicador"), sincronizando = window.Sync.enCurso;
  ind.dataset.pendientes = String(n);
  ind.textContent = sincronizando ? "Sincronizando…" : n ? `${n} ${n === 1 ? "pendiente" : "pendientes"}` : conflictosPendientes ? `Al día · ${conflictosPendientes} ${conflictosPendientes === 1 ? "conflicto" : "conflictos"}` : "Al día";
  ind.className = "sync-indicador " + (sincronizando ? "sincronizando" : n ? "con-pendientes" : conflictosPendientes ? "con-conflictos" : "al-dia");
  ind.title = navigator.onLine ? "Estado de la sincronización (abrir el panel)" : "Sin conexión: los registros se envían al reconectar";
  if ($("#vista-sincronizacion").classList.contains("activa")) pintarPendientes(cola);
}
document.addEventListener("cola:cambio", actualizarSync);
document.addEventListener("sync:inicio", actualizarSync);
$("#sync-indicador").addEventListener("click", () => mostrar("sincronizacion"));

function pintarPendientes(cola) {
  const rechazadas = cola.filter((o) => o.estado === "RECHAZADA").length;
  $("#sync-resumen").textContent = cola.length ? `${cola.length} pendiente(s)${rechazadas ? ` · ${rechazadas} rechazado(s)` : ""}` : "Al día";
  $("#sync-vacio").hidden = cola.length > 0;
  $("#cuerpo-sync").innerHTML = cola.map((o) => `
    <tr data-op="${o.id_operacion}" data-testid="pendiente">
      <td><strong>${esc(TIPO_OPERACION[o.tipo] || o.tipo)}</strong><br><small>${esc(o.resumen)}</small></td>
      <td>${horaLocal(o.fecha_local)}</td>
      <td>${o.estado === "RECHAZADA" ? '<span class="ctrl ctrl-RECHAZADA">Rechazado por el servidor</span>' : '<span class="ctrl ctrl-LOCAL">Pendiente</span>'}</td>
      <td>${o.ultimo_intento ? horaLocal(o.ultimo_intento) : "Aún no se intentó"}${o.ultimo_error ? `<br><small class="atrasado">${esc(o.ultimo_error)}</small>` : ""}</td>
      <td class="celda-acciones">${o.estado === "RECHAZADA" ? '<button type="button" class="mini" data-act="reintentar">Reintentar</button><button type="button" class="mini no" data-act="descartar">Descartar</button>' : ""}</td>
    </tr>`).join("");
  $$("#cuerpo-sync [data-act]").forEach((b) => b.addEventListener("click", async () => {
    const op = cola.find((o) => o.id_operacion === b.closest("tr").dataset.op);
    if (b.dataset.act === "descartar") { await window.Cola.quitar(op.id_operacion); toast("Registro descartado de este dispositivo"); return; }
    await window.Cola.actualizar({ ...op, estado: "PENDIENTE", ultimo_error: null });
    window.Sync.sincronizar();
  }));
}

const lineasDatos = (d) => Object.entries(d).filter(([k, v]) => k !== "id" && v !== null && v !== "")
  .map(([k, v]) => `${k.replaceAll("_", " ")}: ${v}`).join("\n");
async function cargarConflictos() {
  const caja = $("#conflictos");
  let lista;
  try { lista = await api("/api/sincronizacion/conflictos?estado=PENDIENTE"); }
  catch (e) {
    caja.innerHTML = `<p class="vacio" data-testid="conflictos-sin-datos">${sinConexion(e) ? "Sin conexión: los conflictos se consultan al reconectar." : esc(e.mensaje || "No se pudieron consultar los conflictos.")}</p>`;
    return;
  }
  conflictosPendientes = lista.length;
  $("#conflictos-total").textContent = `${lista.length} pendiente(s)`;
  caja.innerHTML = lista.length ? lista.map((c) => `
    <div class="tarjeta conflicto" data-conflicto="${c.id}" data-testid="conflicto">
      <strong>${esc(TIPO_OPERACION[c.tipo] || c.tipo)}</strong> · <span class="ctrl ctrl-RECHAZADA">Conflicto</span>
      <p style="margin:6px 0 0">${esc(c.motivo)}</p>
      <div class="comparar"><div><small>Lo registrado en este dispositivo</small><pre>${esc(lineasDatos(c.datos_cliente))}</pre></div>
        <div><small>Lo que ya tiene el servidor</small><pre>${esc(lineasDatos(c.datos_servidor))}</pre></div></div>
      <div class="acciones">
        <button type="button" class="primario" data-res="CONSERVAR_SERVIDOR" data-testid="conflicto-conservar">Conservar el del servidor</button>
        <button type="button" class="secundario" data-res="APLICAR_CLIENTE" data-testid="conflicto-aplicar">Aplicar el de este dispositivo</button>
        <button type="button" class="secundario" data-res="DESCARTAR" data-testid="conflicto-descartar">Descartar</button>
      </div>
      <small class="error" data-testid="conflicto-error"></small>
    </div>`).join("") : '<p class="vacio" data-testid="sin-conflictos">No hay conflictos pendientes.</p>';
  $$("#conflictos [data-res]").forEach((b) => b.addEventListener("click", async () => {
    const tarjeta = b.closest("[data-conflicto]");
    try {
      await api(`/api/sincronizacion/conflictos/${tarjeta.dataset.conflicto}/resolver`, { method: "POST", body: JSON.stringify({ resolucion: b.dataset.res }) });
      toast("Conflicto resuelto");
      await cargarConflictos();
      actualizarSync();
    } catch (e) { tarjeta.querySelector("[data-testid=conflicto-error]").textContent = sinConexion(e) ? "Sin conexión: inténtelo al reconectar." : (e.errores?.[0] || e).mensaje || "No se pudo resolver."; }
  }));
}
async function cargarSincronizacion() {
  const ultima = await window.Cola.meta("ultima_sincronizacion");
  $("#sync-ultima").textContent = ultima ? `Última sincronización exitosa: ${horaLocal(ultima)}` : "Aún no hay una sincronización exitosa en este dispositivo.";
  const aviso = $("#sync-aviso");
  aviso.hidden = window.Cola.persistente;
  aviso.textContent = "Este navegador no permite guardar datos en el dispositivo: lo pendiente se perderá al cerrar la pestaña. Sincronice antes de cerrarla.";
  pintarPendientes(await window.Cola.listar());
  cargarConflictos();
}
$("#sync-ahora").addEventListener("click", async () => {
  if (!navigator.onLine) { toast("Sin conexión: se sincronizará al reconectar", false); return; }
  if (!await window.Sync.sincronizar()) toast("No hay registros por enviar");
});

/* Al terminar una sincronización: aviso, indicador y refresco de la pantalla abierta. */
document.addEventListener("sync:fin", async (ev) => {
  const r = ev.detail;
  await actualizarSync();
  if (r.error) { toast(`No se pudo sincronizar: ${r.error}`, false); return; }
  const partes = [];
  if (r.aplicadas) partes.push(`${r.aplicadas} aplicado(s)`);
  if (r.duplicadas) partes.push(`${r.duplicadas} ya existían`);
  if (r.conflictos) partes.push(`${r.conflictos} en conflicto`);
  if (r.rechazadas) partes.push(`${r.rechazadas} rechazado(s)`);
  if (partes.length) toast(`Sincronización: ${partes.join(", ")}`, !r.rechazadas && !r.conflictos);
  try { await refrescarConflictos(); } catch (_) { /* sin conflictos que mostrar */ }
  const activa = $(".pestana.activa")?.dataset.vista;
  if (activa === "expediente" && expedienteActual?.id_cliente && r.mapeos[expedienteActual.id_cliente]) abrirExpediente(r.mapeos[expedienteActual.id_cliente]);
  else if (activa === "expediente" && expedienteActual?.id) abrirExpediente(expedienteActual.id);
  else if (activa !== "expediente" && activa !== "registro") mostrar(activa);
  else actualizarInsignia();
});
async function refrescarConflictos() {
  const lista = await api("/api/sincronizacion/conflictos?estado=PENDIENTE");
  conflictosPendientes = lista.length;
  await actualizarSync();
}

/* ---------- inicio ---------- */
const primeroDelMesAnterior = (iso) => { const [a, m] = iso.split("-").map(Number); return new Date(Date.UTC(a, m - 2, 1)).toISOString().slice(0, 10); };
function fijarFechasPorDefecto() {
  $("#desde").value = primeroDelMesAnterior(HOY);
  $("#hasta").value = HOY;
  valoresPorDefecto();
}
/* Contexto del servidor: «hoy» y, si está fijada, la fecha de referencia (corte del dataset) con un aviso visible. */
async function cargarContexto() {
  try {
    const c = await api("/api/salud");
    const anterior = HOY;
    HOY = c.fecha_hoy;
    const aviso = $("#aviso-referencia");
    aviso.hidden = !c.fecha_referencia;
    if (c.fecha_referencia) aviso.textContent = `Fecha de referencia: ${fecha(c.fecha_referencia)} (corte del dataset)`;
    if (HOY !== anterior) {
      $("#desde").value = primeroDelMesAnterior(HOY);
      $("#hasta").value = HOY;
      // La fecha del control solo se reemplaza si todavía es la que se puso por defecto (no pisa lo que el personal escribió).
      if (!form.elements.fecha.value || form.elements.fecha.value === anterior) form.elements.fecha.value = HOY;
      vistaPrevia();
    }
  } catch (_) { /* sin conexión: se conserva la fecha del navegador */ }
}

(async function iniciar() {
  if (!await window.Auth.ready) return;
  fijarFechasPorDefecto();
  restaurarBorrador();
  estadoRed();
  vistaPrevia();
  actualizarInsignia();
  await cargarContexto();
  await actualizarSync();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
  // HIST-3.2: la sincronización arranca sola al abrir la aplicación con pendientes y, como respaldo del evento «online», cada minuto.
  if (navigator.onLine) { window.Sync.sincronizar(); refrescarConflictos().catch(() => {}); }
  setInterval(async () => { if (navigator.onLine && (await window.Cola.listar()).some((o) => o.estado === "PENDIENTE")) window.Sync.sincronizar(); }, 60000);
})();
