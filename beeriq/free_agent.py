"""Public-demo, zero-API-cost business analysis assistant.

This is *not* a generative language model. It routes common natural-language
questions to deterministic calculation functions, then formats evidence.
"""
from __future__ import annotations

import re
from .core import kpis, sales_breakdown, quality_sales, stock_priorities, plan_pickups


def _money(v):
    return f"{float(v):,.2f}"


def analyze_question(question, sales, catalog, inventory, locations, fleet_state=None):
    q = re.sub(r'\s+', ' ', question.lower()).strip()
    trace = []
    disclosure = '\n\n*All demo data are synthetic and are not The Beer Store’s operational data.*'

    def used(tool, result):
        trace.append({'tool': tool, 'result': result})

    if any(t in q for t in ['truck', 'fleet', 'vehicle', 'driver', 'container movement', 'gps', 'eta']):
        data = fleet_state or {'status': 'No fleet simulation snapshot loaded'}
        used('fleet_summary', data)
        lines = ['### Simulated fleet status', 'The fleet tracker uses simulated movements, not live GPS.']
        if isinstance(data, dict):
            for key, value in list(data.items())[:14]:
                if isinstance(value, (int, float, str)):
                    lines.append(f'- **{key.replace("_", " ").capitalize()}:** {value}')
        lines.append('**Next step:** Open the Truck & Container Tracker tab to review the route map and events.')
        return '\n\n'.join(lines)+disclosure, trace

    if any(t in q for t in ['pickup', 'recycl', 'collection', 'dispatch', 'route', 'depot']):
        data = plan_pickups(locations)
        used('plan_pickups', data)
        rows = [f'- **Truck {r["vehicle"]}:** {", ".join(s["location"] for s in r["stops"])}; load {r["load"]:,} containers, approximate straight-line route {r["distance_km_straight_line"]:.1f} km.' for r in data['routes']]
        return ('### Illustrative collection dispatch plan\n\n'
                f'**Scheduled sites:** {data["scheduled_locations"]} of {data["selected_locations"]} prioritized sites. '
                f'**Unscheduled:** {len(data["unscheduled"])}.\n\n'
                + ('\n'.join(rows) or 'No site met the selected priority threshold.')
                + '\n\n**Method:** Greedy nearest-feasible-site heuristic with straight-line distances; not a guaranteed optimal road route.'
                + disclosure), trace

    if any(t in q for t in ['inventory', 'stock', 'replenish', 'shortage', 'run out', 'restock']):
        data = stock_priorities(sales, inventory)
        flagged = data[data['priority'] == 'Review replenishment'].head(8)
        used('stock_priorities', {'total_store_products':len(data),'flagged_count':int((data.priority == 'Review replenishment').sum()), 'examples':flagged.to_dict('records')})
        lines = [f'- **{r.store} / {r.product}:** {r.on_hand} on hand vs {r.estimated_demand:.1f} estimated 7-day units (gap {r.surplus_units:.1f}).' for r in flagged.itertuples(index=False)]
        return ('### Inventory risk screening\n\n'
                f'**{int((data.priority == "Review replenishment").sum())}** of **{len(data)}** store-product positions are flagged for review.\n\n'
                + ('\n'.join(lines) if lines else 'No negative projected stock gap in the current example.')
                + '\n\n**Recommendation:** Validate current stock levels and upcoming deliveries before creating replenishment orders. Forecasts use a simple 28-day average.'
                + disclosure), trace

    if any(t in q for t in ['rating', 'rated', 'quality', 'review', 'top seller', 'popular']):
        data = quality_sales(sales, catalog)
        used('quality_sales', data.head(10).to_dict('records'))
        known = data.dropna(subset=['rating'])
        if known.empty:
            return '### Product rating comparison\n\nNo matching rating data are available for these products.'+disclosure, trace
        top_sales = known.nlargest(5, 'units')
        best_rating = known.nlargest(5, 'rating')
        fmt = lambda df: '\n'.join(f'- {r["product"]}: rating {r["rating"]}, {int(r["units"]):,} units' for _, r in df.iterrows())
        return ('### Product ratings and sales comparison\n\n**Top five by units**\n'+fmt(top_sales)
                +'\n\n**Top five by illustrative rating**\n'+fmt(best_rating)
                +'\n\n**Interpretation:** Ratings and sales measure different things. These ratings are fabricated for demonstration and do not establish product quality.'
                +disclosure), trace

    if any(t in q for t in ['monthly', 'month', 'trend', 'quarter', 'over time', 'changed', 'change']):
        data = sales_breakdown(sales, 'month', 50).sort_values('month')
        used('sales_breakdown(month)', data.to_dict('records'))
        if len(data) < 2:
            return '### Monthly performance\n\nAt least two months of sales data are needed to compare trends.'+disclosure, trace
        a,b = data.iloc[-2],data.iloc[-1]
        delta = float(b.revenue-a.revenue)
        pct = delta/float(a.revenue)*100 if a.revenue else None
        pct_text = f'{pct:+.1f}%' if pct is not None else 'not defined (prior revenue is zero)'
        return (f'### Latest two months ({a["month"]} → {b["month"]})\n\n'
                f'- **Revenue:** {_money(a.revenue)} → {_money(b.revenue)} ({pct_text}; difference {delta:+,.2f}).\n'
                f'- **Gross margin:** {a.gross_margin_pct:.2f}% → {b.gross_margin_pct:.2f}% '
                f'({b.gross_margin_pct-a.gross_margin_pct:+.2f} percentage points).\n'
                f'- **Units:** {int(a.units):,} → {int(b.units):,}.\n\n'
                '**Next step:** Inspect product and store breakdowns to identify contributors. These figures show changes, not causes.'
                +disclosure), trace

    if any(t in q for t in ['store', 'location', 'branch', 'region']):
        data = sales_breakdown(sales, 'store', 50)
        used('sales_breakdown(store)', data.head(12).to_dict('records'))
        lines = [f'- **{r.store}:** revenue {_money(r.revenue)}, gross margin {r.gross_margin_pct:.1f}%, units {int(r.units):,}.' for r in data.head(8).itertuples(index=False)]
        return '### Store performance by revenue\n\n'+'\n'.join(lines)+'\n\n**Next step:** Compare margin as well as sales volume when assessing performance.'+disclosure, trace

    if any(t in q for t in ['product', 'profitability', 'margin', 'lowest', 'highest', 'best', 'revenue', 'sales', 'category']):
        data = sales_breakdown(sales, 'product', 50)
        if any(t in q for t in ['lowest', 'weakest', 'declin', 'poor', 'investigate', 'margin', 'profitability']):
            data = data.sort_values('gross_margin_pct')
            title = 'Products with lowest gross margins (review candidates)'
        elif 'unit' in q or 'volume' in q:
            data = data.sort_values('units', ascending=False)
            title = 'Products ranked by units sold'
        else:
            data = data.sort_values('revenue', ascending=False)
            title = 'Products ranked by revenue'
        used('sales_breakdown(product)', data.head(10).to_dict('records'))
        lines = [f'- **{r.product}:** revenue {_money(r.revenue)}; gross margin {r.gross_margin_pct:.1f}%; {int(r.units):,} units.' for r in data.head(7).itertuples(index=False)]
        return f'### {title}\n\n'+'\n'.join(lines)+'\n\n**Next step:** Check pricing, costs, discounts and inventory before deciding on changes. Gross profit excludes operating expenses.'+disclosure, trace

    if any(t in q for t in ['summary', 'overview', 'kpi', 'business', 'performance']):
        data = kpis(sales)
        used('kpis',data)
        return ('### Business overview\n\n'
                f'- **Revenue:** {_money(data["revenue"])}\n'
                f'- **Gross profit:** {_money(data["gross_profit"])}\n'
                f'- **Gross margin:** {data["gross_margin_pct"]:.2f}%\n'
                f'- **Units sold:** {data["units"]:,}\n'
                f'- **Transactions:** {data["transactions"]:,}\n'
                f'- **Store count:** {data["stores"]:,}\n\n'
                '**Next step:** Ask about monthly trends, products, stores, inventory, pickups or trucks for a deeper analysis.'
                +disclosure), trace

    return ('### Question not recognized\n\nThis free analyst is a **rule-based tool router**, not a general-purpose AI language model. '
            'Try asking about **monthly sales**, **product margins**, **store performance**, **inventory risks**, '
            '**recycling pickups**, or **truck fleet status**. No numbers were generated for this unsupported question.'), trace
