const main = document.getElementById('detalle');
const id = new URLSearchParams(location.search).get('id');

(async () => {
  const user = await montarLayout();
  const cont = el('div', { class: 'container' });
  main.replaceChildren(cont);

  if (!/^\d+$/.test(id || '')) return mostrarError(cont, 'Juego no válido.');
  cargando(cont, 'Cargando información del juego...');

  let j;
  try {
    j = await api(`/api/juegos/${id}`);
  } catch (e) {
    return mostrarError(cont, e.message);
  }
  document.title = `${j.nombre} · GameVault`;

  // Botón de favoritos (requiere sesión)
  let esFav = Boolean(user?.favoritos.some((f) => f.id === j.id));
  const btnFav = el('button', { class: 'btn btn-fav' });
  const pintarFav = () => {
    btnFav.classList.toggle('on', esFav);
    btnFav.replaceChildren(icono('corazon'), esFav ? 'En favoritos' : 'Agregar a favoritos');
  };
  pintarFav();
  btnFav.addEventListener('click', async () => {
    if (!user) return (location.href = '/login');
    btnFav.disabled = true;
    try {
      if (esFav) await api(`/api/favoritos/${j.id}`, { method: 'DELETE' });
      else await api('/api/favoritos', { method: 'POST', body: JSON.stringify({ id: j.id, nombre: j.nombre, imagen: j.imagen }) });
      esFav = !esFav;
      pintarFav();
      toast(esFav ? 'Agregado a tus favoritos' : 'Eliminado de favoritos');
    } catch (e) {
      toast(e.message);
    }
    btnFav.disabled = false;
  });

  const hero = el('section', { class: 'detail-hero' },
    el('div', { class: 'container' },
      el('a', { href: '/juegos', text: 'Volver al catálogo' }),
      el('h1', { text: j.nombre }),
      el('div', { class: 'chips' }, j.generos.map((g) => el('span', { class: 'chip', text: g }))),
      el('p', { class: 'actions' }, btnFav)
    )
  );
  if (j.imagen) hero.style.backgroundImage = `url("${encodeURI(j.imagen)}")`;

  const dato = (titulo, valor) => (valor ? [el('dt', { text: titulo }), el('dd', { text: valor })] : []);
  const info = el('aside', { class: 'info-box' },
    el('dl', {},
      dato('Calificación', j.rating ? `${j.rating.toFixed(2)} de 5` : null),
      dato('Metacritic', j.metacritic),
      dato('Lanzamiento', j.lanzamiento ? new Date(j.lanzamiento + 'T00:00').toLocaleDateString('es-MX', { dateStyle: 'long' }) : 'Por anunciar'),
      dato('Tiempo de juego promedio', j.tiempo ? `${j.tiempo} horas` : null),
      dato('Plataformas', j.plataformas.join(', ')),
      dato('Desarrollador', j.desarrolladores.join(', ')),
      j.sitio && /^https?:\/\//.test(j.sitio)
        ? [el('dt', { text: 'Sitio oficial' }), el('dd', {}, el('a', { href: j.sitio, target: '_blank', rel: 'noopener noreferrer', text: 'Visitar sitio' }))]
        : []
    )
  );

  const contenido = el('div', {},
    el('h2', { class: 'section-title', text: 'Acerca del juego' }),
    el('p', { class: 'desc', text: j.descripcion || 'Sin descripción disponible.' }),
    j.capturas.length ? el('h2', { class: 'section-title', text: 'Capturas' }) : null,
    el('div', { class: 'shots' }, j.capturas.map((src) => el('img', { src, alt: `Captura de ${j.nombre}`, loading: 'lazy' })))
  );

  main.replaceChildren(hero, el('div', { class: 'container detail-grid' }, contenido, info));
})();
