let charts = {};

async function uploadData() {
    const fileInput = document.getElementById('select_file');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Flaskサーバーが起動しているか確認してください
        const response = await fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        console.log("サーバーからの生データ:", data);

        if (data.status === 'success') {
            // テキスト表示部分
            document.getElementById('display-file_name').innerText = data.file_name;
            document.getElementById('display_students_total').innerText = data.students_total;
            document.getElementById('display_parents_total').innerText = data.parents_total;
            document.getElementById('display_satisfaction').innerText = data.satisfaction.toFixed(3);

            // chart1: 新入生と保護者の「合計」を並べる
            renderChart('chart1', ['合計'], [
                {
                    label: '新入生',
                    data: [data.students_total],
                    color: 'rgba(54, 162, 235, 0.5)' // 明るい青（透明度50%）
                },
                {
                    label: '保護者',
                    data: [data.parents_total],
                    color: 'rgba(255, 159, 64, 0.5)' // 明るいオレンジ（透明度50%）
                }
            ]);

            renderChart('chart2', ['平均'], [
                {
                    label: '全体',
                    data: [data.satisfaction],
                    color: 'rgba(75, 192, 192, 0.5)' // 明るいエメラルド
                },
                {
                    label: '新入生',
                    data: [data.satisfaction_students],
                    color: 'rgba(153, 102, 255, 0.5)' // 明るいパープル
                },
                {
                    label: '保護者',
                    data: [data.satisfaction_parents],
                    color: 'rgba(255, 99, 132, 0.5)' // 明るいピンク
                }
            ]);
            renderChart('chart3', data.time_labels, [
                {
                    label: '全体', 
                    data: data.time_data_all,
                    color: 'rgba(255, 206, 86, 0.5)' // 明るいイエロー
                },
                {
                    label: '新入生', 
                    data: data.time_data_students,
                    color: 'rgba(54, 162, 235, 0.5)' // 明るいブルー
                },
                {
                    label: '保護者', 
                    data: data.time_data_parents,
                    color: 'rgba(255, 159, 64, 0.5)' // 明るいオレンジ
                }
            ]);
            renderChart('chart4', data.good_point_labels, [
                {
                    label: '全体', 
                    data: data.good_point_data_all,
                    color: 'rgba(75, 192, 192, 0.5)' // 明るいエメラルド
                },
                {
                    label: '新入生', 
                    data: data.good_point_data_students,
                    color: 'rgba(153, 102, 255, 0.5)' // 明るいパープル
                },
                {
                    label: '保護者',
                    data: data.good_point_data_parents,
                    color: 'rgba(255, 99, 132, 0.5)' // 明るいピンク
                }
            ]);
            renderChart('chart5', data.good_point_labels, [
                {
                    label: '一人暮らし予定',
                    data: data.good_point_data_living_alone,
                    color: 'rgba(255, 159, 64, 0.5)' // 明るいオレンジ
                },
                {
                    label: '実家通学予定',
                    data: data.good_point_data_living_home,
                    color: 'rgba(54, 162, 235, 0.5)' // 明るいブルー
                }
            ]);
        }
    } catch (error) {
        console.error('通信エラー：', error);
        alert('サーバーに接続できませんでした。Flaskが起動しているか、URLが正しいか確認してください。');
    }
}

// グラフ描画用の関数（引数を整理しました）
// main.js の renderChart 関数をこれに差し替えてみてください
function renderChart(canvasId, xLabels, dataConfigs) { // ← 第3引数が dataConfigs になっているか？
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    // ここで dataConfigs を使って datasets を作ります
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
            scales: { y: { beginAtZero: true } }
        }
    });
}