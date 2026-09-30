"""Probe WordNet synset behavior in this environment."""
import sys
sys.path.insert(0, ".")

import nltk
for r in ("wordnet", "omw-1.4"):
    try:
        nltk.data.find(f"corpora/{r}")
    except LookupError:
        nltk.download(r, quiet=True)

from nltk.corpus import wordnet

def syns(word, pos="n"):
    s = wordnet.synsets(word, pos=pos)
    out = set()
    for syn in s[:3]:
        for lemma in syn.lemmas():
            name = lemma.name().lower().replace("_", " ")
            if name != word:
                out.add(name)
    return s and (s[0].name(), sorted(out)[:6])

print("jackal n:", syns("jackal"))
print("clever n:", syns("clever"))
print("clever a:", syns("clever", "a"))
print("trick v:", syns("trick", "v"))
print("well n:", syns("well"))
print("king n:", syns("king"))
print("baital n:", syns("baital"))     # expect none — OOV handling
print("xyzzy n:", syns("xyzzy"))       # expect none

# Does pos='v' for noun-input words behave? (lemmatizer maps verbs already)
print("sleep n:", syns("sleep"))
print("sleep v:", syns("sleep", "v"))
