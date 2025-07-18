from __future__ import annotations

from flask import Flask, render_template, request

from . import aggregate

app = Flask(__name__)

@app.route("/")
def index() -> str:
    """Render aggregated news as an HTML page."""
    top = request.args.get("n", type=int, default=10)
    news = aggregate(top)
    return render_template("blog.html", news=news)


if __name__ == "__main__":
    app.run(debug=True)
