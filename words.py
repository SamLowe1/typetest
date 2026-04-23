import random
from typing import List, Generator

# A list of common English words (Top 200ish)
COMMON_WORDS: List[str] = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "I", "it", "for", "not", "on", "with", "he", "as", "you",
    "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my", "one",
    "all", "would", "there", "their", "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when",
    "make", "can", "like", "time", "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some",
    "could", "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
    "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any",
    "these", "give", "day", "most", "us", "water", "earth", "fire", "air", "sky", "green", "blue", "red", "yellow", "black",
    "white", "house", "road", "tree", "plant", "animal", "dog", "cat", "bird", "fish", "book", "page", "word", "letter",
    "number", "point", "line", "area", "side", "hand", "foot", "head", "body", "mind", "heart", "soul", "light", "dark",
    "night", "morning", "evening", "sun", "moon", "star", "cloud", "rain", "snow", "wind", "storm", "cold", "heat", "warm",
    "cool", "big", "small", "long", "short", "fast", "slow", "hard", "soft", "loud", "quiet", "near", "far", "high", "low",
    "young", "old", "rich", "poor", "happy", "sad", "good", "bad", "true", "false", "friend", "enemy", "love", "hate",
    "peace", "war", "life", "death", "begin", "end", "open", "close", "read", "write", "speak", "listen", "learn", "teach"
]

def generate_words(count: int) -> str:
    """Returns a string containing 'count' random common words joined by spaces."""
    return " ".join(random.choices(COMMON_WORDS, k=count))

def get_infinite_words() -> Generator[str, None, None]:
    """Generator that yields infinite random words."""
    while True:
        yield random.choice(COMMON_WORDS)
