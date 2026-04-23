import time
from typing import Optional

class Result:
    def __init__(self, wpm: float, accuracy: float, mistakes: int, total_chars: int) -> None:
        self.wpm = wpm
        self.accuracy = accuracy
        self.mistakes = mistakes
        self.total_chars = total_chars

    def __str__(self) -> str:
        return f"WPM: {self.wpm:.1f} | Accuracy: {self.accuracy:.1f}% | Mistakes: {self.mistakes}"

class TypeTestEngine:
    def __init__(self, target_text: str, mode: str, limit: int) -> None:
        self.target_text = target_text
        self.mode = mode  # "time" or "words"
        self.limit = limit
        self.user_input = ""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.mistakes = 0
        self.total_keypresses = 0

    def start(self) -> None:
        self.start_time = time.time()

    def stop(self) -> None:
        self.end_time = time.time()

    def process_key(self, char: str) -> bool:
        """Processes a single keystroke. Returns True if the test should end."""
        if self.start_time is None:
            self.start()

        if char == "KEY_BACKSPACE" or char == "\b" or char == "\x7f":
            if len(self.user_input) > 0:
                self.user_input = self.user_input[:-1]
        elif len(char) == 1:
            # Check if this is a mistake before appending
            current_index = len(self.user_input)
            if current_index < len(self.target_text):
                if char != self.target_text[current_index]:
                    self.mistakes += 1
                self.user_input += char
                self.total_keypresses += 1

        return self.is_finished()

    def is_finished(self) -> bool:
        if self.mode == "words":
            return len(self.user_input) >= len(self.target_text)
        elif self.mode == "time":
            if self.start_time is None:
                return False
            return (time.time() - self.start_time) >= self.limit
        return False

    def get_elapsed_time(self) -> float:
        if self.start_time is None:
            return 0.0
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def get_wpm(self) -> float:
        elapsed = self.get_elapsed_time()
        if elapsed <= 0:
            return 0.0
        # WPM = (chars / 5) / (seconds / 60)
        words = len(self.user_input) / 5
        minutes = elapsed / 60
        return words / minutes

    def get_accuracy(self) -> float:
        if self.total_keypresses == 0:
            return 100.0
        correct = max(0, self.total_keypresses - self.mistakes)
        return (correct / self.total_keypresses) * 100.0

    def get_result(self) -> Result:
        return Result(
            wpm=self.get_wpm(),
            accuracy=self.get_accuracy(),
            mistakes=self.mistakes,
            total_chars=len(self.user_input)
        )
