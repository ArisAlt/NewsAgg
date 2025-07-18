# NewsAgg

NewsAgg is a simple tool that aggregates the most-viewed
articles from several Greek news sites. It combines RSS feeds with
HTML scraping to gather headlines, previews and images. Results can be
viewed from the command line or through a lightweight web application.

## Usage

Run the tool using the provided script or directly as a module:

```bash
python main.py

# or simply
python -m newsagg -n 5
```

You can also invoke the CLI module directly and specify the number of
items per source or show the current version and path information:

```bash
python -m newsagg.cli -n 5 --version
```

The package lives in the `newsagg/` directory and is currently at
version `0.7.0`.
Running with `--version` will also print the paths to the main
aggregator file (`newsagg/aggregator.py`) and the blog template
(`newsagg/templates/blog.html`) used by the web server as well as their
individual versions. The core scraping logic resides in
`newsagg/aggregator.py`.

## Web Application

Run the built-in web server to view the aggregated news in your browser:

```bash
python -m newsagg.webapp
```

Navigate to `http://localhost:5000/` to see the results. You can supply
the query parameter `n` to control how many items per source are
displayed. The page now uses a blog-style template located at
`newsagg/templates/blog.html` for a cleaner, photo-friendly layout
inspired by [Riverside.fm](https://Riverside.fm). Each entry shows a
preview snippet and an article image when available. The server
implementation can be found in `newsagg/webapp.py`.
