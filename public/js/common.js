// =============================================================
//  Código compartido por todas las páginas
// =============================================================

// Petición al web service propio. Las cookies de sesión viajan solas (same-origin).
async function api(url, opciones = {}) {
  const resp = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    ...opciones,
  });
  let data = {};
  try { data = await resp.json(); } catch { /* respuesta sin JSON */ }
  if (!resp.ok) {
    const err = new Error(data.error || 'Ocurrió un error inesperado.');
    err.status = resp.status;
    err.data = data;
    throw err;
  }
  return data;
}

// Crea un elemento de forma segura (textContent evita inyección de HTML / XSS)
function el(tag, attrs = {}, ...hijos) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  }
  for (const h of hijos.flat()) if (h != null) e.append(h instanceof Node ? h : document.createTextNode(h));
  return e;
}

// Iconos de línea (SVG) usados en todo el sitio
const ICONOS = {
  buscar: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  grafica: '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
  corazon: '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
  candado: '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  ojo: '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
  ojoCerrado: '<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.4 10.4 0 0 1 12 5c7 0 10 7 10 7a13 13 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.5 13.5 0 0 0 2 12s3 7 10 7a9.7 9.7 0 0 0 5.39-1.61"/><path d="m2 2 20 20"/>',
  estrella: '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
  menu: '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
  usuario: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  control: '<rect x="2" y="6" width="20" height="12" rx="4"/><path d="M6 12h4"/><path d="M8 10v4"/><path d="M15 13h.01"/><path d="M18 11h.01"/>',
};

function icono(nombre) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('class', 'ico');
  svg.setAttribute('aria-hidden', 'true');
  svg.innerHTML = ICONOS[nombre]; // contenido fijo definido arriba, no datos del usuario
  return svg;
}

// Rellena los elementos del HTML marcados con data-icon="nombre"
document.querySelectorAll('[data-icon]').forEach((e) => e.prepend(icono(e.dataset.icon)));

function toast(msg) {
  let t = document.querySelector('.toast');
  if (!t) document.body.append((t = el('div', { class: 'toast' })));
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 2600);
}

let usuarioActual = null;
async function obtenerUsuario() {
  try {
    usuarioActual = (await api('/api/me')).usuario;
  } catch {
    usuarioActual = null;
  }
  return usuarioActual;
}

// ---------- Navbar y footer ----------
async function montarLayout() {
  const pagina = location.pathname.replace(/\/$/, '') || '/index';
  const links = [
    ['/', 'Inicio'],
    ['/juegos', 'Juegos'],
  ];

  const ul = el('ul', { class: 'nav-links', id: 'nav-links' });
  const header = el('header', { class: 'navbar' },
    el('div', { class: 'container' },
      el('a', { href: '/', class: 'logo' }, icono('control'), el('span', { text: 'GameVault' })),
      el('button', { class: 'nav-toggle', 'aria-label': 'Abrir menú', onclick: () => ul.classList.toggle('open') }, icono('menu')),
      ul
    )
  );
  document.body.prepend(header);

  const footer = el('footer', {},
    el('div', { class: 'container' },
      el('span', { text: `© ${new Date().getFullYear()} GameVault · Práctica Unidad 3` }),
      el('span', {}, 'Datos de videojuegos por ', el('a', { href: 'https://rawg.io', target: '_blank', rel: 'noopener', text: 'RAWG API' }))
    )
  );
  document.body.append(footer);

  const user = await obtenerUsuario();
  if (user) {
    links.push(['/perfil', user.usuario, 'usuario']);
  } else {
    links.push(['/login', 'Iniciar sesión'], ['/registro', 'Registrarse']);
  }

  for (const [href, texto, ico] of links) {
    const activo = href === '/' ? pagina === '/index' || pagina === '' : pagina.startsWith(href);
    ul.append(el('li', {}, el('a', { href, class: activo ? 'active' : null }, ico ? icono(ico) : null, texto)));
  }
  if (user) {
    ul.append(el('li', {}, el('a', {
      href: '#', text: 'Salir',
      onclick: async (e) => {
        e.preventDefault();
        await api('/api/logout', { method: 'POST' });
        location.href = '/';
      },
    })));
  }
  return user;
}

// ---------- Tarjeta de juego ----------
function tarjetaJuego(j) {
  const meta = [
    j.rating ? el('span', { class: 'rating' }, icono('estrella'), j.rating.toFixed(1)) : null,
    j.lanzamiento ? el('span', { text: j.lanzamiento.slice(0, 4) }) : null,
    j.metacritic ? el('span', { class: 'mc', text: j.metacritic }) : null,
  ].filter(Boolean);
  return el('a', { href: `/juego?id=${encodeURIComponent(j.id)}`, class: 'game-card' },
    el('div', { class: 'thumb' },
      j.imagen ? el('img', { src: j.imagen, alt: j.nombre, loading: 'lazy' }) : icono('control')
    ),
    el('div', { class: 'body' },
      el('h3', { text: j.nombre }),
      meta.length ? el('div', { class: 'meta' }, meta) : null,
      el('div', { class: 'chips' }, (j.generos || []).slice(0, 3).map((g) => el('span', { class: 'chip', text: g })))
    )
  );
}

function cargando(cont, texto = 'Cargando...') {
  cont.replaceChildren(el('div', { class: 'loader' }, el('div', { class: 'spinner' }), el('span', { text: texto })));
}

function mostrarError(cont, msg) {
  cont.replaceChildren(el('div', { class: 'alert alert-warn', text: msg }));
}

// ---------- Formularios ----------
function activarMostrarPassword() {
  document.querySelectorAll('.pass-toggle').forEach((b) =>
    b.addEventListener('click', () => {
      const input = document.getElementById(b.dataset.target);
      input.type = input.type === 'password' ? 'text' : 'password';
      b.replaceChildren(icono(input.type === 'password' ? 'ojo' : 'ojoCerrado'));
    })
  );
}

function marcarCampo(input, mensaje) {
  const field = input.closest('.field');
  field.classList.toggle('invalid', Boolean(mensaje));
  field.classList.toggle('valid', !mensaje);
  field.querySelector('.error-msg').textContent = mensaje || '';
}

function mostrarAlerta(texto, tipo = 'error') {
  const a = document.getElementById('alerta');
  a.className = `alert alert-${tipo}`;
  a.textContent = texto;
}
