"""Desk standards and assignment briefs for The Degen.

Specimens are writing exercises. They are not reports, and they name no real party.
"""

DESK_MORE = {
 'chain-watch': dict(
  show=[
   'The technical claim, in the words a reader can check.',
   'The record that would confirm it: a transaction, a log, a client version, or a document.',
   'The record that would knock it down.',
   'What the paper does not yet have, in the same piece.',
  ],
  refuse=[
   'A diagnosis of an incident from a screenshot.',
   'A benchmark number with no workload.',
   'A sentence that treats a client error and a program error as the same event.',
  ],
  specimen='Specimen, not a report: “The application showed Paid. The signature later expired.” That is two sentences a Chain Watch piece would have to source separately. This page has sourced neither.'),
 'money': dict(
  show=[
   'The action the user is being asked to take.',
   'Each party who is paid if the user takes it, named from a document or an interface, not from a hunch.',
   'The cost the interface shows, and the cost it does not show.',
   'Whether the writer was paid, or holds the asset. No writer is named, so no holding is on file.',
  ],
  refuse=[
   'A prediction that a coin will rise.',
   'A referral link.',
   'A fee schedule the paper has not opened.',
  ],
  specimen='Specimen, not a report: a trading screen can show a fee on the button and collect a second fee in the route. A Money piece would have to open both. This page has opened neither.'),
 'power': dict(
  show=[
   'Who can make the decision, and which rule or key lets them.',
   'Who is consulted, and who is not, from a record rather than from a slogan.',
   'What “decentralised” refers to in the piece: validators, token votes, upgrade keys, or something else. The word alone is not the finding.',
  ],
  refuse=[
   'A governance percentage with no denominator.',
   'A claim that a foundation “controls the chain” without saying which decision.',
   'A regulatory summary the paper has not read.',
  ],
  specimen='Specimen, not a report: “The vote passed” is incomplete if the piece never says who was allowed to vote. This page does not describe a real vote.'),
 'culture': dict(
  show=[
   'The behaviour the culture is rewarding: attention, a trade, a status, a joke.',
   'Where the joke stops and a financial promotion starts, if both are present.',
   'The person or the community in their own terms, then the paper’s question. The question is not a caricature.',
  ],
  refuse=[
   'A private message published without a reason that meets the reporting rules.',
   'A medical or financial claim about a named person.',
   'A meme repeated as if repetition were evidence.',
  ],
  specimen='Specimen, not a report: a caption that says “not financial advice” can sit on a post that is nothing but a ticker and a referral. A culture piece would quote both and say what the second one does. This page quotes neither.'),
 'campus': dict(
  show=[
   'A real event, a real opening, or a real complaint, with a way for a reader to check it.',
   'What the student was asked to do, and what they were not asked to do. The student policy forbids requiring a deposit or a loss.',
   'The college’s own role, when the college is a party. The publisher can edit the page. That limit stays visible.',
  ],
  refuse=[
   'A fictional student used as a source.',
   'A lesson-completion tick reported as a student’s understanding.',
   'A paused campus room reported as a story about students. Paused means that project’s CTO agent is not producing work.',
  ],
  specimen='Specimen, not a report: “Students loved the workshop” needs a count, a question, and a named source who agreed to be quoted. None of those exist here.'),
 'opinion': dict(
  show=[
   'The argument, in one paragraph a critic could restate.',
   'What would count against it.',
   'The writer’s relevant interests, or an honest statement that no person is named and so no holding is on file.',
   'The word Opinion, where a reader cannot miss it.',
  ],
  refuse=[
   'A verdict about a named party dressed as an essay.',
   'A stack of outrages with no claim that could be wrong.',
   'An opinion that borrows the authority of a study this journal has not published. No study has been published.',
  ],
  specimen='Specimen, not a report: “Memecoins are how people arrive” is an argument. It becomes a report only when someone counts arrivals. Nobody has. The two commissioned essays on this question have not been written.'),
 'investigations': dict(
  show=[
   'The question, written before the conclusion.',
   'The documents, the interviews, and the check a reader could repeat.',
   'The allegation in one place and the finding in another.',
   'The response, including a refusal or a failure to reach the person.',
  ],
  refuse=[
   'A conclusion chosen because it would travel.',
   'An anonymous accusation with no document and no editor who knows the source. No editor is appointed, so that path is closed.',
   'A reconstruction that fills a gap with a plausible step. A gap stays a gap.',
  ],
  specimen='Specimen, not a report: “Everyone says early” is the cover commission. It asks who receives an allocation and who arrives later. It has no documents and no interviews. Printing it as a finding would break this desk’s rule.'),
}

