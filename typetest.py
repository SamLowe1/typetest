import curses
from ui import UI

def main(stdscr: curses.window) -> None:
    """
    Main entry point for the curses application.
    curses.wrapper calls this and handles initialization/cleanup.
    """
    app_ui = UI(stdscr)
    
    while True:
        # 1. Show Main Menu
        selection = app_ui.main_menu()
        if selection is None:
            break
        
        mode = selection.mode
        value = selection.value
        
        if mode is not None and value is not None:
            # 2. Run Typing Test
            result = app_ui.run_test(mode, value)
            
            # 3. Show Results (if test wasn't aborted)
            if result:
                app_ui.display_results(result)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C
        pass
