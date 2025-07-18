# NewsAgg

NewsAgg is a simple tool that aggregates the most-viewed
articles from several Greek news sites. Results can be viewed from the
command line or through a lightweight web application.

## Usage

Run the tool using the provided script:

```bash
python main.py
```

You can also invoke the CLI module directly and specify the number of
items per source or show the current version and path information:

```bash
python -m newsagg.cli -n 5 --version
```

The package lives in the `newsagg/` directory and is currently at
version `0.2.0`.

## Web Application

Run the built-in web server to view the aggregated news in your browser:

```bash
python -m newsagg.webapp
```

Navigate to `http://localhost:5000/` to see the results. You can supply
the query parameter `n` to control how many items per source are
displayed.
The server implementation can be found in `newsagg/webapp.py`.