BRIEFS = {
 'Your Trade Has More Than One Customer': dict(
  seek='The interface’s own fee line, the route or the program logs that name other recipients, and any document that defines a referral or a rebate. Public records only.',
  ask='Who is paid when the trade lands, in what asset, and which of those payments the screen shows?',
  trap='“This app secretly taxes users.” That sentence is a finding. The assignment is a map. The map has not been drawn.'),
 'The Leverage Slider Is a Design Decision': dict(
  seek='The controls a chosen interface puts next to a leverage setting, and any public note from its designers about defaults. No interface has been chosen.',
  ask='What does the default let a person do before they have read a risk disclosure, and who decided the default?',
  trap='“The slider is predatory.” That is a conclusion. The piece would need the control, the default, and a response from the people who set it. No one has been asked.'),
 'A Million Wallets Is Not a Million People': dict(
  seek='The publisher’s own definition of the metric, the denominator, and any note about sybils, reused wallets, or funded dust. No publisher has been chosen.',
  ask='What does the number count, what does it exclude, and what would change it by a large factor without a new person arriving?',
  trap='Printing the headline as a finding. The headline is the assignment. A million of anything has not been counted here.'),
 'The Influencer Said “Not Financial Advice.” What Else Did They Disclose?': dict(
  seek='A defined sample of posts, a checklist written before the sample is read, and a response from the people in the sample. No sample has been chosen.',
  ask='Besides the disclaimer, what holding, payment, or referral is disclosed, and where is it placed?',
  trap='“Influencers are lying.” The assignment is a disclosure count against a checklist. It is not a motive.'),
 'Who Gets a Grant—and Who Gets an Explanation?': dict(
  seek='One named programme’s public rules, its list of awards if that list is public, and interviews with applicants who agree to be quoted. No programme has been named.',
  ask='What must an applicant show, who decides, and what does a refusal explain?',
  trap='“Grants go to friends.” That is an allegation. It would need the rules, the awards, and a response. None of that work has started.'),
 'Students Built It. Who Owns It?': dict(
  seek='The contribution terms the college proposes or already uses, and any agreement a contributor is asked to accept. This is a reading of terms, not a claim that a student was exploited.',
  ask='Who owns the work, who may use it, and what happens to a contribution if the student leaves?',
  trap='A story about a wronged student who does not exist. No student is named, and no case is filed.'),
 'We Tried to Follow the Fees': dict(
  seek='A bounded workflow, the balance changes across it, and the number the product displays as the fee. The walk has not been done.',
  ask='Which costs are in the displayed fee, and which costs move a balance without appearing there?',
  trap='A total presented as “the real fee” before the balances have been read.'),
 'The Case for Memecoins': dict(
  seek='Nothing yet. This is a commissioned opinion. It has not been commissioned. The writer would have to say what would count against the argument, and disclose relevant interests.',
  ask='What good does the writer claim, for whom, and what evidence would make them drop the claim?',
  trap='Publishing the case as the paper’s finding, or as reporting. It would be Opinion, and it does not exist.'),
 'The Case Against Memecoins': dict(
  seek='Nothing yet. This is commissioned separately from the case for, so one writer is not asked to perform both sides. It has not been commissioned.',
  ask='What harm does the writer claim, for whom, and what evidence would make them drop the claim?',
  trap='Running it as a rebuttal of a case that has not been written, or as a report of a loss the paper has not documented.'),
 'What Sol.College Should Publish About Itself': dict(
  seek='The pages the college already publishes about its own practice forks, its counts, and its limits. The founding editorial does not answer this assignment.',
  ask='Which decisions about the college are visible to a reader, and which decisions have no public record?',
  trap='Pretending the paper can force the publisher. It cannot. Sol.College can edit the page. The assignment is to say what a reader still cannot see.'),
}
