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

        # 計算処理
        data_sum = 8
        students_total = (df['0'] == '新入生ご本人様').sum()
        parents_total = (df['0'] == '保護者様').sum()
        
        satisfaction = df['本日の説明会の満足度を教えてください'].mean()
        satisfaction_students = df[df['0'] == '新入生ご本人様']['本日の説明会の満足度を教えてください'].mean()
        satisfaction_parents = df[df['0'] == '保護者様']['本日の説明会の満足度を教えてください'].mean()
        
        time_labels = ['短い', 'ちょうど良い', '長い']
        good_point_labels = [
            '大学生協のご説明',
            '九工大生の一日（通学編）', 
            '九工大生の一日（講義編）',
            '九工大生の一日（昼食編）',
            '九工大生の一日（学外編）',
            '九工大での4年間',
        ]

        # 2. 全体、新入生、保護者それぞれのカウント関数
        # 1. 時間の集計（パーセント化）
        def time_get_counts(target_df):
            # 該当列の有効回答（空欄以外）を取得
            series = target_df['説明時間はいかがでしたか。'].dropna()
            
            # 分母（有効回答数）を計算
            total = len(series)
            
            if total == 0:
                return [0] * len(time_labels)

            counts = series.value_counts().to_dict()
            
            # (該当数 / 全体数) * 100 でパーセント計算
            return [int((counts.get(label, 0) / total) * 100) for label in time_labels]
        

        # 2. よかった点・全体/属性別（パーセント化）
        def good_point_get_counts(target_df):
            col_name = 'よかった、ためになった説明を教えてください'
            if col_name not in target_df.columns:
                return [0] * len(good_point_labels)

            # 分母は「その属性の総人数」にします（例：新入生が100人いて80人が選んだら80%）
            total_people = len(target_df)
            
            if total_people == 0:
                return [0] * len(good_point_labels)

            series = target_df[col_name].dropna().astype(str)
            all_answers = series.str.split(r',\s*').explode()
            counts = all_answers.str.strip().value_counts().to_dict()
            
            return [int((counts.get(label, 0) / total_people) * 100) for label in good_point_labels] 


        # 3. よかった点・居住形態別（パーセント化）
        def good_point_get_counts_by_living_status(target_df, target_status):
            col_name_point = 'よかった、ためになった説明を教えてください'
            col_name_living = '一人暮らし予定か実家通学予定かお答えください'

            if col_name_point not in target_df.columns or col_name_living not in target_df.columns:
                return [0] * len(good_point_labels)

            # まず条件で絞り込む
            subset = target_df[target_df[col_name_living] == target_status]
            
            # 分母はこの条件（一人暮らし等）に当てはまる人の総数
            total_people = len(subset)

            if total_people == 0:
                return [0] * len(good_point_labels)

            series = subset[col_name_point].dropna().astype(str)
            all_answers = series.str.split(r',\s*').explode()
            counts = all_answers.str.strip().value_counts().to_dict()

            return [int((counts.get(label, 0) / total_people) * 100) for label in good_point_labels]
        
        students_df = df[df['0'] == '新入生ご本人様']
        parents_df = df[df['0'] == '保護者様']
        
        # NaN（未回答）を0に置き換える処理（修正・補完）
        # .item() を使うとnumpy型からPython標準型へ安全に変換できます
        return jsonify ({
            'status': 'success',
            'time_labels': time_labels,
            'time_data_all': time_get_counts(df),
            'time_data_students': time_get_counts(students_df),
            'time_data_parents': time_get_counts(parents_df),
            'good_point_labels': good_point_labels,
            'good_point_data_all': good_point_get_counts(df),
            'good_point_data_students': good_point_get_counts(students_df),
            'good_point_data_parents': good_point_get_counts(parents_df),
            'good_point_data_living_alone': good_point_get_counts_by_living_status(df, '一人暮らし予定'),
            'good_point_data_living_home': good_point_get_counts_by_living_status(df, '実家通学予定'),
            'students_total': int(students_total) if pd.notna(students_total) else 0,
            'parents_total': int(parents_total) if pd.notna(parents_total) else 0,
            'satisfaction': float(satisfaction) if pd.notna(satisfaction) else 0.0,
            'satisfaction_students': float(satisfaction_students) if pd.notna(satisfaction_students) else 0.0,
            'satisfaction_parents': float(satisfaction_parents) if pd.notna(satisfaction_parents) else 0.0,
            'data_sum': int(data_sum),
            'file_name': filename
        })
        
    except Exception as e:
        # ターミナルに詳細なエラーを出すための追記
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)