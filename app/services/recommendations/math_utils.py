"""Pure math helpers for content-based similarity. No DB or HTTP here."""

import math


def compute_idf(all_games_features: list[set[str]]) -> dict[str, float]:
    """Inverse document frequency for each feature across the catalog.

    Rare features (present on few games) get a high idf; near-universal
    features (e.g. tags present on almost every game) get a low one. The +1
    in the denominator avoids division by zero for a feature on every game.
    """
    total_games = len(all_games_features)

    document_counts: dict[str, int] = {}
    for game_features in all_games_features:
        for feature in game_features:
            document_counts[feature] = document_counts.get(feature, 0) + 1

    return {
        feature: math.log(total_games / (1 + count))
        for feature, count in document_counts.items()
    }


def build_profile(weighted_features: list[dict[str, float]]) -> dict[str, float]:
    """Sum per-feature weights across games, then L2-normalize the result."""
    profile: dict[str, float] = {}
    for game_features in weighted_features:
        for feature, weight in game_features.items():
            profile[feature] = profile.get(feature, 0.0) + weight

    return _normalize(profile)


def cosine_similarity(profile: dict[str, float], candidate_features: dict[str, float]) -> float:
    """Cosine similarity between a normalized profile and a candidate's weighted vector.

    Both sides are real-valued (IDF-weighted) vectors, normalized the same
    way. Returns 0.0 if there's no feature overlap.
    """
    if not candidate_features:
        return 0.0

    candidate_vector = _normalize(candidate_features)

    shared_features = profile.keys() & candidate_vector.keys()
    if not shared_features:
        return 0.0

    return sum(profile[feature] * candidate_vector[feature] for feature in shared_features)


def top_contributing_features(
    profile: dict[str, float], candidate_features: dict[str, float], n: int = 3
) -> list[str]:
    """The n features (shared by profile and candidate) with the highest combined weight."""
    shared_features = profile.keys() & candidate_features.keys()
    return sorted(
        shared_features,
        key=lambda feature: profile[feature] * candidate_features[feature],
        reverse=True,
    )[:n]


def _normalize(vector: dict[str, float]) -> dict[str, float]:
    """L2-normalize a sparse vector represented as a dict."""
    norm = math.sqrt(sum(weight * weight for weight in vector.values()))
    if norm == 0:
        return dict(vector)
    return {feature: weight / norm for feature, weight in vector.items()}
