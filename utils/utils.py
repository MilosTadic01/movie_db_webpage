class Utility:
    """Utility methods for decluttering movie_app."""
    @staticmethod
    def hold_up_for_enter():
        """Prompt for enter. Lets user read errors/results b4 next print"""
        input("\n(Press enter to continue)")

    @staticmethod
    def get_user_num_choice(menu: str, menu_len: int):
        """Called in a while True loop. Ensures valid selection."""
        print(menu)
        try:
            usr_input = int(input(f"Enter choice (0-{menu_len - 1}): "))
            if usr_input not in range(menu_len):
                print("Error: not on the menu! Try again!")
                Utility.hold_up_for_enter()
                return -1
        except ValueError:
            print("Error: menu choices must be entered as integers.")
            Utility.hold_up_for_enter()
            return -1
        return usr_input
