"""Fixture checks for the sitewide SEO pass. No site build required."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo

PAGE = '''<!doctype html><html lang=en><head><meta charset=utf-8>
<title>Example walkthrough | Sol.College</title>
<meta name=description content="A short description of the example.">
<link rel=canonical href="https://sol.college/explore/example/">
<meta property=og:image:alt content="Sol.College: Sol.College: learn Solana development from real code">
</head><body><header class=top><nav aria-label=Main><a href="/lessons/">Lessons</a><a href="/journal/">Journal</a></nav></header>
<main id=main><h1>Example</h1><p>Body copy stays.</p></main>
<footer><p>Sol.College</p></footer></body></html>'''

MIRROR = '''<!doctype html><html lang=en><head><meta charset=utf-8>
<title>Agent Court: step-by-step Solana lesson, live on devnet | Sol.College</title>
<meta name=description content="Lock tokens and file a dispute.">
<link rel=canonical href="https://sol.college/lessons/agent-court/">
<meta name=robots content="index,follow">
</head><body><main id=main><h1>Agent Court</h1></main><footer><p>x</p></footer></body></html>'''

SPA = '''<!doctype html><html><head><title>About SOL.COLLEGE</title>
<meta name="description" content="A short about line.">
<link rel="canonical" href="https://sol.college/about/"/>
<meta name="robots" content="index, follow">
</head><body><main class="flex-1"><h1>About</h1><p>$_TSR hydration marker</p></main>
<footer class="x"><p>Solar footer</p></footer></body></html>'''

RICH = '''<!doctype html><html><head><title>Home</title>
<meta name="description" content="Learn on Solana apps and offer patches back. Practice environments are independent forks we ran on devnet, not a claim that the original team is a partner.">
<link rel="canonical" href="https://sol.college/">
</head><body><header><a href="/journal/">Journal</a></header>
<main id="main"><h1>Home</h1></main>
<footer><nav aria-label="Footer"><a href="/lessons/">Lessons</a><a href="/journal/">Journal</a></nav></footer></body></html>'''


class SeoTests(unittest.TestCase):
    def test_fit_keeps_the_limit_sentence(self):
        raw = ('Learn on real Solana applications, turn findings into patches, and offer those '
               'improvements back to the original projects. Practice environments are independent '
               'forks we ran on devnet, not a claim that the original team is a partner.')
        out = seo.fit(raw)
        self.assertLessEqual(len(out), 158)
        self.assertIn('not a claim that the original team is a partner.', out)

    def test_fit_drops_whole_sentences_before_a_limit(self):
        raw = ('Which questions can you ask with these records, and which investigations are not here? '
               'A reading guide. It is not an additional holding and it reports no new measurement.')
        out = seo.fit(raw)
        self.assertLessEqual(len(out), 158)
        self.assertIn('It is not an additional holding and it reports no new measurement.', out)
        self.assertNotIn('A It is', out)

    def test_descriptions_stay_within_the_snippet_limit(self):
        home = ('Learn on Solana apps and offer patches back. Practice environments are independent '
                'forks we ran on devnet, not a claim that the original team is a partner.')
        journal = ('Journal of Solana Studies: the charter, the policies, six prospective protocols '
                   'and twelve sketches. No study has been completed and nothing is peer reviewed.')
        campus = ('Campus rooms for DeFi, DePIN and DeAI. Each project has a CTO agent and open assignments. '
                  'Credentials here are platform records, not accreditations.')
        for text in (home, journal, campus, seo.MAP_DESC):
            self.assertLessEqual(len(text), 158, text)
            self.assertEqual(seo.fit(text), text)

    def test_static_page_gains_schema_nav_and_is_stable(self):
        once, info = seo.patch(PAGE, '/explore/example/', 'explore/example/index.html')
        self.assertTrue(info['indexable'])
        self.assertIn('BreadcrumbList', once)
        self.assertNotIn('LearningResource', once)
        self.assertEqual(once.count('BreadcrumbList'), 1)
        self.assertIn('aria-label=Sections', once)
        self.assertIn('href="/map/"', once)
        self.assertIn('Body copy stays.', once)
        self.assertIn('max-image-preview:large', once)
        self.assertNotIn('Sol.College: Sol.College', once)
        twice, info2 = seo.patch(once, '/explore/example/', 'explore/example/index.html')
        self.assertEqual(twice, once)
        self.assertTrue(info2['indexable'])
        self.assertEqual(twice.count('<script type="application/ld+json">'), 1)

    def test_existing_breadcrumb_schema_is_left_in_place(self):
        page = PAGE.replace('</head>', '<script type="application/ld+json">{"@type":"BreadcrumbList"}</script></head>', 1)
        out, _ = seo.patch(page, '/explore/example/', 'explore/example/index.html')
        self.assertEqual(out.count('BreadcrumbList'), 1)
        self.assertNotIn('<!--sc-seo-->', out)

    def test_lesson_page_is_a_learning_resource(self):
        page = PAGE.replace('https://sol.college/explore/example/', 'https://sol.college/lessons/example/')
        out, info = seo.patch(page, '/lessons/example/', 'lessons/example/index.html')
        self.assertTrue(info['indexable'])
        self.assertIn('LearningResource', out)
        self.assertIn('"isAccessibleForFree":true', out)
        self.assertNotIn('educationalCredentialAwarded', out)

    def test_lesson_mirror_is_noindex(self):
        out, info = seo.patch(MIRROR, '/explore/agent-court/', 'explore/agent-court/index.html')
        self.assertFalse(info['indexable'])
        self.assertIn('noindex', out)
        self.assertNotIn('content="index,follow"', out)
        self.assertNotIn('aria-label=Sections', out)
        self.assertIn('https://sol.college/lessons/agent-court/', out)

    def test_shell_placeholder_is_noindex(self):
        page = PAGE.replace('Example walkthrough | Sol.College', 'Shell').replace('A short description of the example.', 'shell')
        out, info = seo.patch(page, '/faq/', 'faq/index.html')
        self.assertFalse(info['indexable'])
        self.assertIn('noindex', out)

    def test_spa_body_is_not_rewritten(self):
        out, info = seo.patch(SPA, '/about/', 'about/index.html')
        self.assertTrue(info['indexable'])
        self.assertIn('BreadcrumbList', out)
        self.assertIn('Solar footer', out)
        self.assertNotIn('aria-label=Sections', out)
        self.assertNotIn('sc-seo-crumbs', out)
        self.assertEqual(out.count('$_TSR hydration marker'), 1)

    def test_homepage_footer_gains_the_map_link(self):
        out, info = seo.patch(RICH, '/', 'index.html')
        self.assertTrue(info['indexable'])
        self.assertIn('href="/map/">All pages</a>', out)
        self.assertNotIn('EducationalOrganization', out)
        self.assertEqual(out.count('aria-label=Sections'), 0)
        twice, _ = seo.patch(out, '/', 'index.html')
        self.assertEqual(out.count('All pages'), twice.count('All pages'))

    def test_stale_noindex_is_cleared_when_the_canonical_points_elsewhere(self):
        page = PAGE.replace(
            'https://sol.college/explore/example/',
            'https://sol.college/live/',
        ).replace('</head>', '<meta name=robots content="noindex,follow"></head>', 1)
        out, info = seo.patch(page, '/findings/example/', 'findings/example/index.html')
        self.assertTrue(info['indexable'])
        self.assertIn('https://sol.college/findings/example/', out)
        self.assertNotIn('noindex', out)

    def test_own_noindex_stays_hidden(self):
        page = PAGE.replace('</head>', '<meta name=robots content="noindex,follow"></head>', 1)
        out, info = seo.patch(page, '/explore/example/', 'explore/example/index.html')
        self.assertFalse(info['indexable'])
        self.assertIn('noindex', out)

    def test_auth_drops_the_index_directive(self):
        page = SPA.replace('$_TSR hydration marker', 'sign in').replace(
            '<meta name="robots" content="index, follow">',
            '<meta name="robots" content="noindex"/><meta name="robots" content="index, follow">')
        out, info = seo.patch(page, '/auth/', 'auth/index.html')
        self.assertFalse(info['indexable'])
        self.assertIn('noindex', out)
        self.assertNotIn('index, follow', out)


if __name__ == '__main__':
    unittest.main()
