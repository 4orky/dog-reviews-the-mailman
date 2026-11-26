"""Pick the dog's funniest one-line review of the mailman.

The program holds twelve original review lines, grades each one
against the five things the judge cares about most (in that order:
the review is really about the dog and the mailman; the joke comes
from the dog's side of the visit; it sounds like a dog talking;
the line is tight and lands with a turn; the joke could only be
about this dog and this mailman), and writes the best-scoring line
to /output/entry.txt.

Scoring is plain arithmetic, no randomness and no outside input:
every criterion gets a mark from 0 to 5, multiplied by its weight,
and the earliest line wins any tie. A line that leans on a
worn-out talking-dog phrase loses a point of its last mark for
each such phrase, so a joke everybody has heard cannot win on
kind marks alone. Before the program exits it checks the winning
line (one line, 1 to 200 characters, no stray spaces at the ends)
and prints the line together with its SHA-256 digest, so anyone
rerunning it can confirm the exact bytes that were chosen.
"""

import hashlib
import os
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_BAD = 1

# How much each of the judge's five criteria counts, in the
# judge's own order of importance.
CRITERION_WEIGHTS = {
    "about_dog_and_mailman": 5,
    "dogs_side_of_visit": 4,
    "sounds_like_a_dog": 3,
    "tight_with_a_turn": 2,
    "only_this_dog": 1,
}

# Tired talking-dog phrases. One point off the last mark per hit.
WORN_OUT_PHRASES = ("good boy", "who's a good boy", "man's best friend", "fetch")

# The twelve lines, each with its five marks in criterion order.
# Every line below is original, written for this entry.
REVIEWS = [
    {"line": "One star. He comes to MY house every day, shoves paper through MY door, and acts surprised when I answer it with my teeth.", "marks": (5, 4, 4, 4, 4)},
    {"line": "Five stars for consistency: same uniform, same bag, same cowardly sprint back to the truck the second I introduce myself through the fence.", "marks": (5, 3, 4, 4, 4)},
    {"line": "He delivers everyone else's mail and never once brought me a single treat, so I filed a formal complaint with the cat. She is ignoring it too.", "marks": (5, 4, 5, 4, 4)},
    {"line": "Every day he rings the bell, waits for the barking, and leaves. I have decided he is not a mailman. He is my fan.", "marks": (5, 3, 5, 5, 4)},
    {"line": "Two stars: the parcels smell amazing and he keeps ALL of them. I tasted the envelopes. They are not food. I am furious.", "marks": (5, 4, 5, 3, 4)},
    {"line": "He is the only visitor who never once tried to pet me, so obviously I have dedicated my entire life to barking him off my lawn.", "marks": (5, 3, 4, 4, 3)},
    {"line": "He knocks, I bark, he runs. Ten years of this and he still hasn't learned the routine. Honestly, at this point I am just doing it for the exercise.", "marks": (5, 4, 4, 4, 4)},
    {"line": "Daily visitor, zero treats, leaves paper in a slot like a coward. I would give him no stars, but I ate the rating card.", "marks": (5, 4, 5, 5, 4)},
    {"line": "Five stars: every day at noon I bark, he drops the mail and runs. I have trained him well. I still don't know what his job is, but mine is going great.", "marks": (5, 5, 5, 5, 5)},
    {"line": "One star, because he never knocks twice, never stays for belly rubs, and once delivered a parcel that smelled like another dog.", "marks": (5, 4, 4, 4, 4)},
    {"line": "He has been coming for years and still flinches at the gate. I bark because it is tradition. He runs because it is tradition. We are a team.", "marks": (5, 3, 4, 4, 4)},
    {"line": "I gave him five stars once and he still didn't bring treats, so now I bark first and ask questions never.", "marks": (5, 3, 4, 4, 3)},
]


def score_line(line, marks):
    """Weighted total for one review line.

    The last mark is trimmed first: each worn-out phrase found in
    the line itself costs one point there, never below zero.
    """
    keys = list(CRITERION_WEIGHTS)
    scored = list(marks)
    lowered = line.lower()
    hits = sum(1 for phrase in WORN_OUT_PHRASES if phrase in lowered)
    scored[-1] = max(0, scored[-1] - hits)
    return sum(CRITERION_WEIGHTS[key] * mark for key, mark in zip(keys, scored))


def pick_winner(entries):
    """Return the (line, total) of the best-scoring review.

    The earliest entry wins a tie, because only a strictly higher
    total replaces the current leader, so the result is stable.
    """
    best_line, best_total = "", -1
    for entry in entries:
        total = score_line(entry["line"], entry["marks"])
        if total > best_total:
            best_line, best_total = entry["line"], total
    return best_line, best_total


def check_entry(line):
    """Return a complaint string, or None when the line is legal."""
    if not 1 <= len(line) <= 200:
        return "length %d is outside 1..200 characters" % len(line)
    if line != line.strip():
        return "entry has surrounding whitespace"
    if "\n" in line or "\r" in line:
        return "entry is not a single line"
    return None


def fingerprint(text):
    """SHA-256 hex digest of one line, for the self-check."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save_entry(line):
    """Write the winning line and report its SHA-256 digest."""
    complaint = check_entry(line)
    if complaint is not None:
        print("self-check failed: %s" % complaint, file=sys.stderr)
        return EXIT_BAD
    digest = fingerprint(line)
    target = Path(os.environ.get("OUTPUT_PATH", "/output/entry.txt"))
    if target.parent != Path("."):
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(line, encoding="utf-8")
    if fingerprint(target.read_text(encoding="utf-8")) != digest:
        print("self-check failed: written file does not match", file=sys.stderr)
        return EXIT_BAD
    sys.stdout.write(line + "\n")
    sys.stdout.write("sha256: %s\n" % digest)
    return EXIT_OK


def run():
    """Score the twelve lines and save the winner."""
    winning_line, _winning_total = pick_winner(REVIEWS)
    return save_entry(winning_line)


sys.exit(run())
