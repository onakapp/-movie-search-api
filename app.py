from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import openai

app = Flask(__name__)
CORS(app)

# OpenAI APIキーを環境変数から取得
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 映画データの読み込み
with open("映画.json", encoding="utf-8") as f:
    movies = json.load(f)

# ヘルパー関数：ChatGPTでフィルタ用キーワード抽出
def extract_keywords(user_input):
    prompt = f"""
ユーザーの気分や希望に応じて、映画検索用のキーワードを5つに要約してください。
出力形式はJSON配列にしてください。

ユーザー入力:「{user_input}」

出力例: ["感動", "恋愛", "実話", "青春", "泣ける"]
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    keywords = response["choices"][0]["message"]["content"]
    return json.loads(keywords)

@app.route("/api/search", methods=["POST"])
def search_movies():
    data = request.get_json()
    user_input = data.get("user_input", "")

    try:
        keywords = extract_keywords(user_input)
    except Exception as e:
        return jsonify({"error": "キーワード抽出に失敗しました", "details": str(e)}), 500

    # キーワードと一致する映画をフィルター（簡易的な部分一致）
    result = []
    for movie in movies:
        match_count = sum(kw.lower() in json.dumps(movie, ensure_ascii=False).lower() for kw in keywords)
        if match_count > 0:
            result.append({
                "title": movie["title"],
                "description": movie["description"]
            })
        if len(result) >= 5:
            break

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
