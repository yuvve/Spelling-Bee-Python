import random
import string
import os


class WrongAmountOfArguments(ValueError):
    pass


class WordAlreadyFound(Exception):
    pass


class WordNotFound(Exception):
    pass


class WordTooShort(Exception):
    pass


class BadLetters(Exception):
    def __init__(self, letters):
        self.letters = letters


class NoSuperLetter(Exception):
    pass


class Game:
    def __init__(
        self,
        consonants,
        vowels,
        file_name,
        min_words,
        min_letters=3,
        points_per_letter=1,
        bonus_points=3,
        min_bonus_words=0,
    ):
        self.consonants = consonants
        self.vowels = vowels
        self.letters = consonants + vowels  # temp
        self.file_name = file_name
        self.min_words = min_words
        self.min_letters = min_letters
        self.points_per_letter = points_per_letter
        self.bonus_points = bonus_points
        self.min_bonus_words = min_bonus_words

        self.super_letter = ""
        self.picked_letters = []
        self.words = []
        self.found_words = []
        self.points = 0
        self.bonus_words = 0

    def delete_game(self):
        self.super_letter = ""
        self.picked_letters = []
        self.words = []
        self.found_words = []
        self.points = 0
        self.bonus_words = 0

    def pick_letters(self, letters, amount_of_letters):
        leftovers = []
        leftovers[:] = letters[:]
        picked_letters = []
        while len(picked_letters) < amount_of_letters:
            rand = random.randint(0, len(leftovers) - 1)
            picked_letters.append(leftovers[rand])
            leftovers.remove(leftovers[rand])
        return picked_letters

    def generate_wordlist(self, picked_letters, super_letter, file_name, min_letters):
        words = []
        allowed_letters = []
        allowed_letters[:] = picked_letters[:]
        allowed_letters += super_letter
        allowed_letters += string.whitespace
        allowed_letters += chr(10)  # LF

        convert_letters = {
            chr(233): chr(101),  # é = e
            chr(232): chr(101),  # è = e
            chr(234): chr(101),  # ê = e
            chr(226): chr(int("096")),  # â = a
            chr(244): chr(111),  # ô = o
            chr(252): chr(117),  # ü = u
            chr(231): chr(int("099")),  # ç = c
        }

        try:
            path = os.getcwd()
            path += "\\"
            path += file_name
            list_file = open(path, "r", encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError

        for line in list_file.readlines():
            if len(line.strip()) < (min_letters):
                continue
            broken = False
            super = False
            for char in line.lower():
                if char in convert_letters.keys():
                    char = convert_letters[char]
                if char not in allowed_letters:
                    broken = True
                    break
                else:
                    if char in super_letter:
                        super = True
            if (not broken) and (super):
                word = line.strip()
                words.append(word)
        list_file.close()
        return words

    def all_letters_check(self, word, letters):
        for letter in letters:
            if letter not in word:
                return False
        return True

    def count_bonus_words(self, words, letters):
        counter = 0
        for word in words:
            if self.all_letters_check(word, letters):
                counter += 1
        return counter

    def check_a_word(self, word, words, found_words):
        if word in words:
            if word not in found_words:
                return True
            else:
                raise WordAlreadyFound
        else:
            raise WordNotFound

    # This function assumes that "word" is a correct answer
    def count_points(self, word, picked_letters, super_letter, bonus_points):
        points = len(word)
        bonus = 0
        if self.all_letters_check(word, picked_letters + [super_letter]):
            bonus = bonus_points
        return (points, bonus)

    def why_word_bad(self, word, min_letters, super_letter, picked_letters):
        if len(word) < min_letters:
            raise WordTooShort
        if super_letter in word:
            bad_letters = []
            for char in "".join(sorted(set(word), key=word.index)):
                if char != super_letter and (char not in picked_letters):
                    bad_letters.append(char)
            if len(bad_letters) > 0:
                raise BadLetters(bad_letters)
            else:
                raise WordNotFound
        else:
            raise NoSuperLetter

    # User interface functions

    def check_word(self, word):
        try:
            if self.check_a_word(word, self.words, self.found_words):
                points, bonus = self.count_points(
                    word, self.picked_letters, self.super_letter, self.bonus_points
                )
                if bonus > 0:
                    print(
                        "%s is worth %d points +%d for using all letters!"
                        % (word, points, bonus)
                    )
                else:
                    print("%s is worth %d points!" % (word, points))
                self.points += points + bonus
                self.found_words.append(word)
            else:
                self.why_word_bad(
                    word, self.min_letters, self.super_letter, self.picked_letters
                )
        except WordAlreadyFound:
            print("You have already found %s!" % word)
        except WordNotFound:
            try:
                self.why_word_bad(
                    word, self.min_letters, self.super_letter, self.picked_letters
                )
            except NoSuperLetter:
                print(
                    "%s does not include the super letter (%s)!"
                    % (word, self.super_letter)
                )
            except WordTooShort:
                print("%s is too short!" % word)
            except BadLetters as e:
                for letter in e.letters:
                    print(
                        "%s contains the letter %s which is not in your picked letters!"
                        % (word, letter)
                    )
            except WordNotFound:
                print("%s not found!" % word)

    def gen(self):
        self.delete_game()
        self.picked_letters = self.pick_letters(self.letters, 7)
        self.super_letter = self.pick_letters(self.picked_letters, 1)[0]
        self.picked_letters.remove(self.super_letter)
        self.words = self.generate_wordlist(
            self.picked_letters, self.super_letter, self.file_name, self.min_letters
        )
        self.bonus_words = self.count_bonus_words(
            self.words, self.picked_letters + [self.super_letter]
        )
        self.print_letters()
        print(
            "Found %d words (with %d all-letter words)!"
            % (len(self.words), self.bonus_words)
        )

    def find_board(self):
        while (len(self.words) < self.min_words) or (
            self.bonus_words < self.min_bonus_words
        ):
            print("Generating...")
            self.gen()

    def print_letters(self):
        print("Letters: ", self.picked_letters)
        print("Super: ", self.super_letter)

    def print_rules(self):
        print("You must include the super letter in each word.")
        print("You must use at least %s letters in each word." % self.min_letters)
        print("Points per letter: %d." % self.points_per_letter)
        print("Bonus points for using all letters: %d." % self.bonus_points)

    def print_score(self):
        print("You have a total of %d points!" % self.points)


class Menu:
    def __init__(self):
        self.choices = {}
        self.running = True

    def quit(self):
        self.running = False

    def add_choice(self, key, text, func, params_amount=0):
        self.choices[key] = (text, func, params_amount)

    def print_choices(self):
        for key, value in self.choices.items():
            print("%s: %s" % (key, value[0]))

    def use_action(self, key, args=""):
        if key in self.choices.keys():
            if len(args) != self.choices[key][2]:
                raise WrongAmountOfArguments
            self.choices[key][1](*args)
        else:
            raise NotImplementedError

    def take_input(self):
        choice = input(">> ").strip().split()
        key = choice[0]
        if len(choice) == 1:
            self.use_action(key)
        else:
            arguments = choice[1:]
            self.use_action(key, arguments)
        input()

    def run(self):
        self.add_choice("q", "Quit", self.quit, 0)
        while self.running:
            self.print_choices()
            try:
                self.take_input()
            except FileNotFoundError:
                print("Couldn't find the word file!")
            except NotImplementedError:
                print("Couldn't find the command!")
            except WrongAmountOfArguments:
                print("Wrong amount of arguments!")


def main():
    consonants = [
        "b",
        "c",
        "d",
        "f",
        "g",
        "h",
        "j",
        "k",
        "l",
        "m",
        "n",
        "p",
        "q",
        "r",
        "s",
        "t",
        "v",
        "w",
        "x",
        "z",
    ]
    vowels = ["a", "e", "i", "o", "u", "y", "å", "ä", "ö"]
    word_file = "swe_wordlist"
    min_words = 20
    min_letters = 3
    points_per_letter = 1
    bonus_points = 3
    min_bonus_words = 0

    game = Game(
        consonants,
        vowels,
        word_file,
        min_words,
        min_letters,
        points_per_letter,
        bonus_points,
        min_bonus_words,
    )
    game.find_board()

    menu = Menu()
    menu.add_choice("l", "Show Letters", game.print_letters)
    menu.add_choice("e", "Enter Word (i.e. 'e hello')", game.check_word, 1)
    menu.add_choice("f", "Show Found Words", lambda: print(game.found_words))
    menu.add_choice("c", "Show Words (cheating!)", lambda: print(game.words))
    menu.add_choice("g", "Regenerate Letters", game.gen)
    menu.add_choice("s", "Show Score", game.print_score)
    menu.add_choice("r", "Show Rules", game.print_rules)
    menu.run()


main()
