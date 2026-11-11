# BeerIQ AI — Dark Gold Dashboard

A working Streamlit dashboard styled to closely follow the supplied reference image: midnight navy, champagne-gold highlights, executive KPI tiles, sales-channel donut, change bars, container recovery, supplier breakdown, community impact, and simulation modules.

**Not affiliated with The Beer Store.** 2024 company-wide reporting is sourced from The Beer Store public reports. Transaction-level, store-level, product-level, ratings, inventory, routes, and GPS are synthetic. The free assistant uses Python rule-based analysis, not a generative LLM.

## Run on Mac

```bash
cd "/Users/kishoreshanmugam/Documents/beer store project/BeerIQ_AI_Dark_Gold_Exact_Style"
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Use the sidebar to access Fleet Command, Container Recovery, Channel Performance, Inventory, Growth Strategy, and AI Assistant. No API key is needed.

## Data sources
- [The Beer Store 2024 Operations Report](https://www.thebeerstore.ca/api/images/wyfly6ekgxs8/5J7jgki4GLkwyXquTRASlc/889686a44d43bc0218a01e1460ec0f0c/OpsReport2024_FINAL.pdf)
- [The Beer Store 2024 Stewardship Report](https://www.thebeerstore.ca/api/images/wyfly6ekgxs8/gMafvCITsRs50ejsGtLG7/21fc02d4c93c5a48adf795566151bbe4/StewardshipReport2024_SinglePages.pdf)

## Security and publishing
The reference-inspired header and sidebar atmosphere are bundled imagery, not real fleet, customers or actual store photography. Do not imply that generated assets are photographic evidence. No API secrets are included. For public Streamlit hosting, upload this folder contents to GitHub, select app.py, and deploy on Streamlit Community Cloud.


## NEW: Automated Store Operations (synthetic sandbox)

Open **⚡ Automated Store Operations** in the sidebar. Select **Simulate a full business day** to ingest fictional POS sales and empty-container returns. The system updates perpetual inventory, applies reorder points and quantity rules, creates simulated SAP-style order references, reserves hypothetical warehouse stock, schedules fictional fleet activities, flags exceptions, and maintains an auditable event log. Run individual POS/return events or enter a physical cycle count. Managers can approve high-value orders; deliveries and empties handoffs require confirmation.

**No live integration:** Does not connect to SAP, POS, store databases, trucking telemetry, or any retailer. All workflow data is synthetic, no confidential data is used, and nothing is sent externally. SAP references are entirely simulated. Transaction IDs are deduplicated. Never attribute simulated cost savings, inventory, shrinkage, truck activity or orders to The Beer Store. This is not actual deployment-ready ERP automation.
