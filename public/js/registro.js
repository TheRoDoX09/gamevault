// Validación del formulario de registro (lado del cliente).
// El servidor vuelve a validar todo: nunca se confía solo en el navegador.
montarLayout().then((user) => { if (user) location.href = '/perfil'; });
activarMostrarPassword();

const form = document.getElementById('form-registro');
const tocados = new Set();

const REQS = {
  len: (p) => p.length >= 8,
  may: (p) => /[A-Z]/.test(p),
  min: (p) => /[a-z]/.test(p),
  num: (p) => /\d/.test(p),
  sim: (p) => /[^A-Za-z0-9]/.test(p),
};

function edad(fecha) {
  const nac = new Date(fecha);
  if (!fecha || isNaN(nac)) return -1;
  const hoy = new Date();
  let e = hoy.getFullYear() - nac.getFullYear();
  const m = hoy.getMonth() - nac.getMonth();
  if (m < 0 || (m === 0 && hoy.getDate() < nac.getDate())) e--;
  return e;
}

const validadores = {
  nombre: (v) => {
    v = v.trim();
    if (!v) return 'El nombre es obligatorio.';
    if (v.length < 3) return 'Mínimo 3 caracteres.';
    if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$/.test(v)) return 'Solo se permiten letras y espacios.';
    return '';
  },
  usuario: (v) => {
    if (!v) return 'El nombre de usuario es obligatorio.';
    if (v.length < 4 || v.length > 20) return 'Debe tener entre 4 y 20 caracteres.';
    if (!/^[A-Za-z0-9_]+$/.test(v)) return 'Solo letras, números y guion bajo (_).';
    return '';
  },
  email: (v) => {
    if (!v) return 'El correo es obligatorio.';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) return 'Escribe un correo electrónico válido.';
    return '';
  },
  password: (v) => {
    if (!v) return 'La contraseña es obligatoria.';
    if (!Object.values(REQS).every((fn) => fn(v))) return 'La contraseña no cumple todos los requisitos.';
    return '';
  },
  confirmar: (v) => {
    if (!v) return 'Confirma tu contraseña.';
    if (v !== form.password.value) return 'Las contraseñas no coinciden.';
    return '';
  },
  nacimiento: (v) => {
    if (!v) return 'La fecha de nacimiento es obligatoria.';
    const e = edad(v);
    if (e < 0) return 'La fecha no puede ser futura.';
    if (e < 13) return 'Debes tener al menos 13 años para registrarte.';
    if (e > 120) return 'Escribe una fecha válida.';
    return '';
  },
  plataforma: (v) => (v ? '' : 'Selecciona tu plataforma favorita.'),
  terminos: (_, input) => (input.checked ? '' : 'Debes aceptar los términos.'),
};

function validar(nombre) {
  const input = form[nombre];
  const msg = validadores[nombre](input.value, input);
  marcarCampo(input, msg);
  return !msg;
}

// Barra de fuerza de contraseña
function actualizarFuerza() {
  const p = form.password.value;
  let puntos = 0;
  for (const [clave, fn] of Object.entries(REQS)) {
    const ok = fn(p);
    document.querySelector(`[data-req="${clave}"]`).classList.toggle('ok', ok);
    if (ok) puntos++;
  }
  const colores = ['#f87171', '#f87171', '#fb923c', '#fbbf24', '#a3e635', '#34d399'];
  const barra = document.getElementById('barra');
  barra.style.width = `${(puntos / 5) * 100}%`;
  barra.style.background = colores[puntos];
}

// Validación en tiempo real
for (const nombre of Object.keys(validadores)) {
  const input = form[nombre];
  const evento = input.type === 'checkbox' || input.tagName === 'SELECT' ? 'change' : 'input';
  input.addEventListener(evento, () => {
    tocados.add(nombre);
    validar(nombre);
    if (nombre === 'password') {
      actualizarFuerza();
      if (tocados.has('confirmar')) validar('confirmar');
    }
  });
  input.addEventListener('blur', () => { tocados.add(nombre); validar(nombre); });
}

// No permitir fechas futuras en el selector
form.nacimiento.max = new Date().toISOString().slice(0, 10);

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const resultados = Object.keys(validadores).map(validar);
  if (resultados.includes(false)) {
    mostrarAlerta('Revisa los campos marcados en rojo.');
    form.querySelector('.field.invalid input, .field.invalid select')?.focus();
    return;
  }

  const datos = {
    nombre: form.nombre.value.trim(),
    usuario: form.usuario.value.trim(),
    email: form.email.value.trim(),
    password: form.password.value,
    confirmar: form.confirmar.value,
    nacimiento: form.nacimiento.value,
    plataforma: form.plataforma.value,
    terminos: form.terminos.checked,
  };

  const btn = document.getElementById('btn-enviar');
  btn.disabled = true;
  btn.textContent = 'Creando cuenta...';
  try {
    await api('/api/registro', { method: 'POST', body: JSON.stringify(datos) });
    mostrarAlerta('¡Cuenta creada con éxito! Redirigiendo a tu perfil...', 'ok');
    setTimeout(() => (location.href = '/perfil'), 1000);
  } catch (err) {
    // Errores de validación que regresa el servidor (ej. correo ya registrado)
    const errores = err.data?.errores;
    if (errores) {
      for (const [campo, msg] of Object.entries(errores)) if (form[campo]) marcarCampo(form[campo], msg);
      mostrarAlerta('No se pudo crear la cuenta. Revisa los campos.');
    } else {
      mostrarAlerta(err.message);
    }
    btn.disabled = false;
    btn.textContent = 'Crear cuenta';
  }
});
