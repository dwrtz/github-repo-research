# Setup

create a virtual environment
```bash
python3 -m venv .venv
```

activate the virtual environment
```bash
source .venv/bin/activate
```

install dependencies
```bash
pip install -r requirements.txt
```

create a .env file
```bash
cp .env.example .env
```

add your credentials to the .env file

# Run

run the script
```bash
python3 scrape.py
```

# Rate Limiting

According to ChatGPT, the GitHub api rate limit is 5000 authenticated requests per hour.