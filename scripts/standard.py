"""The Degen Standard: the student newspaper of Sol.College.

This release is the charter, the policies, one editorial, and an assignment board.
It is not a news edition. No story has been reported. No student is named.
"""
import html, json, os, re, urllib.parse
PUBLISHED = '2026-11-17'
SITE = 'https://sol.college'
ISSUE = 'https://github.com/Blockchains/sol-college/issues/new'

def E(s):
  return html.escape(str(s if s is not None else ''), quote=True)

def issue(title, body):
  return ISSUE + '?title=' + urllib.parse.quote(title) + '&body=' + urllib.parse.quote(body)

LETTER = issue('Letter to The Degen Standard',
  'Your letter:\n\nThis issue is public. Do not include private keys, recovery phrases, or anything you need kept private. A letter is edited before it is published. Sending one does not mean it will be published.\n')
TIP = issue('Tip for The Degen Standard',
  'What you want the paper to know:\n\nThis issue is public. It is not a confidential tip line. Do not include private keys, recovery phrases, unpublished vulnerability details, or anything that has to stay private. If it cannot be public, do not send it.\n')
CORRECTION = issue('Correction for The Degen Standard',
  'Page:\n\nWhat is wrong:\n\nWhat the source says:\n\n')
COMPLAINT = issue('Complaint about Sol.College coverage',
  'What the paper, or the college, got wrong:\n\nThis issue is public. The publisher can edit any page that results. There is no separate editor who can overrule Sol.College.\n')

DESKS = [
 dict(id='chain-watch', nav='News', title='Chain Watch',
  question='Explain a technical dispute without turning it into a team chant.',
  standard='The paper does not diagnose a protocol incident from a screenshot. A technical claim needs a technical read.',
  beats=['Reliability disputes.', 'Transaction failures and congestion.', 'Execution and ordering.', 'MEV and market structure.', 'Wallet incidents.', 'Application failures.', 'The gap between a benchmark and what a user hits.']),
 dict(id='money', nav='Money', title='Money and markets',
  question='What is the user being encouraged to do, and who gets paid when they do it?',
  standard='Which coin will pump is not a beat.',
  beats=['Memecoin launches and trading culture.', 'Perpetual futures and leverage.', 'Liquidations and execution.', 'Fees, rebates, incentives, and referrals.', 'Token distribution and insider access.', 'Liquidity and the conditions for getting out.', 'How a trading interface is designed.']),
 dict(id='power', nav='Power', title='Power and politics',
  question='Who can make a decision, whose interests are represented, and who has no meaningful voice?',
  standard='Decentralisation is something to investigate. It is not a slogan to repeat.',
  beats=['Validator and infrastructure influence.', 'Governance participation.', 'Foundation and ecosystem funding.', 'Protocol-change debates.', 'Access to distribution and to developer support.', 'Moderation and platform power.', 'Regulatory arguments, and what they change in practice.']),
 dict(id='culture', nav='Culture', title='Internet culture',
  question='What does this culture reward, and what does that do to the people inside it?',
  standard='The ecosystem is a community of people, not a price.',
  beats=['Memes and identity.', 'Influencers and reputation.', 'Community feuds.', 'Status and the performance of wealth.', 'Collectibles and fandom.', 'Burnout.', 'Where a joke ends and a financial promotion begins.']),
 dict(id='campus', nav='Campus', title='Campus',
  question='What is happening to students when the market is quiet?',
  standard='A campus item has to be a real event, a real opportunity, or a real complaint. A fictional student is not a source.',
  beats=['Student projects and demonstrations.', 'Clubs, competitions, and hackathons.', 'What the learning was actually like.', 'Internships and contributor openings.', 'Accessibility and inclusion.', 'College decisions.', 'Complaints about lessons, facilities, or policies.', 'Student elections, if a representative structure is created.']),
 dict(id='opinion', nav='Opinion', title='Opinion and debate',
  question='What is the argument, and what would count against it?',
  standard='A piece is selected for substance. Outrage is not a desk.',
  beats=['Are memecoins an onboarding tool or a reputational liability?', 'Should a college teach leveraged trading?', 'When should a project subsidise its users?', 'What should decentralised mean in practice?', 'Can an ecosystem criticise itself without handing ammunition to rivals?']),
 dict(id='investigations', nav='Investigations', title='Investigations',
  question='What can documents, interviews, and a reproducible check establish?',
  standard='An investigation starts from a question. It does not start from a verdict.',
  beats=['Undisclosed promotions.', 'How grants are allocated.', 'Activity metrics that do not match their definition.', 'Conflicts in a ranking or an award.', 'A public claim that the accessible evidence does not support.', 'Students asked to work without pay.', 'A sponsor leaning on the college.']),
]

