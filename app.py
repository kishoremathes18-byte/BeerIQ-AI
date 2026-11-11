"""BeerIQ AI — independent portfolio demo; not affiliated with any retailer."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from beeriq.core import load_sales, kpis, sales_breakdown, quality_sales, forecast, stock_priorities, plan_pickups
from beeriq.free_agent import analyze_question
from beeriq.fleet import build_fleet_schedule, snapshot, fleet_summary
from beeriq.operations import init_demo, run_demo_day, record_sale, record_return, approve_order, confirm_delivery, confirm_empty_pickup, reconcile_count, state_summary, STORES, CATALOG, RETURN_TYPES

BASE = Path(__file__).resolve().parent

@st.cache_data
def demo(name):
    return pd.read_csv(BASE / 'data' / name)

st.set_page_config(page_title='BeerIQ AI | The Beer Store 2024 Operational Data', page_icon='🍺', layout='wide', initial_sidebar_state='expanded')
import base64

def asset_base64(name):
    return base64.b64encode((BASE / 'assets' / name).read_bytes()).decode('ascii')

HERO_IMAGE=asset_base64('storefront_hero.jpg')
FOREST_IMAGE=asset_base64('sidebar_forest.jpg')
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html,body,[data-testid='stApp'],.stApp {background:#070f19!important;color:#f6f6f3!important;font-family:Inter,system-ui,sans-serif!important;}
[data-testid='stAppViewContainer'] {background:#07111d!important;}
[data-testid='stHeader']{background:transparent!important;}
[data-testid='stDecoration']{display:none!important;}
.block-container{max-width:1920px!important;padding:0.7rem 1.5rem 3rem!important;}
[data-testid='stSidebar'] {background:linear-gradient(180deg,#07111f 0%,#0a1524 70%,#05101a 100%)!important;border-right:1px solid #334358!important;}
[data-testid='stSidebar']>div:first-child {background-image:linear-gradient(180deg,rgba(5,15,27,1) 0%,rgba(5,15,27,.97) 65%,rgba(5,15,27,.60) 90%,rgba(5,15,27,.5) 100%),url('data:image/jpeg;base64,__FOREST__');background-position: center,bottom;background-repeat:no-repeat;background-size:cover,100% 45%;}
[data-testid='stSidebar'] [data-testid='stRadio'] label{font-size:.9rem;padding:13px 11px!important;border:1px solid transparent!important;border-radius:9px!important;margin:3px 0!important;color:#e4e9f0!important;}
[data-testid='stSidebar'] [role='radiogroup'] {gap:0.15rem;}
[data-testid='stSidebar'] [role='radiogroup'] label:has(input:checked){background:linear-gradient(110deg,#ffdf83,#b68635)!important;border-color:#ffe09a!important;box-shadow:0 6px 24px rgba(240,185,77,.17)!important;}
[data-testid='stSidebar'] [role='radiogroup'] label:has(input:checked) p {color:#0c111b!important;font-weight:800!important;}
[data-testid='stSidebar'] [role='radiogroup'] label:hover:not(:has(input:checked)){background:#1a2a40!important;}
[data-testid='stSidebar'] [data-testid='stWidgetLabel'] p, [data-testid='stSidebar'] p,[data-testid='stSidebar'] span {color:#e7e9ed;}
[data-testid='stSidebar'] h3 {color:#f5dfaf!important;}
[data-testid='stSidebar'] [data-testid='stFileUploader'] {background:#172638;border:1px solid #3a4960;border-radius:10px;}
.side-brand{padding:21px 0 18px;margin:0 0 19px;border-bottom:1px solid #2f3950;}
.side-logo{font-family:Manrope,sans-serif;font-size:1.75rem;font-weight:800;letter-spacing:-1.3px;color:#faf5e9;line-height:1.1;}
.side-logo strong {color:#e8b957;}
.side-sub{font-size:.69rem;color:#b9c4d1;letter-spacing:.08em;margin-top:6px;}
.side-footer {padding:18px 10px;border:1px solid #a37c39;border-radius:12px;background:rgba(12,21,34,.74);font-weight:650;font-size:.85rem;margin-top:30px;line-height:1.5;color:#f4e0ae;}
.sidebar-mini {font-size:.7rem;color:#c4a76d;letter-spacing:.12em;margin:20px 0 3px;font-weight:800;}
h1,h2,h3,h4, [data-testid='stMarkdownContainer'] h1,[data-testid='stMarkdownContainer'] h2,[data-testid='stMarkdownContainer'] h3 {color:#f5f3f0!important;font-family:Manrope,Inter,sans-serif!important;letter-spacing:-.025em;}
p,li {color:#d0d8e5;}
a {color:#edc46b!important;}
[data-testid='stMetric'] {background:linear-gradient(145deg,#172438,#0e1723)!important;border:1px solid #6b6d72!important;border-radius:13px;padding:15px 15px!important;min-height:110px;box-shadow:inset 0 1px 0 rgba(255,255,255,.06)!important;}
[data-testid='stMetricLabel'] p {color:#c3cbd7!important;font-size:.78rem!important;}
[data-testid='stMetricValue'] {color:#fff!important;font-weight:800!important;font-size:clamp(1.1rem,2vw,1.9rem)!important;}
[data-testid='stMetricDelta'] {color:#eac46b!important;}
[data-testid='stPlotlyChart'] {background:linear-gradient(135deg,#142337,#0e1929)!important;border:1px solid #596678!important;border-radius:14px!important;padding:5px!important;overflow:hidden;}
[data-testid='stDataFrame']{border:1px solid #536177;border-radius:10px;overflow:hidden;}
[data-testid='stExpander'] {background:#142238!important;border:1px solid #46556a!important;border-radius:12px!important;}
[data-testid='stVerticalBlockBorderWrapper'] {border-color:#495870!important;}
[data-testid='stAlert']{background:#1a2c3e!important;border-radius:10px!important;}
[data-testid='stAlert'] p {color:#ebedf3!important;}
[data-testid='stButton'] button[kind=primary],[data-testid='stBaseButton-primary']{background:linear-gradient(105deg,#ffe49a,#c99437)!important;color:#121622!important;border:1px solid #f6d381!important;font-weight:800!important;border-radius:11px!important;}
[data-testid='stButton'] button:not([kind=primary]),[data-testid='stDownloadButton'] button {background:#192a40!important;color:#f6dba2!important;border-color:#586274!important;border-radius:10px!important;}
input,textarea,[data-baseweb='select']>div {background-color:#17283b!important;color:#fff!important;}
[data-testid='stSlider'] p,[data-testid='stNumberInput'] p {color:#cbd5e0!important;}
hr{border-color:#364459!important;}
.hero-banner{background-image:linear-gradient(90deg,#07111de8 0%,#07111d8c 45%,#07111d1f 100%),url('data:image/jpeg;base64,__HERO__');background-size:cover;background-position:center right;border-radius:0;padding:32px 24px 31px;min-height:142px;margin:-11px -24px 11px;display:flex;align-items:center;border-bottom:1px solid #28394e;}
.hero-banner h1{font-size:clamp(1.35rem,2vw,2.2rem)!important;margin:0 0 6px!important;font-weight:800;white-space:normal;}
.hero-banner p{font-size:.92rem;color:#e7e7e6;margin:0;}
.hero-top{position:absolute;right:40px;top:17px;font-size:.67rem;border:1px solid #84909c;border-radius:12px;padding:6px 10px;color:#fff;background:#0b1527df;}
.kpi-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:8px;margin-bottom:13px;}
.kpi-tile{min-height:99px;padding:17px 13px 12px;border:1px solid #657183;background:linear-gradient(140deg,#16253a,#0d1624);border-radius:14px;display:flex;align-items:center;gap:12px;box-shadow:inset 0 1px 1px #ffffff18;}
.kpi-icon{font-size:2.1rem;color:#edc463;min-width:33px;text-align:center;}
.kpi-value{font-size:clamp(1.05rem,1.65vw,1.82rem);font-weight:800;color:white;line-height:1.15;white-space:nowrap;letter-spacing:-.035em;}
.kpi-value small{font-size:.62em;}
.kpi-label{color:#dbe1eb;font-size:.72rem;margin-top:6px;line-height:1.3;}
.growth-strip{border:1px solid #b9954f;background:linear-gradient(105deg,#302d27,#1d2430 55%,#142132);border-radius:11px;display:flex;justify-content:space-around;gap:15px;flex-wrap:wrap;padding:12px 16px;margin-bottom:13px;font-weight:700;font-size:.87rem;}
.growth-strip strong,.growth-strip .up{color:#ffcf57;font-weight:800;}
.pane{background:linear-gradient(135deg,#152337,#0b1726);border:1px solid #677183;border-radius:13px;padding:13px 14px 10px;margin-bottom:12px;min-height:210px;}
.pane h3{margin:0 0 12px;font-size:1rem!important;letter-spacing:-.04em;}
.recovery-row{display:grid;grid-template-columns:1.5fr 1fr 40px;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #2d3b50;font-size:.78rem;}
.bar-wrap{height:12px;border-radius:40px;background:#354457;overflow:hidden;}
.bar-fill{height:100%;background:linear-gradient(90deg,#2bd89e,#77bb91);border-radius:40px;}
.metric-mini-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:4px;}
.metric-mini{border:1px solid #42536b;background:#0e1b2b;border-radius:10px;padding:13px 5px;text-align:center;}
.metric-mini span{display:block;font-size:1.3rem;color:#f0bd55;}
.metric-mini strong{display:block;font-size:1.25rem;color:white;margin:4px 0;}
.metric-mini small{display:block;font-size:.62rem;line-height:1.25;color:#d8dfeb;}
.origin-meter{display:flex;border-radius:11px;overflow:hidden;border:1px solid #6f7790;margin-top:18px;text-align:center;font-weight:800;}
.origin-meter div{padding:15px 2px;background:linear-gradient(90deg,#ffdf86,#c8953e);color:#131720;width:80%;}
.origin-meter span{background:#1b3450;color:white;width:20%;padding:15px 2px;}
.impact-row{display:flex;gap:12px;align-items:center;padding:8px 1px;border-bottom:1px solid #314157;}
.impact-icon{color:#e7b64c;font-size:1.4rem;min-width:30px;}
.impact-row strong{display:block;color:#f7f4f0;font-size:.95rem;}
.impact-row small{display:block;color:#c9d4e0;font-size:.69rem;margin-top:2px;}
.ai-card{background:linear-gradient(165deg,#242535,#0b1320);border:1px solid #c3a05b;border-radius:13px;padding:16px 13px;}
.ai-card h3{font-size:.97rem!important;margin:0 0 16px;color:#ffe2a0!important;}
.insight{background:#212b39;border:1px solid #566071;border-radius:11px;padding:12px;margin-bottom:9px;}
.insight strong{display:block;color:white;font-size:.79rem;}
.insight p{font-size:.72rem;color:#dce3ec;margin:4px 0 0;line-height:1.45;}
.gold-btn{margin-top:11px;color:#101623;background:linear-gradient(90deg,#ffe59b,#c99740);border-radius:10px;padding:12px;font-size:.85rem;text-align:center;font-weight:800;}
.source-bar{border:1px solid #415168;background:#101e2e;border-radius:12px;padding:11px 13px;color:#d4dbe5;font-size:.72rem;line-height:1.5;margin-top:0;}
.source-bar strong{color:#f2ce7a;}
.legend-dot{width:9px;height:9px;display:inline-block;border-radius:50%;margin:0 3px 0 12px;background:#38ba8b;}
.foot-note{font-size:.7rem;color:#abb7c7!important;margin:7px 0;}
.page-intro{padding:19px 6px 14px;margin-bottom:10px;}
.page-kicker{color:#ebbe65;font-size:.68rem;font-weight:800;letter-spacing:.18em;}
.page-intro h1{margin:6px 0 4px!important;font-size:1.9rem;}
.page-intro p{margin:0;color:#c7d1df;}
.source-strip{padding:10px 13px;border-radius:9px;background:#162439;border:1px solid #3b4e62;color:#dce3ee;font-size:.76rem;margin:10px 0 18px;}
.source-strip strong{color:#f7c461;}
.section-heading{font-size:1.4rem;font-weight:800;color:white;}
.section-subtitle{color:#c5cfdb;margin-bottom:15px;}
.info-card {background:#142337;border:1px solid #475a71;border-radius:12px;padding:18px;}
.info-card .label{color:#eec572;font-size:.72rem;font-weight:800;letter-spacing:.12em;}
.info-card .headline{color:white;font-weight:800;margin:8px 0;}
.info-card .description{color:#cfdae8;}
@media(max-width:1200px){.kpi-grid{grid-template-columns:repeat(3,minmax(0,1fr));}.kpi-tile{min-height:90px;}}
@media(max-width:750px){.kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));}.block-container{padding:1rem .8rem 2rem!important;}.hero-banner{margin:-16px -13px 10px;padding:25px 18px;}.kpi-value{font-size:1.17rem}.kpi-icon{font-size:1.4rem}.growth-strip{display:block}.growth-strip div{margin:5px 0}.hero-top{display:none}}
</style>
""".replace('__HERO__', HERO_IMAGE).replace('__FOREST__',FOREST_IMAGE),unsafe_allow_html=True)
catalog = demo('synthetic_catalog.csv')
inventory = demo('synthetic_inventory.csv')
locations = demo('synthetic_collection_locations.csv')
with st.sidebar:
    st.markdown("""<div class='side-brand'><div class='side-logo'>🍺 BeerIQ <strong>AI</strong></div><div class='side-sub'>RETAIL · DISTRIBUTION · SUSTAINABILITY</div></div>""",unsafe_allow_html=True)
    uploaded = None
    currency = 'CAD'
