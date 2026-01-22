## script.rpy - Baseline Test Game
##
## Tests: quit functionality, dialog boxes, basic navigation

label start:
    # Jump to theme test - comment this out to run normal game
    jump theme_test_start

label start_original:
    scene bg_welcome with dissolve

    "Welcome to the Paradigm Project test game."

    guide "I'm the Guide. I'll help you test the features."

    guide "First, let's test the QUIT functionality."
    guide "Click the X button on the window now."
    guide "You should see a custom quit message."

    menu:
        "Did the quit dialog work correctly?"

        "Yes, it showed the warning message":
            guide "Great! The quit functionality is working."

        "No, it just reset the game":
            guide "There's still an issue. Check options.rpy"

    guide "Now let's test dialog boxes."

    "This is the narrator using default.png"

    guide "This is Guide using guide.png (or default fallback)"

    novy "This is Novy using novy.png (or default fallback)"

    guide "Test complete!"

    menu:
        "What would you like to do?"

        "Run test again":
            jump start

        "Exit":
            guide "Goodbye!"
            return
