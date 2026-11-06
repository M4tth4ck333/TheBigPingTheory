const log = document.getElementById('terminal-log');

document.getElementById('run-button').addEventListener('click', () => {
  const timestamp = new Date().toISOString().split('T')[1].slice(0, 8);
  log.textContent += `\n[${timestamp}] Simulation gestartet.`;
  log.scrollTop = log.scrollHeight;
});

document.getElementById('clear-button').addEventListener('click', () => {
  log.textContent = '[INFO] Log geleert.';
});
