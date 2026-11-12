#!/usr/bin/env python3
"""Builds the Millennium Chambers static site into docs/ for GitHub Pages.

Content lives in content/<slug>.md (first line '# Title'); page metadata in pages.json.
Run: python3 build.py
"""
import json, os, re, html, datetime, shutil
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
DOMAIN = "https://www.millenniumchambers.in"
TODAY = datetime.date.today().isoformat()

FIRM = {
    "name": "Millennium Chambers",
    "street": "325H, Sector 38",
    "city": "Gurugram",
    "region": "Haryana",
    "pin": "122001",
    "email": "millenniumchambersindia@gmail.com",
    "phone": "+91 9217648824",
    "wa": "https://wa.me/919217648824",
    "linkedin_firm": "https://www.linkedin.com/company/millennium-chambers-gurugram",
    "linkedin_varun": "https://www.linkedin.com/in/varun-bhutani-2862b3158",
    "youtube": "https://www.youtube.com/@varunvibe003",
    "superlawyer": "https://superlawyer.in/when-courtroom-strategy-meets-startup-innovation-the-journey-of-a-legal-leader-varun-bhutani",
}

NAV = [
    ("/", "Home"),
    ("/varun-bhutani-advocate-gurugram", "Advocate Varun Bhutani"),
    ("/startup-corporate-law-practice-areas-gurugram", "Practice Areas"),
    ("/labour-codes-startups-india-guide", "Labour Codes"),
    ("/startup-insights", "Startup Insights"),
    ("/#guides", "Guides"),
]

GUIDES = [
    ("dpdp-act-compliance-startups-india", "DPDP Act compliance for startups", "Phased deadlines to May 2027, consent, user rights and penalties."),
    ("founders-agreement-startups-india", "Founders' agreements", "Equity, vesting, IP, exits and disputes between co-founders."),
    ("term-sheet-startups-india", "Term sheets", "Valuation, liquidation preference, anti-dilution and control rights."),
    ("esop-startups-india-legal-guide", "ESOPs for startups", "Rule 12, vesting, DPIIT relaxations and tax at a glance."),
    ("labour-codes-startups-india-guide", "The Labour Codes", "What changed on 21 November 2025 and what startups must do."),
    ("trademark-registration-startups-india", "Trademark registration", "Search, class, TM-A filing, examination, opposition and renewal."),
]

BCI_SHORT = ("As per Bar Council of India rules, this website is for information only and is not a "
             "solicitation or advertisement.")

def org_schema():
    return {
        "@type": ["LegalService", "Organization"],
        "@id": DOMAIN + "/#firm",
        "name": FIRM["name"],
        "url": DOMAIN + "/",
        "email": FIRM["email"],
        "telephone": FIRM["phone"],
        "description": "Gurugram-based legal practice advising founders and growing companies on corporate, commercial and regulatory matters.",
        "address": {"@type": "PostalAddress", "streetAddress": FIRM["street"], "addressLocality": FIRM["city"],
                    "addressRegion": FIRM["region"], "postalCode": FIRM["pin"], "addressCountry": "IN"},
        "areaServed": [{"@type": "City", "name": "Gurugram"}, {"@type": "Country", "name": "India"}],
        "knowsAbout": ["Startup law", "Venture capital transactions", "Commercial contracts", "DPDP Act 2023",
                       "Labour Codes", "Gig worker compliance", "Consumer protection", "Trademarks", "Commercial leasing"],
        "founder": {"@id": DOMAIN + "/varun-bhutani-advocate-gurugram#varun"},
        "sameAs": [FIRM["linkedin_firm"], FIRM["youtube"]],
    }

def person_schema():
    return {
        "@type": "Person",
        "@id": DOMAIN + "/varun-bhutani-advocate-gurugram#varun",
        "name": "Varun Bhutani",
        "jobTitle": "Advocate and Independent Partner",
        "worksFor": {"@id": DOMAIN + "/#firm"},
        "url": DOMAIN + "/varun-bhutani-advocate-gurugram",
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": "Ramaiah College of Law, Bengaluru"},
                     {"@type": "CollegeOrUniversity", "name": "National Law School of India University, Bengaluru"}],
        "address": {"@type": "PostalAddress", "addressLocality": "Gurugram", "addressRegion": "Haryana", "addressCountry": "IN"},
        "knowsAbout": ["Startup and venture capital law", "DPDP Act 2023", "Labour Codes", "Fintech and NBFC regulation",
                       "Commercial contracts", "Trademarks", "IBC and SARFAESI"],
        "sameAs": [FIRM["linkedin_varun"], FIRM["superlawyer"], FIRM["youtube"]],
    }

