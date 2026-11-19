"""Pre-launch Solana hub pages: /learn/, /for-teams/, Solana legal stubs.

Replaces retired solar SPA routes with Solana-focused content.
"""
from __future__ import annotations

import html
import json
import os
from pathlib import Path

E = html.escape


def _page(body: str, title: str, desc: str, path: str, css: str = '') -> str:
  return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="https://sol.college{path}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="https://sol.college{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Sol.College">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="stylesheet" href="/assets/landing.css">
{css}
</head>
<body class="prelaunch-page">
<header class="site-header">
  <a class="brand" href="/">Sol.College</a>
  <nav aria-label="Primary">
    <a href="/learn/">Learn</a>
    <a href="/lessons/path/">Learning path</a>
    <a href="/lessons/">Lessons</a>
    <a href="/for-teams/">For teams</a>
  </nav>
</header>
<main id="main" class="band">
  <div class="inner">
{body}
  </div>
</main>
<footer class="site-footer">
  <p>Sol.College complements official Solana documentation with application-focused practice. It is not operated, endorsed or accredited by the Solana Foundation.</p>
  <p><a href="/">Home</a> · <a href="/learn/">Learn</a> · <a href="/lessons/">Lessons</a> · <a href="/legal/terms/">Terms</a> · <a href="/legal/privacy/">Privacy</a></p>
</footer>
</body>
</html>
'''


def learn_hub_html(counts: dict | None = None) -> str:
  c = counts or {}
  guided = c.get('guided_lessons')
  challenges = c.get('debug_challenges')
  path_n = c.get('core_path_lessons')
  guided_line = (
    f'<p>This catalogue currently lists <b>{guided}</b> published guided lessons'
    + (f' and <b>{challenges}</b> debug challenges' if challenges is not None else '')
    + '. Counts are generated from the curriculum registry.</p>'
    if guided is not None else
    '<p>Lesson counts are generated from the curriculum registry on each build.</p>'
  )
  path_line = (
    f'<p>The core staged path currently contains <b>{path_n}</b> guided lessons.</p>'
    if path_n is not None else ''
  )
  body = f'''
    <p class="eyebrow">Learning hub</p>
    <h1>Learn Solana through application practice</h1>
    <p class="lead">Start with the foundations, then connect them to application behaviour. Choose a guided path or explore individual lessons according to your experience.</p>
    {guided_line}

    <section id="start-here">
      <h2>Start here</h2>
      <p><b>Intended audience.</b> Developers who want to understand Solana by inspecting application code, reproducing behaviour and explaining results.</p>
      <p><b>Prerequisites.</b> Comfort reading TypeScript or Rust helps for application labs. Foundations assume no prior Solana experience.</p>
      <p><b>What the exercises involve.</b> Guided walkthroughs, controlled debugging challenges and reviewable engineering tasks. Not every lesson uses every step of the full journey.</p>
      <p><b>Required tools.</b> A modern browser. A Devnet practice wallet only when a lesson asks you to send a transaction. Observation mode is available without a wallet.</p>
      <p><b>Wallet and network boundaries.</b> Practice applies only to the environment identified on each lesson page. Do not use wallets that hold valuable assets. A Devnet label does not remove every risk associated with downloads, dependencies, browser connections or signing requests.</p>
      <p><b>Official documentation.</b> Consult <a href="https://solana.com/docs" rel="noopener">Solana docs</a> for protocol reference. Sol.College complements that material with application-focused practice.</p>
    </section>

    <section id="learning-path">
      <h2>Follow the learning path</h2>
      <p>The ordered sequence lists stage, prerequisites, objective, estimated duration, required environment and expected output for each published entry.</p>
      {path_line}
      <p class="cta-row"><a class="btn" href="/lessons/path/">Explore the learning path</a>
      <a class="btn ghost" href="/lessons/">Browse lessons</a></p>
    </section>

    <section id="debugging">
      <h2>Practise debugging</h2>
      <p>A guided walkthrough shows a recorded flow. A debug challenge presents a scoped investigation with a task and rubric. Challenges are labelled separately and are not required to complete the core path.</p>
      <p><a href="/lessons/#challenges">Open the debug laboratory</a></p>
    </section>

    <section id="terminology">
      <h2>Understand the terminology</h2>
      <p><a href="/lessons/glossary/">Glossary</a> · <a href="/library/">Library and official references</a></p>
    </section>

    <section id="environment">
      <h2>Prepare your environment</h2>
      <p>Configuration is lesson-specific. Read each lesson’s required tools, network, program identifiers and known limitations before sending transactions. Shared mutable state on Devnet can change after a recorded verification date.</p>
    </section>
