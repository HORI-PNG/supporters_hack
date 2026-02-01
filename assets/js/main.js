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
            // 省略：テキスト表示部分

            // chart1: 新入生と保護者の「合計」を並べる
            renderChart('chart1', ['合計'], [
                { label: '新入生', data: [data.students_total], color: 'rgba(0, 68, 113, 0.8)' },
                { label: '保護者', data: [data.parents_total], color: 'rgba(255, 153, 0, 0.8)' }
            ]);

            // chart2: 全体・新入生・保護者の「満足度平均」を並べる
            renderChart('chart2', ['平均'], [
                { label: '全体', data: [data.satisfaction], color: 'rgba(75, 192, 192, 0.8)' },
                { label: '新入生', data: [data.satisfaction_students], color: 'rgba(0, 68, 113, 0.8)' },
                { label: '保護者', data: [data.satisfaction_parents], color: 'rgba(255, 153, 0, 0.8)' }
            ]);
        }
    } catch (error) {
        console.error('通信エラー：', error);
    }
}

function renderChart(canvasId, xLabels, dataConfigs) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const datasets = dataConfigs.map(config => ({
        label: config.label,
        data: config.data,
        backgroundColor: config.color,
        borderWidth: 1
    }));

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: xLabels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}