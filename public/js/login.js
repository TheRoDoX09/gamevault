montarLayout().then((user) => { if (user) location.href = '/perfil'; });
activarMostrarPassword();

const form = document.getElementById('form-login');
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const identificador = form.identificador.value.trim();
  const password = form.password.value;

  marcarCampo(form.identificador, identificador ? '' : 'Escribe tu usuario o correo.');
  marcarCampo(form.password, password ? '' : 'Escribe tu contraseña.');
  if (!identificador || !password) return;

  const btn = document.getElementById('btn-enviar');
  btn.disabled = true;
  btn.textContent = 'Entrando...';
  try {
    await api('/api/login', { method: 'POST', body: JSON.stringify({ identificador, password }) });
    mostrarAlerta('¡Bienvenido! Redirigiendo...', 'ok');
    setTimeout(() => (location.href = '/perfil'), 700);
  } catch (err) {
    mostrarAlerta(err.message);
    btn.disabled = false;
    btn.textContent = 'Entrar';
  }
});
