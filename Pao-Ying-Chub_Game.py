import random as rd
import pandas as pd

def pao_ying_chub_game():
    welcome = """Welcome to the funny time!
    This is the era game that called ROCK PAPER SCIRRORS GAME.
    You will guess answer from rock or scirrors or paper.
    """
    items = ["rock", "scirrors", "paper"]
    print(welcome)
    name = input("What's your name?: ")
    ready = input(f"Hi {name}! Are you ready to start? (y/n): ")
    if ready.lower() == "y":
        rounds = []
        answers = []
        checks = []
        results = []
        round = 0
        win = 0
        draw = 0
        lose = 0
        print("If you want to quit the game, please print exit")
        while True:
            round += 1
            rounds.append(round)
            check = rd.choice(items)
            checks.append(check)
            guess = input("Guess the answer: ")
            answers.append(guess)
            if guess.lower() == "exit":
                rounds.pop()
                checks.pop()
                answers.pop()
                data = {
                    "round": rounds,
                    "Answer": answers,
                    "Check": checks,
                    "Result": results
                }
                df = pd.DataFrame(data)
                summary = f"""Logs your answer \n {df}
                Game summary:
                Win = {win}
                Lose = {lose}
                Draw = {draw}
                Thank you for join with me.
                """
                print(summary)
                #print(f"Logs your answer\n {df}")
                #print("Thank you for join with me")
                break
            elif guess.lower() == items[0]:
                if check == items[0]:
                    print("Draw! Try again.")
                    results.append("Draw")
                    draw += 1
                elif check == items[1]:
                    print("Hooray! Your guess correctly.")
                    results.append("Win")
                    win += 1
                elif check == items[2]:
                    print("Lose! please try again.")
                    results.append("Lose")
                    lose += 1
            elif guess.lower() == items[1]:
                if check == items[0]:
                    print("Lose! please try again.")
                    results.append("Lose")
                    lose += 1
                elif check == items[1]:
                    print("Draw! Try again.")
                    results.append("Draw")
                    draw += 1
                elif check == items[2]:
                    print("Hooray! Your guess correctly.")
                    results.append("Win")
                    win += 1
            elif guess.lower() == items[2]:
                if check == items[0]:
                    print("Hooray! Your guess correctly.")
                    results.append("Win")
                    win += 1
                elif check == items[1]:
                    print("Lose! please try again.")
                    results.append("Lose")
                    lose += 1
                elif check == items[2]:
                    print("Draw! Try again.")
                    results.append("Draw")
                    draw += 1
            else:
                rounds.pop()
                answers.pop()
                checks.pop()
                print("Your guess is NOT match, please try again!")
    else :
        print("Thank you for coming.")

pao_ying_chub_game()
