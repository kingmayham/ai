const runBtn = document.getElementById('runBtn');
const taskInput = document.getElementById('task');
const filesInput = document.getElementById('files');
const applyInput = document.getElementById('apply');
const output = document.getElementById('output');
const intentChip = document.getElementById('intentChip');

function parseFiles(value) {
  const items = value
    .split(',')
    .map((v) => v.trim())
    .filter(Boolean);
  return items.length ? items : null;
}

runBtn.addEventListener('click', async () => {
  const task = taskInput.value.trim();
  if (!task) {
    output.textContent = 'Please enter a task.';
    return;
  }

  output.textContent = 'Running assistant...';

  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        task,
        files: parseFiles(filesInput.value),
        apply: applyInput.checked,
      }),
    });

    const data = await res.json();
    if (!res.ok) {
      output.textContent = `Error: ${JSON.stringify(data, null, 2)}`;
      return;
    }

    intentChip.textContent = `Intent: ${data.intent}`;
    output.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    output.textContent = `Request failed: ${err.message}`;
  }
});
