# Requirements
1. Python 3.11
2. [uv package manager](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)

# Setup
Create a virtual environment

```sh
uv venv
```

Install the dependencies

```sh
uv sync
```

# Running the Server
Activate the virtual environment

```sh
source .venv/bin/activate
```

Run the FastAPI development server

```sh
fastapi dev src/main.py
```

Or run FastAPI in production mode

```sh
fastapi run src/main.py
```
