from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd

app = Flask(__name__,
            template_folder='../../templates',
            static_folder='../../assets/js',
            static_url_path='/static'
            )
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file'not in request.files:
        return jsonify({'error': 'ファイルが見つかりません'}), 400
    file = request.files['file']
    filename = file.filename
    if filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file, sheet_name='Sheet1')
        else:
            return jsonify({'error': 'ファイル形式が違います。CSVまたはExcelファイルをアップロードしてください。'}), 400
        print(df.columns)

        data_sum = 8
        students_total = (df['新入生ご本人様か保護者の方か教えてください。'] == '新入生ご本人様').sum()
        parents_total = (df['新入生ご本人様か保護者の方か教えてください。'] == '保護者の方').sum()
        satisfaction = df['今回の説明会の満足度を教えてください。'].mean()
        satisfaction_students = df[df['新入生ご本人様か保護者の方か教えてください。'] == '新入生ご本人様']['今回の説明会の満足度を教えてください。'].mean()
        satisfaction_parents = df[df['新入生ご本人様か保護者の方か教えてください。'] == '保護者の方']['今回の説明会の満足度を教えてください。'].mean()
        fell_time = df['説明時間はいかがでしたか。'].mean()
        fell_time_students = df[df['新入生ご本人様か保護者の方か教えてください。'] == '新入生ご本人様']['説明時間はいかがでしたか。'].mean()
        fell_time_parents = df[df['新入生ご本人様か保護者の方か教えてください。'] == '保護者の方']['説明時間はいかがでしたか。'].mean()
    
        return jsonify({
            'status': 'success',
            'students_total': students_total,
            'parents_total': parents_total,
            'satisfaction': satisfaction,
            'satisfaction_students': satisfaction_students,
            'satisfaction_parents': satisfaction_parents,
            'fell_time': fell_time,
            'fell_time_students': fell_time_students,
            'fell_time_parents': fell_time_parents,
            'data_sum': data_sum
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)