PAGES = {
    'Overview': '2024 Executive Review',
    'Automation': 'Autonomous Store Operations',
    'Strategy': 'Growth Opportunities',
    'Sales': 'Demo Sales Intelligence',
    'Products': 'Demo Product Explorer',
    'Inventory': 'Demo Inventory Risk',
    'Collections': 'Demo Reverse Logistics',
    'Fleet': 'Demo Fleet Command',
    'Assistant': 'Free Analytics Assistant',
    'Sources': 'Sources & Methodology',
}
with st.sidebar:
    st.markdown("<div class='sidebar-mini'>WORKSPACE</div>", unsafe_allow_html=True)
    page = st.radio('Navigate', list(PAGES), label_visibility='collapsed',
                    format_func=lambda x: {
                        'Overview':'⌂  Executive Dashboard',
                        'Automation':'⚡  Automated Store Operations',
                        'Strategy':'↗  Sales Growth Strategy',
                        'Sales':'▥  Channel Performance',
                        'Products':'♧  Product Intelligence',
                        'Inventory':'◈  Inventory & Forecasting',
                        'Collections':'♻  Container Recovery',
                        'Fleet':'🚚  Route & Truck Operations',
                        'Assistant':'✦  AI Business Assistant',
                        'Sources':'ⓘ  Sources & Methods',
                    }[x])
    st.markdown("<div class='side-footer'>♻ &nbsp; Supporting a More Circular Ontario</div>",unsafe_allow_html=True)
    with st.expander('Demo controls',expanded=False):
        uploaded = st.file_uploader('Optional sales file',type=['csv','xlsx'],help='Do not upload personal or confidential data to a public app.')
        currency = st.selectbox('Currency label for synthetic sales', ['CAD','USD','INR'], index=0)
        st.caption('Currency label only: no FX conversion. Free rules-based assistant; no API key.')

