# Precinct Scraper

This repository contains a simple Python script for aggregating U.S. election office information from various APIs (VoteAmerica, Google Civic Information, CivicAPI, etc.).

## Setup

1. Install Python 3 and `pip`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables for any API keys you have:
   - `VOTEAMERICA_API_KEY`
   - `GOOGLE_CIVIC_API_KEY`
   - `CIVIC_API_KEY`

## Usage

Run the scraper with:

```bash
python precinct_scraper.py
```

The script will output a CSV file named `precincts.csv` containing aggregated precinct data.

**Note:** Each API has its own terms of service and rate limits. Make sure you have permission to use the data and comply with any restrictions.
