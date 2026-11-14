/* NUEVO: MODULO PORTATIL DEL APARTADO "GRAFICAS" (JAVASCRIPT PURO, SIN LIBRERIAS) */
/* NUEVO: LO USA graficas.html (VISTA EN EL BACKEND) Y SE PUEDE COPIAR AL FRONTEND TAL CUAL */
(function (global) {
  'use strict';

  // NUEVO: SECCIONES DEL MENU "GRAFICAS" SEGUN EL ROL DEL USUARIO
  var SECCIONES = {
    ADMIN: [
      { id: 'estudiantes', etiqueta: 'Estudiantes / Devs', graficas: [
        { ruta: '/api/graficas/admin/estudiantes', titulo: 'Estudiantes / Devs' }
      ] },
      { id: 'retos', etiqueta: 'Retos', graficas: [
        { ruta: '/api/graficas/admin/retos-estado', titulo: 'Retos en total' },
        { ruta: '/api/graficas/admin/retos-tomados', titulo: 'Retos tomados y en proceso' }
      ] },
      { id: 'empresas', etiqueta: 'Empresas patrocinadoras', graficas: [
        { ruta: '/api/graficas/admin/empresas', titulo: 'Empresas patrocinadoras' }
      ] }
    ],
    USUARIO: [
      { id: 'mis-retos', etiqueta: 'Mis retos', graficas: [
        { ruta: '/api/graficas/estudiante/mis-retos', titulo: 'Mis retos: en proceso y culminados' }
      ] }
    ]
  };

  // NUEVO: CREA UN ELEMENTO HTML CON CLASE Y TEXTO (USA textContent PARA EVITAR INYECCION DE HTML)
  function el(etiqueta, clase, texto) {
    var nodo = document.createElement(etiqueta);
    if (clase) nodo.className = clase;
    if (texto !== undefined) nodo.textContent = texto;
    return nodo;
  }

  // NUEVO: PIDE LA IMAGEN AL BACKEND ENVIANDO EL TOKEN JWT Y LA MUESTRA EN UN <img>
  function cargarImagen(cfg, grafica, img, estado) {
    estado.textContent = 'Cargando gráfica…';
    estado.className = 'gp-estado';
    img.hidden = true;
    fetch(cfg.apiBase + grafica.ruta, {
      headers: { Authorization: 'Bearer ' + cfg.obtenerToken() }
    }).then(function (resp) {
      if (!resp.ok) {
        return resp.json().catch(function () { return {}; }).then(function (cuerpo) {
          var msg = cuerpo.message || cuerpo.error || ('Error ' + resp.status);
          if (resp.status === 401 || resp.status === 403) msg = 'No tienes permiso para ver esta gráfica.';
          throw new Error(msg);
        });
      }
      return resp.blob();
    }).then(function (blob) {
      if (img.dataset.url) URL.revokeObjectURL(img.dataset.url);
      var url = URL.createObjectURL(blob);
      img.dataset.url = url;
      img.src = url;
      img.hidden = false;
      estado.textContent = '';
    }).catch(function (err) {
      estado.textContent = err.message;
      estado.className = 'gp-estado gp-error';
    });
  }

  // NUEVO: DIBUJA LAS GRAFICAS DE UNA SECCION EN EL CONTENEDOR "vista"
  function mostrarSeccion(cfg, seccion) {
    cfg.vista.textContent = '';
    cfg.vista.appendChild(el('h2', 'gp-h2', seccion.etiqueta));
    seccion.graficas.forEach(function (g) {
      var tarjeta = el('section', 'gp-tarjeta');
      var cabecera = el('div', 'gp-cabecera');
      cabecera.appendChild(el('h3', 'gp-h3', g.titulo));
      var boton = el('button', 'gp-actualizar', 'Actualizar');
      boton.type = 'button';
      cabecera.appendChild(boton);
      var estado = el('p', 'gp-estado');
      var img = el('img', 'gp-img');
      img.alt = g.titulo;
      img.hidden = true;
      boton.addEventListener('click', function () { cargarImagen(cfg, g, img, estado); });
      tarjeta.appendChild(cabecera);
      tarjeta.appendChild(estado);
      tarjeta.appendChild(img);
      cfg.vista.appendChild(tarjeta);
      cargarImagen(cfg, g, img, estado);
    });
  }

  // NUEVO: DIBUJA EL APARTADO "GRAFICAS" DESPLEGABLE EN EL CONTENEDOR "menu"
  function montar(cfg) {
    // cfg = { menu, vista, apiBase, rol, obtenerToken }
    var secciones = SECCIONES[cfg.rol] || [];
    cfg.menu.textContent = '';
    if (!secciones.length) return;

    var grupo = el('div', 'gp-grupo');
    var titulo = el('button', 'gp-titulo');
    titulo.type = 'button';
    titulo.setAttribute('aria-expanded', 'false');
    titulo.appendChild(el('span', '', '📊 Gráficas'));
    var flecha = el('span', 'gp-flecha', '▾');
    titulo.appendChild(flecha);

    var lista = el('ul', 'gp-sub');
    lista.hidden = true;

    secciones.forEach(function (s) {
      var li = document.createElement('li');
      var b = el('button', 'gp-item', s.etiqueta);
      b.type = 'button';
      b.addEventListener('click', function () {
        Array.prototype.forEach.call(lista.querySelectorAll('.gp-item'), function (x) { x.classList.remove('gp-activo'); });
        b.classList.add('gp-activo');
        mostrarSeccion(cfg, s);
      });
      li.appendChild(b);
      lista.appendChild(li);
    });

    // NUEVO: AL HACER CLIC EN "GRAFICAS" SE ABRE O SE CIERRA LA LISTA DE APARTADOS
    titulo.addEventListener('click', function () {
      var abierto = lista.hidden;
      lista.hidden = !abierto;
      titulo.setAttribute('aria-expanded', String(abierto));
      flecha.textContent = abierto ? '▴' : '▾';
    });

    grupo.appendChild(titulo);
    grupo.appendChild(lista);
    cfg.menu.appendChild(grupo);
  }

  global.GraficasPanel = { montar: montar };
})(window);
