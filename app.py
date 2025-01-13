from flask import Flask, request, jsonify, render_template
from platform_class import Platform

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/parse', methods=['POST'])
def parse():
    try:
        data = request.get_json()
        url = data.get('url')
        xpath = data.get('xpath')

        if not url or not xpath:
            return jsonify({'error': 'Missing URL or XPath'}), 400

        # Використання логіки парсера
        platform = Platform(url=url, xpath=xpath)
        result = platform.parser()

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)