FEATURES = [
 ('The Fine Print', 'One fee schedule, promotion, incentive, or product term, read closely.'),
 ('Who Gets Paid?', 'The parties who earn money from one transaction or one behaviour.'),
 ('Claim Check', 'A public claim set next to the evidence that is actually available.'),
 ('Chain of Events', 'An incident reconstructed in time order.'),
 ('The Other Side', 'A serious response from someone who disagrees.'),
 ('Office Hours', 'Students ask uncomfortable, useful questions.'),
 ('Campus Dispatch', 'Projects, opportunities, meetings, and student concerns.'),
 ('Letters to the Standard', 'Reader correspondence, edited before it is published.'),
 ('Corrections Desk', 'A correction, in public, with the explanation.'),
 ('Exit Liquidity', 'Satire and cartoons. The label has to be unmistakable, especially when the joke resembles an allegation.'),
]

ASSIGNMENTS = [
 ('Your Trade Has More Than One Customer', 'Map who is paid along one defined trading journey.'),
 ('The Leverage Slider Is a Design Decision', 'Read selected interfaces. Interview designers and people who work on risk. No one has been interviewed.'),
 ('A Million Wallets Is Not a Million People', 'Ask how a published activity metric is defined. The headline is the assignment. It is not a finding.'),
 ('The Influencer Said “Not Financial Advice.” What Else Did They Disclose?', 'Review one defined sample with criteria written down first, and ask the people involved to respond. No sample has been chosen.'),
 ('Who Gets a Grant—and Who Gets an Explanation?', 'Read one named programme’s public process and interview applicants. No programme has been named.'),
 ('Students Built It. Who Owns It?', 'Read the contribution terms the college proposes or already uses. This is not a claim that a student was exploited.'),
 ('We Tried to Follow the Fees', 'Rebuild the disclosed costs of one bounded workflow. The walk has not been done.'),
 ('The Case for Memecoins', 'A commissioned opinion, with disclosures. It has not been commissioned and it has not been written.'),
 ('The Case Against Memecoins', 'A counterargument commissioned separately from the case for. It has not been commissioned and it has not been written.'),
 ('What Sol.College Should Publish About Itself', 'An editorial asking the publisher for transparency. The founding editorial does not answer this assignment.'),
]

def desks_nav():
  return ''.join(f'<a href="/standard/desks/#{d["id"]}">{E(d["nav"])}</a>' for d in DESKS)

def mast(home):
  name = '<h1>The Degen Standard</h1>' if home else '<p class=papername><a href="/standard/">The Degen Standard</a></p>'
  return f'''<header class=mast>
<p class=dateline>Founding package · 17 Nov 2026 · Not a news edition</p>
{name}
<p class=motto>Question the chain.</p>
<nav class=desknav aria-label=Desks>{desks_nav()}</nav>
</header>'''

def foot():
  return f'''<nav class=paperfoot aria-label=Paper>
<a href="/standard/letters/">Letters</a>
<a href="/standard/corrections/">Corrections</a>
<a href="/standard/tips/">Send a tip</a>
<a href="/standard/assignments/">Assignments</a>
<a href="/standard/charter/">Charter</a>
<a href="/standard/policies/">Policies</a>
<a href="/standard/templates/">Templates</a>
</nav>
<p class=colophon>Reading is free. There is no subscription, no payment, and no fund. Prepared with automated assistance and published by Sol.College on 17 Nov 2026. No page in this release reports an interview, a quote, a site visit, or an observation.</p>'''

