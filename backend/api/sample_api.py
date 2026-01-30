from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np # NaN判定をより確実にするために追加

app = Flask(__name__,
            template_folder='../../templates',
            static_folder='../../assets',
            static_url_path='/static'
            )
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルが見つかりません'}), 400
    file = request.files['file']
    filename = file.filename
    if filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xls', '.xlsx')):
            # シート名を指定。openpyxlがインストールされている必要があります
            df = pd.read_excel(file, sheet_name='フォームの回答 1')
        else:
            return jsonify({'error': 'ファイル形式が違います。CSVまたはExcelファイルをアップロードしてください。'}), 400
        
        print("読み込まれた列名一覧:", df.columns.tolist())
        
        df['本日の説明会の満足度を教えてください'] = pd.to_numeric(df['本日の説明会の満足度を教えてください'], errors='coerce')
        df['説明時間はいかがでしたか。'] = pd.to_numeric(df['説明時間はいかがでしたか。'], errors='coerce')

        # 計算処理
        data_sum = 8
        students_total = (df['0'] == '新入生ご本人様').sum()
        parents_total = (df['0'] == '保護者様').sum()
        
        satisfaction = df['本日の説明会の満足度を教えてください'].mean()
        satisfaction_students = df[df['0'] == '新入生ご本人様']['本日の説明会の満足度を教えてください'].mean()
        satisfaction_parents = df[df['0'] == '保護者様']['本日の説明会の満足度を教えてください'].mean()
        
        fell_time = df['説明時間はいかがでしたか。'].mean()
        fell_time_students = df[df['0'] == '新入生ご本人様']['説明時間はいかがでしたか。'].mean()
        fell_time_parents = df[df['0'] == '保護者様']['説明時間はいかがでしたか。'].mean()
        
        # NaN（未回答）を0に置き換える処理（修正・補完）
        # .item() を使うとnumpy型からPython標準型へ安全に変換できます
        res_data = {
            'students_total': int(students_total) if pd.notna(students_total) else 0,
            'parents_total': int(parents_total) if pd.notna(parents_total) else 0,
            'satisfaction': float(satisfaction) if pd.notna(satisfaction) else 0.0,
            'satisfaction_students': float(satisfaction_students) if pd.notna(satisfaction_students) else 0.0,
            'satisfaction_parents': float(satisfaction_parents) if pd.notna(satisfaction_parents) else 0.0,
            'fell_time': float(fell_time) if pd.notna(fell_time) else 0.0,
            'fell_time_students': float(fell_time_students) if pd.notna(fell_time_students) else 0.0,
            'fell_time_parents': float(fell_time_parents) if pd.notna(fell_time_parents) else 0.0,
            'data_sum': int(data_sum)
        }
        
        return jsonify({
            'status': 'success',
            **res_data
        })
        
    except Exception as e:
        # ターミナルに詳細なエラーを出すための追記
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)