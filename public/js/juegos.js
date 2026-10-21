montarLayout();

const form = document.getElementById('filtros');
const resultados = document.getElementById('resultados');
const resumen = document.getElementById('resumen');
const pager = document.getElementById('pager');
const params = new URLSearchParams(location.search);

const estado = {
  busqueda: params.get('busqueda') || '',
  genero: params.get('genero') || '',
  orden: params.get('orden') || '-added',
  pagina: Number(params.get('pagina')) || 1,
};

form.busqueda.value = estado.busqueda;
form.orden.value = estado.orden;

async function cargarGeneros() {
  try {
    const generos = await api('/api/generos');
    for (const g of generos) form.genero.append(el('option', { value: g.slug, text: g.nombre }));
    form.genero.value = estado.genero;
  } catch { /* si falla, solo queda "Todos los géneros" */ }
}

async function buscar() {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(estado)) if (v) q.set(k, v);
  history.replaceState(null, '', `?${q}`);

  cargando(resultados, 'Consultando la API de RAWG...');
  resumen.textContent = '';
  pager.classList.add('hidden');
  try {
    const data = await api(`/api/juegos?${q}`);
    if (!data.juegos.length) {
      resultados.replaceChildren(el('div', { class: 'empty', text: 'No se encontraron juegos con esos filtros.' }));
      return;
    }
    resumen.textContent = `${data.total.toLocaleString('es-MX')} juegos encontrados`;
    resultados.replaceChildren(el('div', { class: 'grid' }, data.juegos.map(tarjetaJuego)));

    pager.classList.remove('hidden');
    document.getElementById('num-pagina').textContent = `Página ${estado.pagina}`;
    document.getElementById('prev').disabled = estado.pagina <= 1;
    document.getElementById('next').disabled = !data.siguiente || estado.pagina >= 50;
  } catch (e) {
    mostrarError(resultados, e.message);
  }
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  estado.busqueda = form.busqueda.value.trim();
  estado.genero = form.genero.value;
  estado.orden = form.orden.value;
  estado.pagina = 1;
  buscar();
});
form.genero.addEventListener('change', () => form.requestSubmit());
form.orden.addEventListener('change', () => form.requestSubmit());

document.getElementById('prev').addEventListener('click', () => { estado.pagina--; buscar(); scrollTo(0, 0); });
document.getElementById('next').addEventListener('click', () => { estado.pagina++; buscar(); scrollTo(0, 0); });

cargarGeneros();
buscar();