def esc(s):
    return html.escape(s, quote=True)

CSS_VER = "1"

def page(slug, title, description, body, h1, *, schema_extra=None, image=None, lead=None, crumbs=True, kind="page"):
    url = DOMAIN + ("/" if slug == "" else "/" + slug)
    graph = [org_schema()]
    if schema_extra:
        graph += schema_extra
    if crumbs and slug:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": h1, "item": url}]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    nav = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if (h == "/" + slug or (h == "/" and slug == "")) else ""}>{esc(t)}</a>'
        for h, t in NAV)
    og_img = image or (DOMAIN + "/assets/img/og-default.jpg")
    crumb_html = (f'<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span aria-hidden="true">/</span> '
                  f'<span>{esc(h1)}</span></nav>') if (crumbs and slug) else ""
    hero = "" if slug == "" else f"""
<header class="pagehead">
  <div class="wrap">
    {crumb_html}
    <h1>{esc(h1)}</h1>
    {f'<p class="lead">{esc(lead)}</p>' if lead else ''}
  </div>
</header>"""
    return f"""<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="{'article' if kind == 'article' else 'website'}">
<meta property="og:site_name" content="Millennium Chambers">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="en_IN">
{f'<meta property="og:image" content="{esc(og_img)}">' if og_img else ''}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1c1d1f">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={CSS_VER}">
<script type="application/ld+json">
{ld}
</script>
</head>
<body class="{'home' if slug == '' else 'inner'}">
<a class="skip" href="#main">Skip to main content</a>
<div class="bci" role="note"><div class="wrap">{esc(BCI_SHORT)} <a href="/disclaimer">Read the disclaimer</a></div></div>
<header class="site">
  <div class="wrap bar">
    <a class="brand" href="/" aria-label="Millennium Chambers home"><span class="mark" aria-hidden="true">MC</span><span>Millennium Chambers</span></a>
    <button class="menu" aria-expanded="false" aria-controls="nav" onclick="var n=document.getElementById('nav');var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)">Menu</button>
    <nav id="nav" aria-label="Main">{nav}</nav>
  </div>
</header>
{hero}
<main id="main">
{body}
</main>
<footer class="site">
  <div class="wrap cols">
    <div>
      <p class="fbrand">Millennium Chambers</p>
      <address>{FIRM['street']}, {FIRM['city']}, {FIRM['region']} {FIRM['pin']}<br>
      <a href="mailto:{FIRM['email']}">{FIRM['email']}</a><br>
      <a href="{FIRM['wa']}">WhatsApp {FIRM['phone']}</a></address>
    </div>
    <div>
      <p class="fhead">Guides for founders</p>
      <ul>{''.join(f'<li><a href="/{s}">{esc(t)}</a></li>' for s, t, _ in GUIDES)}</ul>
    </div>
    <div>
      <p class="fhead">About</p>
      <ul>
        <li><a href="/varun-bhutani-advocate-gurugram">Advocate Varun Bhutani</a></li>
        <li><a href="/startup-corporate-law-practice-areas-gurugram">Practice areas</a></li>
        <li><a href="/startup-insights">Startup Insights</a></li>
        <li><a href="{FIRM['linkedin_firm']}">LinkedIn</a> · <a href="{FIRM['youtube']}">YouTube</a></li>
        <li><a href="/disclaimer">Disclaimer</a> · <a href="/privacy-policy">Privacy</a> · <a href="/terms-of-use">Terms</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap fine">{esc(BCI_SHORT)} Nothing on this site is legal advice, and viewing it or contacting us does not create an advocate-client relationship.</div>
</footer>
</body>
</html>
"""

MD = markdown.Markdown(extensions=["extra", "sane_lists", "toc"], extension_configs={"toc": {"permalink": False}})

def render_md(text):
    MD.reset()
    out = MD.convert(text)
    # external links open normally but get rel attributes
    out = re.sub(r'<a href="(https?://(?!www\.millenniumchambers\.in)[^"]+)"', r'<a href="\1" rel="noopener"', out)
    return out

def write(slug, content):
    d = OUT if slug == "" else os.path.join(OUT, slug)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w") as f:
        f.write(content)

def first_para(text):
    for block in text.split("\n\n"):
        b = block.strip()
        if b and not b.startswith("#") and not b.startswith("-") and not b.startswith("["):
            return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", re.sub(r"\*\*", "", b))
    return ""