def crumbs(here):
  return f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/standard/">The Degen Standard</a> / <span>{E(here)}</span></nav>'

def box(title, text):
  return f'<aside class=box><p class=label>{E(title)}</p><p>{text}</p></aside>'

NOTE = box('What this package contains',
  'The charter, the policies, the founding editorial, the desk descriptions, and an assignment board. No report has been published. No student editor is named. Editorial independence is not established. Sol.College is the publisher and the only party who can change these pages.')

def home_page():
  items = [
    ('/standard/editorial/the-chain-needs-a-student-paper/', 'The Chain Needs a Student Paper', 'Editorial. A statement of intent, not a report.'),
    ('/standard/charter/', 'Editorial charter', 'What the paper is for, and what it refuses to pretend.'),
    ('/standard/policies/', 'Policies', 'Interests, trading, reporting, promotion, students, and disputes.'),
    ('/standard/desks/', 'The seven desks', 'Beats and questions. No story is filed.'),
    ('/standard/assignments/', 'Assignment board', 'Ten commissions and a cover question. Not reported.'),
    ('/standard/templates/', 'Templates', 'How a report, an opinion, an investigation, and a satire are labelled.'),
    ('/standard/noticeboard/', 'Campus noticeboard', 'No event is posted.'),
    ('/standard/letters/', 'Letters', 'How to send one. None has been published.'),
    ('/standard/corrections/', 'Corrections', 'The log. No correction has been issued.'),
    ('/standard/tips/', 'Tips', 'A public issue. Not a confidential line.'),
  ]
  listing = ''.join(
    f'<li data-paper="{E(title + " " + kind)}"><a href="{href}">{E(title)}</a> <span class=kind>{E(kind)}</span></li>'
    for href, title, kind in items)
  assigns = ''.join(
    f'<li data-paper="{E(title + " assignment")}"><span class=kind>Assignment · not reported</span> {E(title)}</li>'
    for title, _why in ASSIGNMENTS)
  return f'''<article class=tds>
{mast(True)}
{NOTE}
<form class=papersearch role=search>
<label>Search these pages <input type=search data-standard-search placeholder="A name, a desk, a policy" enterkeyhint=search></label>
</form>
<div class=cols>
<div>
<p class=label>Lead · Editorial, not an investigation</p>
<h2><a href="/standard/editorial/the-chain-needs-a-student-paper/">The Chain Needs a Student Paper</a></h2>
<p class=deck>The paper states what it will cover and what it will not pretend. The text does not establish a fact about a market, a person, or an incident.</p>
<p class=byline>By Sol.College · 17 Nov 2026 · Editorial</p>
<p><a class=ink href="/standard/editorial/the-chain-needs-a-student-paper/">Read the editorial</a></p>
</div>
<aside>
<h2>Latest reporting</h2>
<p>No report has been published. The cover investigation, “Everyone says early”, is a commission. It is on the <a href="/standard/assignments/">assignment board</a>. It is not a story.</p>
<h2>Campus noticeboard</h2>
<p>No verified event, meeting, club, election, or opening is posted. The <a href="/campus/">campus</a> and the <a href="/lessons/">lessons</a> are the college’s practice pages. They are not news reports.</p>
<p><a href="/standard/noticeboard/">The noticeboard</a></p>
</aside>
</div>
<hr class=rule>
<div class=cols>
<section>
<h2>The argument</h2>
<p>One editorial is published. No response to it has been written. The case for memecoins and the case against them are assignments. Neither has been commissioned.</p>
</section>
<section>
<h2>The Fine Print</h2>
<p>No product term has been examined.</p>
<h2>Claim Check</h2>
<p>No public claim has been checked.</p>
</section>
</div>
<h2>Recurring features</h2>
<p>These are formats. None of them has an edition.</p>
<ul class=features>{''.join(f'<li><b>{E(n)}.</b> {E(d)}</li>' for n, d in FEATURES)}</ul>
<h2>Masthead</h2>
<p>No student editor, managing editor, technical editor, contributor, or adviser has agreed to be named. A name is added only after that person agrees. Sol.College can edit every page. Nothing separates that edit from the publisher. A weekly edition is the aim once there is checked work to print. This package is not that edition, and this is not a continuous newsroom.</p>
<h2 id=index>In this package</h2>
<ul class=index>{listing}</ul>
<h2>Assignments, not stories</h2>
<ul class=index>{assigns}</ul>
{foot()}
<script>
(function(){{
  var q=document.querySelector('[data-standard-search]');
  if(!q) return;
  var items=[].slice.call(document.querySelectorAll('[data-paper]'));
  q.form.addEventListener('submit', function(e){{ e.preventDefault(); document.getElementById('index').scrollIntoView(); }});
  q.addEventListener('input', function(){{
    var words=q.value.toLowerCase().split(/\\s+/).filter(Boolean);
    items.forEach(function(el){{
      var t=((el.getAttribute('data-paper')||'')+' '+(el.textContent||'')).toLowerCase();
      el.hidden=words.some(function(w){{ return t.indexOf(w)<0; }});
    }});
  }});
}})();
</script>
</article>'''

