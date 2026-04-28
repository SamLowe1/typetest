from itertools import groupby
import curses
import time
from typing import Any, Optional, List, Tuple, Union
from engine import TypeTestEngine, Result
import words

class Theme:
    """Represents a color theme. Each attribute is an index in curses.color_pair()."""
    def __init__(self, correct: int, wrong: int, default: int) -> None:
        self.correct = correct
        self.wrong = wrong
        self.default = default

class Test:
    """Represents a typing test configuration."""
    def __init__(self, mode: str, value: int):
        self.mode = mode
        self.value = value

class MenuOption:
    """Represents an entry in a menu."""
    def __init__(self, text: str, type: str | None = None, test: Test | None = None):
        self.text = text
        self.type = type
        self.test = test

class UI:
    def __init__(self, stdscr: curses.window) -> None:
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.THEMES = dict()
        
        # Setup color themes
        self.init_color_themes()
        self.set_color_theme(self.THEMES["dark"])
        
        curses.curs_set(0)

    def init_colors(self) -> None:
        # Setup colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)  # Correct dark
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Incorrect dark
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # default light
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE) # incorrect light
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_WHITE) # default light
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_RED) # SUPER WRONG

    def init_color_themes(self) -> None:
        self.init_colors()

        # light
        default = curses.color_pair(3)
        wrong = curses.color_pair(4)
        correct = curses.color_pair(5)
        self.THEMES["light"] = Theme(correct=correct, wrong=wrong, default=default)

        # dark
        default = curses.color_pair(0)
        wrong = curses.color_pair(2)
        correct = curses.color_pair(1)
        self.THEMES["dark"] = Theme(correct=correct, wrong=wrong, default=default)

    def draw_centered_text(self, y: int, text: str, color: int = 0) -> None:
        x = max(0, (self.width - len(text)) // 2)
        if 0 <= y < self.height and 0 <= x < self.width:
            try:
                self.stdscr.addstr(y, x, text[:self.width-x], color)
            except curses.error:
                pass

    def get_input(self, prompt: str) -> Optional[int]:
        """Gets a numeric input from the user."""
        self.stdscr.nodelay(False)
        curses.curs_set(1)
        input_str = ""
        while True:
            self.stdscr.erase()
            self.draw_centered_text(self.height // 2 - 1, prompt)
            self.draw_centered_text(self.height // 2 + 1, input_str)
            self.stdscr.refresh()
            
            ch = self.stdscr.getch()
            if ch in [10, 13]: # Enter
                break
            elif ch in [curses.KEY_BACKSPACE, 127, 8]:
                input_str = input_str[:-1]
            elif ord('0') <= ch <= ord('9'):
                if len(input_str) < 5: # Limit length
                    input_str += chr(ch)
            elif ch == 27: # ESC
                curses.curs_set(0)
                return None
        
        curses.curs_set(0)
        return int(input_str) if input_str else None

    def display_menu(self, label: str, options: List[MenuOption]) -> Optional[MenuOption]:
        """Displays a menu and returns the selected MenuOption or None."""
        current_selection = 0
        curses.curs_set(0)

        while True:
            self.stdscr.erase()
            self.height, self.width = self.stdscr.getmaxyx()
            
            self.draw_centered_text(self.height // 2 - 4, f"=== {label} ===", curses.A_BOLD)
            
            for i, option in enumerate(options):
                style = curses.A_REVERSE if i == current_selection else 0
                self.draw_centered_text(self.height // 2 - 1 + i, option.text, style)

            self.stdscr.refresh()
            
            key = self.stdscr.getch()
            if key == curses.KEY_UP:
                current_selection = (current_selection - 1) % len(options)
            elif key == curses.KEY_DOWN:
                current_selection = (current_selection + 1) % len(options)
            elif key in [10, 13]: # Enter
                return options[current_selection]
            elif key == ord('q') or key == 27: # q or ESC
                return None

    def get_custom_selection(self) -> Optional[Test]:
        """Runs a setup wizard to create custom typing conditions."""
        mode_choice = self.display_menu(
            "SELECT MODE", [MenuOption("Time", "time"), MenuOption("Words", "words")])
        if not mode_choice or not mode_choice.type:
            return None
        
        mode = mode_choice.type
        prompt = f"Enter number of {'seconds' if mode == 'time' else 'words'}:"
        value = self.get_input(prompt)
        
        if value is None or value <= 0:
            return None
            
        return Test(mode, value)

    def main_menu(self) -> Optional[Test]:
        options = [
            MenuOption("Presets", "preset"),
            MenuOption("Custom Test", "custom"),
            MenuOption("Select Color Theme", "color"),
            MenuOption("Exit", "exit")
        ]
        
        selection = self.display_menu("TERMINAL TYPE TEST", options)

        if not selection or selection.type == "exit":
            return None
        
        if selection.type == "preset":
            return self.get_preset_selection()
        
        if selection.type == "custom":
            return self.get_custom_selection()
        if selection.type == "color":
            color_theme = self.theme_menu()
            self.set_color_theme(color_theme)
            return self.main_menu()
            
        return selection.test
    
    def get_preset_selection(self) -> Test | None:
        options = [
            MenuOption("Time Test (30s)", "test", Test("time", 30)),
            MenuOption("Time Test (60s)", "test", Test("time", 60)),
            MenuOption("Words Test (25 words)", "test", Test("words", 25)),
            MenuOption("Words Test (50 words)", "test", Test("words", 50)),
        ]

        selection = self.display_menu("Choose a Preset", options)
        
        if selection and selection.test: return selection.test
        else: return None

    def set_color_theme(self, theme: Theme) -> None:
        self.COLOR_CORRECT = theme.correct
        self.COLOR_DEFAULT = theme.default
        self.COLOR_WRONG = theme.wrong
    
    def theme_menu(self) -> Theme:
        theme_options = [
            MenuOption("Dark Mode", "dark"),
            MenuOption("Light Mode (WIP)", "light")
        ]

        selection = self.display_menu("Select Color Theme", theme_options)

        if (selection is None):
            return self.THEMES["dark"]

        color_theme = self.THEMES[selection.type]
        return color_theme

    def _draw_stats(self, engine: TypeTestEngine) -> None:
        """Draws the status bar at the top."""
        elapsed = engine.get_elapsed_time()
        wpm = engine.get_wpm()
        
        if engine.mode == "time":
            stats = f"Time: {max(0, engine.limit - elapsed):.1f}s | WPM: {wpm:.1f}"
        else:
            progress = (len(engine.user_input) / len(engine.target_text)) * 100
            stats = f"Progress: {progress:.0f}% | WPM: {wpm:.1f}"
        
        self.stdscr.addstr(0, 0, stats, curses.A_DIM)
        self.stdscr.addstr(1, 0, "-" * self.width)

    def _render_text(self, engine: TypeTestEngine) -> Tuple[int, int]:
        """Renders the target text with highlighting and returns the cursor position."""
        y_offset, x_offset = 4, 2
        curr_x, curr_y = x_offset, y_offset
        cursor_pos = (curr_y, curr_x)
        
        word_list = engine.target_text.split(' ')
        char_idx = 0
        
        for word_idx, word in enumerate(word_list):
            full_word = word + (" " if word_idx < len(word_list) - 1 else "")
            
            if curr_x + len(word) > self.width - 2:
                curr_x = x_offset
                curr_y += 1
            
            if curr_y >= self.height - 1:
                break

            for char in full_word:
                color = self.COLOR_DEFAULT
                if char_idx < len(engine.user_input):
                    color = self.COLOR_CORRECT if engine.user_input[char_idx] == char else self.COLOR_WRONG
                    # if the character is a space, we set the color to SUPER WRONG so it's visible
                    if (char == ' ' and color == self.COLOR_WRONG):
                        # color = curses.color_pair(6)
                        char = '•'
                elif char_idx == len(engine.user_input):
                    cursor_pos = (curr_y, curr_x)

                try:
                    self.stdscr.addch(curr_y, curr_x, char, color)
                except curses.error:
                    pass
                
                curr_x += 1
                char_idx += 1
        
        return cursor_pos

    def run_test(self, test: Test) -> Optional[Result]:
        """Runs the typing test loop."""
        if test.mode == "words":
            target_text = words.generate_words(test.value)
        else:
            target_text = words.generate_words(200) 
        
        target_text = ' '.join(k for k, _ in groupby(target_text.split()))
        engine = TypeTestEngine(target_text, test.mode, test.value)
        
        self.stdscr.nodelay(True)
        curses.curs_set(1)
        
        while True:
            self.stdscr.erase()
            self.height, self.width = self.stdscr.getmaxyx()
            
            self._draw_stats(engine)
            cursor_pos = self._render_text(engine)
            
            self.stdscr.move(*cursor_pos)
            self.stdscr.refresh()

            try:
                key = self.stdscr.getkey()
                if key == '\x1b': # ESC
                    engine.stop()
                    return None
                if engine.process_key(key):
                    engine.stop()
                    return engine.get_result()
            except curses.error:
                if engine.is_finished():
                    engine.stop()
                    return engine.get_result()
                time.sleep(0.01)

    def display_results(self, result: Result) -> None:
        """Displays the result screen with a grace period."""
        start_time = time.time()
        curses.curs_set(0)
        while True:
            self.stdscr.erase()
            self.height, self.width = self.stdscr.getmaxyx()
            mid_y = self.height // 2
            
            self.draw_centered_text(mid_y - 4, "=== TEST RESULTS ===", curses.A_BOLD)
            self.draw_centered_text(mid_y - 2, f"WPM: {result.wpm:.1f}", self.COLOR_CORRECT)
            self.draw_centered_text(mid_y - 1, f"Accuracy: {result.accuracy:.1f}%")
            self.draw_centered_text(mid_y, f"Mistakes: {result.mistakes}", self.COLOR_WRONG)
            self.draw_centered_text(mid_y + 2, "Press any key to return to menu")
            
            self.stdscr.refresh()
            
            if time.time() - start_time < 1.0:
                self.stdscr.nodelay(True)
                self.stdscr.getch()
                time.sleep(0.05)
                continue
            
            self.stdscr.nodelay(False)
            curses.flushinp()
            self.stdscr.getch()
            return
