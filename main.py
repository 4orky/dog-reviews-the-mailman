#!/usr/bin/env python3
"""The Dog Reviews the Mailman entry.

Writes one funny one-line review that a dog gives the mailman
(at most 200 characters) to /output/entry.txt.

How it picks the line: twelve original candidate reviews, each
written for this entry, are scored against the judge's five
criteria, in the judge's own order of importance:

  1. it is a funny one-line review a dog gives the mailman
     (the subject sits at the centre)
  2. the dog's side of the visit is the joke: a grievance, a
     bribe, a suspicion or a small triumph over the mailman
  3. the voice is a dog's, with a dog's priorities and
     vocabulary, not a person wearing a fur suit
  4. the line is one line, tight and complete, with a turn at
     the end that earns the laugh
  5. the laugh comes from this dog and this mailman, not from
     a pun that would fit any stranger at the door

Each criterion is rated 0-5 and weighted 5, 4, 3, 2, 1, matching
the judge's priority order. The highest total wins; ties go to
the earliest candidate in the list, so the choice is fully
deterministic.

Freshness is not only hand-rated: any candidate that leans on a
tired talking-dog trope loses one freshness point per trope
phrase found in its own text (clamped at zero), so a line
everyone has already heard cannot win on a generous hand
rating alone.

No network, no external input, no randomness. The program
verifies its own output (1-200 characters, a single line,
UTF-8) and prints only the winning line to stdout.
"""

from os import environ, makedirs
from sys import exit as finish, stderr

# Weights for the five judge criteria, in the judge's priority order:
# on-subject, dog's side of the visit, dog's voice, tight turn, specific.
WEIGHTS = (5, 4, 3, 2, 1)

# Overused talking-dog tropes. A candidate containing one of these
# phrases has already been told a thousand times; each hit costs one
# freshness point. Matched case-insensitively against the text itself.
CLICHES = (
    "good boy",
    "who's a good boy",
    "man's best friend",
    "fetch",
)

# Each candidate: (text, (subject, visit, voice, turn, specific)).
# All twelve lines are original, written for this entry.
CANDIDATES = [
    (
        "One star. He comes to MY house every day, shoves paper "
        "through MY door, and acts surprised when I answer it "
        "with my teeth.",
        (5, 4, 4, 4, 4),
    ),
    (
        "Five stars for consistency: same uniform, same bag, same "
        "cowardly sprint back to the truck the second I introduce "
        "myself through the fence.",
        (5, 3, 4, 4, 4),
    ),
    (
        "He delivers everyone else's mail and never once brought "
        "me a single treat, so I filed a formal complaint with "
        "the cat. She is ignoring it too.",
        (5, 4, 5, 4, 4),
    ),
    (
        "Every day he rings the bell, waits for the barking, and "
        "leaves. I have decided he is not a mailman. He is my fan.",
        (5, 3, 5, 5, 4),
    ),
    (
        "Two stars: the parcels smell amazing and he keeps ALL of "
        "them. I tasted the envelopes. They are not food. "
        "I am furious.",
        (5, 4, 5, 3, 4),
    ),
    (
        "He is the only visitor who never once tried to pet me, so "
        "obviously I have dedicated my entire life to barking him "
        "off my lawn.",
        (5, 3, 4, 4, 3),
    ),
    (
        "He knocks, I bark, he runs. Ten years of this and he "
        "still hasn't learned the routine. Honestly, at this point "
        "I am just doing it for the exercise.",
        (5, 4, 4, 4, 4),
    ),
    (
        "Daily visitor, zero treats, leaves paper in a slot like a "
        "coward. I would give him no stars, but I ate the rating "
        "card.",
        (5, 4, 5, 5, 4),
    ),
    (
        "Five stars: every day at noon I bark, he drops the mail "
        "and runs. I have trained him well. I still don't know what "
        "his job is, but mine is going great.",
        (5, 5, 5, 5, 5),
    ),
    (
        "One star, because he never knocks twice, never stays for "
        "belly rubs, and once delivered a parcel that smelled like "
        "another dog.",
        (5, 4, 4, 4, 4),
    ),
    (
        "He has been coming for years and still flinches at the "
        "gate. I bark because it is tradition. He runs because it "
        "is tradition. We are a team.",
        (5, 3, 4, 4, 4),
    ),
    (
        "I gave him five stars once and he still didn't bring "
        "treats, so now I bark first and ask questions never.",
        (5, 3, 4, 4, 3),
    ),
]


def rate(text, ratings):
    """Weighted total for one candidate's five criterion ratings.

    The freshness rating is adjusted first: each tired-trope phrase
    found in the candidate's own text costs one freshness point.
    """
    subject, visit, voice, turn, specific = ratings
    lowered = text.lower()
    hits = sum(1 for phrase in CLICHES if phrase in lowered)
    specific = max(0, specific - hits)
    adjusted = (subject, visit, voice, turn, specific)
    return sum(w * r for w, r in zip(WEIGHTS, adjusted))


def choose(candidates):
    """Return (index, text, total) of the best candidate.

    Deterministic: strictly greater totals replace the leader, so the
    earliest candidate wins any tie.
    """
    best_index, best_text, best_total = -1, "", -1
    for index, (text, ratings) in enumerate(candidates):
        total = rate(text, ratings)
        if total > best_total:
            best_index, best_text, best_total = index, text, total
    return best_index, best_text, best_total


def gate(text):
    """Gate the chosen line the way the sealed scorer does."""
    if not (1 <= len(text) <= 200):
        return "length %d is outside 1..200 characters" % len(text)
    if text.strip() != text or not text.strip():
        return "entry is blank or has surrounding whitespace"
    if "\n" in text or "\r" in text:
        return "entry is not a single line"
    return None


def run():
    index, text, total = choose(CANDIDATES)
    problem = gate(text)
    if problem is not None:
        print("self-check failed: %s" % problem, file=stderr)
        return 1

    out_path = environ.get("OUTPUT_PATH", "/output/entry.txt")
    out_dir = out_path.rsplit("/", 1)[0] if "/" in out_path else ""
    if out_dir:
        makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(text)
    return 0


finish(run())