EDITORIAL = '''<p>Sol.College exists to teach people how to understand and build. A college newspaper has another responsibility: to ask what is being built, who benefits, and what deserves to change.</p>
<p>We will cover the experiments and the excesses. The useful products and the bad incentives. The memes, the arguments, the engineering, and the people doing the work.</p>
<p>We will not mistake cynicism for intelligence or enthusiasm for evidence.</p>
<p>We will question projects, influencers, institutions, and this college. We will publish disagreement without pretending every claim is equally supported. When we get something wrong, we will correct it.</p>
<p>This is not a publication about pretending the ecosystem is respectable. It is a publication about taking its consequences seriously.</p>
<p>Welcome to The Degen Standard.</p>
<p>Question the chain.</p>'''

def editorial_page():
  return f'''<article class=tds>
{crumbs('Editorial')}
{mast(False)}
<p class=label>Editorial · not reporting</p>
<h1>The Chain Needs a Student Paper</h1>
<p class=byline>By Sol.College · 17 Nov 2026</p>
<aside class=box>
<p class=label>Status</p>
<dl class=facts>
<dt>Type</dt><dd>Editorial. A statement of intent.</dd>
<dt>Reporting</dt><dd>None. This page does not report an event.</dd>
<dt>Author</dt><dd>Sol.College, the publisher. No person is named. The “we” is the publisher, not a student staff.</dd>
<dt>Published</dt><dd>17 Nov 2026. That is the page date. It is not an edition date.</dd>
<dt>Sources</dt><dd>None. The editorial does not cite an event, a document, or a person.</dd>
<dt>Disclosure</dt><dd>The publisher wrote the page and can change it. No holding is disclosed, because no person is named. That absence is not a claim that nobody at Sol.College holds a token.</dd>
<dt>Corrections</dt><dd>None. <a href="/standard/corrections/">The log</a>.</dd>
</dl>
</aside>
{EDITORIAL}
{foot()}
</article>'''

