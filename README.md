# NewsAgg

NewsAgg is a simple command-line tool that aggregates the most-viewed
articles from several Greek news sites.

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
version `0.1.0`.