try:
    if uploaded:
        raw = pd.read_csv(uploaded) if uploaded.name.lower().endswith('.csv') else pd.read_excel(uploaded)
        sales = load_sales(raw)
        st.info('Your uploaded sales file is active. Other tabs still use **separate synthetic catalog, inventory and location data**; product matches may be missing. Do not interpret those as your own operations.')
    else:
        sales = load_sales(demo('synthetic_sales.csv'))
except Exception as err:
    st.error(f'Could not load the file: {err}')
    st.stop()

PAGE_KICKERS = {'Overview':'COMPANY PERFORMANCE', 'Automation':'SYNTHETIC · EVENT-DRIVEN AUTOMATION', 'Strategy':'GROWTH OPPORTUNITIES',
                'Sales':'SYNTHETIC · SALES DATA', 'Products':'SYNTHETIC · PRODUCT DATA',
                'Inventory':'SYNTHETIC · INVENTORY', 'Collections':'SYNTHETIC · COLLECTION POINTS',
                'Fleet':'SYNTHETIC · TRUCK SIMULATION', 'Assistant':'RULE-BASED ANALYTICS',
                'Sources':'TRANSPARENCY & SOURCES'}
PAGE_DESCRIPTIONS = {
    'Overview':'A boardroom-ready view of published 2024 scale, channel movement and stewardship.',
    'Automation':'POS → Stock → ERP-style request → Warehouse → Trucks, including empty returns and count exceptions.',
    'Strategy':'Six testable initiatives tied to measurable operating outcomes.',
    'Sales':'Explore sample transactions. These do not represent actual Beer Store sales.',
    'Products':'Understand sales velocity, assortment and illustrative product ratings.',
    'Inventory':'Identify possible shortfalls using explainable demand estimates.',
    'Collections':'Explore capacity-constrained pickup planning on simulated locations.',
    'Fleet':'Replay truck journeys and follow simulated empty-container movements.',
    'Assistant':'Ask questions about the demo datasets. No paid API key needed.',
    'Sources':'Published reports, calculations, data boundaries and limitations.'}
if page != "Overview":
    st.markdown(f"""<div class="page-intro"><div class="page-kicker">{PAGE_KICKERS[page]}</div><h1>{PAGES[page]}</h1><p>{PAGE_DESCRIPTIONS[page]}</p></div>""",unsafe_allow_html=True)
if page not in ('Sources','Overview'):
    st.markdown('<div class="source-strip"><strong>DATA LABEL</strong> <span>Published company-wide 2024 reporting</span> <i>+</i> <span>Clearly marked synthetic operational demos</span></div>', unsafe_allow_html=True)


# 2024 authoritative reporting, kept separate from simulated operational examples.
OPS_URL = 'https://www.thebeerstore.ca/api/images/wyfly6ekgxs8/5J7jgki4GLkwyXquTRASlc/889686a44d43bc0218a01e1460ec0f0c/OpsReport2024_FINAL.pdf'
STEW_URL = 'https://www.thebeerstore.ca/api/images/wyfly6ekgxs8/gMafvCITsRs50ejsGtLG7/21fc02d4c93c5a48adf795566151bbe4/StewardshipReport2024_SinglePages.pdf'
NIQ_URL = 'https://nielseniq.com/global/en/insights/analysis/2025/2024-beverage-alcohol-year-in-review/'
LCBO_URL = 'https://www.lcbo.com/content/lcbo/en/corporate-pages/about-LCBO/media-centre/press-releases/2025/12-04.html'
channels = demo('official_2024_channels.csv')
recovery = demo('official_2024_recovery.csv')
keydata = demo('official_2024_kpis.csv')
PLOT = {'paper_bgcolor':'rgba(0,0,0,0)','plot_bgcolor':'rgba(0,0,0,0)','font':{'color':'#293845'}}