def charter_page():
  rows = '''<tr><td><a href="/library/">The Solana Library</a></td><td>Where can I find a source?</td><td>A catalogue of explanations, references, and records. Not this paper.</td></tr>
<tr><td><a href="/articles/">Articles</a></td><td>Can someone explain this clearly?</td><td>A lesson in prose, from a recorded example.</td></tr>
<tr><td><a href="/lessons/">Lessons</a></td><td>Can I learn to do it?</td><td>Practice on a live fork.</td></tr>
<tr><td>Journal of Solana Studies</td><td>What does a specified investigation establish?</td><td>A research record, with a method. Not this paper.</td></tr>
<tr><td>The Degen Standard</td><td>What is happening, who benefits, and what should we question?</td><td>This paper. Fewer pieces than the articles list, and a different job from the journal.</td></tr>'''
  return f'''<article class=tds>
{crumbs('Charter')}
{mast(False)}
<p class=label>Charter</p>
<h1>What the paper is for</h1>
<p class=deck>The Degen Standard is the student newspaper of Sol.College. Degen is the cultural voice. Standard is the counterweight. The voice is not permission to print a rumour.</p>
<h2>About</h2>
<p>The Degen Standard covers the people, markets, technology, politics, and culture surrounding Solana, from memecoin launches and perpetual futures to governance disputes, engineering failures, and student life.</p>
<p>The paper is curious about experimentation and sceptical of easy money. It separates reporting from opinion, discloses relevant interests, and corrects mistakes. It covers Sol.College with the same scrutiny it applies to everyone else.</p>
<p>Independent-minded describes the stance the paper wants. It does not mean editorial independence is established. No editor stands between a story and the publisher. Sol.College can change any page.</p>
{NOTE}
<h2>A different job from the rest of the college</h2>
<table>
<thead><tr><th>Publication</th><th>Its question</th><th>What it is</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<p>A long tutorial is not a report. A technical article is not an investigation. A research protocol is not news. This paper publishes less often than the articles list, and it does not borrow the journal’s status by using a lighter headline.</p>
<h2 id=features>Recurring features</h2>
<ul class=features>{''.join(f'<li><b>{E(n)}.</b> {E(d)}</li>' for n, d in FEATURES)}</ul>
<p>Satire that resembles a real allegation has to be unmistakable as satire. No satire is published in this release.</p>
<h2>How the paper is meant to run</h2>
<p>The aim is a student editor, a managing editor, a technical editor, contributors for news, investigations, culture, and campus, and an adviser. The adviser supports safety and standards. The adviser does not pre-approve criticism of the college.</p>
<p>None of those seats is filled. A name goes on the masthead only after that person agrees. Writing the aim down does not appoint anyone.</p>
<p>A weekly edition is the aim once there is checked work to print. There is no quota, and there is no continuous newsroom behind this package.</p>
<p>The rules for interests, trading, reporting, promotion, students, and disputes are on the <a href="/standard/policies/">policies</a> page. The labels a future story has to carry are on the <a href="/standard/templates/">templates</a> page.</p>
{foot()}
</article>'''

def policies_page():
  return f'''<article class=tds>
{crumbs('Policies')}
{mast(False)}
<p class=label>Policies</p>
<h1>Rules before there is a newsroom</h1>
<p class=deck>These rules are in force as publication standards. They do not describe a staff, because no one has been appointed.</p>
<h2 id=interests>Financial interests</h2>
<p>A writer or an editor discloses a relevant token holding, job, consulting arrangement, grant, sponsorship, referral deal, gift, or preferential access. Relevant means a reader needs it to judge the piece.</p>
<p>No person is appointed, so no holding is on file. That is not a claim that nobody at Sol.College holds a token. It is a claim that no writer has been named, and so no writer has declared one.</p>
<h2 id=trading>Trading</h2>
<p>A person who has seen unpublished reporting about a market must not trade the asset that reporting concerns, and must not tip someone else to, until the reporting is published or killed. They step off a story in which they have a relevant interest.</p>
<p>No one is in that position. No market-sensitive story is under way. The rule is published before any such story is assigned.</p>
<h2 id=reporting>Reporting</h2>
<p>A report needs a record of its sources, evidence for a material assertion, and a visible line between an allegation and a finding. A person or an organisation facing a serious criticism gets a meaningful chance to respond. A high-risk story needs a second read. Where the story needs legal advice, it waits.</p>
<p>None of that machinery has been used. There is no second reader, no lawyer retained for the paper, and no story in draft.</p>
<p>A contributor may write under a pseudonym only if an editor knows who is accountable. No editor is appointed, so no pseudonymous piece can be accepted. A pseudonym does not make evidence stronger or weaker.</p>
<h2 id=promotion>Promotion</h2>
<p>The paper does not take payment for a token recommendation, and it does not take a trading-referral fee. No advertising is sold. A sponsor does not buy a kind story or the silence around a hard one. If advertising is ever introduced, it has to be labelled and kept apart from the reporting. None is running. This paper does not show token prices, flashing gains, referral buttons, or a list of coins.</p>
<h2 id=students>Students</h2>
<p>A student is not required to trade, deposit funds, take a loss, or hand over personal financial details in order to report for the paper or to complete coursework. Where a story needs the writer to try a product, the trial uses a simulation or a test environment, and the piece says what that trial cannot show. No such assignment has been given to a student. No student is named on these pages.</p>
<h2 id=disputes>Disputes with the college</h2>
<p>The paper’s standard is to scrutinise Sol.College the same way it scrutinises anyone else. The protection for that standard is not in place. A complaint is a <a href="{COMPLAINT}">public GitHub issue</a>. The publisher can edit the page that results. There is no separate editor who can overrule Sol.College. Until that seat exists, “we scrutinise the college” is a rule on a page, not a guarantee.</p>
<h2 id=ai>Automated assistance</h2>
<p>Automation may help with transcription, sorting, discovery, and editing, if the material is allowed to leave the newsroom and a person checks the result. It must not manufacture an interview, a quote, an eyewitness, an anonymous source, a student experience, evidence of misconduct, or the appearance of a reporting trip.</p>
<p>The paper does not rewrite other publications into a feed. These charter pages were prepared with automated assistance. They report no observation. A generated paragraph is not a source.</p>
{foot()}
</article>'''

