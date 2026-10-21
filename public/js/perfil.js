(async () => {
  const user = await montarLayout();
  // Ruta protegida: si no hay sesión, se manda al login
  if (!user) return (location.href = '/login');

  const cont = document.getElementById('perfil');
  const fecha = new Date(user.creado).toLocaleDateString('es-MX', { dateStyle: 'long' });

  const grid = el('div', { class: 'grid' });
  const pintarFavoritos = (favs) => {
    contador.textContent = `${favs.length} juego(s) guardado(s)`;
    if (!favs.length) {
      grid.replaceChildren(el('div', { class: 'empty' }, 'Aún no tienes favoritos. ', el('a', { href: '/juegos', text: 'Explora el catálogo' })));
      return;
    }
    grid.replaceChildren(...favs.map((f) => {
      const card = tarjetaJuego({ id: f.id, nombre: f.nombre, imagen: f.imagen });
      const quitar = el('button', { class: 'btn btn-outline btn-sm', text: 'Quitar' });
      quitar.addEventListener('click', async (e) => {
        e.preventDefault();
        const r = await api(`/api/favoritos/${f.id}`, { method: 'DELETE' });
        pintarFavoritos(r.favoritos);
        toast('Eliminado de favoritos');
      });
      card.querySelector('.body').append(quitar);
      return card;
    }));
  };

  const contador = el('p', { class: 'section-sub' });
  cont.replaceChildren(
    el('div', { class: 'page-header' }, el('h1', { text: 'Mi perfil' })),
    el('div', { class: 'profile-card' },
      el('div', { class: 'avatar', text: user.nombre.charAt(0).toUpperCase() }),
      el('div', { class: 'info' },
        el('h2', { text: user.nombre }),
        el('p', { text: `@${user.usuario} · ${user.email}` }),
        el('p', { text: `Plataforma favorita: ${user.plataforma} · Miembro desde ${fecha}` })
      )
    ),
    el('h2', { class: 'section-title', text: 'Mis favoritos' }),
    contador,
    grid
  );
  pintarFavoritos(user.favoritos);
})();