def build_inner(slug, meta):
    src = open(os.path.join(ROOT, "content", slug + ".md")).read().strip()
    m = re.match(r"#\s+(.+)\n", src)
    h1 = m.group(1).strip()
    body_md = src[m.end():].strip()
    img = meta.get("image")
    img_abs = (DOMAIN + img) if img and img.startswith("/") else img
    figure = ""
    if img:
        cls = "portrait" if meta.get("type") == "person" else "wide"
        figure = (f'<figure class="{cls}"><img src="{esc(img)}" alt="{esc(meta.get("image_alt", h1))}" '
                  f'loading="eager" referrerpolicy="no-referrer"></figure>')
    article = render_md(body_md)
    extra = []
    kind = meta.get("type", "page")
    if kind == "article":
        extra.append({"@type": "Article", "headline": h1, "description": meta["description"],
                      "author": {"@id": DOMAIN + "/varun-bhutani-advocate-gurugram#varun"},
                      "publisher": {"@id": DOMAIN + "/#firm"}, "dateModified": TODAY, "inLanguage": "en-IN",
                      "mainEntityOfPage": DOMAIN + "/" + slug, **({"image": img_abs} if img else {})})
        extra.append(person_schema())
    if kind == "person":
        p = person_schema()
        if img:
            p["image"] = img_abs
        extra.append(p)
        extra.append({"@type": "ProfilePage", "mainEntity": {"@id": p["@id"]}, "url": DOMAIN + "/" + slug})
    byline = ""
    if kind == "article":
        byline = (f'<p class="byline">By <a href="/varun-bhutani-advocate-gurugram">Varun Bhutani, Advocate</a> · '
                  f'Millennium Chambers, Gurugram · Updated <time datetime="{TODAY}">'
                  f'{datetime.date.today().strftime("%-d %B %Y")}</time></p>')
    related = ""
    if kind == "article":
        items = "".join(f'<li><a href="/{s}"><strong>{esc(t)}</strong><span>{esc(d)}</span></a></li>'
                        for s, t, d in GUIDES if s != slug)
        related = f'<aside class="related" aria-labelledby="rel"><h2 id="rel">More guides for founders</h2><ul class="cards">{items}</ul></aside>'
    note = ('<p class="note">This page is general information only, not legal advice, and is not a solicitation '
            'or advertisement under the Bar Council of India Rules.</p>') if kind in ("article", "person") else ""
    body = f"""<div class="wrap content-grid">
<article class="prose">
{byline}
{figure}
{article}
{note}
</article>
<aside class="side" aria-label="Contact Millennium Chambers">
  <div class="sidecard">
    <p class="fhead">Millennium Chambers</p>
    <p>{FIRM['street']}, {FIRM['city']}, {FIRM['region']} {FIRM['pin']}</p>
    <p><a href="mailto:{FIRM['email']}">{FIRM['email']}</a><br><a href="{FIRM['wa']}">WhatsApp {FIRM['phone']}</a></p>
    <p class="note">Information only. Not a solicitation or legal advice.</p>
  </div>
  <div class="sidecard light">
    <p class="fhead">Guides for founders</p>
    <ul>{''.join(f'<li><a href="/{s}">{esc(t)}</a></li>' for s, t, _ in GUIDES if s != slug)}</ul>
  </div>
</aside>
</div>
{f'<div class="wrap">{related}</div>' if related else ''}"""
    html_out = page(slug, meta["title"], meta["description"], body, h1, schema_extra=extra, image=img_abs, kind=kind)
    write(slug, html_out)
    return h1

