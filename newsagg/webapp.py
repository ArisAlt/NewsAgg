from __future__ import annotations

from flask import Flask, render_template_string, request

from . import aggregate

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <meta charset='utf-8'>
    <title>NewsAgg</title>
</head>
<body>
    <h1>Aggregated News</h1>
    <ul>
    {% for item in news %}
        <li><a href="{{ item['link'] }}">{{ item['source'] }} - {{ item['title'] }}</a></li>
    {% endfor %}
    </ul>
</body>
</html>
"""


@app.route("/")
def index() -> str:
    """Render aggregated news as an HTML page."""
    top = request.args.get("n", type=int, default=10)
    news = aggregate(top)
    return render_template_string(HTML_TEMPLATE, news=news)


if __name__ == "__main__":
    app.run(debug=True)
