/* Cliente web del PMV (PWA). Consume la API REST del Incremento 1. */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const ETIQUETA = { SIN_ANEMIA: "Sin anemia", LEVE: "Anemia leve", MODERADA: "Anemia moderada", SEVERA: "Anemia severa", NO_APLICA: "No aplica (< 6 m)" };
const COLOR = { SIN_ANEMIA: "#1F7A3D", LEVE: "#C99200", MODERADA: "#D26A1B", SEVERA: "#B0222B", NO_APLICA: "#8C99A6" };
const CLAVE_BORRADOR = "anemia-junin:borrador-registro";
const CAMPOS_NINO = ["dni", "nombres", "apellidos", "sexo", "fecha_nacimiento", "establecimiento", "distrito", "comunidad", "altitud_m", "tutor_nombre", "tutor_celular"];
const CAMPOS_EVAL = ["fecha", "hemoglobina_observada", "peso_kg", "talla_cm"];
const NUMERICOS = ["altitud_m", "hemoglobina_observada", "peso_kg", "talla_cm"];
const hoyISO = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);

async function api(ruta, opciones = {}) {
  const r = await fetch(ruta, {
    ...opciones,
    headers: { "Content-Type": "application/json", "X-Usuario": $("#usuario").value, ...(opciones.headers || {}) },
  });
  const cuerpo = r.headers.get("content-type")?.includes("json") ? await r.json() : null;
  if (!r.ok) throw { estado: r.status, ...(cuerpo || { mensaje: "Error de comunicación." }) };
  return cuerpo;
}

function toast(texto, ok = true) {
  const t = $("#toast");
  t.textContent = texto; t.className = "toast" + (ok ? " ok" : ""); t.hidden = false;
  clearTimeout(t._t); t._t = setTimeout(() => (t.hidden = true), 3200);
}

const badge = (c) => c ? `<span class="badge ${c}">${ETIQUETA[c]}</span>` : `<span class="badge NO_APLICA">Sin control</span>`;
const edad = (m) => (m < 12 ? `${m} m` : `${Math.floor(m / 12)} a ${m % 12} m`);
const fecha = (iso) => (iso ? iso.split("-").reverse().join("/") : "—");
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* ---------- navegación ---------- */
function mostrar(vista) {
  $$(".pestana").forEach((b) => b.classList.toggle("activa", b.dataset.vista === vista));
  $$(".vista").forEach((v) => v.classList.toggle("activa", v.id === "vista-" + vista));
  if (vista === "seguimiento") cargarSeguimiento();
}
$$(".pestana").forEach((b) => b.addEventListener("click", () => mostrar(b.dataset.vista)));

/* ---------- conectividad (indicador; la sincronización llega en INC-3) ---------- */
function estadoRed() { $("#red").classList.toggle("fuera", !navigator.onLine); $("#red").title = navigator.onLine ? "En línea" : "Sin conexión: el borrador se conserva en el dispositivo"; }
addEventListener("online", estadoRed); addEventListener("offline", estadoRed);

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
  try { localStorage.setItem(CLAVE_BORRADOR, JSON.stringify(leerFormulario())); $("#borrador").hidden = false; } catch (_) { /* almacenamiento no disponible */ }
}
function restaurarBorrador() {
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
    pintarErrores(e.errores || []);
    const alerta = $("#alerta-registro");
    alerta.textContent = e.estado === 409 ? e.mensaje : (e.mensaje || "No se pudo guardar.");
    alerta.hidden = false;
  }
});
function valoresPorDefecto() {
  form.elements.establecimiento.value = "P. S. Chongos Alto";
  form.elements.distrito.value = "Chongos Alto";
  form.elements.altitud_m.value = 3550;
  form.elements.fecha.value = hoyISO();
}
$("#limpiar").addEventListener("click", () => { form.reset(); borrarBorrador(); limpiarErrores(); valoresPorDefecto(); vistaPrevia(); });

