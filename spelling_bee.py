import random
import string
import os

class WrongAmountOfArguments(ValueError):
    pass

class Game:
    def __init__(self, 
    consonants, 
    vowels, 
    file_name, 
    min_words, 
    min_letters = 3,
    points_per_letter = 1,
    extra_for_all_letters = 3
    ):
        self.consonants = consonants
        self.vowels = vowels
        self.letters = consonants + vowels #temp
        self.file_name = file_name
        self.min_words = min_words
        self.min_letters = min_letters
        self.points_per_letter = points_per_letter
        self.extra_for_all_letters = extra_for_all_letters

        self.super_letter = ''
        self.picked_letters = []
        self.words = []
        self.found_words = []
        self.points = 0

    def delete_game(self):
        self.super_letter = ''
        self.picked_letters = []
        self.words = []
        self.found_words = []
        self.points = 0
    
    def pick_letters(self):
        self.delete_game()
        leftovers = []

        leftovers[:] = self.letters[:]
        rand = random.randint(0, len(leftovers)-1)
        self.super_letter = leftovers[rand]
        leftovers.remove(self.super_letter)
        for i in range(0,6):
            rand = random.randint(0, len(leftovers)-1)
            self.picked_letters.append(leftovers[rand])
            leftovers.remove(leftovers[rand])
        self.print_letters()

    def gen(self):
        self.pick_letters()
        self.generate_wordlist()

        while (len(self.words) < self.min_words):
            print("Regenerating...")
            self.pick_letters()
            self.generate_wordlist()
        
        print("Found %d words!" % (len(self.words)))

    def generate_wordlist(self):
        self.words = []

        allowed_letters = []
        allowed_letters[:] = self.picked_letters[:]
        allowed_letters += self.super_letter
        allowed_letters += string.whitespace
        allowed_letters += chr(10) #LF

        convert_letters = {
            chr(233):chr(101),         #é = e
            chr(232):chr(101),         #è = e
            chr(234):chr(101),         #ê = e
            chr(226):chr(int('096')),  #â = a
            chr(244):chr(111),         #ô = o
            chr(252):chr(117),         #ü = u
            chr(231):chr(int('099'))   #ç = c 
        }

        try:
            path = os.getcwd()
            path += '\\' 
            path += self.file_name
            list_file = open(path, 'r', encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError
        
        for line in list_file.readlines():
            if (len(line) < (self.min_letters + 1)): #letters + \n
                continue
            broken = False
            super = False

            for char in line.lower():
    
                if (char in convert_letters.keys()):
                    char = convert_letters[char]

                if (char not in allowed_letters):
                    broken = True
                    break
                else:
                    if (char in self.super_letter):
                        super = True

            if ((not broken) and (super)):
                self.words.append(line.strip())

        list_file.close()
    
    def check_word(self, word):
        if (word in self.words):
            if (word not in self.found_words):
                self.found_words.append(word)
                self.points += len(word)
                bonus = True
                for letter in (self.picked_letters):
                    if (letter not in word):
                        bonus = False
                        break
                if (bonus):
                    self.points += self.extra_for_all_letters
                    print("%s bonus points!" %self.extra_for_all_letters)
                print("%s is correct! +%d points! Total of %d points!" % (word, len(word), self.points))
            else:
                print("You have already found %s!" %(word))
        else:
            if (len(word) < self.min_letters):
                print ("%s is too short!" % word)
            if (self.super_letter in word):
                bad_letters = False
                for char in ''.join(sorted(set(word), key=word.index)):
                    if (char != self.super_letter and (char not in self.picked_letters)):
                        print ("%s contains the letter %s which is not in your picked letters!" %(word, char))
                        bad_letters = True
                if (not bad_letters):
                    print ("Word %s not found!" % word)
            else: 
                print ("%s does not include the super letter (%s)!" % (word, self.super_letter))

    def print_letters(self):
        print ("Letters: ", self.picked_letters)
        print ("Super: ", self.super_letter)

    def print_rules(self):
        print ("You must include the super letter in each word.")
        print ("You must use at least %s letters in each word." % self.min_letters)
        print ("Points per letter: %d." % self.points_per_letter)
        print ("Bonus points for using all letters: %d." % self.extra_for_all_letters)

    def print_score(self):
        print("You have a total of %d points!" % self.points)
class Menu:
    def __init__(self):
        self.choices = {}
        self.running = True

    def quit(self):
        self.running = False

    def add_choice(self, key, text, func, params_amount = 0):
        self.choices[key] = (text, func, params_amount)

    def print_choices(self):
        for key, value in self.choices.items():
            print("%s: %s" %(key, value[0]))
        
    def use_action(self, key, args = ''):
        if (key in self.choices.keys()):
            if (len(args) != self.choices[key][2]):
                raise WrongAmountOfArguments
            self.choices[key][1](*args)
        else:
            raise NotImplementedError

    def take_input(self):
        choice = input(">> ").strip().split()
        key = choice[0]
        if (len(choice) == 1):
            self.use_action(key)
        else:
            arguments = choice[1:]
            self.use_action(key, arguments)
        input()

    def run(self):
        self.add_choice('q','Quit',self.quit,0)
        while(self.running):
            self.print_choices()
            try:
                self.take_input()
            except FileNotFoundError:
                print ("Couldn't find the word file!")
            except NotImplementedError:
                print ("Couldn't find the command!")
            except WrongAmountOfArguments:
                print("Wrong amount of arguments!")

def main():
    consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 
    'q', 'r', 's', 't', 'v', 'w', 'x', 'z']
    vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'å', 'ä', 'ö']
    word_file = "swe_wordlist"
    min_words = 20

    game = Game(consonants,vowels,word_file, min_words)
    game.gen()

    menu = Menu()
    menu.add_choice('l',"Show Letters", game.print_letters)
    menu.add_choice('e', "Enter Word (i.e. 'e hello')", game.check_word, 1)
    menu.add_choice('f', "Show Found Words", lambda : print(game.found_words))
    menu.add_choice('c',"Show Words (cheating!)", lambda : print(game.words))
    menu.add_choice('g',"Regenerate Letters", game.gen)
    menu.add_choice('s',"Show Score", game.print_score)
    menu.add_choice('r',"Show Rules", game.print_rules)
    menu.run()

main()