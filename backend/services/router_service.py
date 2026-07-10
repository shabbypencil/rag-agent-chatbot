FAQ_PHRASES = {
    "annual pass": 3,
    "e-ticket": 3,
    "seat reservation": 3,
    "seat reservations": 3,
    "late arrival": 2,
    "rainy weather": 3,
    "severe weather": 3,
    "light rain": 2,
    "wheelchair rental": 3,
    "priority seating": 2,
    "car park": 2,
    "information counter": 2,
    "information counters": 2,
    "feeding session": 2,
    "feeding sessions": 2,
    "corporate event": 3,
    "corporate events": 3,
    "online booking": 2,
    "show seats": 2,
}

FAQ_KEYWORDS = {
    "ticket": 2,
    "tickets": 2,
    "admission": 2,
    "entry": 2,
    "bundle": 2,
    "bundles": 2,
    "membership": 3,
    "member": 2,
    "members": 2,
    "pass": 2,
    "passes": 2,
    "discount": 2,
    "discounts": 2,
    "student": 2,
    "senior": 2,
    "child": 1,
    "children": 1,
    "buy": 1,
    "purchase": 1,
    "book": 2,
    "booking": 2,
    "bookings": 2,
    "reserve": 1,
    "reservation": 2,
    "reservations": 2,
    "online": 1,
    "email": 1,
    "opening": 2,
    "open": 2,
    "close": 2,
    "closing": 2,
    "hours": 2,
    "timing": 2,
    "time": 1,
    "operate": 3,
    "operating": 3,
    "weather": 3,
    "rain": 3,
    "rainy": 3,
    "delayed": 2,
    "cancelled": 2,
    "transport": 2,
    "parking": 3,
    "mrt": 3,
    "bus": 2,
    "shuttle": 3,
    "taxi": 2,
    "food": 2,
    "meal": 2,
    "meals": 2,
    "refreshments": 2,
    "cafe": 2,
    "cafes": 2,
    "kiosk": 2,
    "kiosks": 2,
    "restaurant": 2,
    "restaurants": 2,
    "drink": 1,
    "accessibility": 3,
    "accessible": 3,
    "wheelchair": 3,
    "stroller": 3,
    "restroom": 2,
    "restrooms": 2,
    "locker": 3,
    "lockers": 3,
    "rental": 2,
    "rent": 2,
    "information": 1,
    "counter": 1,
    "counters": 1,
    "wifi": 3,
    "wi-fi": 3,
    "pet": 2,
    "pets": 2,
    "drone": 3,
    "drones": 3,
    "feed": 2,
    "seat": 1,
    "seats": 1,
    "late": 1,
    "corporate": 2,
    "event": 2,
    "events": 2,
    "function": 2,
    "functions": 2,
}

MANDAI_PHRASES = {
    "singapore zoo": 4,
    "river wonders": 4,
    "night safari": 4,
    "bird paradise": 4,
    "rainforest wild adventure": 4,
    "breakfast in the wild": 4,
    "once upon a river": 4,
    "creatures of the night": 4,
    "safari tram": 4,
    "tram ride": 2,
    "river keepers talk": 4,
    "into the wild": 4,
    "winged wonders": 4,
    "predators on wings": 4,
    "african lion": 4,
    "asian elephant": 4,
    "white tiger": 4,
    "giant panda": 4,
    "malayan tapir": 4,
    "clouded leopard": 4,
    "scarlet macaw": 4,
    "flying fox": 3,
    "green iguana": 4,
}

MANDAI_KEYWORDS = {
    "animal": 3,
    "animals": 3,
    "fact": 3,
    "facts": 3,
    "species": 3,
    "habitat": 3,
    "habitats": 3,
    "presentation": 3,
    "presentations": 3,
    "show": 2,
    "shows": 2,
    "zoo": 2,
    "safari": 2,
    "lion": 3,
    "elephant": 3,
    "tiger": 3,
    "panda": 3,
    "manatee": 3,
    "capybara": 3,
    "tapir": 3,
    "leopard": 3,
    "binturong": 3,
    "macaw": 3,
    "hornbill": 3,
    "flamingo": 3,
    "gibbon": 3,
    "iguana": 3,
    "nocturnal": 2,
    "conservation": 2,
    "endangered": 2,
    "diet": 2,
    "bamboo": 2,
    "mane": 2,
    "stripes": 2,
    "tram": 2,
    "otter": 2,
    "otters": 2,
    "bird": 2,
    "birds": 2,
    "parrot": 2,
    "reptile": 2,
    "mammal": 2,
    "mammals": 2,
}

AMBIGUOUS_TERMS = {
    "park", "parks", "time", "times", "family", "kids", "children"
}


def _score_text(query: str, phrases: dict[str, int], keywords: dict[str, int]) -> int:
    q = query.lower()
    score = 0

    for phrase, weight in phrases.items():
        if phrase in q:
            score += weight

    tokens = q.replace("?", " ").replace(",", " ").replace(".", " ").split()
    for token in tokens:
        if token in keywords:
            score += keywords[token]

    return score


def route_query(query: str) -> str:
    q = query.lower().strip()

    faq_score = _score_text(q, FAQ_PHRASES, FAQ_KEYWORDS)
    mandai_score = _score_text(q, MANDAI_PHRASES, MANDAI_KEYWORDS)

    tokens = set(q.replace("?", " ").replace(",", " ").replace(".", " ").split())
    if tokens and tokens.issubset(AMBIGUOUS_TERMS):
        return "hybrid"

    if faq_score == 0 and mandai_score == 0:
        return "hybrid"

    if faq_score > 0 and mandai_score > 0:
        if abs(faq_score - mandai_score) <= 2:
            return "hybrid"

    if faq_score > mandai_score:
        return "faq"

    if mandai_score > faq_score:
        return "mandai"

    return "hybrid"


def debug_route_query(query: str) -> dict:
    q = query.lower().strip()
    faq_score = _score_text(q, FAQ_PHRASES, FAQ_KEYWORDS)
    mandai_score = _score_text(q, MANDAI_PHRASES, MANDAI_KEYWORDS)
    route = route_query(query)

    return {
        "query": query,
        "faq_score": faq_score,
        "mandai_score": mandai_score,
        "route": route,
    }