/* ---------- HU-04: seguimiento ---------- */
let temporizadorBusqueda;
async function cargarSeguimiento() {
  const p = new URLSearchParams({ estado: $("#filtro-estado").value });
  if ($("#buscar").value.trim()) p.set("q", $("#buscar").value.trim());
  if ($("#filtro-clasificacion").value) p.set("clasificacion", $("#filtro-clasificacion").value);
  const filas = await api("/api/ninos?" + p);
  $("#total-seguimiento").textContent = `${filas.length} niño(s)`;
  $("#sin-resultados").hidden = filas.length > 0;
  $("#cuerpo-seguimiento").innerHTML = filas.map((f) => `
    <tr class="click" data-id="${f.id}">
      <td><strong>${esc(f.nombre_completo)}</strong></td><td>${f.dni}</td><td>${edad(f.edad_meses)}</td><td>${esc(f.comunidad)}</td>
      <td class="${f.control_atrasado ? "atrasado" : ""}">${fecha(f.ultima_fecha_control)}${f.dias_desde_ultimo_control !== null ? ` · ${f.dias_desde_ultimo_control} d` : ""}</td>
      <td>${f.ultima_hb_ajustada !== null ? f.ultima_hb_ajustada.toFixed(1) : "—"}</td><td>${badge(f.ultima_clasificacion)}</td>
    </tr>`).join("");
  $$("#cuerpo-seguimiento tr").forEach((tr) => tr.addEventListener("click", () => abrirExpediente(tr.dataset.id)));
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
  mostrar("expediente");
  const exp = await api("/api/ninos/" + id);
  const u = exp.evaluaciones[0];
  $("#expediente").innerHTML = `
    <div class="tarjeta">
      <div class="cabecera-exp">
        <div><h2 style="font-size:19px;margin:0">${esc(exp.nombres)} ${esc(exp.apellidos)}</h2>
          <span class="chip">${exp.estado === "ACTIVO" ? "Seguimiento activo" : "Alta"}</span> ${u ? badge(u.clasificacion) : ""}</div>
        <div><button class="secundario" id="btn-editar">Editar datos</button></div>
      </div>
      <div class="datos">
        <div><span>DNI</span><strong>${exp.dni}</strong></div>
        <div><span>Edad</span><strong>${edad(exp.edad_meses)}</strong></div>
        <div><span>Nacimiento</span><strong>${fecha(exp.fecha_nacimiento)}</strong></div>
        <div><span>Sexo</span><strong>${exp.sexo}</strong></div>
        <div><span>Comunidad / distrito</span><strong>${esc(exp.comunidad)} · ${esc(exp.distrito)}</strong></div>
        <div><span>Altitud</span><strong>${exp.altitud_m} m s. n. m.</strong></div>
        <div><span>Madre / tutor</span><strong>${esc(exp.tutor_nombre)}</strong></div>
        <div><span>Celular</span><strong>${exp.tutor_celular || "—"}</strong></div>
        <div><span>Establecimiento</span><strong>${esc(exp.establecimiento)}</strong></div>
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
        <tbody>${exp.evaluaciones.map((e) => `<tr><td>${fecha(e.fecha)}</td><td>${edad(e.edad_meses)}</td><td>${e.hemoglobina_observada.toFixed(1)}</td>
          <td><strong>${e.hemoglobina_ajustada.toFixed(1)}</strong></td><td>${badge(e.clasificacion)}</td><td>${e.peso_kg} kg · ${e.talla_cm} cm</td></tr>`).join("")}</tbody></table>
      </div>
      <div class="tarjeta">
        <h2>Evolución de hemoglobina ajustada</h2>${grafico(exp.evaluaciones) || '<p class="vacio" style="padding:0">Se mostrará con dos o más controles.</p>'}
        <h2 style="margin-top:14px">Registrar nuevo control</h2>
        <form id="form-control" novalidate>
          <div class="fila2"><div class="campo"><label>Fecha</label><input type="date" name="fecha" value="${hoyISO()}"><small class="error"></small></div>
          <div class="campo"><label>Hb observada (g/dL)</label><input type="number" step="0.1" name="hemoglobina_observada"><small class="error"></small></div></div>
          <div class="fila2"><div class="campo"><label>Peso (kg)</label><input type="number" step="0.1" name="peso_kg"><small class="error"></small></div>
          <div class="campo"><label>Talla (cm)</label><input type="number" step="0.1" name="talla_cm"><small class="error"></small></div></div>
          <div class="acciones"><button class="primario" data-testid="guardar-control">Guardar control</button></div>
        </form>
      </div>
    </div>`;
  $("#btn-editar").addEventListener("click", () => ($("#form-editar").hidden = !$("#form-editar").hidden));
  $("#form-editar").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const f = ev.target; const cambios = {};
    ["comunidad", "tutor_nombre", "tutor_celular", "estado"].forEach((c) => (cambios[c] = f.elements[c].value.trim()));
    cambios.altitud_m = Number(f.elements.altitud_m.value);
    try { await api("/api/ninos/" + id, { method: "PATCH", body: JSON.stringify(cambios) }); toast("Expediente actualizado"); abrirExpediente(id); }
    catch (e) { pintarErrores(e.errores || [], f); }
  });
  $("#form-control").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const f = ev.target; $$(".campo", f).forEach((c) => c.classList.remove("invalido")); $$(".error", f).forEach((x) => (x.textContent = ""));
    const datos = { fecha: f.elements.fecha.value || null };
    ["hemoglobina_observada", "peso_kg", "talla_cm"].forEach((c) => (datos[c] = f.elements[c].value === "" ? null : Number(f.elements[c].value)));
    try { await api(`/api/ninos/${id}/evaluaciones`, { method: "POST", body: JSON.stringify(datos) }); toast("Control registrado"); abrirExpediente(id); }
    catch (e) { pintarErrores(e.errores || [], f); }
  });
}
$("#btn-buscar-dni").addEventListener("click", async () => {
  try { const exp = await api("/api/ninos/dni/" + $("#buscar-dni").value.trim()); abrirExpediente(exp.id); }
  catch (e) { toast(e.mensaje || "No encontrado", false); }
});

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

/* ---------- inicio ---------- */
(function iniciar() {
  const h = hoyISO(); const d = new Date(); d.setDate(1);
  $("#desde").value = new Date(d.getFullYear(), d.getMonth() - 1, 1).toISOString().slice(0, 10);
  $("#hasta").value = h;
  valoresPorDefecto();
  restaurarBorrador();
  estadoRed();
  vistaPrevia();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
})();
