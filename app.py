import os, urllib.parse
import requests as req
from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = "yesilcam2026"

# ──────────────────────────────────────────────────────
#  DATABASE CONFIGURATION
# ──────────────────────────────────────────────────────

DB = dict(
    host="localhost", port=3306,
    user="root", password= "<enter your password>",
    database="yesilcam", charset="utf8mb4",
)

def query(sql, params=None, one=False):
    conn = mysql.connector.connect(**DB)
    cur  = conn.cursor(dictionary=True)
    cur.execute(sql, params or ())
    r = cur.fetchone() if one else cur.fetchall()
    conn.close()
    return r

def execute(sql, params=None):
    conn = mysql.connector.connect(**DB)
    cur  = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    lid = cur.lastrowid
    conn.close()
    return lid

# ──────────────────────────────────────────────────────
#  TMDB GRAPHICS API
# ──────────────────────────────────────────────────────

TMDB_KEY  = "<your_tmdb_api_key>" #enter your TMDB API key"
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG  = "https://image.tmdb.org/t/p"

_pcache = {}
_acache = {}

def tr_clear(text):
    text = text.strip().lower()
    text = text.replace("ı", "i").replace("ş", "s").replace("ğ", "g")
    text = text.replace("ç", "c").replace("ü", "u").replace("ö", "o")
    return text

def tmdb_poster(title, year=""):
    key = (title, str(year))
    if key in _pcache:
        return _pcache[key]
        
    flat_title = tr_clear(title)

    try:
        q = urllib.parse.quote(title)
        for url in [
            f"{TMDB_BASE}/search/movie?api_key={TMDB_KEY}&query={q}&year={year}&language=tr-TR",
            f"{TMDB_BASE}/search/movie?api_key={TMDB_KEY}&query={q}&language=tr-TR",
        ]:
            data = req.get(url, timeout=4).json()
            for res in data.get("results", []):
                p = res.get("poster_path")
                if p:
                    img = f"{TMDB_IMG}/w500{p}"
                    _pcache[key] = img
                    return img
    except Exception:
        pass
    _pcache[key] = None
    return None

def tmdb_person(name):
    if name in _acache:
        return _acache[name]
    try:
        q = urllib.parse.quote(name)
        data = req.get(f"{TMDB_BASE}/search/person?api_key={TMDB_KEY}&query={q}", timeout=4).json()
        for res in data.get("results", []):
            p = res.get("profile_path")
            if p:
                img = f"{TMDB_IMG}/w185{p}"
                _acache[name] = img
                return img
    except Exception:
        pass
    _acache[name] = None
    return None

# ──────────────────────────────────────────────────────
#  UI STYLES & RETRO CINEMA THEME (CSS)
# ──────────────────────────────────────────────────────

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Source+Sans+3:wght@300;400;600&family=Space+Mono:wght@400&display=swap');
:root {
  --bg:#0b0907; --surface:#161310; --card:#1e1b12; --border:#2d2a1a;
  --gold:#c8952a; --gold-lt:#e6b44a; --gold-dk:#7a5c12;
  --text:#e8dfc8; --muted:#9a9070; --dim:#504838;
  --serif:'Playfair Display',Georgia,serif;
  --body:'Source Sans 3',sans-serif;
  --mono:'Space Mono',monospace;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:var(--body);font-size:15px;line-height:1.65;min-height:100vh}
a{color:var(--gold);text-decoration:none}
a:hover{color:var(--gold-lt)}
img{display:block;max-width:100%}
button{cursor:pointer;font-family:var(--body)}
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--gold-dk);border-radius:3px}