def desks_page():
  blocks = []
  for d in DESKS:
    beats = ''.join(f'<li>{E(b)}</li>' for b in d['beats'])
    blocks.append(f'''<section id={d["id"]}>
<h2>{E(d["title"])}</h2>
<p class=deck>{E(d["question"])}</p>
<p>{E(d["standard"])}</p>
<ul>{beats}</ul>
<p class=kind>No story is filed on this desk.</p>
</section>''')
  return f'''<article class=tds>
{crumbs('Desks')}
{mast(False)}
<p class=label>Desks</p>
<h1>Seven desks, no stories yet</h1>
<p class=deck>The masthead says News for the technical desk. The desk’s name is Chain Watch. Opening a desk does not fill it.</p>
{''.join(blocks)}
{foot()}
</article>'''

def assignments_page():
  cover = box('Cover commission',
    'Everyone says “early.” Who gets to be early, and who arrives to provide the exit? The question is a commission for a reported feature about launch access, allocations, promotion, and ordinary participation. No reporting has been done. The conclusion is not written. It has to follow the reporting. This is not an allegation about any organisation.')
  rows = ''.join(
    f'<li><h3>{E(title)}</h3><p>{E(why)}</p><p class=kind>Assignment. Not reported. No finding.</p></li>'
    for title, why in ASSIGNMENTS)
  return f'''<article class=tds>
{crumbs('Assignments')}
{mast(False)}
<p class=label>Assignment board · not the paper</p>
<h1>Commissions, not stories</h1>
<p class=deck>Unfinished work stays on this board. It is not printed as a headline with an invented finding.</p>
{cover}
<ol class=assigns>{rows}</ol>
{foot()}
</article>'''

def templates_page():
  return f'''<article class=tds>
{crumbs('Templates')}
{mast(False)}
<p class=label>Templates</p>
<h1>How a piece has to be labelled</h1>
<p class=deck>These are empty forms. No report, investigation, or satire uses them yet. The founding editorial uses the opinion label, and it says it is not reporting.</p>
<h2>Reporting</h2>
<ul>
<li>The question the reporter actually asked.</li>
<li>What was checked, and where.</li>
<li>What the evidence supports.</li>
<li>What it does not support.</li>
<li>Who was asked to respond, and what they said, including a refusal.</li>
<li>The writer’s relevant interests.</li>
<li>The limits of the check.</li>
</ul>
<p>The deck may say what the reporting establishes only after the reporting exists and has been checked.</p>
<h2>Opinion</h2>
<ul>
<li>The word Opinion, where a reader cannot miss it.</li>
<li>The argument.</li>
<li>What would count against it.</li>
<li>The writer’s relevant interests.</li>
<li>A byline that names a real, consenting person, or the publisher if no person is writing.</li>
</ul>
<p>An opinion does not become a finding because it sits next to a report.</p>
<h2>Investigation</h2>
<ul>
<li>The question, before the conclusion.</li>
<li>The documents.</li>
<li>The interviews.</li>
<li>The chance to respond.</li>
<li>Findings kept separate from allegations.</li>
</ul>
<p>A verdict chosen in advance is not an investigation.</p>
<h2>Satire</h2>
<aside class=satire>
<p class=label>Satire</p>
<p>A made-up headline would go here. This box is the specimen, not a joke about a real party. Nothing in this box happened.</p>
</aside>
<p>If a joke resembles a real allegation, the satire label has to be unmistakable. A clever tone is not a label. No satire is published in this release.</p>
{foot()}
</article>'''

