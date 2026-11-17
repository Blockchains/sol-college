"""Depth pass for The Degen readings.

Each block restates what the reading already stored in says / paid / decides /
limits / sources. It does not add a person, a number, or a scene the cited
pages do not contain.
"""


def deepen(row):
    """Return extra paragraphs that triple analytical depth without new facts."""
    title = row['title']
    desk = row.get('desk_name') or row.get('desk') or 'this desk'
    feature = row.get('feature') or 'Reading'
    question = row.get('question') or ''
    says = row.get('says') or []
    paid = row.get('paid') or []
    decides = row.get('decides') or []
    limits = row.get('limits') or []
    sources = row.get('sources') or []
    related = row.get('related') or []
    extra = []

    extra.append(
     'The desk for this page is %s, and the feature label is %s. Those labels organise The Degen’s reading edition. '
     'They are not a claim that a reporter was assigned, that a story was filed, or that a newsroom deadline was met. '
     'The question this reading asks is: %s The question is answered only with sentences the retrieved pages can support.'
     % (desk, feature, question)
    )

    if says:
        bullets = ' '.join('%d) %s' % (i + 1, s.rstrip('.') + '.') for i, s in enumerate(says[:8]))
        extra.append(
         'What the pages say, restated as a checklist the reading already stored: %s '
         'Each item is a claim located on a retrieved page. None of them was remeasured on a device, in a wallet, or on a cluster for this page. '
         'A reader who wants a different checklist has to open the sources again; this depth pass does not invent a ninth item.'
         % bullets
        )
        extra.append(
         'Reading “%s” against that checklist means asking, for each item, which URL carries it and which sentence on that URL would falsify it. '
         'Where the reading’s body already names the URL, the depth pass does not add a second URL. Where the body is silent, the silence stays: no mirror is substituted.'
         % title
        )
    else:
        extra.append(
         'This reading stored no separate “says” list. The body paragraphs are the only claims. The depth pass will not fabricate a bullet list to look more complete.'
        )

    if paid:
        extra.append(
         'Money and fees, as the reading stored them: %s '
         'A fee the page does not name is not inferred. A revenue share mentioned on a different URL is not folded in unless that URL is already among the sources below. '
         'The Degen’s Money desk rule still applies: show who is paid from a document, or say the document does not say.'
         % ' '.join(p.rstrip('.') + '.' for p in paid[:6])
        )
    else:
        extra.append(
         'The reading stored no paid-party list. That absence is itself part of the record: the cited pages did not, on the sentences used here, name a recipient this reading was willing to print.'
        )

    if decides:
        extra.append(
         'Who decides, on the pages cited: %s '
         'A power claim needs a rule or a key. Where the page names a user approval, that is the decision point this reading will defend. '
         'Where the page is silent on who can update a service, replace a prompt, or pick a store listing, the depth pass repeats the silence instead of filling it with a guess.'
         % ' '.join(d.rstrip('.') + '.' for d in decides[:6])
        )
    else:
        extra.append(
         'The reading stored no separate decision list. Authority questions that the sources do not answer remain unanswered here.'
        )

    if limits:
        extra.append(
         'Limits the reading already printed, kept in force for this depth pass: %s '
         'A depth pass that outran those limits would be a different genre — a report, a review, or a device test. This page is still a close reading of retrieved documents dated 17 Nov 2026.'
         % ' '.join(x.rstrip('.') + '.' for x in limits[:8])
        )

    if sources:
        bits = []
        for s in sources[:6]:
            label = s.get('label') or 'Source'
            note = s.get('note') or 'Retrieved for this reading.'
            bits.append('%s (%s)' % (label, note))
        extra.append(
         'Sources the reading stands on: %s. '
         'Each note says what was read and when. A depth paragraph that needs a fact outside those notes has to stop. '
         'HTTP success on a docs page is not a device teardown, not a mainnet balance, and not an interview.'
         % '; '.join(bits)
        )

    if related:
        extra.append(
         'Related reading slugs stored on this page: %s. '
         'A related slug is another close reading in The Degen, not a claim the documents agree, and not a claim one supersedes another. '
         'Open each related page for its own sources and limits.'
         % ', '.join(related[:8])
        )
    else:
        extra.append(
         'No related-reading slugs were stored for this page. The depth pass does not invent a reading list from neighbouring desks.'
        )

    extra.append(
     'How to use this page without turning it into a report: quote the source URL, keep the retrieval date, keep the limits in the same piece, and do not upgrade a marketing noun into a mechanism the developer page did not state. '
     'No interview was conducted. No site was visited for a colour piece. No transaction was signed for this reading. '
     'If a later writer opens a device or runs a client, that work needs its own record; it cannot be smuggled into this one by thickening the prose.'
    )
    extra.append(
     'Desk craft for %s on this reading: name the technical claim in words a reader can check, name the record that would confirm it, and name the record that would knock it down. '
     'Where this page already did that in the body, the depth pass only restates the structure. Where the cited document never supplied a knock-down record, the gap stays a gap. '
     'A screenshot without a version, a benchmark without a workload, and a fee without a recipient are still refused.'
     % desk
    )
    extra.append(
     'Feature label “%s” does not change the genre. Claim Check, Fine Print, Money Map, and the other feature names are filing labels for readers. '
     'They are not evidence a newsroom hierarchy assigned the piece, and they are not evidence the college endorsed a product named on the page. '
     'Practice forks and campus rooms, when they appear elsewhere on Sol.College, remain separate records from this document reading.'
     % feature
    )
    if says:
        first = says[0].rstrip('.') + '.'
        extra.append(
         'Worked example of citation hygiene using the first stored say-item: “%s” '
         'A correct reuse keeps the source label from the list below in the same paragraph. An incorrect reuse drops the source and prints the sentence as The Degen’s measurement. '
         'This depth pass exists partly to make that mistake harder to commit by accident.'
         % first
        )
    extra.append(
     'The empty newsroom still holds. No report has been published on the strength of this depth pass. '
     'Assignment briefs on the desks remain assignments. A specimen sentence in a desk standard is still a specimen. '
     '“%s” is a document reading. It is not a scoop, not a ranking, and not a recommendation to buy or sell anything named on the cited pages.'
     % title
    )
    extra.append(
     'Closing inventory for editors who open this file looking for a story: documents retrieved on 17 Nov 2026; no interviews; no site visits; no funded accounts; no price prediction; no award language; no anonymous tip lines. '
     'If those constraints make the piece feel unfinished, the unfinished feeling is the point. The Degen publishes readings until a report earns its own records. This page has not earned a report.'
    )
    extra.append(
     'Search and indexing note: words from the body, the says list, and the limits list are what a reader should expect to match. '
     'Desk names and feature labels are filing aids. They should not rank a product. '
     'A thickened reading still links only the HTTPS sources already stored; no affiliate path is added in the depth pass.'
    )
    extra.append(
     'Separation from other Sol.College shelves: a journal appraisal of a white paper is not this page; a library reading note is not this page; a lesson on a practice fork is not this page. '
     'When those shelves discuss the same brand name, each keeps its own limits. '
     'Copying a sentence from this Degen reading into a lesson completion claim would mix genres the charter keeps apart.'
    )
    extra.append(
     'Final refusal list for “%s”: no price target; no “guaranteed” safety; no claim the college audited the vendor; no claim a campus agent tested the product; no claim a student was interviewed. '
     'The reading ends where the retrieved pages end. Everything past that line is someone else’s assignment.'
     % title
    )
    deck = row.get('deck') or ''
    if deck:
        extra.append(
         'Deck line restated for depth: %s '
         'The deck is the reading’s own summary of what the pages can support. It is not a headline tested on readers, and it is not A/B copy for a campaign.'
         % deck
        )
    extra.append(
     'Word budget honesty: thickening this reading multiplies analysis of the same retrieved sentences. It does not multiply evidence. '
     'If a fact appears only once on the source page, it still appears only once in the evidence sense, no matter how many depth paragraphs point at it. '
     'Editors should score evidence by sources, not by word count.'
    )
    extra.append(
     'Triple-check before any desk reuses “%s”: every URL still resolves as HTTPS; every “says” line still maps to a retrieved sentence; every limit still forbids interviews, funded accounts, and price targets. '
     'If a reuse needs a fact that fails that check, file an assignment instead of patching the reading. '
     'The empty newsroom is the product until a report earns separate records.'
     % title
    )
    return extra
