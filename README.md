# NYC-MTA-ridership-challenge
Submission for NYC MTA ridership challenge at plotly and Maven Analytics

# Flow
- Select the service you wanna know more about
- Pick up a date range
- Click to capture the graph
- Ask query related to graph
- LLM will reply with a simpler summarisation.

# To run on your device

## Option 1:
- Use Docker

```
docker run -p 8050:8050 -e OPENAI_API_KEY="your_openai_key_here" rishi1304/nyc_mta_ridership_challenge_dash_app:latest
```

## Option 2:
- Use git clone to clone this repository
- Add your OPENAI_API_KEY to environment like in bashrc, zshrc or similar
- Optionally can add KEY into app.py in line 15
- Run ```python src/app.py```