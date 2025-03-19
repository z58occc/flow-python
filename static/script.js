function changeMonth(offset) {
    var currentYear = parseInt(document.querySelector('h1').innerText.split('年')[0]);
    var currentMonth = parseInt(document.querySelector('h1').innerText.split('年')[1].split('月')[0]);
    var newMonth = currentMonth + offset;

    if (newMonth < 1) {
        newMonth = 12;
        currentYear -= 1;
    } else if (newMonth > 12) {
        newMonth = 1;
        currentYear += 1;
    }

    window.location.href = `/?year=${currentYear}&month=${newMonth}`;
}

function showFootfall(year, month, day) {
    const img = document.getElementById('footfallChart');
    img.src = `/footfall_chart/${year}/${month}/${day}.png`;
    img.style.display = 'block';

    fetch(`/api/footfall/${year}/${month}/${day}`)
        .then(response => response.json())
        .then(data => {
            const detailsDiv = document.getElementById('footfall-details');
            detailsDiv.innerHTML = `<h2>${year}-${month}-${day} 人流資料</h2>`;
            if (data.error) {
                detailsDiv.innerHTML += `<p>${data.error}</p>`;
                img.style.display = 'none';
            } else {
                detailsDiv.innerHTML += `<p>總人流量: ${data.footfall.reduce((a, b) => a + b, 0)}</p>`;
            }
            detailsDiv.style.display = 'block'; // 顯示原本隱藏的人流資料
        })
        .catch(error => {
            console.error('Error fetching footfall data:', error);
        });
}