def corrections_page():
  return f'''<article class=tds>
{crumbs('Corrections')}
{mast(False)}
<p class=label>Corrections desk</p>
<h1>Corrections</h1>
<p>No correction has been issued. When one is, it stays on this page, names the page it corrects, says what was wrong, and says what the record supports instead. A quiet edit is not a correction.</p>
<p><a href="{CORRECTION}">Send a correction</a>. The issue is public.</p>
{foot()}
</article>'''

def letters_page():
  return f'''<article class=tds>
{crumbs('Letters')}
{mast(False)}
<p class=label>Letters</p>
<h1>Letters to the Standard</h1>
<p>No letter has been published. A letter is edited for length, clarity, and evidence. Sending one does not mean it will run. A letter is not a report, and it is labelled as correspondence.</p>
<p><a href="{LETTER}">Send a letter</a>. The issue is public. Do not include a private key, a recovery phrase, or anything you need kept private. This is not a confidential letter.</p>
{foot()}
</article>'''

def tips_page():
  return f'''<article class=tds>
{crumbs('Tips')}
{mast(False)}
<p class=label>Tips</p>
<h1>Send a tip</h1>
<aside class=box>
<p class=label>Privacy</p>
<p>The tip line is a public GitHub issue. Anyone can read it. It is not a confidential tip line. There is no encrypted drop, no private inbox for the paper, and no promise that a message stays between you and an editor. If a tip cannot be public, do not send it here.</p>
</aside>
<p>Do not include a private key, a recovery phrase, unpublished vulnerability details, or another person’s private information. A tip is a lead. It is not a finding, and it is not published as one.</p>
<p><a href="{TIP}">Open a public tip</a></p>
{foot()}
</article>'''

def noticeboard_page():
  return f'''<article class=tds>
{crumbs('Campus')}
{mast(False)}
<p class=label>Campus noticeboard</p>
<h1>Nothing is pinned</h1>
<p class=deck>A notice is added when the event, the opening, or the complaint is real and can be checked. None is recorded here.</p>
<ul>
<li>No meeting is listed.</li>
<li>No club is listed.</li>
<li>No student election is listed. No representative structure has been created.</li>
<li>No internship or contributor opening is listed.</li>
<li>No complaint has been filed through the paper.</li>
</ul>
<p>The <a href="/campus/">campus</a> is the college’s public list of practice rooms. The <a href="/lessons/">lessons</a> are the practice. A project page is not a campus dispatch, and a paused room is not a news story about the students.</p>
<p>Do not send a private key or a personal financial detail to fill this board. A public notice can go through the <a href="{LETTER}">letters issue</a>, and it is still public.</p>
{foot()}
</article>'''

def ld(title, desc, path):
  return {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    'headline': title,
    'description': desc,
    'datePublished': PUBLISHED,
    'url': SITE + path,
    'isPartOf': {'@type': 'WebSite', 'name': 'The Degen Standard', 'publisher': {'@type': 'Organization', 'name': 'Sol.College', 'url': SITE}},
  }

def write_page(S, page, css, path, title, desc, main, data):
  doc = 'The Degen Standard | Sol.College' if title == 'The Degen Standard' else title + ' | The Degen Standard'
  html_page = page(css + main, doc, desc, path)
  blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
  html_page = html_page.replace('</head>', '<script type="application/ld+json">' + blob + '</script></head>', 1)
  if '<h1>' not in html_page:
    raise SystemExit('standard: missing h1 ' + path)
  os.makedirs(S + path, exist_ok=True)
  open(S + path + 'index.html', 'w').write(html_page)
  return path

