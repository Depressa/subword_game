import json
import random
import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}
BUTTON_CLASS = "btn btn-grey wordblock-link changeable-word"

ENGLISH_WORDS_1000 = 'en_words_1000.txt'
ENGLISH_WORDS_10000 = 'en_words_10000.txt'
DEFAULT_JSON_NAME = 'default_dict.json'
USER_JSON_NAME = 'user_dict.json'

MINIMAL_LENGTH = 5
MINIMAL_AMOUNT = 8

class Word:
    """
    Class Word
    Args:
        word (str): generated word
        subwords (list):  list of word subwords
    """
    def __init__(self):
        """
        Create Word object, generate random word from json-file and find all its subwords
        """
        with open('default_dict.json', 'r') as openfile:
            json_object = json.load(openfile)
        self.word = random.choice(list(json_object.keys()))
        self.subwords = json_object[self.word]

    def check_word(self, word):
        """
        Check that user new word  including in subwords
        Args:
            word (str): player word
        Returns:
            bool: 1 if player  word in subwords, 0 otherwise
        """
        return word in self.subwords

    def count_words(self, min_length):
        """
        Calculate count of subwords. Returns one less because word is also in the list of subwords
        Returns:
            int: len of subwords
        """
        return len([i for i in self.subwords if len(i) > min_length]) - 1


class Player:
    """
    Class Player
    Args:
        name (str): the name of the player
        used_words (list): list of guessed words
    """
    def __init__(self, name):
        """
        Create Player object
        Args:
            name (str): the name of the player
        """
        self.name = name
        self.used_words = []

    def add_word(self, word):
        """
        Append new guessed word to used_words
        Args:
            word (str): users guessed word
        """
        self.used_words.append(word)

    def check_word(self, word):
        """
        Check that user new word not including in used_words
        Args:
            word (str): users word
        Returns:
            bool: 1 if word in used_words, 0 otherwise
        """
        return word in self.used_words

    def count_words(self):
        """
        Calculate count of guessed words
        Returns:
            int: count of guessed words
        """
        return len(self.used_words)

def generate_json(en_words=ENGLISH_WORDS_1000, min_len=MINIMAL_LENGTH, json_name=USER_JSON_NAME):
    """
    Writing dictionary file with words and subwords as a JSON representation
    Args:
        en_words (str, optional): txt-file name with words. Defaults to ENGLISH_WORDS_1000.
        min_len (int, optional): minimal subwords length. Defaults to MINIMAL_LENGTH.
        json_name (str, optional): json-file name with words and subwords. Defaults to USER_JSON_NAME.
    """
    english_dict = {}
    with open(en_words, 'r') as file:
        for line in file:
            word = line.rstrip('\n')
            if len(word) > min_len:
                response = requests.get(f"https://wordfinderx.com/words-for/{word}/?dictionary=all_en", headers=HEADERS)
                english_dict[word] = generate_subwords(response.text)
    json_object = json.dumps(english_dict, indent=4)
    with open(json_name, "w") as outfile:
        outfile.write(json_object)

def generate_subwords(text):
    """
    Generate a list of words from html-page
    Args:
        text (str): html-page
    Returns:
        list: list of word
    """
    soup = BeautifulSoup(text, 'html.parser')
    return [btn['data-word'] for btn in soup.find_all('button',class_= BUTTON_CLASS) if 'data-word' in btn.attrs]


def main():
    print("Hello! What's your name?")
    player = Player(input())
    word = Word()
    word_amount = min(MINIMAL_AMOUNT, word.count_words(MINIMAL_LENGTH))
    print(f"Let's play, {player.name}")
    print()
    print(f"Your need to make {word_amount} words from word '{word.word}'.")
    print(f"New words must be at least {MINIMAL_LENGTH - 1} letters long.")
    print("If you want to leave this game - write 'STOP'.")
    print("Good luck!")
    print()
    while len(player.used_words) < word_amount:
        new_word = input("Type your new word or 'STOP' to leave this game: ")
        if new_word == 'STOP':
            print(f"We will miss you {player.name}! You guessed only {player.count_words()} words!")
            return
        else:
            if len(new_word) < MINIMAL_LENGTH - 1:
                print("This is very short subword! Don't forget about rules! Try again.")
                print()
            elif new_word == word.word:
                print("Thought to cheat? We do not defend this word! Try again.")
                print()
            elif not word.check_word(new_word):
                print(f"This is incorrect subword! Don't forget your word - '{word.word}'. Try again.")
                print()
            elif player.check_word(new_word):
                print("You already guessed this word. Try again.")
                print()
            else:
                player.add_word(new_word)
                print(f"It's good subword! You guessed {player.count_words()} of {word_amount}! Let's go next.")
                print()

    print(f"All subwords are guessed! You are amazing {player.name}! Come and we'll play again!")

if __name__ == "__main__":
    main()
