document.getElementById('purchase-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const userId = document.getElementById('user-id').value;
  const itemId = document.getElementById('item-id').value;
  const price = parseFloat(document.getElementById('price').value);

  const res = await fetch('/buy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, item_id: itemId, price })
  });

  if (res.ok) {
    alert('Purchase submitted!');
  } else {
    alert('Failed to submit.');
  }
});

document.getElementById('fetch-purchases').addEventListener('click', async () => {
  const userId = document.getElementById('user-id').value;
  const res = await fetch(`/purchases?user_id=${userId}`);
  const data = await res.json();

  const tbody = document.querySelector('#purchases-table tbody');
  tbody.innerHTML = ''; // clear

  data.forEach(({ user_id, item_id, price }) => {
    const row = document.createElement('tr');
    row.innerHTML = `<td>${user_id}</td><td>${item_id}</td><td>${price}</td>`;
    tbody.appendChild(row);
  });
});