/* NAV */
nav{position:fixed;top:0;left:0;right:0;z-index:999;height:60px;display:flex;align-items:center;gap:4px;padding:0 36px;background:rgba(11,9,7,.97);border-bottom:1px solid var(--border);backdrop-filter:blur(8px)}
.nav-logo{font-family:var(--serif);font-size:1.25rem;font-weight:900;letter-spacing:.08em;color:var(--gold)!important;margin-right:24px;flex-shrink:0}
.nav-link{font-family:var(--mono);font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:6px 11px;border-radius:4px;transition:.18s}
.nav-link:hover,.nav-link.active{color:var(--gold-lt);background:rgba(200,149,42,.08)}
.nav-right{display:flex;align-items:center;gap:8px;margin-left:auto}
.nav-sf{display:flex;gap:0}
.nav-sf input{background:rgba(255,255,255,.04);border:1px solid var(--border);border-right:none;color:var(--text);padding:6px 12px;font-size:.85rem;border-radius:4px 0 0 4px;outline:none;width:180px;transition:.18s}
.nav-sf input:focus{border-color:var(--gold);width:220px}
.nav-sf button{background:var(--gold);border:none;color:#000;padding:6px 12px;border-radius:0 4px 4px 0}

/* BUTTONS */
.btn{display:inline-block;font-family:var(--mono);font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;padding:7px 16px;border-radius:4px;border:none;transition:.18s;cursor:pointer}
.btn-gold{background:var(--gold);color:#000;font-weight:700}
.btn-gold:hover{background:var(--gold-lt);color:#000}
.btn-outline{background:none;border:1px solid var(--gold-dk);color:var(--gold)}
.btn-outline:hover{border-color:var(--gold);background:rgba(200,149,42,.08)}
.btn-ghost{background:none;border:1px solid var(--border);color:var(--muted)}
.btn-ghost:hover{border-color:var(--muted);color:var(--text)}

/* LAYOUT */
.pt-nav{padding-top:60px}
.page-top{padding:44px 60px 36px;background:linear-gradient(to bottom,var(--surface),var(--bg));border-bottom:1px solid var(--border)}
.page-title{font-family:var(--serif);font-size:clamp(1.8rem,3vw,2.8rem);font-weight:900;color:var(--text)}
.page-title span{color:var(--gold);font-style:italic}
.page-sub{font-size:.95rem;color:var(--muted);margin-top:4px}
.section{padding:48px 60px}
.sec-head{display:flex;align-items:baseline;justify-content:space-between;border-bottom:1px solid var(--border);padding-bottom:14px;margin-bottom:28px}
.sec-title{font-family:var(--serif);font-size:1.6rem;font-weight:700}
.sec-title::before{content:'';display:inline-block;width:4px;height:.9em;background:var(--gold);margin-right:12px;vertical-align:middle;border-radius:2px}
.sec-link{font-family:var(--mono);font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;color:var(--dim)}
.sec-link:hover{color:var(--gold)}

/* HERO */
.hero{margin-top:60px;min-height:86vh;display:flex;align-items:center;background:radial-gradient(ellipse at 65% 50%,#231a05 0%,#0b0907 62%);position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(255,255,255,.006) 3px,rgba(255,255,255,.006) 4px)}
.fs{position:absolute;left:0;right:0;height:26px;background:var(--surface);background-image:repeating-linear-gradient(90deg,transparent 0,transparent 20px,rgba(255,255,255,.07) 20px,rgba(255,255,255,.07) 32px);border-top:2px solid #000;border-bottom:2px solid #000}
.fs.top{top:0}.fs.bottom{bottom:0}
.hero-inner{position:relative;z-index:2;padding:80px 80px 80px 100px;max-width:760px}
.hero-eye{font-family:var(--mono);font-size:.65rem;letter-spacing:.28em;text-transform:uppercase;color:var(--gold);display:flex;align-items:center;gap:10px;margin-bottom:18px}
.hero-eye::before{content:'';width:28px;height:1px;background:var(--gold)}
.hero-h1{font-family:var(--serif);font-size:clamp(3rem,5.5vw,5.5rem);font-weight:900;line-height:1.05;color:#fff;margin-bottom:10px}
.hero-h1 em{color:var(--gold)}
.hero-p{font-size:1.05rem;color:var(--muted);max-width:500px;margin-bottom:32px;font-weight:300}
.hero-btns{display:flex;gap:12px;flex-wrap:wrap}
.hbtn{font-family:var(--serif);font-size:.95rem;font-weight:700;padding:12px 30px;border-radius:4px;border:none;letter-spacing:.02em;cursor:pointer;transition:.18s;display:inline-block}
.hbtn-g{background:var(--gold);color:#000}
.hbtn-g:hover{background:var(--gold-lt);color:#000;transform:translateY(-1px)}
.hbtn-o{background:none;border:1px solid var(--gold-dk);color:var(--gold)}
.hbtn-o:hover{background:rgba(200,149,42,.08);border-color:var(--gold)}

/* STATS */
.stats-bar{display:flex;justify-content:center;align-items:center;background:var(--surface);border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:18px 0}
.stat{text-align:center;padding:0 44px}
.stat-n{font-family:var(--serif);font-size:2.2rem;font-weight:700;color:var(--gold);display:block;line-height:1}
.stat-l{font-family:var(--mono);font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);margin-top:2px}
.stats-sep{color:var(--gold-dk);font-size:1.2rem}

/* MOVIE GRID & CARD */
.movie-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:12px}
.movie-card{background:var(--card);border:1px solid var(--border);border-radius:4px;overflow:hidden;cursor:pointer;transition:transform .18s,box-shadow .18s,border-color .18s;display:block;color:inherit}
.movie-card:hover{transform:translateY(-4px);box-shadow:0 14px 36px rgba(0,0,0,.75);border-color:var(--gold-dk)}
.card-poster{width:100%;aspect-ratio:2/3;background:linear-gradient(160deg,#2a2010,#141008);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;border-bottom:1px solid var(--border);overflow:hidden;padding:0}
.card-poster img{width:100%;height:100%;object-fit:cover}
.card-poster-ph{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;padding:14px}
.card-poster-ph .icon{font-size:2.4rem;opacity:.5}
.card-poster-ph .pt{font-family:var(--serif);font-size:.8rem;font-weight:700;text-align:center;color:var(--muted);line-height:1.3}
.card-body{padding:11px 13px 13px}
.card-title{font-family:var(--serif);font-size:.9rem;font-weight:700;color:var(--text);line-height:1.3;margin-bottom:3px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card-meta{font-family:var(--mono);font-size:.65rem;color:var(--dim)}
.card-dir{font-size:.78rem;color:var(--muted);margin-top:2px}
.card-rating{display:inline-flex;align-items:center;gap:3px;margin-top:7px;font-family:var(--serif);font-size:.8rem;color:var(--gold);background:rgba(200,149,42,.1);border:1px solid var(--gold-dk);border-radius:3px;padding:2px 7px}
.card-rating.none{color:var(--dim);border-color:var(--border);background:none}
.hscroll{display:flex;gap:14px;overflow-x:auto;padding-bottom:8px}
.hscroll::-webkit-scrollbar{height:3px}
.hscroll .movie-card{flex:0 0 155px}

/* FILTERS */
.filters{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;background:var(--surface);border-bottom:1px solid var(--border);padding:16px 60px}
.fg{display:flex;flex-direction:column;gap:4px}
.fg label{font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--dim)}
.fg select,.fg input{background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:7px 10px;font-family:var(--body);font-size:.88rem;outline:none;transition:.18s;min-width:140px}
.fg select:focus,.fg input:focus{border-color:var(--gold)}

/* DETAIL HERO */
.detail-hero{margin-top:60px;padding:52px 60px 44px;display:flex;gap:40px;align-items:flex-end;background:radial-gradient(ellipse at 70% 40%,#231a05 0%,#0b0907 65%);border-bottom:1px solid var(--border)}
.detail-poster{flex-shrink:0;width:170px;aspect-ratio:2/3;background:linear-gradient(160deg,#2a2010,#141008);border:1px solid var(--border);border-radius:4px;overflow:hidden;display:flex;align-items:center;justify-content:center}
.detail-poster img{width:100%;height:100%;object-fit:cover}
.detail-poster-ph{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;padding:14px;width:100%;height:100%}
.detail-poster-ph .icon{font-size:3rem;opacity:.4}
.detail-poster-ph .pt{font-family:var(--serif);font-size:.85rem;font-weight:700;text-align:center;color:var(--muted);line-height:1.3}
.detail-info{flex:1}
.genre-tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.genre-tag{font-family:var(--mono);font-size:.62rem;letter-spacing:.07em;text-transform:uppercase;padding:3px 9px;border-radius:20px;background:rgba(200,149,42,.1);border:1px solid var(--gold-dk);color:var(--gold)}
.detail-title{font-family:var(--serif);font-size:clamp(1.9rem,4vw,3.2rem);font-weight:900;color:#fff;line-height:1.1;margin-bottom:8px}
.detail-meta{font-family:var(--mono);font-size:.68rem;color:var(--dim);margin-bottom:6px}
.detail-dir{font-size:.92rem;color:var(--gold-dk);margin-bottom:12px}
.detail-syn{font-size:.98rem;color:var(--muted);line-height:1.75;max-width:660px;margin-bottom:18px}
.detail-rating-big{font-family:var(--serif);font-size:2.4rem;font-weight:900;color:var(--gold);line-height:1}
.detail-rating-lbl{font-family:var(--mono);font-size:.6rem;color:var(--dim);letter-spacing:.1em;text-transform:uppercase}
.detail-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}

/* CAST */
.cast-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px}
.cast-card{background:var(--card);border:1px solid var(--border);border-radius:4px;overflow:hidden;text-align:center}
.cast-card.lead{border-color:var(--gold-dk)}
.cast-photo{width:100%;aspect-ratio:1;background:linear-gradient(135deg,#2a2010,#3a3020);overflow:hidden;display:flex;align-items:center;justify-content:center;font-size:2rem}
.cast-photo img{width:100%;height:100%;object-fit:cover;object-position:top}
.cast-body{padding:10px 8px}
.cast-name{font-family:var(--serif);font-size:.82rem;font-weight:700;color:var(--text)}
.cast-role{font-size:.74rem;color:var(--dim);font-style:italic;margin-top:2px}
.lead-badge{font-family:var(--mono);font-size:.55rem;letter-spacing:.07em;text-transform:uppercase;color:var(--gold);margin-top:3px}

/* REVIEWS */
.review-card{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:16px 18px;margin-bottom:10px}
.review-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.review-user{font-family:var(--serif);font-weight:700;color:var(--gold-lt)}
.review-score{font-family:var(--serif);font-size:.95rem;color:var(--gold);background:rgba(200,149,42,.1);border:1px solid var(--gold-dk);border-radius:3px;padding:2px 9px}
.review-body{font-size:.93rem;color:var(--muted);line-height:1.6}
.review-date{font-family:var(--mono);font-size:.62rem;color:var(--dim);margin-top:5px}
.rform{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:22px;margin-bottom:24px}
.rform h3{font-family:var(--serif);font-size:1.05rem;color:var(--text);margin-bottom:14px}
.stars{display:flex;gap:5px;margin-bottom:12px}
.star-btn{font-size:1.5rem;background:none;border:none;color:var(--dim);transition:color .12s}
.star-btn.on{color:var(--gold)}
textarea.rtext{width:100%;background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:4px;color:var(--text);padding:9px 11px;font-family:var(--body);font-size:.92rem;resize:vertical;min-height:78px;outline:none;margin-bottom:10px;transition:.18s}
textarea.rtext:focus{border-color:var(--gold)}

/* PERSON GRID */
.person-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}
.person-card{background:var(--card);border:1px solid var(--border);border-radius:4px;overflow:hidden;transition:.18s}
.person-card:hover{border-color:var(--gold-dk);transform:translateY(-2px)}
.person-photo{width:100%;aspect-ratio:3/4;background:linear-gradient(160deg,#2a2010,#141008);overflow:hidden;display:flex;align-items:center;justify-content:center;font-size:3rem;color:var(--dim)}
.person-photo img{width:100%;height:100%;object-fit:cover;object-position:top}
.person-body{padding:14px}
.person-name{font-family:var(--serif);font-size:1rem;font-weight:700;color:var(--text);margin-bottom:3px}
.person-meta{font-family:var(--mono);font-size:.62rem;letter-spacing:.07em;color:var(--dim);text-transform:uppercase}
.person-bio{font-size:.84rem;color:var(--muted);line-height:1.55;margin-top:7px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.person-badge{display:inline-flex;align-items:center;gap:4px;margin-top:9px;font-family:var(--mono);font-size:.6rem;letter-spacing:.07em;text-transform:uppercase;color:var(--gold);background:rgba(200,149,42,.1);border:1px solid var(--gold-dk);border-radius:3px;padding:3px 8px}

/* DASHBOARD */
.dash-stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin-bottom:36px}
.dash-stat{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:16px;text-align:center}
.ds-n{font-family:var(--serif);font-size:1.9rem;font-weight:700;color:var(--gold)}
.ds-l{font-family:var(--mono);font-size:.58rem;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);margin-top:3px}
.tabs{display:flex;border-bottom:1px solid var(--border);margin-bottom:24px}
.tab-btn{font-family:var(--mono);font-size:.66rem;letter-spacing:.09em;text-transform:uppercase;padding:10px 20px;background:none;border:none;border-bottom:2px solid transparent;color:var(--dim);cursor:pointer;transition:.18s}
.tab-btn.active,.tab-btn:hover{color:var(--gold);border-bottom-color:var(--gold)}
.tab-panel{display:none}
.tab-panel.active{display:block}
.hist-row{display:flex;align-items:center;gap:14px;padding:11px 0;border-bottom:1px solid var(--border)}
.hist-icon{font-size:1.3rem;flex-shrink:0}
.hist-title{font-family:var(--serif);font-size:.9rem;font-weight:700;color:var(--text)}
.hist-meta{font-family:var(--mono);font-size:.62rem;color:var(--dim);margin-top:1px}
.hist-pct{margin-left:auto;flex-shrink:0;font-family:var(--mono);font-size:.65rem;color:var(--gold);background:rgba(200,149,42,.1);border:1px solid var(--gold-dk);border-radius:3px;padding:2px 7px}

/* AUTH */
.auth-wrap{margin-top:60px;min-height:calc(100vh - 60px);display:flex;align-items:center;justify-content:center;padding:40px 20px;background:radial-gradient(ellipse at 50% 40%,#1a1406 0%,#0b0907 60%)}
.auth-box{background:var(--card);border:1px solid var(--border);border-radius:4px;padding:38px 34px;width:100%;max-width:390px;box-shadow:0 20px 56px rgba(0,0,0,.8)}
.auth-title{font-family:var(--serif);font-size:1.7rem;font-weight:700;color:var(--text);margin-bottom:6px}
.auth-sub{font-size:.88rem;color:var(--muted);margin-bottom:26px}
.auth-err{font-size:.82rem;color:#e05050;margin-bottom:10px}
.fg-a{margin-bottom:14px}
.fg-a label{display:block;font-family:var(--mono);font-size:.62rem;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin-bottom:5px}
.fg-a input{width:100%;background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:4px;color:var(--text);padding:9px 11px;font-family:var(--body);font-size:.92rem;outline:none;transition:.18s}
.fg-a input:focus{border-color:var(--gold)}
.fg-a input::placeholder{color:var(--dim)}
.auth-btn{width:100%;padding:11px;margin-top:4px;background:var(--gold);color:#000;border:none;border-radius:4px;font-family:var(--serif);font-size:.98rem;font-weight:700;cursor:pointer;transition:.18s}
.auth-btn:hover{background:var(--gold-lt)}
.auth-sw{text-align:center;margin-top:16px;font-size:.84rem;color:var(--muted)}
.auth-hint{text-align:center;margin-top:10px;font-size:.76rem;color:var(--dim)}

/* FOOTER */
footer{text-align:center;padding:44px 24px 32px;border-top:1px solid var(--border);background:var(--surface)}
.footer-logo{font-family:var(--serif);font-size:1.7rem;font-weight:900;color:var(--gold);letter-spacing:.1em;margin-bottom:6px}
.footer-sub{font-size:.84rem;color:var(--dim)}
.footer-copy{font-family:var(--mono);font-size:.6rem;color:var(--dim);margin-top:4px;letter-spacing:.07em}

/* TOAST */
#toast{position:fixed;bottom:22px;right:22px;z-index:9999;background:var(--card);border:1px solid var(--border);border-left:3px solid var(--gold);border-radius:4px;padding:11px 16px;font-size:.88rem;color:var(--text);box-shadow:0 8px 28px rgba(0,0,0,.7);transform:translateY(70px);opacity:0;transition:transform .28s ease,opacity .28s ease;max-width:270px;pointer-events:none}
#toast.show{transform:translateY(0);opacity:1}
#toast.err{border-left-color:#8b2020}

/* UTILS */
.empty{color:var(--dim);font-style:italic;padding:16px 0}

@media(max-width:860px){
  .hero-inner{padding:60px 24px}
  .section,.page-top{padding:32px 20px}
  .filters{padding:14px 20px}
  .detail-hero{flex-direction:column;padding:28px 20px}
  nav .nav-link{display:none}
}
@media(max-width:560px){
  .stats-bar{flex-wrap:wrap}
  .stats-sep{display:none}
  .movie-grid{grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px}
}
</style>
"""

# ──────────────────────────────────────────────────────
#  JAVASCRIPT REACTION CONTROLLERS
# ──────────────────────────────────────────────────────

JS = """
<script>
let _tt;
function toast(msg,err=false){
  let el=document.getElementById('toast');
  if(!el){el=document.createElement('div');el.id='toast';document.body.appendChild(el)}
  el.textContent=msg; el.className=err?'err':'';
  requestAnimationFrame(()=>el.classList.add('show'));
  clearTimeout(_tt); _tt=setTimeout(()=>el.classList.remove('show'),3000);
}
let selR=0;
function initStars(){
  const btns=document.querySelectorAll('.star-btn');
  const inp=document.getElementById('rating-val');
  if(!btns.length)return;
  btns.forEach((b,i)=>{
    b.addEventListener('mouseenter',()=>paintS(i+1));
    b.addEventListener('mouseleave',()=>paintS(selR));
    b.addEventListener('click',()=>{selR=i+1;paintS(i+1);if(inp)inp.value=i+1});
  });
}
function paintS(n){
  document.querySelectorAll('.star-btn').forEach((b,i)=>{
    b.textContent=i<n?'★':'☆'; b.classList.toggle('on',i<n);
  });
}
function toggleWatchlist(mid){
  const btn=document.getElementById('wl-btn');
  const inList=btn&&btn.dataset.in === '1';
  fetch('/api/watchlist/'+mid,{method:inList?'DELETE':'POST'})
    .then(r=>r.json()).then(d=>{
      if(d.error){toast(d.error,true);return}
      btn.dataset.in=inList?'0':'1';
      btn.innerHTML=inList?'+ Add to Watchlist':'✓ In Watchlist';
      btn.className=inList?'btn btn-outline':'btn btn-ghost';
      toast(inList?'Removed from watchlist':'Added to watchlist!');
    }).catch(()=>toast('Error',true));
}
function submitReview(mid){
  const rating=document.getElementById('rating-val')?.value;
  const comment=document.getElementById('rev-comment')?.value.trim();
  if(!rating||rating<1){toast('Please select a rating',true);return}
  const fd=new FormData();
  fd.append('movie_id',mid);fd.append('rating',rating);fd.append('comment',comment);
  fetch('/api/review',{method:'POST',body:fd})
    .then(r=>r.json()).then(d=>{
      if(d.error){toast(d.error,true);return}
      toast('Review saved! Avg: '+d.new_avg+' ★');
      setTimeout(()=>location.reload(),1200);
    }).catch(()=>toast('Error',true));
}
function switchTab(name){
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.querySelector('.tab-btn[data-t="'+name+'"]')?.classList.add('active');
  document.getElementById('tp-'+name)?.classList.add('active');
}
document.addEventListener('DOMContentLoaded',()=>{
  initStars();
  document.querySelectorAll('.auto-sub').forEach(el=>{
    el.addEventListener('change',()=>el.closest('form').submit());
  });
  const first=document.querySelector('.tab-btn');
  if(first)switchTab(first.dataset.t);
});
</script>
"""

# ──────────────────────────────────────────────────────
#  TEMPLATING HELPERS & COMPONENTS (SAFE REPLACE METHOD)
# ──────────────────────────────────────────────────────

def nav_html():
    uid  = session.get("user_id")
    user = session.get("full_name", "")
    profile = "<a class='nav-link' href='/dashboard'>My Profile</a>" if uid else ""
    if uid:
        right = f"<span style='font-size:.82rem;color:var(--muted);'>{user}</span><a class='btn btn-ghost' href='/logout'>Logout</a>"
    else:
        right = "<a class='btn btn-outline' href='/login'>Login</a><a class='btn btn-gold' href='/register'>Sign Up</a>"
    
    html = """
    <nav>
    <a class='nav-logo' href='/'>Yeşilçam</a>
    <a class='nav-link' href='/'>Home</a>
    <a class='nav-link' href='/movies'>Movies</a>
    <a class='nav-link' href='/directors'>Directors</a>
    <a class='nav-link' href='/actors'>Actors</a>
    __PROFILE__
    <div class='nav-right'>
    <form class='nav-sf' method='GET' action='/movies'>
    <input type='text' name='search' placeholder='Search films…'>
    <button type='submit'>⎕</button>
    </form>
    __RIGHT__
    </div></nav>
    """
    return html.replace("__PROFILE__", profile).replace("__RIGHT__", right)

def footer_html():
    return (
        "<footer>"
        "<div class='footer-logo'>Yeşilçam</div>"
        "<p class='footer-sub'>Turkish Cinema 1950 — 1990</p>"
        "<p class='footer-copy'>© 2026 Cinema Yesilcam Database</p>"
        "</footer>"
    )

def page(title, content):
    html = """
    <!DOCTYPE html><html lang='en'><head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width,initial-scale=1.0'>
    <title>__TITLE__ — Cinema Yesilcam</title>
    <link rel='preconnect' href='https://fonts.googleapis.com'>
    <link href='https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Source+Sans+3:wght@300;400;600&family=Space+Mono:wght@400&display=swap' rel='stylesheet'>
    __CSS__
    </head><body>
    __NAV__
    __CONTENT__
    __FOOTER__
    <div id='toast'></div>
    __JS__
    </body></html>
    """
    return render_template_string(
        html.replace("__TITLE__", title)
            .replace("__CSS__", CSS)
            .replace("__NAV__", nav_html())
            .replace("__CONTENT__", content)
            .replace("__FOOTER__", footer_html())
            .replace("__JS__", JS)
    )

def movie_card(m):
    title  = m.get("title", "")
    year   = m.get("release_year", "")
    r      = m.get("avg_rating")
    dur    = f" \u00b7 {m['duration_min']} min" if m.get("duration_min") else ""
    rating = f'<div class="card-rating">★ {r}</div>' if r else '<div class="card-rating none">No rating</div>'
    poster = tmdb_poster(title, year)
    
    if poster:
        clean_title = title.replace("'", "").replace('"', '')
        img = f"<img src='{poster}' alt='{clean_title}' onerror=\"this.parentElement.innerHTML='<div class=card-poster-ph><div class=icon>🎬</div><div class=pt>{clean_title}</div></div>'\">"
    else:
        img = f"<div class='card-poster-ph'><div class='icon'>🎬</div><div class='pt'>{title}</div></div>"

    html = """
    <a class='movie-card' href='/movie/__MID__'>
    <div class='card-poster'>__IMG__</div>
    <div class='card-body'>
    <div class='card-title'>__TITLE__</div>
    <div class='card-meta'>__YEAR____DUR__</div>
    <div class='card-dir'>__DIR__</div>
    __RATING__
    </div></a>
    """
    return (
        html.replace("__MID__", str(m['movie_id']))
            .replace("__IMG__", img)
            .replace("__TITLE__", title)
            .replace("__YEAR__", str(year))
            .replace("__DUR__", dur)
            .replace("__DIR__", m.get('director', ''))
            .replace("__RATING__", rating)
    )

def person_card(p, is_director=False):
    name  = p.get("full_name", "")
    photo = tmdb_person(name)
    if photo:
        clean_name = name.replace("'", "").replace('"', '')
        photo_html = f"<img src='{photo}' alt='{clean_name}' onerror=\"this.parentElement.innerHTML='&#127937;'\">"
    else:
        photo_html = "🎬" if is_director else "🎭"

    mc   = p.get("mc", p.get("movie_count", 0))
    ar   = p.get("ar", p.get("avg_rating", None))
    bio  = p.get("bio", "") or ""
    meta_parts = []
    if p.get("birth_year"): meta_parts.append(str(p["birth_year"]))
    if p.get("nationality") and is_director: meta_parts.append(p["nationality"])
    if p.get("birth_place") and not is_director: meta_parts.append(p["birth_place"])
    meta = " \u00b7 ".join(meta_parts)

    icon_type = "🎬" if is_director else "🎭"
    plural_s = "s" if mc != 1 else ""
    rating_part = f" \u00b7 ★ {ar}" if ar else ""
    
    badge = f"<div class='person-badge'>{icon_type} {mc} film{plural_s}{rating_part}</div>"
    bio_html = f"<div class='person-bio'>{bio}</div>" if bio else ""

    html = """
    <div class='person-card'>
    <div class='person-photo'>__PHOTO__</div>
    <div class='person-body'>
    <div class='person-name'>__NAME__</div>
    <div class='person-meta'>__META__</div>
    __BIO__
    __BADGE__
    </div></div>
    """
    return (
        html.replace("__PHOTO__", photo_html)
            .replace("__NAME__", name)
            .replace("__META__", meta)
            .replace("__BIO__", bio_html)
            .replace("__BADGE__", badge)
    )


# ──────────────────────────────────────────────────────
#  ROUTES CONTROLLERS
# ──────────────────────────────────────────────────────

@app.route("/")
def index():
    featured = query("""
        SELECT m.movie_id,m.title,m.release_year,m.avg_rating,m.duration_min,d.full_name AS director
        FROM Movies m JOIN Directors d ON m.director_id=d.director_id
        ORDER BY m.avg_rating DESC LIMIT 8
    """)
    trending = query("""
        SELECT m.movie_id,m.title,m.release_year,m.avg_rating,m.duration_min,
               d.full_name AS director, COUNT(wh.history_id) AS watches
        FROM Movies m
        JOIN Directors d ON m.director_id=d.director_id
        JOIN WatchHistory wh ON m.movie_id=wh.movie_id
        GROUP BY m.movie_id,m.title,m.release_year,m.avg_rating,m.duration_min,d.full_name
        ORDER BY watches DESC LIMIT 6
    """)
    stats = query("""
        SELECT (SELECT COUNT(*) FROM Movies) AS tm,
               (SELECT COUNT(*) FROM Directors) AS td,
               (SELECT COUNT(*) FROM Actors) AS ta,
               (SELECT COUNT(*) FROM Reviews) AS tr
    """, one=True)

    cards_html    = "".join(movie_card(m) for m in featured)
    trending_html = "".join(movie_card(m) for m in trending)

    html = """
    <section class='hero'>
    <div class='fs top'></div>
    <div class='hero-inner'>
    <div class='hero-eye'>1950 — 1990 · Turkish Cinema</div>
    <h1 class='hero-h1'>The Golden Age<br>of <em>Yeşilçam</em></h1>
    <p class='hero-p'>From Yilmaz Guney to Ertem Egilmez — explore the timeless masterpieces of Turkey’s most beloved film era.</p>
    <div class='hero-btns'>
    <a class='hbtn hbtn-g' href='/movies'>Browse Films</a>
    <a class='hbtn hbtn-o' href='/directors'>Directors</a>
    </div></div>
    <div class='fs bottom'></div>
    </section>

    <div class='stats-bar'>
    <div class='stat'><span class='stat-n'>__STAT_M__</span><span class='stat-l'>Films</span></div>
    <span class='stats-sep'>✦</span>
    <div class='stat'><span class='stat-n'>__STAT_D__</span><span class='stat-l'>Directors</span></div>
    <span class='stats-sep'>✦</span>
    <div class='stat'><span class='stat-n'>__STAT_A__</span><span class='stat-l'>Actors</span></div>
    <span class='stats-sep'>✦</span>
    <div class='stat'><span class='stat-n'>__STAT_R__</span><span class='stat-l'>Reviews</span></div>
    </div>

    <div class='section'>
    <div class='sec-head'><h2 class='sec-title'>Top Rated Films</h2>
    <a class='sec-link' href='/movies?sort=avg_rating'>See all →</a></div>
    <div class='movie-grid'>__FEATURED__</div>
    </div>

    <div class='section' style='background:var(--surface);border-top:1px solid var(--border);border-bottom:1px solid var(--border);'>
    <div class='sec-head'><h2 class='sec-title'>Trending Now</h2>
    <a class='sec-link' href='/movies?sort=view_count'>See all →</a></div>
    <div class='hscroll'>__TRENDING__</div>
    </div>
    """
    content = (
        html.replace("__STAT_M__", str(stats["tm"]))
            .replace("__STAT_D__", str(stats["td"]))
            .replace("__STAT_A__", str(stats["ta"]))
            .replace("__STAT_R__", str(stats["tr"]))
            .replace("__FEATURED__", cards_html)
            .replace("__TRENDING__", trending_html)
    )
    return page("Home", content)


@app.route("/movies")
def movies():
    genre  = request.args.get("genre", "")
    year   = request.args.get("year", "")
    rating = request.args.get("rating", "")
    sort   = request.args.get("sort", "avg_rating")
    search = request.args.get("search", "").strip()

    where, params = ["1=1"], []
    if genre:
        where.append("g.genre_name = %s"); params.append(genre)
    if year:
        where.append("m.release_year = %s"); params.append(year)
    if rating:
        where.append("m.avg_rating >= %s"); params.append(float(rating))
    if search:
        where.append("(m.title LIKE %s OR d.full_name LIKE %s)")
        params += [f"%{search}%", f"%{search}%"]

    order = {"avg_rating":"m.avg_rating DESC","release_year":"m.release_year DESC",
             "view_count":"m.view_count DESC","title":"m.title ASC"} .get(sort, "m.avg_rating DESC")

    rows = query(
        "SELECT DISTINCT m.movie_id,m.title,m.release_year,m.avg_rating,m.view_count,m.duration_min,"
        "d.full_name AS director FROM Movies m "
        "JOIN Directors d ON m.director_id=d.director_id "
        "LEFT JOIN MovieGenres mg ON m.movie_id=mg.movie_id "
        "LEFT JOIN Genres g ON mg.genre_id=g.genre_id "
        "WHERE " + " AND ".join(where) + " ORDER BY " + order, params
    )
    genres = query("SELECT genre_name FROM Genres ORDER BY genre_name")
    years  = query("SELECT DISTINCT release_year FROM Movies ORDER BY release_year DESC")

    def opt(val, label, sel):
        selected_attr = " selected" if sel == val else ""
        return f"<option value='{val}'{selected_attr}>{label}</option>"

    genre_opts  = "<option value=''>All Genres</option>" + "".join(opt(g["genre_name"], g["genre_name"], genre) for g in genres)
    year_opts   = "<option value=''>All Years</option>"  + "".join(opt(str(y["release_year"]), str(y["release_year"]), year) for y in years)
    sort_opts   = (opt("avg_rating","Top Rated",sort) + opt("release_year","Newest",sort) +
                   opt("view_count","Most Watched",sort) + opt("title","A → Z",sort))
    rating_opts = opt("","Any",rating) + opt("4.0","4.0+",rating) + opt("4.2","4.2+",rating) + opt("4.4","4.4+",rating)

    cards_html = "".join(movie_card(m) for m in rows) if rows else "<p class='empty'>No films found.</p>"

    html = """
    <div class='page-top pt-nav'>
    <h1 class='page-title'>All <span>Films</span></h1>
    <p class='page-sub'>__COUNT__ film__PLURAL__ found</p>
    </div>
    <form method='GET' action='/movies'>
    <div class='filters'>
    <div class='fg'><label>Search</label><input type='text' name='search' value='__SEARCH__' placeholder='Title or director…'></div>
    <div class='fg'><label>Genre</label><select name='genre' class='auto-sub'>__GENRES__</select></div>
    <div class='fg'><label>Year</label><select name='year' class='auto-sub'>__YEARS__</select></div>
    <div class='fg'><label>Min Rating</label><select name='rating' class='auto-sub'>__RATING__</select></div>
    <div class='fg'><label>Sort</label><select name='sort' class='auto-sub'>__SORT__</select></div>
    <div class='fg' style='justify-content:flex-end;'><button type='submit' class='btn btn-gold'>Apply</button></div>
    <div class='fg' style='justify-content:flex-end;'><a href='/movies' class='btn btn-ghost'>Reset</a></div>
    </div></form>
    <div class='section'><div class='movie-grid'>__CARDS__</div></div>
    """
    content = (
        html.replace("__COUNT__", str(len(rows)))
            .replace("__PLURAL__", "s" if len(rows) != 1 else "")
            .replace("__SEARCH__", search)
            .replace("__GENRES__", genre_opts)
            .replace("__YEARS__", year_opts)
            .replace("__RATING__", rating_opts)
            .replace("__SORT__", sort_opts)
            .replace("__CARDS__", cards_html)
    )
    return page("Movies", content)


@app.route("/movie/<int:mid>")
def movie_detail(mid):
    movie = query(
        "SELECT m.*,d.full_name AS director,d.bio AS dir_bio "
        "FROM Movies m JOIN Directors d ON m.director_id=d.director_id "
        "WHERE m.movie_id=%s", (mid,), one=True
    )
    if not movie:
        return redirect(url_for("movies"))

    genres  = query("SELECT g.genre_name FROM Genres g JOIN MovieGenres mg ON g.genre_id=mg.genre_id WHERE mg.movie_id=%s", (mid,))
    cast    = query("SELECT a.full_name,ma.character_name,ma.is_lead FROM Actors a JOIN MovieActors ma ON a.actor_id=ma.actor_id WHERE ma.movie_id=%s ORDER BY ma.is_lead DESC", (mid,))
    reviews = query("SELECT r.rating,r.comment,r.created_at,u.username,u.full_name FROM Reviews r JOIN Users u ON r.user_id=u.user_id WHERE r.movie_id=%s ORDER BY r.created_at DESC", (mid,))

    uid      = session.get("user_id")
    user_rev = query("SELECT * FROM Reviews WHERE user_id=%s AND movie_id=%s", (uid, mid), one=True) if uid else None
    in_wl    = bool(query("SELECT 1 FROM Watchlists WHERE user_id=%s AND movie_id=%s", (uid, mid), one=True)) if uid else False

    execute("UPDATE Movies SET view_count=view_count+1 WHERE movie_id=%s", (mid,))

    clean_movie_title = movie["title"].replace("'", "").replace('"', '')

    dp = tmdb_poster(movie["title"], movie.get("release_year", ""))
    if dp:
        poster_html = f"<img src='{dp}' alt='{clean_movie_title}' onerror=\"this.parentElement.innerHTML='<div class=detail-poster-ph><div class=icon>🎬</div></div>'\">"
    else:
        poster_html = f"<div class='detail-poster-ph'><div class='icon'>🎬</div><div class='pt'>{movie['title']}</div></div>"

    genre_tags = "".join(f"<a class='genre-tag' href='/movies?genre={g['genre_name']}'>{g['genre_name']}</a>" for g in genres)

    def cast_card(c):
        ph   = tmdb_person(c["full_name"])
        lead = c["is_lead"]
        if ph:
            clean_name = c["full_name"].replace("'", "").replace('"', '')
            av = f"<img src='{ph}' alt='{clean_name}' onerror=\"this.parentElement.innerHTML='&#127937;'\">"
        else:
            av = "🎭"
        role  = f"<div class='cast-role'>{c['character_name']}</div>" if c.get("character_name") else ""
        badge = "<div class='lead-badge'>★ Lead</div>" if lead else ""
        cls   = "cast-card lead" if lead else "cast-card"
        
        inner_html = """
        <div class='__CLS__'>
        <div class='cast-photo'>__AV__</div>
        <div class='cast-body'>
        <div class='cast-name'>__NAME__</div>
        __ROLE____BADGE__
        </div></div>
        """
        return (
            inner_html.replace("__CLS__", cls)
                .replace("__AV__", av)
                .replace("__NAME__", c['full_name'])
                .replace("__ROLE__", role)
                .replace("__BADGE__", badge)
        )

    cast_html = "".join(cast_card(c) for c in cast)

    reviews_list = []
    for r in reviews:
        comment_part = f"<div class='review-body'>{r['comment']}</div>" if r.get("comment") else ""
        rev_tpl = """
        <div class='review-card'>
        <div class='review-head'>
        <span class='review-user'>__USER__</span>
        <span class='review-score'>★ __RATING__ / 5</span>
        </div>
        __COMMENT__
        <div class='review-date'>__DATE__</div>
        </div>
        """
        reviews_list.append(
            rev_tpl.replace("__USER__", r['full_name'] or r['username'])
                .replace("__RATING__", str(r['rating']))
                .replace("__COMMENT__", comment_part)
                .replace("__DATE__", str(r['created_at']))
        )
    rev_html = "".join(reviews_list) or "<p class='empty'>No reviews yet. Be the first!</p>"

    if uid:
        er = user_rev["rating"] if user_rev else 0
        ec = user_rev["comment"] if user_rev else ""
        
        stars_list = []
        for i in range(1, 6):
            is_on = " on" if er >= i else ""
            char = "★" if er >= i else "☆"
            stars_list.append(f"<button type='button' class='star-btn{is_on}' data-v='{i}'>{char}</button>")
        stars_html = "".join(stars_list)

        rform_tpl = """
        <div class='rform'>
        <h3>__TXT__</h3>
        <div class='stars'>__STARS__</div>
        <input type='hidden' id='rating-val' value='__ER__'>
        <textarea id='rev-comment' class='rtext' placeholder='Share your thoughts…'>__EC__</textarea>
        <button class='btn btn-gold' onclick='submitReview(__MID__)'>__BTN__ Review</button>
        </div>
        <script>selR=__ER__;</script>
        """
        rform = (
            rform_tpl.replace("__TXT__", 'Update your review' if user_rev else 'Write a review')
                .replace("__STARS__", stars_html)
                .replace("__ER__", str(er))
                .replace("__EC__", ec or '')
                .replace("__MID__", str(mid))
                .replace("__BTN__", 'Update' if user_rev else 'Submit')
        )
    else:
        rform = "<div class='rform'><p style='color:var(--muted)'><a href='/login'>Login</a> to write a review.</p></div>"

    avg = movie.get("avg_rating") if movie.get("avg_rating") else "—"
    dur = movie.get("duration_min")

    if uid:
        wl_btn = f"<button id='wl-btn' data-in='{'1' if in_wl else '0'}' onclick='toggleWatchlist({mid})' class='btn {'btn-ghost' if in_wl else 'btn-outline'}'>{'✓ In Watchlist' if in_wl else '+ Add to Watchlist'}</button>"
    else:
        wl_btn = "<a href='/login' class='btn btn-outline'>Login to save</a>"

    synopsis_html = f"<p class='detail-syn'>{movie['synopsis']}</p>" if movie.get("synopsis") else ""
    duration_html = f" \u00b7 {dur} min" if dur else ""

    main_html = """
    <div class='detail-hero'>
    <div class='detail-poster'>__POSTER__</div>
    <div class='detail-info'>
    <div class='genre-tags'>__TAGS__</div>
    <h1 class='detail-title'>__TITLE__</h1>
    <div class='detail-meta'>__YEAR____DUR__ \u00b7 __LANG__ \u00b7 __VIEWS__ views</div>
    <div class='detail-dir'>Directed by <strong>__DIR__</strong></div>
    __SYN__
    <div style='display:flex;align-items:flex-end;gap:20px;'>
    <div>
    <div class='detail-rating-big'>__AVG__</div>
    <div class='detail-rating-lbl'>avg rating \u00b7 __REV_COUNT__ review__PLURAL__</div></div>
    </div>
    <div class='detail-actions'>__WL_BTN__</div>
    </div></div>
    """
    part1 = (
        main_html.replace("__POSTER__", poster_html)
            .replace("__TAGS__", genre_tags)
            .replace("__TITLE__", movie['title'])
            .replace("__YEAR__", str(movie['release_year']))
            .replace("__DUR__", duration_html)
            .replace("__LANG__", movie['language'])
            .replace("__VIEWS__", str(movie['view_count']))
            .replace("__DIR__", movie['director'])
            .replace("__SYN__", synopsis_html)
            .replace("__AVG__", str(avg))
            .replace("__REV_COUNT__", str(len(reviews)))
            .replace("__PLURAL__", "s" if len(reviews) != 1 else "")
            .replace("__WL_BTN__", wl_btn)
    )
    
    part2 = f"<div class='section'><div class='sec-head'><h2 class='sec-title'>Cast</h2></div><div class='cast-grid'>{cast_html}</div></div>" if cast else ""
    part3 = f"<div class='section' style='background:var(--surface);border-top:1px solid var(--border);'><div class='sec-head'><h2 class='sec-title'>Reviews</h2></div>{rform}{rev_html}</div>"
    
    part4 = ""
    if movie.get("dir_bio"):
        dir_tpl = """
        <div class='section'><div class='sec-head'><h2 class='sec-title'>About the Director</h2></div>
        <div class='person-card' style='max-width:600px;'>
        <div class='person-body'><div class='person-name'>__DNAME__</div>
        <div class='person-bio' style='-webkit-line-clamp:unset;'>__DBIO__</div></div>
        </div></div>
        """
        part4 = dir_tpl.replace("__DNAME__", movie['director']).replace("__DBIO__", movie['dir_bio'])
        
    content = part1 + part2 + part3 + part4
    return page(movie["title"], content)


@app.route("/directors")
def directors():
    rows = query("""
        SELECT d.director_id,d.full_name,d.birth_year,d.nationality,d.bio,
               COUNT(m.movie_id) AS mc,
               ROUND(AVG(m.avg_rating),1) AS ar
        FROM Directors d LEFT JOIN Movies m ON d.director_id=m.director_id
        GROUP BY d.director_id,d.full_name,d.birth_year,d.nationality,d.bio
        ORDER BY mc DESC
    """)
    cards = "".join(person_card(r, is_director=True) for r in rows)
    html = """
    <div class='page-top pt-nav'>
    <h1 class='page-title'>The <span>Directors</span></h1>
    <p class='page-sub'>Masters behind the camera</p>
    </div>
    <div class='section'><div class='person-grid'>__CARDS__</div></div>
    """
    return page("Directors", html.replace("__CARDS__", cards))


@app.route("/actors")
def actors():
    rows = query("""
        SELECT a.actor_id,a.full_name,a.birth_year,a.birth_place,a.bio,
               COUNT(ma.movie_id) AS mc
        FROM Actors a LEFT JOIN MovieActors ma ON a.actor_id=ma.actor_id
        GROUP BY a.actor_id,a.full_name,a.birth_year,a.birth_place,a.bio
        ORDER BY mc DESC
    """)
    cards = "".join(person_card(r, is_director=False) for r in rows)
    html = """
    <div class='page-top pt-nav'>
    <h1 class='page-title'>The <span>Actors</span></h1>
    <p class='page-sub'>Faces that defined an era</p>
    </div>
    <div class='section'><div class='person-grid'>__CARDS__</div></div>
    """
    return page("Actors", html.replace("__CARDS__", cards))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    uid = session["user_id"]

    stats = query("""
        SELECT COUNT(DISTINCT wh.movie_id) AS mw,
               IFNULL(SUM(wh.watch_duration_min),0) AS tot,
               ROUND(IFNULL(AVG(wh.watch_duration_min),0),0) AS avgm
        FROM WatchHistory wh WHERE wh.user_id=%s
    """, (uid,), one=True)

    history = query("""
        SELECT m.movie_id,m.title,m.release_year,wh.watched_at,wh.watch_pct,
               wh.watch_duration_min AS wmin
        FROM WatchHistory wh JOIN Movies m ON wh.movie_id=m.movie_id
        WHERE wh.user_id=%s ORDER BY wh.watched_at DESC
    """, (uid,))

    watchlist = query("""
        SELECT m.movie_id,m.title,m.release_year,m.avg_rating,m.duration_min,d.full_name AS director
        FROM Watchlists wl JOIN Movies m ON wl.movie_id=m.movie_id
        JOIN Directors d ON m.director_id=d.director_id
        WHERE wl.user_id=%s ORDER BY wl.added_at DESC
    """, (uid,))

    my_reviews = query("""
        SELECT m.movie_id,m.title,r.rating,r.comment,r.created_at
        FROM Reviews r JOIN Movies m ON r.movie_id=m.movie_id
        WHERE r.user_id=%s ORDER BY r.created_at DESC
    """, (uid,))

    recs = query("""
        SELECT m.movie_id,m.title,m.release_year,m.avg_rating,m.duration_min,
               d.full_name AS director,rc.reason
        FROM Recommendations rc
        JOIN Movies m ON rc.movie_id=m.movie_id
        JOIN Directors d ON m.director_id=d.director_id
        WHERE rc.user_id=%s ORDER BY rc.created_at DESC LIMIT 6
    """, (uid,))

    hist_list = []
    for h in history:
        tpl = """
        <div class='hist-row'>
        <div class='hist-icon'>🎬</div>
        <div>
        <a href='/movie/__MID__' class='hist-title'>__TITLE__</a>
        <div class='hist-meta'>__YEAR__ · __DATE__</div>
        </div>
        <div class='hist-pct'>__PCT__% · __MIN__ min</div>
        </div>
        """
        hist_list.append(
            tpl.replace("__MID__", str(h["movie_id"]))
               .replace("__TITLE__", h["title"])
               .replace("__YEAR__", str(h["release_year"]))
               .replace("__DATE__", str(h["watched_at"]))
               .replace("__PCT__", str(h["watch_pct"]))
               .replace("__MIN__", str(h["wmin"] or 0))
        )
    hist_html = "".join(hist_list) or "<p class='empty'>No watch history yet.</p>"

    wl_html = (f"<div class='movie-grid'>{''.join(movie_card(m) for m in watchlist)}</div>") if watchlist else "<p class='empty'>Watchlist is empty. <a href='/movies'>Browse films</a></p>"

    rev_list = []
    for r in my_reviews:
        comment_part = f"<div class='review-body'>{r['comment']}</div>" if r.get("comment") else ""
        tpl = """
        <div class='review-card'>
        <div class='review-head'>
        <a href='/movie/__MID__' class='review-user'>__TITLE__</a>
        <span class='review-score'>★ __RATING__ / 5</span>
        </div>
        __COMMENT__
        <div class='review-date'>__DATE__</div>
        </div>
        """
        rev_list.append(
            tpl.replace("__MID__", str(r["movie_id"]))
               .replace("__TITLE__", r["title"])
               .replace("__RATING__", str(r["rating"]))
               .replace("__COMMENT__", comment_part)
               .replace("__DATE__", str(r["created_at"]))
        )
    rv_html = "".join(rev_list) or "<p class='empty'>No reviews yet.</p>"

    rec_html = (f"<div class='movie-grid'>{''.join(movie_card(m) for m in recs)}</div>") if recs else "<p class='empty'>No recommendations yet.</p>"

    html = """
    <div class='page-top pt-nav'>
    <h1>Hello, <span style='color:var(--gold); font-style:italic;'>__FNAME__</span></h1>
    <p class='page-sub'>Your cinema activity</p>
    </div>
    <div class='section'>
    <div class='dash-stats'>
    <div class='dash-stat'><div class='ds-n'>__STAT_W__</div><div class='ds-l'>Films Watched</div></div>
    <div class='dash-stat'><div class='ds-n'>__STAT_T__</div><div class='ds-l'>Total Minutes</div></div>
    <div class='dash-stat'><div class='ds-n'>__STAT_A__</div><div class='ds-l'>Avg / Session</div></div>
    <div class='dash-stat'><div class='ds-n'>__REV_COUNT__</div><div class='ds-l'>Reviews</div></div>
    <div class='dash-stat'><div class='ds-n'>__WL_COUNT__</div><div class='ds-l'>Watchlist</div></div>
    </div>

    <div class='tabs'>
    <button class='tab-btn' data-t='history' onclick='switchTab("history")'>Watch History</button>
    <button class='tab-btn' data-t='watchlist' onclick='switchTab("watchlist")'>Watchlist</button>
    <button class='tab-btn' data-t='reviews' onclick='switchTab("reviews")'>My Reviews</button>
    <button class='tab-btn' data-t='recs' onclick='switchTab("recs")'>Recommendations</button>
    </div>

    <div class='tab-panel' id='tp-history'>__HIST__</div>
    <div class='tab-panel' id='tp-watchlist'>__WL__</div>
    <div class='tab-panel' id='tp-reviews'>__REV__</div>
    <div class='tab-panel' id='tp-recs'>__REC__</div>
    </div>
    """
    content = (
        html.replace("__FNAME__", session["full_name"])
            .replace("__STAT_W__", str(stats["mw"] or 0))
            .replace("__STAT_T__", str(int(stats["tot"] or 0)))
            .replace("__STAT_A__", str(int(stats["avgm"] or 0)))
            .replace("__REV_COUNT__", str(len(my_reviews)))
            .replace("__WL_COUNT__", str(len(watchlist)))
            .replace("__HIST__", hist_html)
            .replace("__WL__", wl_html)
            .replace("__REV__", rv_html)
            .replace("__REC__", rec_html)
    )
    return page("My Profile", content)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")
        row = query("SELECT * FROM Users WHERE username=%s AND password=%s", (u, p), one=True)
        if row:
            session["user_id"]   = row["user_id"]
            session["username"]  = row["username"]
            session["full_name"] = row["full_name"]
            return redirect(url_for("dashboard"))
        error = "Wrong username or password."

    err = f"<div class='auth-err'>{error}</div>" if error else ""
    html = """
    <div class='auth-wrap'><div class='auth-box'>
    <h2 class='auth-title'>Welcome back</h2>
    <p class='auth-sub'>Sign in to your account</p>
    __ERR__
    <form method='POST' action='/login'>
    <div class='fg-a'><label>Username</label><input type='text' name='username' placeholder='your_username' required></div>
    <div class='fg-a'><label>Password</label><input type='password' name='password' placeholder='••••••' required></div>
    <button type='submit' class='auth-btn'>Sign In</button>
    </form>
    <p class='auth-sw'>Don't have an account? <a href='/register'>Sign up</a></p>
    <p class='auth-hint'>Demo: <strong>oyku_a</strong> / <strong>pass123</strong></p>
    </div></div>
    """
    return page("Login", html.replace("__ERR__", err))


@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username  = request.form.get("username", "").strip()
        email     = request.form.get("email", "").strip()
        password  = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        if not all([username, email, password, full_name]):
            error = "All fields are required."
        elif query("SELECT 1 FROM Users WHERE username=%s OR email=%s", (username, email), one=True):
            error = "Username or email already taken."
        else:
            uid = execute(
                "INSERT INTO Users (username,email,password,full_name,join_date) VALUES(%s,%s,%s,%s,CURDATE())",
                (username, email, password, full_name)
            )
            execute("INSERT INTO Subscriptions (user_id,plan,start_date) VALUES(%s,'free',CURDATE())", (uid,))
            session["user_id"]   = uid
            session["username"]  = username
            session["full_name"] = full_name
            return redirect(url_for("dashboard"))

    err = f"<div class='auth-err'>{error}</div>" if error else ""
    html = """
    <div class='auth-wrap'><div class='auth-box'>
    <h2 class='auth-title'>Create account</h2>
    <p class='auth-sub'>Join Cinema Yesilcam</p>
    __ERR__
    <form method='POST' action='/register'>
    <div class='fg-a'><label>Full Name</label><input type='text' name='full_name' placeholder='Your Name' required></div>
    <div class='fg-a'><label>Username</label><input type='text' name='username' placeholder='username' required></div>
    <div class='fg-a'><label>Email</label><input type='email' name='email' placeholder='you@mail.com' required></div>
    <div class='fg-a'><label>Password</label><input type='password' name='password' placeholder='••••••' required></div>
    <button type='submit' class='auth-btn'>Create Account</button>
    </form>
    <p class='auth-sw'>Already have an account? <a href='/login'>Sign in</a></p>
    </div></div>
    """
    return page("Register", html.replace("__ERR__", err))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ──────────────────────────────────────────────────────
#  API ENDPOINTS (AJAX DELEGATES)
# ──────────────────────────────────────────────────────

@app.route("/api/review", methods=["POST"])
def api_review():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    uid     = session["user_id"]
    mid     = int(request.form.get("movie_id"))
    rating  = int(request.form.get("rating"))
    comment = request.form.get("comment", "").strip()
    if not 1 <= rating <= 5:
        return jsonify({"error": "Rating must be 1-5"}), 400
        
    ex = query("SELECT review_id FROM Reviews WHERE user_id=%s AND movie_id=%s", (uid, mid), one=True)
    if ex:
        execute("UPDATE Reviews SET rating=%s,comment=%s WHERE review_id=%s", (rating, comment, ex["review_id"]))
    else:
        next_id = query("SELECT IFNULL(MAX(review_id), 0) + 1 AS nid FROM Reviews", one=True)["nid"]
        execute("INSERT INTO Reviews(review_id,user_id,movie_id,rating,comment,created_at) VALUES(%s,%s,%s,%s,%s,CURDATE())", 
                (next_id, uid, mid, rating, comment))
                
    avg = query("SELECT ROUND(AVG(rating),1) AS a FROM Reviews WHERE movie_id=%s", (mid,), one=True)
    execute("UPDATE Movies SET avg_rating=%s WHERE movie_id=%s", (avg["a"], mid))
    return jsonify({"ok": True, "new_avg": float(avg["a"] or 0)})


@app.route("/api/watchlist/<int:mid>", methods=["POST", "DELETE"])
def api_watchlist(mid):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    uid = session["user_id"]
    if request.method == "POST":
        if not query("SELECT 1 FROM Watchlists WHERE user_id=%s AND movie_id=%s", (uid, mid), one=True):
            next_id = query("SELECT IFNULL(MAX(watchlist_id), 0) + 1 AS nid FROM Watchlists", one=True)["nid"]
            execute("INSERT INTO Watchlists(watchlist_id,user_id,movie_id,added_at) VALUES(%s,%s,%s,CURDATE())", (next_id, uid, mid))
        return jsonify({"ok": True})
        
    execute("DELETE FROM Watchlists WHERE user_id=%s AND movie_id=%s", (uid, mid))
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)