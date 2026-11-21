# India Bullion Tracker (zero-cost starter)

A public Streamlit dashboard for Indian gold and silver benchmark history, with optional international benchmark conversion to INR.

## Important source and licensing policy

This project deliberately does **not** scrape MCX, price aggregators, broker websites or unofficial APIs.

- **IBJA:** Enter values from an authorised IBJA publication or official API only where your access and intended republication are permitted. The public display of a rate does not automatically grant an unrestricted right to automate extraction or republish it.
- **LBMA/IBA:** Do not enter LBMA benchmark prices unless your licence or written permission permits the intended use. LBMA says a licence is required for obtaining, using or redistributing benchmark data.
- **FBIL:** Use a directly obtained FBIL reference-rate publication and follow its applicable terms.

The application does not fetch any prices automatically. GitHub Actions runs a daily CSV structure/freshness check only; it does not collect market data. This is intentional so the project does not bypass source restrictions or misrepresent a website as an authorised feed.

## Free architecture

- GitHub: code and CSV history.
- Streamlit Community Cloud: public dashboard hosting on its free offering.
- GitHub Actions: scheduled validation workflow (subject to GitHub's free usage limits).
- No paid database or paid market-data API is required for this manual-data version. CSV files in the repository are the persistent store.

Free services can change their limits, sleep policies and availability. There is no uptime guarantee.

## Deploy

1. Create a GitHub account if you do not already have one.
2. Create a **public** repository, for example `india-bullion-tracker`.
3. Upload all files and folders from this project to the repository root.
4. Open https://share.streamlit.io/ and sign in with GitHub.
5. Choose **Create app**, select your repository, branch `main`, and file `app.py`.
6. Deploy. Streamlit will provide a public `*.streamlit.app` URL.
7. To update prices, edit the relevant CSV file in GitHub and commit the changes. Streamlit will reload the app after the repository changes are deployed.

Official deployment guide: https://docs.streamlit.io/deploy/streamlit-community-cloud

## Daily data entry

Use ISO dates (`YYYY-MM-DD`) and numeric values without currency symbols or commas.

### `data/ibja_daily.csv`

Columns:
`date,session,gold_999_inr_10g,gold_916_inr_10g,gold_750_inr_10g,silver_999_inr_kg,source_name,source_url`

Example format only (not a market quote):
`2026-11-21,PM,123456,113333,92592,150000,IBJA,https://www.ibja.co/`

Enter one row per date/session. Keep AM and PM as separate rows if both are available.

### `data/usd_inr.csv`

Columns:
`date,usd_inr,source_name,source_url`

### `data/international_daily.csv`

Columns:
`date,gold_usd_per_troy_oz,silver_usd_per_troy_oz,source_name,source_url`

The international chart is calculated only for dates that exactly match the FX date. No interpolation or forward-filling is performed.

## Unit conversion

- Gold INR/gram = gold USD/troy oz × USD/INR ÷ 31.1034768
- Silver INR/kg = silver USD/troy oz × USD/INR ÷ 31.1034768 × 1,000

Converted prices are indicative currency conversions, not Indian retail prices. They exclude import duty, GST, freight, local premiums and differences in benchmark timing/specification.

## Daily workflow

The included GitHub Actions workflow runs at 19:00 IST Monday-Friday. It validates the CSV schema and prints the latest dates. It **does not fetch prices**. Update the CSV rows from authorised direct-source publications, then commit them to GitHub. Weekend and holiday gaps are normal for some benchmarks.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
