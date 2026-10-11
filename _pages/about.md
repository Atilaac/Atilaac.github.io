---
permalink: /
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

<section class="hero">
  <div class="hero__text">
    <p class="hero__eyebrow">Computational materials scientist · BAM, Berlin</p>
    <h1 class="hero__title">I use atomistic simulations to understand how glasses form, deform, and fail.</h1>
    <p class="hero__lead">I am Dr. Achraf Atila. I work at the Bundesanstalt für Materialforschung und -prüfung (BAM) in Berlin on atomistic simulations of inorganic glasses. My research sits at the intersection of materials science and physics: I am strongly interested in the relationship between composition and physical properties of glasses, from the atomic scale up to macroscopic properties, and in building the simulation workflows that make that science possible.</p>
    <div class="hero__actions">
      <a class="btn btn--primary" href="/cv/"><i class="fas fa-file-lines" aria-hidden="true"></i> CV</a>
      <a class="btn btn--inverse" href="{{ site.author.googlescholar }}"><i class="ai ai-google-scholar" aria-hidden="true"></i> Google Scholar</a>
      <a class="btn btn--inverse" href="mailto:{{ site.author.email }}"><i class="fas fa-envelope" aria-hidden="true"></i> Email</a>
    </div>
  </div>
  <div class="hero__visual">{% include hero-network.svg %}</div>
</section>

<div class="research-tags">
  <span class="tag">Amorphous materials</span>
  <span class="tag">Molecular dynamics</span>
  <span class="tag">Glass science</span>
  <span class="tag">Structural analysis</span>
  <span class="tag">Fracture mechanics</span>
  <span class="tag">Open-source workflows</span>
</div>

## News

<ul class="news-list">
{% for item in site.data.news limit: 6 %}<li class="news-list__item"><time class="news-list__date" datetime="{{ item.date | date_to_xmlschema }}">{{ item.date | date: "%b %Y" }}</time><span class="news-list__text">{% if item.url %}<a href="{{ item.url }}">{{ item.text }}</a>{% else %}{{ item.text }}{% endif %}</span></li>
{% endfor %}</ul>

## Selected Publications

{% assign featured_pubs = site.publications | where_exp: "pub", "pub.featured" | sort: "featured" %}
<div class="featured-pubs">
{% for post in featured_pubs %}<a class="featured-pub" href="{{ post.url }}"><span class="featured-pub__venue">{% if post.venue == "Submitted" %}Under review{% else %}<i>{{ post.venue }}</i>{% endif %} · {{ post.date | date: "%Y" }}</span><span class="featured-pub__title">{{ post.title }}</span></a>
{% endfor %}</div>

All papers, preprints and citation metrics are on the [Publications](/publications/) page.


## Open-Source Software

<div class="software-cards">
{% for post in site.portfolio %}{% include software-card.html %}{% endfor %}
</div>

More details on the [Software](/portfolio/) page. You can also browse my [GitHub](https://github.com/Atilaac) and [Google Scholar](https://scholar.google.com/citations?user=TTAujLUAAAAJ&hl=en) profiles.

## In the Press

Our recent paper in [Physical Review Letters](https://journals.aps.org/prl/abstract/10.1103/1plj-7p4z) on the slipperiness of ice attracted broad media coverage:

<div class="news-cards">
  <a class="news-card" href="https://www.quantamagazine.org/why-is-ice-slippery-a-new-hypothesis-slides-into-the-chat-20251208" target="_blank">
    <span class="news-card__source">Quanta Magazine</span>
    <span class="news-card__headline">Why Is Ice Slippery? A New Hypothesis Slides Into the Chat.</span>
  </a>
  <a class="news-card" href="https://phys.org/news/2025-09-ice-physicists-centuries-assumptions.html" target="_blank">
    <span class="news-card__source">Phys.org</span>
    <span class="news-card__headline">Why we slip on ice: Physicists challenge centuries-old assumptions</span>
  </a>
  <a class="news-card" href="https://interestingengineering.com/science/why-ice-is-slippery" target="_blank">
    <span class="news-card__source">Interesting Engineering</span>
    <span class="news-card__headline">Scientists rewrite physics by debunking 200-year-old theory on why ice is slippery</span>
  </a>
  <a class="news-card" href="https://www.uni-saarland.de/aktuell/eis-oberflaeche-rutschen-schmelzen-39295.html" target="_blank">
    <span class="news-card__source">Universität des Saarlandes</span>
    <span class="news-card__headline">Warum wir auf Eis ausrutschen: Forscher stellen neues Paradigma über das Schmelzen von Eis auf</span>
  </a>
</div>