'''
  return _page(
    body,
    'Learn Solana through application practice | Sol.College',
    'Start with foundations, follow the learning path, or explore guided Solana lessons and debug challenges.',
    '/learn/',
  )


def for_teams_html(project_url: str) -> str:
  body = f'''
    <p class="eyebrow">For teams</p>
    <h1>Explore application-focused Solana learning for your team</h1>
    <p class="lead">Sol.College is preparing guided learning experiences built around application code, controlled debugging and reviewable engineering tasks.</p>
    <p>We are inviting expressions of interest from teams and institutions that want to discuss a suitable pilot.</p>

    <h2>Proposed discussion areas</h2>
    <ul>
      <li>Audience and prerequisites</li>
      <li>Learning objectives</li>
      <li>Lesson selection</li>
      <li>Environment requirements</li>
      <li>Instructor or reviewer involvement</li>
      <li>Expected outputs</li>
      <li>Progress reporting</li>
      <li>Privacy and access requirements</li>
    </ul>

    <p class="cta-row"><a class="btn" href="{E(project_url)}">Discuss a pilot</a>
    <a class="btn ghost" href="/learn/">Explore the learning hub</a></p>
    <p class="honest">Programme scope, availability and delivery arrangements are agreed individually. Submitting an enquiry does not constitute enrolment or an accepted partnership.</p>
'''
  return _page(
    body,
    'Sol.College for Teams — Explore a Solana Learning Pilot',
    'Discuss an application-focused Solana learning pilot for your team. Enquiry is not enrolment.',
    '/for-teams/',
  )


def legal_html(kind: str) -> str:
  if kind == 'terms':
    title = 'Terms of use | Sol.College'
    h1 = 'Terms of use'
    body = '''
    <h1>Terms of use</h1>
    <p class="lead">Sol.College provides educational material about Solana application practice. Content is offered as-is for learning purposes.</p>
    <p>Practice environments are independent forks on Devnet unless a page states otherwise. Using this site does not create a student enrolment, accreditation or employment relationship.</p>
    <p>Do not submit recovery phrases or private keys. Do not use wallets that hold valuable assets for practice exercises.</p>
    <p>Sol.College is not operated, endorsed or accredited by the Solana Foundation unless a documented relationship authorises that statement.</p>
'''
  else:
    title = 'Privacy | Sol.College'
    h1 = 'Privacy'
    body = '''
    <h1>Privacy</h1>
    <p class="lead">Lesson progress saved in your browser stays on your device unless you export it.</p>
    <p>Launch-interest and pilot enquiries use GitHub issue templates on the public Sol.College repository. Do not include secrets in those issues.</p>
    <p>Server logs for the static site host may retain standard request metadata according to that host’s policy.</p>
'''
  return _page(body, title, f'{h1} for Sol.College, a Solana learning platform.', f'/legal/{kind}/')


def write_prelaunch_pages(site_dir: str, counts: dict | None = None, project_url: str = '') -> list[str]:
  root = Path(site_dir)
  project = project_url or (
    'https://github.com/Blockchains/sol-college/issues/new?template=project-partnership.yml'
  )
  written = []
  pages = {
    'learn/index.html': learn_hub_html(counts),
    'for-teams/index.html': for_teams_html(project),
    'legal/terms/index.html': legal_html('terms'),
    'legal/privacy/index.html': legal_html('privacy'),
  }
  for rel, html_out in pages.items():
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_out, encoding='utf-8')
    written.append('/' + rel.replace('index.html', ''))
  return written


if __name__ == '__main__':
  site = os.environ.get('SITE_OUT', 'site')
  print(write_prelaunch_pages(site))