def build_home():
    title = "Millennium Chambers | Startup & Corporate Lawyers in Gurugram"
    desc = ("Millennium Chambers is a Gurugram-based legal practice advising Indian founders and growing companies on "
            "corporate, commercial and regulatory matters: fundraising, contracts, DPDP, Labour Codes and disputes.")
    areas = [
        ("Startups & venture capital", "Incorporation, founder and shareholder agreements, ESOPs, term sheets, investment documentation and post-closing compliance."),
        ("Commercial contracts", "Vendor, customer, SaaS, payment-gateway, franchise and partnership agreements."),
        ("Labour & gig workforce", "The four Labour Codes, gig and platform-worker compliance, employment policies."),
        ("Data protection & technology", "DPDP Act, 2023 compliance, privacy policies and platform terms."),
        ("Consumer protection", "Consumer notices, complaints and e-commerce compliance."),
        ("Intellectual property", 'Trademark filing, prosecution and opposition.'),
        ("Real estate & leasing", "Commercial leases and leave-and-licence agreements."),
        ("Notices & disputes", "Legal notices, recovery and arbitration support."),
    ]
    area_html = "".join(f"<li><h3>{esc(a)}</h3><p>{esc(b)}</p></li>" for a, b in areas)
    guides = "".join(f'<li><a href="/{s}"><strong>{esc(t)}</strong><span>{esc(d)}</span></a></li>' for s, t, d in GUIDES)
    videos = [("r7C3XZ8Vo5Y", "Telecom Regulatory Sandbox Rules, 2026: what startups should know"),
              ("MrQHZOz9YGk", "NCLAT on share-purchase money and Section 5(8) IBC")]
    vid_html = "".join(
        f'<li><a class="video" href="https://www.youtube.com/watch?v={v}" rel="noopener">'
        f'<img src="https://i.ytimg.com/vi/{v}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">'
        f'<span class="play" aria-hidden="true"></span><strong>{esc(t)}</strong></a></li>' for v, t in videos)
    faq = [
        ("Where is Millennium Chambers located?", "Millennium Chambers is at 325H, Sector 38, Gurugram, Haryana 122001, and works with founders and companies across India."),
        ("What kind of matters does Millennium Chambers handle?", "Corporate, commercial and regulatory work for startups and growing companies: incorporation and fundraising documents, commercial contracts, DPDP Act and Labour Code compliance, consumer protection, trademarks, commercial leases, legal notices and arbitration support."),
        ("Who leads Millennium Chambers?", "Advocate Varun Bhutani, enrolled with the Bar Council of Delhi since December 2018, is the Independent Partner. He has worked in-house with technology and consumer companies, most recently as Head of Legal at YesMadam."),
        ("When do the main DPDP Act obligations apply?", "Under the DPDP Rules, 2025, consent manager rules apply from 13 November 2026 and the core obligations for data fiduciaries apply from 13 May 2027."),
    ]
    faq_html = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faq)
    faq_schema = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    body = f"""
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Gurugram · Corporate, commercial &amp; regulatory law</p>
    <h1>Legal counsel for India's startups</h1>
    <p class="lead">Millennium Chambers is a Gurugram-based legal practice advising founders and growing companies on corporate, commercial and regulatory matters, from incorporation and fundraising to contracts, compliance and disputes.</p>
    <p class="cta"><a class="btn" href="/startup-corporate-law-practice-areas-gurugram">Practice areas</a> <a class="btn ghost" href="#guides">Guides for founders</a></p>
  </div>
</section>

<section class="band" aria-labelledby="pa">
  <div class="wrap">
    <h2 id="pa">Practice areas</h2>
    <ul class="areas">{area_html}</ul>
    <p><a class="more" href="/startup-corporate-law-practice-areas-gurugram">Practice areas in detail</a></p>
  </div>
</section>

<section class="band guides-band" id="guides" aria-labelledby="gd">
  <div class="wrap">
    <h2 id="gd">Guides for founders</h2>
    <p class="sub">Plain-English notes on the legal questions Indian startups ask most. General information only.</p>
    <ul class="cards">{guides}</ul>
  </div>
</section>

<section class="band" aria-labelledby="brief">
  <div class="wrap two">
    <div>
      <h2 id="brief">Startup Legal Brief: the DPDP countdown</h2>
      <p class="date">29 October 2026</p>
      <p>The Digital Personal Data Protection Rules, 2025 were notified on 13 November 2025 and are coming into force in phases. Rules on the Data Protection Board applied immediately. Rule 4 on the registration and obligations of Consent Managers applies from 13 November 2026. The core obligations (notice and consent, reasonable security safeguards, breach intimation, data retention, verifiable parental consent for children's data, data principal rights, Significant Data Fiduciary duties and cross-border transfers) apply from 13 May 2027.</p>
      <p>Points startups commonly review before May 2027: a map of what personal data is collected and why; consent notices in clear language; security safeguards and a breach-response plan; retention and deletion schedules; processes for handling access, correction and erasure requests; age-gating where children may use the product; and data-processing terms with vendors. Penalties under the DPDP Act can go up to Rs 250 crore for a failure to take reasonable security safeguards.</p>
      <p class="note">This note is general information only and is not legal advice. <a href="/dpdp-act-compliance-startups-india">Read the full DPDP guide</a> · <a href="/startup-insights">Weekly Startup Insights</a></p>
    </div>
    <div>
      <h2>Explainers</h2>
      <ul class="videos">{vid_html}</ul>
    </div>
  </div>
</section>

<section class="band contact-band" aria-labelledby="ab">
  <div class="wrap two">
    <div>
      <h2 id="ab">About</h2>
      <p><strong>Varun Bhutani, Independent Partner.</strong> BA LLB, Ramaiah College of Law, Bengaluru (2018). Nearly eight years in legal practice, most of them in-house with technology and consumer businesses, most recently as Head of Legal at YesMadam, and earlier with Zypp Electric, Ecom Express and OfBusiness/Oxyzo, after beginning in litigation practice before the Delhi High Court. Guest lecturer at law schools in the NCR.</p>
      <p><a class="more" href="/varun-bhutani-advocate-gurugram">Full profile of Advocate Varun Bhutani</a></p>
      <h3>Internships</h3>
      <p>We take a small number of recent law graduates (not current students) for internships focused on legal research and regulatory compliance for startups (no litigation work). To apply, email your CV and a short note on your areas of interest to <a href="mailto:{FIRM['email']}">{FIRM['email']}</a> with the subject "Internship Application".</p>
    </div>
    <div id="contact">
      <h2>Contact</h2>
      <address class="contact">
        {FIRM['street']}, {FIRM['city']}, {FIRM['region']} {FIRM['pin']}<br>
        Email: <a href="mailto:{FIRM['email']}">{FIRM['email']}</a><br>
        WhatsApp: <a href="{FIRM['wa']}">{FIRM['phone']}</a><br>
        <a href="{FIRM['linkedin_firm']}">LinkedIn: Millennium Chambers</a><br>
        <a href="{FIRM['youtube']}">YouTube: startup law explainers</a>
      </address>
      <p class="note">Under the rules of the Bar Council of India, advocates are not permitted to solicit work or advertise. This website is for general information only and does not constitute solicitation, advertisement or legal advice. By using it, you acknowledge that you are seeking information about Millennium Chambers of your own accord and that no advocate-client relationship is created by viewing this website or contacting us through it.</p>
    </div>
  </div>
</section>

<section class="band" aria-labelledby="fq">
  <div class="wrap narrow">
    <h2 id="fq">Common questions</h2>
    {faq_html}
  </div>
</section>
"""
    write("", page("", title, desc, body, "Home", schema_extra=[person_schema(), faq_schema,
                   {"@type": "WebSite", "@id": DOMAIN + "/#site", "url": DOMAIN + "/", "name": "Millennium Chambers",
                    "publisher": {"@id": DOMAIN + "/#firm"}, "inLanguage": "en-IN"}], crumbs=False))
    return title, desc

