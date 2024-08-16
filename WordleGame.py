import nltk
import pygame
from nltk.corpus import brown
import random
import string

nltk.download('brown')
word_list = brown.words()

# ChatGPT helped with these
white_block = '\u2B1C'  # White Large Square
yellow_block = '\U0001F7E8'  # Yellow Square
green_block = '\U0001F7E9'  # Green Square
black_block = '\u2B1B' # Black Square

max_guesses = 6
enlargen_dimension = 3
gap_width = 3
size_lower_bound = 3
size_upper_bound = 10
ascii_shift = 97

def play():
    n_letter_words = choose_word_size(word_list)
    is_hard_mode = choose_mode()
    rand_word = random.choice(n_letter_words)
    run_game(rand_word, n_letter_words, is_hard_mode)

def play_self(my_word):
    n_letter_words = [word.lower() for word in word_list if len(word) == len(my_word)]
    is_hard_mode = choose_mode()
    if my_word not in n_letter_words:
        raise AssertionError("This is not a valid word. Please choose something else.")
    run_game(my_word, n_letter_words, is_hard_mode)

def choose_word_size(word_list):
    word_size = int(input("\nPlease choose a word length from " + str(size_lower_bound) + " to " + str(size_upper_bound) + ": "))
    while word_size < size_lower_bound or word_size > size_upper_bound:
        word_size = int(input("Please keep the length between " + str(size_lower_bound) + " to " + str(size_upper_bound) + ": "))
    
    n_letter_words = [word.lower() for word in word_list if len(word) == word_size]
    return n_letter_words

def choose_mode():
    mode = (input("\nWould you like to play on hard mode? In hard mode, you must use previous hints in your next guess. Please type 'yes' if so, and anything else if not: ")).lower()
    print("\n")
    if mode == 'yes':
        return True
    else:
        return False

def run_game(word, n_letter_words, hard_mode):
    winning_output = green_block * len(word)
    keyboard = {letter: white_block for letter in string.ascii_lowercase}
    num_guesses = 0
    curr_output = ""
    total_output = ""
    curr_guess = ""
    duplicates = create_duplicate_tracker(word)
    while (num_guesses < max_guesses and curr_output != winning_output):
        num_guesses += 1
        curr_guess = guess_word(len(word), n_letter_words)
        if hard_mode:
            while not validate_guess(curr_guess, keyboard):
                print("This guess is not accepted in hard mode.\n")
                curr_guess = guess_word(len(word), n_letter_words)
        curr_output = output_result(curr_guess, word, duplicates.copy(), keyboard)
        en_curr_output = enlargen(curr_output, curr_guess)
        total_output = total_output + en_curr_output + "\n "
        print("\nOutput:\n " + total_output + "\n")
        print("Your Keyboard: " + str(keyboard) + "\n")
    
    if curr_output == winning_output:
        print("Congratulations! You won!")
    else:
        print("Sorry, you lost! The word was " + word + "!")

    return

def guess_word(word_size, n_letter_words):
    curr_guess = input("What is your current guess (" + str(word_size) + " letters)?: ")
    while len(curr_guess) != word_size or curr_guess.lower() not in n_letter_words:
        curr_guess = input("Please guess a valid " + str(word_size) + " letter word: ")
    return curr_guess.lower()

def validate_guess(guess, keyboard):
    for letter in guess:
        if keyboard[letter] == black_block:
            return False
    
    for letter in keyboard.keys():
        if (keyboard[letter] == green_block or keyboard[letter] == yellow_block) and letter not in guess:
            return False
        
    return True

def enlargen(result, guess):
    en_result = ""
    midpoint = (enlargen_dimension - 1) / 2
    for i in range(enlargen_dimension):
        for j in range(len(guess)):
            for k in range(enlargen_dimension):
                if i == midpoint and k == midpoint:
                    en_result = en_result + " " + guess[j].upper()
                else:
                    en_result += result[j]
            elem_gap = " " * gap_width
            en_result += elem_gap
        en_result += "\n "
    
    return en_result



def output_result(guess, word, w_duplicates, keyboard):
    result = ""
    g_duplicates = create_duplicate_tracker(guess)
    for i in range(len(guess) - 1, -1, -1):
        letter = guess[i]
        if letter not in word:
            result += black_block
            if keyboard[letter] == white_block:
                keyboard[letter] = black_block
        elif word[i] == letter:
            result += green_block
            keyboard[letter] = green_block
        elif g_duplicates[ord(letter) - ascii_shift] <= w_duplicates[ord(letter) - ascii_shift]:
            result += yellow_block
            g_duplicates[ord(letter) - ascii_shift] -= 1
            if keyboard[letter] == white_block:
                keyboard[letter] = yellow_block
        else:
            result += black_block
            g_duplicates[ord(letter) - ascii_shift] -= 1
            if keyboard[letter] == white_block:
                keyboard[letter] = black_block
    return result[::-1]

def create_duplicate_tracker(word):
    result = [-1] * 26
    for letter in word:
        result[ord(letter) - ascii_shift] += 1
    return result

play()
