let charts = {};

async function uploadData() {
    const fileInput = document.getElementById('select_file');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            renderChart('students_total_chart', '新入生ご本人様の合計', ['合計'], [data.students_total]);
            renderChart('parents_total_chart', '保護者の方の合計', ['合計'], [data.parents_total]);
            renderChart('satisfaction_chart', '説明会の満足度', ['平均'], [data.satisfaction]);
            renderChart('satisfaction_students_chart', '新入生ご本人様の満足度', ['平均'], [data.satisfaction_students]);
            renderChart('satisfaction_parents_chart', '保護者の方の満足度', ['平均'], [data.satisfaction_parents]);
            renderChart('fell_time_chart', '説明会の所要時間', ['平均'], [data.fell_time]);
            renderChart('fell_time_students_chart', '新入生ご本人様の所要時間', ['平均'], [data.fell_time_students]);
            renderChart('fell_time_parents_chart', '保護者の方の所要時間', ['平均'], [data.fell_time_parents]);
        }
    } catch (error) {
        console.error('通信エラー：', error);
    }
}

function renderChart(canvasId, label, labels, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}