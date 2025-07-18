from __future__ import annotations

from flask import Flask, render_template, request

import os

from . import __version__, aggregate

FILE_PATH = os.path.abspath(__file__)
FILE_VERSION = __version__

app = Flask(__name__)

@app.route("/")
def index() -> str:
    """Render aggregated news as an HTML page."""
    top = request.args.get("n", type=int, default=10)
    news = aggregate(top)
    return render_template("blog.html", news=news)


if __name__ == "__main__":
    app.run(debug=True)
