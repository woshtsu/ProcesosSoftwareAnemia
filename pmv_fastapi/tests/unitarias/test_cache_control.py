"""Pruebas unitarias para las cabeceras Cache-Control de rutas estáticas y API."""


def test_cache_control_inicio_no_cache(cliente):
    r = cliente.get("/")
    assert r.status_code == 200
    assert r.headers.get("Cache-Control") == "no-cache"


def test_cache_control_sw_no_cache(cliente):
    r = cliente.get("/sw.js")
    assert r.status_code == 200
    assert r.headers.get("Cache-Control") == "no-cache"


def test_cache_control_static_sw_no_cache(cliente):
    r = cliente.get("/static/sw.js")
    assert r.status_code == 200
    assert r.headers.get("Cache-Control") == "no-cache"


def test_cache_control_static_estilos_revalida(cliente):
    r = cliente.get("/static/estilos.css")
    assert r.status_code == 200
    assert r.headers.get("Cache-Control") == "no-cache"
    assert r.headers.get("ETag")


def test_cache_control_static_app_js_revalida_con_304(cliente):
    r = cliente.get("/static/app.js")
    assert r.status_code == 200
    assert r.headers.get("Cache-Control") == "no-cache"
    r2 = cliente.get("/static/app.js", headers={"If-None-Match": r.headers["ETag"]})
    assert r2.status_code == 304


def test_cache_control_vendor_largo(cliente):
    r = cliente.get("/static/vendor/swagger-ui-bundle.js")
    assert r.status_code == 200
    assert r.headers.get("Cache-Control") == "public, max-age=86400"


def test_cache_control_static_manifest_public_max_age(cliente):
    r = cliente.get("/static/manifest.json")
    assert r.status_code == 200
    assert r.headers.get("Cache-Control") == "public, max-age=86400"


def test_cache_control_api_salud_no_store(cliente):
    r = cliente.get("/api/salud")
    assert r.status_code == 200
    assert r.headers.get("Cache-Control") == "no-store"
