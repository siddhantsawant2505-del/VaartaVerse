import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.inverted_index import InvertedIndex
from app.core.vsm_engine import VSMEngine
from app.core.nl_parser import NLQueryParser

index = InvertedIndex()
index.load()
vsm = VSMEngine(index)
parser = NLQueryParser()

queries = [
    "stories of akbar and birbal",
    "tenali rama horse grass",
    "hanuman brings sanjeevani mountain for lakshmana",
    "yaksha prashna riddles of the pool",
    "ekalavya archery thumb guru dakshina",
    "brahmin mongoose snake",
    "blue jackal indigo vat",
]

for q in queries:
    p = parser.parse(q)
    filters = p.get("filters", {})
    res = vsm.search(
        p["normalized_query"] or q,
        top_k=2,
        collection_filter=filters.get("tradition"),
    )
    print(f'Query: "{q}"')
    print(f'  Mode: {p["mode"]}, Detected Tradition: {filters.get("tradition")}')
    for r in res:
        print(f'  -> [{r["tale_id"]}] {r["title"]} ({r["tradition"]}) score={r["score"]}')
    print()
