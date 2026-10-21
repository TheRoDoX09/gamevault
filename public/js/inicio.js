(async () => {
  const user = await montarLayout();
  if (user) {
    const cta = document.getElementById('cta-registro');
    cta.textContent = `Ver mis favoritos (${user.favoritos.length})`;
    cta.href = '/perfil';
  }

  const cont = document.getElementById('populares');
  cargando(cont, 'Cargando juegos desde la API...');
  try {
    const data = await api('/api/juegos?orden=-metacritic');
    cont.replaceChildren(el('div', { class: 'grid' }, data.juegos.slice(0, 8).map(tarjetaJuego)));
  } catch (e) {
    mostrarError(cont, e.message);
  }
})();