def build_extras(pages, titles):
    urls = [("", "1.0")] + [(s, "0.8" if m.get("type") in ("article", "person") else "0.5") for s, m in pages.items()]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for s, pr in urls:
        sm.append(f"  <url><loc>{DOMAIN}/{s}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    lines = ["# Millennium Chambers", "",
             "> Gurugram-based legal practice (325H, Sector 38, Gurugram, Haryana 122001) advising Indian founders and growing "
             "companies on corporate, commercial and regulatory law. Led by Advocate Varun Bhutani (Bar Council of Delhi, 2018). "
             "Website content is general information only, not legal advice or solicitation (Bar Council of India rules).", "",
             "## Key pages", ""]
    for s, m in pages.items():
        lines.append(f"- [{titles[s]}]({DOMAIN}/{s}): {m['description']}")
    lines += ["", "## Contact", "", f"- Email: {FIRM['email']}", f"- WhatsApp: {FIRM['phone']}"]
    open(os.path.join(OUT, "llms.txt"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    # /home on the old Google Site -> redirect to /
    os.makedirs(os.path.join(OUT, "home"), exist_ok=True)
    open(os.path.join(OUT, "home", "index.html"), "w").write(
        f'<!doctype html><meta charset="utf-8"><title>Millennium Chambers</title><link rel="canonical" href="{DOMAIN}/">'
        f'<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=/"><a href="/">Continue to Millennium Chambers</a>')
    nf = page("404", "Page not found | Millennium Chambers", "This page could not be found.",
              '<div class="wrap prose"><p>The page you were looking for has moved or does not exist. '
              'Try the <a href="/">home page</a>, our <a href="/#guides">guides for founders</a> or '
              '<a href="/startup-insights">Startup Insights</a>.</p></div>', "Page not found", crumbs=False)
    nf = nf.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">')
    open(os.path.join(OUT, "404.html"), "w").write(nf)

def main():
    pages = json.load(open(os.path.join(ROOT, "pages.json")))
    for item in os.listdir(OUT):
        if item in ("assets", "CNAME"):
            continue
        p = os.path.join(OUT, item)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    titles = {}
    for slug, meta in pages.items():
        titles[slug] = build_inner(slug, meta)
    build_home()
    build_extras(pages, titles)
    print("built", len(pages) + 1, "pages")

if __name__ == "__main__":
    main()