def write(S, page, css):
  home_desc = 'The Degen Standard is the student newspaper of Sol.College. This package is the charter, the policies, and one editorial. No report has been published.'
  pages = [
    ('/standard/', 'The Degen Standard', home_desc, home_page()),
    ('/standard/charter/', 'Editorial charter', 'What The Degen Standard is for, how it differs from the articles and the journal, and which seats are empty.', charter_page()),
    ('/standard/policies/', 'Newspaper policies', 'Interest disclosures, a trading rule, reporting standards, a ban on paid tips, student protection, and the limit on disputes with the college.', policies_page()),
    ('/standard/editorial/the-chain-needs-a-student-paper/', 'The Chain Needs a Student Paper', 'The founding editorial. A statement of intent by Sol.College. It does not report an event.', editorial_page()),
    ('/standard/desks/', 'Desks', 'Seven desks for The Degen Standard. Each one states its question. No story is filed.', desks_page()),
    ('/standard/assignments/', 'Assignment board', 'Cover commission and ten assignments. None has been reported. None is an allegation.', assignments_page()),
    ('/standard/templates/', 'Story templates', 'How a report, an opinion, an investigation, and a satire have to be labelled. The forms are empty.', templates_page()),
    ('/standard/corrections/', 'Corrections', 'The corrections log of The Degen Standard. No correction has been issued.', corrections_page()),
    ('/standard/letters/', 'Letters', 'How to send a letter to The Degen Standard. None has been published. The issue is public.', letters_page()),
    ('/standard/tips/', 'Send a tip', 'Tips to The Degen Standard go to a public GitHub issue. It is not a confidential tip line.', tips_page()),
    ('/standard/noticeboard/', 'Campus noticeboard', 'The campus noticeboard. No event, club, election, or opening is listed.', noticeboard_page()),
  ]
  paths = []
  for path, title, desc, main in pages:
    paths.append(write_page(S, page, css, path, title, desc, main, ld(title, desc, path)))
  blob = '\n'.join(open(S + p + 'index.html').read() for p in paths)
  checks = [
    ('No report has been published.', 'home'),
    ('Editorial independence is not established.', 'independence'),
    ('No student editor', 'masthead'),
    ('It is not a confidential tip line.', 'tips'),
    ('No correction has been issued.', 'corrections'),
    ('Assignment. Not reported. No finding.', 'assignments'),
    ('Nothing in this box happened.', 'satire specimen'),
    ('No story is filed on this desk.', 'desks'),
    ('does not mean editorial independence is established', 'about'),
  ]
  for needle, name in checks:
    if needle not in blob:
      raise SystemExit('standard: missing ' + name)
  banned = ['sources told', 'a student said', 'we interviewed', 'our reporter', 'hot coin', 'price ticker',
            'editorially independent', 'an independent newsroom', 'award-winning', 'ISSN', 'doi:']
  low = blob.lower()
  for phrase in banned:
    if phrase.lower() in low:
      raise SystemExit('standard: banned phrase ' + phrase)
  if blob.count('No story is filed on this desk.') < len(DESKS):
    raise SystemExit('standard: a desk is missing its empty-file line')
  if blob.count('Assignment. Not reported. No finding.') < len(ASSIGNMENTS):
    raise SystemExit('standard: an assignment is missing its label')
  llms = f'{S}/llms.txt'
  if os.path.exists(llms):
    block = '\n## The Degen Standard\n' + ''.join(f'- [{t}]({SITE}{p}): {d}\n' for p, t, d, _m in pages)
    text = re.sub(r'\n## The Degen Standard\n.*?(?=\n## |\Z)', '', open(llms).read(), flags=re.S)
    open(llms, 'w').write(text.rstrip() + '\n' + block)
  print('standard:', len(paths), 'pages')
  return paths
