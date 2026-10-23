/* Sesiones gestionadas por el servidor: no se guardan tokens en JS ni localStorage. */
window.Auth = (() => {
  let modo = "supabase", recuperacion = null;
  const $ = (s) => document.querySelector(s);
  const error = (texto) => { $("#login-error").textContent = texto; $("#login-error").hidden = false; };
  const request = (ruta, opciones = {}) => fetch(ruta, {
    ...opciones, credentials: "same-origin", cache: "no-store",
    headers: { "Content-Type": "application/json", "X-CSRF-Protection": "1", ...opciones.headers },
  });
  const mensaje = async (r) => {
    try { const b = await r.json(); return b.errores?.[0]?.mensaje || "No se pudo completar la solicitud."; }
    catch (_) { return "No se pudo completar la solicitud."; }
  };
  function mostrar(usuario) {
    $("#acceso").hidden = true;
    $("#aplicacion").hidden = false;
    const demo = modo === "demo";
    $("#usuario").hidden = !demo;
    $("#usuario-demo-label").hidden = !demo;
    $("#usuario-autenticado").hidden = demo;
    $("#cerrar-sesion").hidden = demo;
    if (usuario) $("#usuario-autenticado").textContent = usuario.email;
  }
  function recuperar() {
    if (!recuperacion) recuperacion = request("/api/auth/session").finally(() => { recuperacion = null; });
    return recuperacion;
  }
  async function iniciar() {
    try {
      const respuesta = await request("/api/auth/config");
      if (!respuesta.ok) throw new Error("No se pudo comprobar el acceso. Recarga la página.");
      const config = await respuesta.json();
      modo = config.modo;
      if (modo === "demo") { mostrar(null); return true; }
      // Los borradores clínicos de la demo anterior no se comparten entre usuarios.
      try { localStorage.removeItem("anemia-junin:borrador-registro"); } catch (_) {}
      if (!config.configurado) throw new Error("El acceso aún no está habilitado. Contacta al administrador.");
      $("#login-enviar").disabled = false;
      $("#login-estado").textContent = "Usa el correo y la contraseña de tu cuenta autorizada.";
      const r = await recuperar();
      if (r.ok) { mostrar((await r.json()).usuario); return true; }
      if (r.status !== 401) error(await mensaje(r));
    } catch (e) { error(e.message || "Sin conexión. Recarga la página para intentar de nuevo."); }
    return false;
  }
  $("#form-login").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    $("#login-error").hidden = true;
    const btn = $("#login-enviar");
    btn.disabled = true; btn.textContent = "Ingresando…";
    try {
      const r = await request("/api/auth/login", { method: "POST", body: JSON.stringify({
        email: $("#login-email").value.trim(), password: $("#login-password").value,
      }) });
      $("#login-password").value = "";
      if (!r.ok) { error(await mensaje(r)); return; }
      location.reload();
    } catch (_) { error("No se pudo conectar. Comprueba tu conexión e inténtalo nuevamente."); }
    finally { btn.disabled = false; btn.textContent = "Iniciar sesión"; }
  });
  $("#cerrar-sesion").addEventListener("click", async () => {
    $("#cerrar-sesion").disabled = true;
    try {
      const r = await request("/api/auth/logout", { method: "POST" });
      if (!r.ok && r.status !== 503) throw new Error("No se pudo cerrar la sesión. Inténtalo nuevamente.");
      location.reload();
    } catch (e) { alert(e.message || "Sin conexión. No se pudo cerrar la sesión."); $("#cerrar-sesion").disabled = false; }
  });
  return {
    get modo() { return modo; },
    ready: iniciar(),
    async fetch(ruta, opciones) {
      let r = await request(ruta, opciones);
      if (r.status === 401 && modo !== "demo") {
        const sesion = await recuperar();
        if (sesion.ok) r = await request(ruta, opciones);
        else if (sesion.status === 401) location.reload();
      }
      return r;
    },
  };
})();
