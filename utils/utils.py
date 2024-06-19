PROMPT = "Enter choice "
INVALID = -1


class Utility:
    """Utility methods for decluttering the movie_app file, but really only
    very selectively - other static methods I had reasons to keep in that
    file. Readability is always a balance, right?"""
    @staticmethod
    def hold_up_for_enter():
        """Prompt for enter. Lets user read errors/results b4 next print"""
        input("\n(Press enter to continue)")

    @staticmethod
    def get_user_num_choice(menu: str, menu_len: int):
        """Called in a while True loop. Ensures valid selection."""
        print(menu)
        try:
            usr_input = int(input(f"{PROMPT}(0-{menu_len - 1}):\n> ").strip())
            if usr_input not in range(menu_len):
                print("Error: not on the menu! Try again!")
                Utility.hold_up_for_enter()
                return INVALID
        except ValueError:
            print("Error: menu choices must be entered as integers.")
            Utility.hold_up_for_enter()
            return INVALID
        return usr_input