if page == 'Overview':
    import plotly.graph_objects as go
    # Visually mirrors the user's navy/gold reference image while retaining real interactive plots.
    st.markdown("""<div class='hero-banner'><div><h1>The Beer Store — 2024 Operational Data</h1><p>BeerIQ AI | Sales • Operations • Sustainability • Growth</p></div><span class='hero-top'>Data: 2024 (Published) ⓘ</span></div>""",unsafe_allow_html=True)
    tiles = [
       ('♜','3,145,896 <small>hL</small>','Total Beer Distributed'),
       ('⬡','38,442,849','Equivalent 24-Bottle Cases'),
       ('♻','76%','Container Recovery Rate'),
       ('▤','407','Retail Stores'),
       ('♧','1.6 Billion+','Containers Collected'),
    ]
    st.markdown('<div class="kpi-grid">'+''.join(f'<div class="kpi-tile"><div class="kpi-icon">{i}</div><div><div class="kpi-value">{v}</div><div class="kpi-label">{l}</div></div></div>' for i,v,l in tiles)+'</div>',unsafe_allow_html=True)
    st.markdown('''<div class="growth-strip"><div><span class="up">↗ &nbsp;</span> B2B Wholesale Growth: &nbsp;<strong>+6.5%</strong> &nbsp; | &nbsp; +182,936 hL</div><div><span class="up">↗ &nbsp;</span> Grocery-Channel Growth: &nbsp;<strong>+15.6%</strong> &nbsp; | &nbsp; +64,075 hL</div></div>''',unsafe_allow_html=True)
    left,middle,right=st.columns([1.08,1.08,.92],gap='small')
    dark_plot=dict(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='Inter',color='#e9eef7',size=12),showlegend=False)
    channels_labels=['Home consumer / Retail','LCBO','Licensees','Grocery stores','Retail partners / Agency','Convenience stores','Other']
    shares=[50.85,16.32,13.41,7.63,7.53,3.87,0.38]
    palette=['#ffd166','#3c8df5','#2264b6','#48b98b','#8165be','#b6a1e7','#f07679']
    with left:
        with st.container(border=True):
            st.markdown("<h3 style='margin:0'>Sales Volume by Channel (2024)</h3>",unsafe_allow_html=True)
            fig=go.Figure(go.Pie(labels=channels_labels,values=shares,hole=.64,sort=False,marker=dict(colors=palette,line=dict(width=0)),textinfo='none',hovertemplate='%{label}<br>%{value:.2f}%<extra></extra>'))
            fig.update_layout(**dark_plot,height=274,margin=dict(l=0,r=0,t=0,b=0),annotations=[dict(text='<b>3,145,896 hL</b><br><span style="font-size:10px">Total volume</span>',x=.5,y=.5,showarrow=False,font=dict(color='#fff',size=16))])
            st.plotly_chart(fig,width='stretch',config={'displayModeBar':False})
            for label,v,color in zip(channels_labels,shares,palette):
                st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:.72rem;padding:3px 0;color:#e3e9f0"><span><i style="display:inline-block;background:{color};height:9px;width:9px;border-radius:3px;margin-right:8px"></i>{label}</span><strong>{v:.2f}%</strong></div>',unsafe_allow_html=True)
    with middle:
        with st.container(border=True):
            st.markdown("<h3 style='margin:0'>Channel Share Change (2023 → 2024)</h3>",unsafe_allow_html=True)
            delta=[('Grocery stores',.90),('Retail partners / Agency',-.19),('Other',-.03),('Licensees',-.45),('LCBO',-1.31),('Home consumer / Retail',-2.81)]
            fig=go.Figure(go.Bar(x=[d[1] for d in delta],y=[d[0] for d in delta],orientation='h',marker_color=['#3dbd83' if d[1]>=0 else '#db797d' for d in delta],text=[f'{d[1]:+.2f} pp' for d in delta],textposition='outside',textfont=dict(color='#e8ecf4',size=11),hovertemplate='%{y}: %{x:+.2f} pp<extra></extra>'))
            fig.update_layout(**dark_plot,height=360,xaxis=dict(range=[-3.5,1.7],zeroline=True,zerolinecolor='#acbbcd',showgrid=False,visible=False),yaxis=dict(autorange='reversed',showgrid=False,tickfont=dict(size=11)),bargap=.4)
            st.plotly_chart(fig,width='stretch',config={'displayModeBar':False})
            st.markdown('<div class="foot-note">Convenience stores: 3.87% of 2024 volume; no separately published 2023 share for a like-for-like change.</div>',unsafe_allow_html=True)
    with right:
        st.markdown("""<div class='ai-card'><h3>✦ AI Insights &amp; Recommendations</h3>
        <div class='insight'><strong>↗ Expand grocery &amp; convenience</strong><p>Published grocery deliveries rose 15.6% (+64,075 hL). Prioritize partner fill rates and test service improvements.</p></div>
        <div class='insight'><strong>▤ Protect store sales</strong><p>Home-consumer volume share moved from 53.66% to 50.85%. Investigate pickup convenience and availability.</p></div>
        <div class='insight'><strong>⬡ Improve inventory availability</strong><p>Use simulated reorder alerts to explore how stock risk could be monitored. Real SKU data is unavailable.</p></div>
        <div class='gold-btn'>✦ Open AI Business Assistant →</div></div>""",unsafe_allow_html=True)
        if st.button('Ask BeerIQ a question',type='primary',width='stretch',key='overview_ask'):
            st.session_state['nav_to_assistant']=True
            st.info('Choose “AI Business Assistant” from the left navigation to ask a question.')
    c1,c2,c3=st.columns([1.07,1.02,1.12],gap='small')
    with c1:
        st.markdown("<div class='pane'><h3>Container Recovery by Type (2024)</h3>",unsafe_allow_html=True)
        for label,rate in [('All glass bottles',86),('Refillable bottles',89),('Non-refillable bottles',81),('Metal cans',73),('Kegs',102),('Total system',76)]:
            st.markdown(f'<div class="recovery-row"><span>{label}</span><div class="bar-wrap"><div class="bar-fill" style="width:{min(rate,100)}%;background:{"linear-gradient(90deg,#f1d16f,#e0a83e)" if label=="Total system" else "linear-gradient(90deg,#36d4a0,#7ab68c)"}"></div></div><strong style="text-align:right;color:#fff">{rate}%</strong></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('''<div class="pane"><h3>Supplier &amp; Product Network</h3><div class="metric-mini-grid">
        <div class="metric-mini"><span>▥</span><strong>261</strong><small>Brewers represented</small></div>
        <div class="metric-mini"><span>✦</span><strong>176</strong><small>Ontario-based brewers</small></div>
        <div class="metric-mini"><span>◎</span><strong>81</strong><small>Imported brewers</small></div>
        <div class="metric-mini"><span>◇</span><strong>1,051</strong><small>Brands listed</small></div></div>
        <div class="origin-meter"><div>96%<br><small>Ontario-based sales</small></div><span>4%<br><small>Other sales</small></span></div></div>''',unsafe_allow_html=True)
    with c3:
        st.markdown('''<div class="pane"><h3>Sustainability &amp; Community Impact</h3>
        <div class="impact-row"><span class="impact-icon">♻</span><div><strong>176,818 tonnes</strong><small>Material diverted from landfill</small></div></div>
        <div class="impact-row"><span class="impact-icon">❧</span><div><strong>195,301 tonnes</strong><small>Estimated CO₂e avoided</small></div></div>
        <div class="impact-row"><span class="impact-icon">♥</span><div><strong>$1,670,000+</strong><small>Charitable funds raised</small></div></div>
        <div class="impact-row"><span class="impact-icon">▤</span><div><strong>$948,300,000</strong><small>Government tax revenue generated</small></div></div></div>''',unsafe_allow_html=True)
    st.markdown('''<div class="source-bar"><strong>ⓘ DATA SOURCE:</strong> The Beer Store 2024 Operations Report and 2024 Stewardship Report. Published company-wide figures represent 2024, not current operations. Product-level, store-level, route-level, and tracking data in the other modules are simulated for demonstration. This independent portfolio project is not affiliated with or endorsed by The Beer Store. <span class="legend-dot"></span> Published (2024) <span class="legend-dot" style="background:#9075d0"></span> Simulated (Demo)</div>''',unsafe_allow_html=True)
    st.caption(f'[2024 Operations Report]({OPS_URL}) · [2024 Stewardship Report]({STEW_URL}) · Percentages rounded as reported; charts are interactive.')

if page == 'Strategy':
    st.markdown('### Commercial growth | an evidence-led opportunity map')
    st.caption('Proposals and experiments — not actual company initiatives or proven increases in sales. Reported metrics below describe 2024; simulated analytics are separate.')
    st.markdown('''<div class="info-card"><div class="label">THE CENTRAL QUESTION</div><div class="headline">How could a distributor grow as purchasing shifts across retail channels?</div><div class="description">Prioritize the expanding B2B channel, test store convenience improvements, and use inventory and recycling data to support service quality. All interventions require commercial validation.</div></div>''',unsafe_allow_html=True)
    x,y,z=st.columns(3)
    x.metric('B2B wholesale growth • 2024','+6.5%','+182,936 hL')
    y.metric('Grocery deliveries • 2024','+15.6%','+64,075 hL')
    z.metric('Home consumer mix','50.85%','−2.81 pp vs 2023')
    st.caption(f'Published channel and wholesale comparisons: [2024 Operations Report]({OPS_URL}). Falling share is not by itself proof of falling absolute home-retail volumes.')
    moves=[
        ('01','Channel expansion','Use store/partner forecasts to prioritize replenishment for grocery and convenience partners.','Wholesale volume growth and fill rate','2024 B2B volume +6.5%; convenience and grocery channels expanded.'),
        ('02','Retail experience','Test faster pickup readiness and in-stock substitution workflows at selected stores.','Order fulfillment time and availability','Home-consumer channel share fell 2.81 percentage points.'),
        ('03','Assortment discipline','Test localized SKU assortments using product velocity and margin, with documented holdout comparisons.','Units, gross margin and stockouts','1,051 listed brands across 261 brewers in 2024.'),
        ('04','Stock risk reduction','Flag high-velocity products whose coverage falls below expected lead-time demand.','Out-of-stock and service level','Potential lever; requires non-public SKU-level stock and demand.'),
        ('05','Returns experience','Test reduced waiting times for container returns; measure separately whether repeat visits improve.','Return wait time; return-to-purchase conversion','2024 system recovery 76%; 2023 recovery 79%.'),
        ('06','Fleet & collections','Simulate capacity-aware truck scheduling with estimated transit times and depot capacity.','Cost per stop, on-time delivery','536 delivery trucks and 26 distribution locations reported in 2024.'),
    ]
    for number,title,action,kpi,evidence in moves:
        with st.expander(f'{number}  {title}',expanded=number in ['01','02']):
            st.markdown(f'**Testable action:** {action}\n\n**How to measure:** {kpi}\n\n**Evidence / caveat:** {evidence}')
    st.markdown('#### Industry context, not Beer Store transaction data')
    st.write('NIQ reported 2024 beer value down **0.7%** and volume down **2.9%** in its measured beverage-alcohol market. LCBO reported growth in beer, RTDs and non-alcoholic beer/cider in its **Nov 2024–Nov 2025** reporting period. Different geographies and reporting periods mean these figures should **not** be merged with The Beer Store’s 2024 operating series.')
    st.caption(f'[NIQ 2024 Beverage Alcohol Year in Review]({NIQ_URL}) · [LCBO 2025 beverage trends]({LCBO_URL})')
    st.markdown('#### What would prove this worked?')
    st.markdown('A defensible evaluation would compare pilot locations against matched holdouts, define KPIs in advance, account for seasonality, and report confidence intervals. This demo does **not** claim measured sales uplift, cost savings, or The Beer Store endorsement.')

if page == 'Automation':
    import json
    st.markdown("<div class='section-heading'>Retail automation control center</div><div class='section-subtitle'>One connected workflow for beer replenishment, empty returns and exception-based stock counting.</div>", unsafe_allow_html=True)
    st.warning('**SIMULATED PROTOTYPE:** All transactions, stores, stock, SAP-style requests, fleet dispatches, timestamps, and savings are fictional. No real POS, SAP, warehouse, fleet, or company systems are connected. No actual orders are placed.')
    if 'ops_demo' not in st.session_state:
        st.session_state.ops_demo = init_demo()
    state=st.session_state.ops_demo
    left,right=st.columns([2,1])
    with left:
        store_choice=st.selectbox('Demo store',list(STORES),index=list(STORES).index(state['store']))
    with right:
        st.caption('This is an isolated public sandbox. The sequence can be replayed safely.')
    if store_choice!=state['store']:
        st.session_state.ops_demo=init_demo(store_choice)
        state=st.session_state.ops_demo
    col_run,col_reset=st.columns([2,1])
    if col_run.button('▶ Simulate a full business day',type='primary',width='stretch'):
        run_demo_day(state)
        st.rerun()
    if col_reset.button('↺ Reset simulation',width='stretch'):
        st.session_state.ops_demo=init_demo(store_choice)
        st.rerun()
    summary=state_summary(state)
    blocks=st.columns(4)
    for c,k in zip(blocks,['Units sold','ERP requests','Empty pickups scheduled','Open exceptions']):
        c.metric(k,summary[k])
    st.markdown('### Connected workflow')
    st.markdown("<div class='growth-strip'><div>🛒 <strong>POS</strong> → Inventory</div><div>📦 <strong>Reorder</strong> → ERP simulator</div><div>🏭 <strong>Warehouse</strong> → Dispatch</div><div>♻️ <strong>Returns</strong> → Pickup</div><div>🔍 <strong>Counts</strong> → Exceptions</div></div>", unsafe_allow_html=True)
    st.markdown('### Trigger an individual event')
    sale_col,return_col=st.columns(2)
    with sale_col:
        with st.form('sale_form'):
            st.markdown('**Simulated POS sale**')
            sku=st.selectbox('Product',list(CATALOG))
            units=st.number_input('Units purchased',min_value=1,max_value=200,value=12,step=1)
            submitted=st.form_submit_button('Process POS transaction',width='stretch')
            if submitted:
                record_sale(state,sku,int(units),f'POS-MANUAL-{state["seq"]+1}')
                st.success('Sale ingested; inventory and reorder status updated.')
    with return_col:
        with st.form('return_form'):
            st.markdown('**Simulated empties return**')
            container=st.selectbox('Container type',list(RETURN_TYPES))
            qty=st.number_input('Containers returned',min_value=1,max_value=1500,value=240,step=1)
            submitted=st.form_submit_button('Process return transaction',width='stretch')
            if submitted:
                record_return(state,container,int(qty),f'EMPTY-MANUAL-{state["seq"]+1}')
                st.success('Return ingested; empty collection threshold checked.')
    a,b=st.columns(2)
    with a:
        st.markdown('### Store stock & reorder points')
        inv_rows=[{'Product':sku,'Expected on hand':qty,'Reorder point':CATALOG[sku]['demand_per_day']*4,
                   'Demand / day (demo)':CATALOG[sku]['demand_per_day']} for sku,qty in state['inventory'].items()]
        st.dataframe(pd.DataFrame(inv_rows),width='stretch',hide_index=True)
        st.markdown('### ERP-style requests (SIMULATED)')
        if state['orders']:
            st.dataframe(pd.DataFrame(state['orders']),width='stretch',hide_index=True)
        else:st.info('No replenishment requests yet. Run a demo day or record a sale.')
        waiting=[o for o in state['orders'] if o['status']=='Awaiting approval']
        if waiting:
            oid=st.selectbox('Approve high-value order', [o['id'] for o in waiting])
            if st.button('Approve in demo'):
                approve_order(state,oid);st.rerun()
        dispatched=[o for o in state['orders'] if o['status']=='Dispatched']
        if dispatched:
            with st.expander('Confirm a physical delivery (requires verification)'):
                did=st.selectbox('Dispatched order', [o['id'] for o in dispatched])
                expected=next(o['quantity'] for o in dispatched if o['id']==did)
                received=st.number_input('Units physically received',0,expected,expected,step=1)
                if st.button('Confirm receipt'):
                    confirm_delivery(state,did,int(received));st.rerun()
    with b:
        st.markdown('### Empties & pickup automation')
        total_empties=sum(state['return_balances'].values())
        st.metric('Expected empty containers on site',f'{total_empties:,}',f'{total_empties/state["empty_capacity"]:.0%} of demo storage capacity',delta_color='off')
        st.dataframe(pd.DataFrame([{'Container type':k,'Expected units':v} for k,v in state['return_balances'].items()]),width='stretch',hide_index=True)
        if state['pickups']:
            st.dataframe(pd.DataFrame(state['pickups']),width='stretch',hide_index=True)
            pickups=[p for p in state['pickups'] if p['status']=='Pickup scheduled']
            if pickups:
                with st.expander('Confirm empty pickup (scanned handoff)'):
                    pid=st.selectbox('Pickup request',[p['id'] for p in pickups])
                    expected=next(p['quantity'] for p in pickups if p['id']==pid)
                    count=st.number_input('Scanned empty count',0,expected,expected,step=1)
                    if st.button('Confirm container handoff'):
                        confirm_empty_pickup(state,pid,int(count));st.rerun()
        else: st.caption('Collection is automatically requested when stored returns exceed 80% of capacity.')
        st.markdown('### Risk-based count / possible shrinkage')
        with st.form('count_form'):
            sku_check=st.selectbox('Select product to verify',list(CATALOG),key='count_sku')
            expected=state['inventory'][sku_check]
            physical=st.number_input('Physically counted units',min_value=0,value=max(expected,0),step=1)
            if st.form_submit_button('Reconcile count'):
                variance=reconcile_count(state,sku_check,int(physical))
                if variance:st.warning(f'Variance {variance:+d} recorded as an **exception**, not proof of theft.')
                else:st.success('Count reconciles with expected on-hand inventory.')
    st.markdown('### Warehouse and truck assignments')
    if state['truck_assignments']:
        st.dataframe(pd.DataFrame(state['truck_assignments']),width='stretch',hide_index=True)
    else:st.caption('Truck assignments will appear when replenishment or return pickup is triggered.')
    st.markdown('### Exceptions and audit trail')
    l,r=st.columns([1,1.4])
    with l:
        if state['exceptions']:
            st.dataframe(pd.DataFrame(state['exceptions']),width='stretch',hide_index=True)
        else:st.success('No open exceptions in this simulation.')
    with r:
        if state['events']:
            st.dataframe(pd.DataFrame(state['events']).sort_values('step',ascending=False),width='stretch',hide_index=True)
    st.caption(f'Illustrative administrative actions avoided: {summary["Estimated manual steps avoided"]}. This is a COUNTER of scripted steps, not validated hours or savings. Physical counts, custody verification, receiving, compliance and human approvals still apply.')
    st.download_button('Download simulated event log (CSV)', pd.DataFrame(state['events']).to_csv(index=False),file_name='beeriq_automation_events_simulated.csv',mime='text/csv')
    st.download_button('Download simulated ERP + fleet records (JSON)',json.dumps({'orders':state['orders'],'pickups':state['pickups'],'fleet':state['truck_assignments'],'exceptions':state['exceptions']},indent=2),file_name='beeriq_automation_simulated.json',mime='application/json')

if page == 'Sales':
    st.caption('SYNTHETIC DEMONSTRATION DATA — not 2024 company sales totals or store performance.')
    st.markdown("<div class='section-heading'>Sales performance</div><div class='section-subtitle'>Revenue, gross profit, location performance and product demand at a glance.</div>", unsafe_allow_html=True)
    metrics = kpis(sales)
    cols = st.columns(5)
    for col,label,value in zip(cols, ['Revenue', 'Gross profit', 'Gross margin', 'Units sold', 'Transactions'],
                                [f'{currency} {metrics["revenue"]:,.0f}', f'{currency} {metrics["gross_profit"]:,.0f}', f'{metrics["gross_margin_pct"]:.1f}%', f'{metrics["units"]:,}', f'{metrics["transactions"]:,}']):
        col.metric(label,value)
    monthly = sales_breakdown(sales, 'month', 50)
    st.plotly_chart(px.line(monthly,x='month',y=['revenue','gross_profit'],markers=True,title='Monthly revenue and gross profit',color_discrete_sequence=['#b3945c','#e2a33d']),width='stretch')
    a,b = st.columns(2)
    with a:
        st.plotly_chart(px.bar(sales_breakdown(sales,'store',50),x='store',y='revenue',title='Revenue by location',color_discrete_sequence=['#b3945c']),width='stretch')
    with b:
        st.plotly_chart(px.bar(sales_breakdown(sales,'product',10),x='product',y='units',title='Units by leading products',color_discrete_sequence=['#e2a33d']),width='stretch')
    st.dataframe(monthly,width='stretch',hide_index=True)
    st.download_button('Export monthly metrics CSV',monthly.to_csv(index=False),file_name='beeriq_monthly_metrics.csv',mime='text/csv')

if page == 'Products':
    st.markdown("<div class='section-heading'>Product intelligence</div><div class='section-subtitle'>Explore the relationship between synthetic product ratings, volume and revenue.</div>", unsafe_allow_html=True)
    st.caption('Fictional product names and ratings. A higher rating or more sales does not establish objective quality.')
    combined = quality_sales(sales,catalog)
    by_style = st.multiselect('Filter by style', sorted(catalog['style'].unique().tolist()), default=[])
    shown = combined[combined['style'].isin(by_style)] if by_style else combined
    valid = shown.dropna(subset=['rating'])
    if not valid.empty:
        fig = px.scatter(valid,x='rating',y='units',size='revenue',color='style',hover_name='product',
                         title='Illustrative ratings vs observed units', size_max=35)
        st.plotly_chart(fig,width='stretch')
    else:
        st.info('No matching products in the synthetic catalog. Upload catalog metadata to compare ratings in a real implementation.')
    st.dataframe(shown,width='stretch',hide_index=True)
    st.download_button('Download product analysis',shown.to_csv(index=False),file_name='beeriq_product_analysis.csv',mime='text/csv')

if page == 'Inventory':
    st.markdown("<div class='section-heading'>Inventory signals</div><div class='section-subtitle'>See baseline demand estimates and prioritize items that may need replenishment.</div>", unsafe_allow_html=True)
    st.caption('On-hand inventory is synthetic. Forecasts use a 28-day average including days with zero sales; they are not seasonal predictions.')
    selected_store = st.selectbox('Store',sorted(sales.store.unique()),key='forecast_store')
    selected_product = st.selectbox('Product',sorted(sales['product'].unique()),key='forecast_product')
    days = st.slider('Forecast horizon (days)',1,30,7)
    estimate = forecast(sales,selected_store,selected_product,days=days)
    m1,m2,m3 = st.columns(3)
    m1.metric('Estimated future units',f'{estimate["estimated_units"]:,.1f}')
    m2.metric('Historical daily average',f'{estimate["daily_average"]:,.2f}')
    m3.metric('Lookback',f'{estimate["historical_days"]} days')
    st.info(estimate['caution'])
    priorities = stock_priorities(sales,inventory,horizon=days)
    st.subheader('Illustrative replenishment watchlist')
    st.dataframe(priorities.head(40),width='stretch',hide_index=True)
    st.download_button('Download inventory watchlist',priorities.to_csv(index=False),file_name='beeriq_inventory_watchlist.csv',mime='text/csv')
    st.caption('Watchlist only compares synthetic on-hand units to baseline demand. It does not consider lead times, safety stock, promotions or supplier constraints.')

if page == 'Collections':
    st.markdown("<div class='section-heading'>Return collection planning</div><div class='section-subtitle'>Plan hypothetical pickup runs based on storage utilization and truck capacity.</div>", unsafe_allow_html=True)
    st.caption('Collection points are approximate illustrative city coordinates, NOT actual store facilities or real return volumes.')
    x,y,z = st.columns(3)
    capacity = x.number_input('Vehicle capacity (containers)',min_value=100,max_value=20000,value=2400,step=100)
    trucks = y.slider('Number of vehicles',1,10,4)
    threshold = z.slider('Collect if storage utilization ≥',0.1,1.0,.72,.02)
    plan = plan_pickups(locations,int(capacity),int(trucks),threshold)
    c1,c2,c3 = st.columns(3)
    c1.metric('Selected points',plan['selected_locations'])
    c2.metric('Scheduled points',plan['scheduled_locations'])
    c3.metric('Straight-line distance',f'{plan["total_distance_km_straight_line"]:,.1f} km')
    st.map(locations.rename(columns={'lat':'latitude','lon':'longitude'})[['latitude','longitude']])
    for route in plan['routes']:
        st.write(f'**Vehicle {route["vehicle"]}:** '+ ' → '.join(['Depot']+[stop['location'] for stop in route['stops']]+['Depot']))
        st.caption(f'Load {route["load"]:,}/{capacity:,} containers • {route["distance_km_straight_line"]:.1f} km straight-line')
    if plan['unscheduled']:
        st.error('Unscheduled high-utilization points: ' + ', '.join(x['location'] for x in plan['unscheduled']))
    st.warning(plan['limitations'])
    st.download_button('Download route plan (JSON)',__import__('json').dumps(plan,indent=2),file_name='beeriq_route_plan.json',mime='application/json')


if page == 'Fleet':
    st.markdown("<div class='section-heading'>Fleet command center</div><div class='section-subtitle'>Replay simulated vehicle movements and track pickup events through depot delivery.</div>", unsafe_allow_html=True)
    st.info('**Playback only:** Truck coordinates, travel times, loads and collection events are simulated. This is NOT live GPS data, not a The Beer Store system, and not connected to any fleet.')
    ctrl1, ctrl2, ctrl3 = st.columns(3)
    demo_trucks = ctrl1.slider('Demo trucks', 1, 8, 4, key='fleet_vehicles')
    demo_capacity = ctrl2.slider('Truck capacity • containers', 800, 7000, 3000, 100, key='fleet_capacity')
    demo_threshold = ctrl3.slider('Site pickup threshold', .30, 1.0, .65, .05, key='fleet_threshold')
    try:
        schedule = build_fleet_schedule(locations, truck_capacity=demo_capacity,
                                        vehicle_count=demo_trucks, priority_threshold=demo_threshold)
    except ValueError as err:
        st.error(str(err))
        st.stop()
    if 'fleet_minute' not in st.session_state:
        st.session_state.fleet_minute = 0
    st.session_state.fleet_minute = min(st.session_state.fleet_minute, schedule['duration_minutes'])
    a, b, c = st.columns([1,1,3])
    if a.button('▶ Advance 10 min', width='stretch'):
        st.session_state.fleet_minute = min(schedule['duration_minutes'], st.session_state.fleet_minute + 10)
    if b.button('↺ Restart', width='stretch'):
        st.session_state.fleet_minute = 0
    minute = c.slider('Simulated minutes from dispatch', 0, schedule['duration_minutes'],
                      key='fleet_minute', step=1)
    trucks_df, site_df, events_df = snapshot(schedule, minute)
    summary = fleet_summary(schedule, minute)
    st.session_state['fleet_ai_state'] = summary
    metrics = st.columns(5)
    for col, title, val in zip(metrics,
        ['Trucks active', 'Containers picked up', 'On trucks', 'Delivered to depot', 'Pickup sites completed'],
        [summary['trucks_active'], summary['containers_collected'],
         summary['containers_on_trucks'], summary['containers_delivered_to_depot'],
         f"{summary['sites_collected']}/{summary['sites_scheduled']}"]):
        col.metric(title, val)
    st.caption('Container counts are items, not physical bins. A pickup is logged after simulated loading time; depot delivery is logged on return.')
    st.markdown('#### Live simulation view')
    import plotly.graph_objects as go
    fig = go.Figure()
    sites = locations[~locations.is_depot.astype(bool)]
    fig.add_trace(go.Scattermap(lat=sites.lat, lon=sites.lon, mode='markers',
                               marker={'size': 12, 'color': '#229f81'}, name='Simulated collection points',
                               text=sites.location, hovertemplate='%{text}<extra></extra>'))
    depot = locations[locations.is_depot.astype(bool)]
    fig.add_trace(go.Scattermap(lat=depot.lat, lon=depot.lon, mode='markers',
                               marker={'size': 17, 'color': '#dca633'}, name='Demo depot',
                               text=depot.location, hovertemplate='%{text}<extra></extra>'))
    if not trucks_df.empty:
        fig.add_trace(go.Scattermap(lat=trucks_df.latitude, lon=trucks_df.longitude,
                                   mode='markers+text', text=trucks_df.truck_id,
                                   textposition='top right', marker={'size': 16, 'color': '#315ed3'},
                                   name='Simulated trucks',
                                   customdata=trucks_df[['status','containers_onboard','next_stop']].to_numpy(),
                                   hovertemplate='%{text}<br>%{customdata[0]}<br>Load %{customdata[1]}<br>Next: %{customdata[2]}<extra></extra>'))
    fig.update_layout(map={'style':'open-street-map', 'center': {'lat': float(locations.lat.mean()),
                           'lon': float(locations.lon.mean())}, 'zoom': 7},
                      height=490, margin={'t':0,'b':0,'l':0,'r':0}, legend={'orientation':'h'})
    st.plotly_chart(fig, width='stretch')
    st.caption('Map tiles require internet. Icons move in straight lines between simulated waypoints; they are NOT on actual roads.')
    st.markdown('#### Fleet status & ETA')
    st.dataframe(trucks_df.drop(columns=['latitude','longitude']), width='stretch', hide_index=True)
    left, right = st.columns(2)
    with left:
        st.markdown('#### Container pickup ledger')
        st.dataframe(site_df, width='stretch', hide_index=True)
    with right:
        st.markdown('#### Collection & depot events')
        st.dataframe(events_df, width='stretch', hide_index=True)
    if schedule['plan']['unscheduled']:
        st.warning(f"{len(schedule['plan']['unscheduled'])} sites could not be scheduled using the current capacity settings.")
    st.download_button('Export simulated fleet snapshot (CSV)', trucks_df.to_csv(index=False),
                       file_name='beeriq_fleet_snapshot.csv', mime='text/csv')
    st.download_button('Export container movement events (CSV)', events_df.to_csv(index=False),
                       file_name='beeriq_container_events.csv', mime='text/csv')
    st.download_button('Export dispatch plan (JSON)', __import__('json').dumps(schedule, indent=2),
                       file_name='beeriq_fleet_dispatch_plan.json', mime='application/json')
    st.warning(schedule['disclosure'])

if page == 'Assistant':
    st.markdown("<div class='section-heading'>Ask BeerIQ</div><div class='section-subtitle'>Get clear, reproducible answers grounded in the demo data. No API key required.</div>", unsafe_allow_html=True)
    st.caption('No API key needed. The assistant selects an analytical function based on your question, computes results from the loaded data, and explains its evidence. This is a deterministic tool-routing assistant, not an LLM.')
    examples = [
        'What are the top products by revenue?',
        'How did monthly sales and gross margins change?',
        'Which stores have the highest sales?',
        'Are highly rated products also top sellers?',
        'Which inventory positions need replenishment?',
        'Which recycling locations need pickups?',
        'What is the simulated truck fleet status?',
        'Give me an overall business summary',
    ]
    selected = st.selectbox('Suggested questions', ['Type my own question'] + examples)
    question = st.text_area('Business question', value='' if selected == 'Type my own question' else selected,
                            placeholder='Example: Which products have the lowest margins?')
    if st.button('✨ Analyze business question',type='primary'):
        if not question.strip():
            st.warning('Enter a question or choose an example.')
        else:
            with st.spinner('Calculating from source data...'):
                answer, traces = analyze_question(
                    question, sales, catalog, inventory, locations,
                    fleet_state=st.session_state.get('fleet_ai_state', fleet_summary(build_fleet_schedule(locations), 0)),
                )
            st.markdown(answer)
            with st.expander('Audit trail: functions and numbers used'):
                st.json(traces)
    st.info('How it works: a rule-based assistant chooses Python analytics functions. It is not a generative LLM. Results use synthetic data and require independent validation.')

if page == 'Sources':
    st.markdown(f'### Sources & methodology\n\n**Historical 2024 data:** [The Beer Store Operations Report]({OPS_URL}) and [The Beer Store Stewardship Report]({STEW_URL}).\n\n**Industry trends:** [NIQ]({NIQ_URL}) and [LCBO]({LCBO_URL}).\n\n**Important:** Calculated 2024 channel estimates use rounded shares and may not reconcile exactly. Product, stock, location, sales transactions, truck locations and routes are entirely simulated.\n\n---')
    st.markdown('''### Intended business decisions
- **Fleet dispatchers:** replay synthetic truck routes, container loading events and depot deliveries with explainable load and ETA calculations.
- **Retail managers:** inspect revenue, volume and gross-margin changes from transaction data.
- **Merchandising analysts:** examine whether *illustrative* ratings correlate with observed unit sales, without implying quality or causation.
- **Inventory planners:** flag possible shortfalls using an explainable, deliberately simple demand baseline.
- **Recycling operations:** prioritize high-utilization collection points and draft capacity-feasible straight-line pickup routes.

### What is and is not real
All bundled transaction, product, cost, rating, collection, and stock data are **fabricated** for a reproducible portfolio demo. The project is inspired by general retail and return-logistics workflows. It has no operational connection with The Beer Store. Theoretical use cases are not claims about the company's internal performance.

### Critical limitations
- `gross_profit = units × (unit_price − unit_cost)` is **not net profit** and excludes labor, rent, delivery and other operating costs.
- Ratings are fabricated, not scraped from reviewers. Quality is subjective.
- The baseline forecast is a trailing average, not a trained machine-learning model.
- Truck locations are simulated and linearly interpolated, not live GPS or road paths. ETA uses a constant illustrative speed.
- Collection routing is a greedy heuristic, not an exact optimizer; it uses **straight-line** distances, not drive times.
- Uploading sales does not replace the bundled synthetic inventory/catalog/collection datasets.
- The product explorer is descriptive, not a recommendation engine to encourage alcohol purchasing.
- The free assistant uses deterministic keyword routing to analytical functions, not a generative LLM. No paid API is required. Avoid uploading confidential data to a public web application.

### Input schema
Sales CSV/XLSX requires `date`, `store`, `product`, `units`, `unit_price`, `unit_cost`. See sample data.

### How to verify
Run `python3 -m pytest -q`. Recreate demonstration files with `python3 create_demo_data.py`.
''')
