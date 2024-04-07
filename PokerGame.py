from random import random
import itertools
import os

# Main class 
class Poker_Game:
    positions = {0: "Small Blind", 1: "Big Blind", -1: "Dealer"}
    game_states = ['Preflop', 'Flop', 'Turn', 'River', 'Postriver']

    # Sets up necessary variables and runs the game
    def __init__(self):
        self.pot = 0
        self.players = []
        self.board = []
        self.current_bet = 0
        self.run()
    
    # Bets the blinds at the start of each round, accounting for all-ins
    def bet_blinds(self, bb_amount):
        small_blind = self.players[0]
        big_blind = self.players[1]
        
        small_is_all_in = False
        big_is_all_in = False
        
        if small_blind.get_chips() < bb_amount // 2:
            small_is_all_in = True
        if big_blind.get_chips() < bb_amount:
            big_is_all_in = True
        
        self.players[0].bet(bb_amount // 2, self, small_is_all_in)
        self.players[1].bet(bb_amount, self, big_is_all_in)
        self.current_bet = bb_amount
    
    # Adds chips to the pot
    def add_to_pot(self, amount):
        self.pot += amount
    
    # Resets all variables for a new round
    def reset(self):
        self.pot = 0
        self.board = []
        self.current_bet = 0
    
    # Players with 0 chips can get new buy-ins at the end of each round
    def buy_ins(self):
        for player in self.players:
            if player.get_chips() == 0:
                choice = input(player.name + ", you are out of chips. Will you continue playing?" +
                               " Please choose 'True' or 'False'.").lower()            
                while choice not in ['true', 'false']:
                    choice = input("Please choose 'True' or 'False':\t").lower()  # Convert input to lowercase
                if choice == 'false':
                    self.players.remove(player)
                else:
                    num_chips = int(input("How many chips will you buy in for?:\t"))            
                    while num_chips <= 0:
                        new_game = int(input("Please choose a valid number of chips:\t")) 
                    player.buy_in(num_chips)
    
    # Players with chips can cash out at the end of each round
    def cash_outs(self):
        cashing_out = True
        while(cashing_out):
            cash_outer = input('Would any player like to cash_out? Please type your name:\t').lower()
            if cash_outer in [player.name.lower() for player in self.players]:
                cashing_player = [player for player in self.players if player.name.lower() == cash_outer][0]
                cashing_player.cash_out()
                self.players.remove(cashing_player)
            else:
                cashing_out = False

    # Ends the game if one player left, otherwise resets necessary variables and moves on to the next game state
    def end_game_state(self, deck, num_cards_to_deal):
        os.system('cls')
        for player in self.players:
            player.reset_chips()
            self.players = [player for player in self.players if not player.folded]
            if len(self.players) == 1:
                print("\nCongratulations " + self.players[0].name + ", you won the hand!")
                self.players[0].receive_chips(self.pot)
                self.players[0].win()
                print(self.players[0])
                return True
                    
        for i in range(num_cards_to_deal):
            self.board.append(deck.deal())
                    
        self.current_bet = 0
        return False
    
    
    # Main method for users to bet, raise, call, fold during each game state
    def betting_round(self, i, last_actor):
        previous_action = ''
        while i < last_actor:
            os.system('cls')
            current_player = self.players[i % len(self.players)]
            print(previous_action)
            if current_player.in_play():
                only_desired_player = input("The current player is " + current_player.name + 
                                            ". All others leave the computer!\nWhen " + 
                                            current_player.name + " is the only one at the computer," +
                                            " please type in 'Here':\t").lower()
                while only_desired_player != 'here':
                    only_desired_player = input("\nAll others leave!\nWhen " + current_player.name +
                                                " is the only one here, type 'Here':\t").lower()
                
                print("\nThe Board is:")
                for card in self.board:
                    print(card)
                print(current_player.display_hand())
                print("The Pot has " + str(self.pot) + " chips.")
                temp = self.current_bet

                if self.current_bet == 0:
                    choice = self.player_choice(False, current_player)
                    previous_action = choice[0]
                    self.current_bet = choice[1]
                else:
                    choice = self.player_choice(True, current_player)
                    previous_action = choice[0]
                    self.current_bet = choice[1]
                            
                if self.current_bet > temp:
                    last_actor = i + len(self.players)
            i += 1
        
        print(previous_action)
        

    # Players make their choice of either betting, calling, raising, or folding
    def player_choice(self, currently_bet, player, preflop_big = False):
        print(player.name + ", you currently have " + str(player.get_chips()) + " chips.")
        if preflop_big:
            choice = player.get_user_choice(currently_bet, self.current_bet, preflop_big)
            if choice == 'RAISE':
                raised_bet = player.raise_bet(int(input('How many chips would you like to raise?\t')), self.current_bet, self)
                while raised_bet == -1:
                    raised_bet = player.raise_bet(int(input('How many chips would you like to raise?\t')), self.current_bet, self)
                return (player.name + " raised to " + str(raised_bet) + " chips.", raised_bet)
            return (player.name + " checked.", self.current_bet)
        
        choice = player.get_user_choice(currently_bet, self.current_bet)
        
        if currently_bet:
            if choice == 'CALL':
                player_bet = player.bet(self.current_bet, self, True)
                return (player.name + " called for " + str(self.current_bet) + " chips.", self.current_bet)
            elif choice == 'RAISE':
                raised_bet = player.raise_bet(int(input('How many chips would you like to raise?\t')), self.current_bet, self)
                while raised_bet == -1:
                    raised_bet = player.raise_bet(int(input('How many chips would you like to raise?\t')), self.current_bet, self)
                return (player.name + " raised to " + str(raised_bet) + " chips.", raised_bet)
            else:
                player.fold()
                return (player.name + " folded.", self.current_bet)
        else:
            if choice == 'BET':
                player_bet = player.bet(int(input('How many chips would you like to bet?\t')), self)
                while player_bet == -1:
                    player_bet = player.bet(int(input('How many chips would you like to bet?\t')), self)
                return (player.name + " bet " + str(player_bet) + " chips.", player_bet)
        return (player.name + " checked.", self.current_bet)
            

    # Main run method which has a banner and runs the game with multiple rounds if necessary
    def run(self):
        print(" _________________________________________\n" +
            "| WELCOME TO DHRUVA'S POKER PROGRAM!     |" +
            "\n|\tProject: Poker Game\t\t |\n" +
            "| A SIDE NOTE: SCROLLING UP IS NECESSARY |" +
            "\n| AS PROGRAM OUTPUTS LOT OF INFO AT ONCE |" +
            "\n|\t\tENJOY!\t\t\t |\n" +
            "|________________________________________|\n") # Banner
        
        deck = Deck() # Initial deck

        # Create the players and therefore their hands:
        num_players = int(input('How many players will be playing poker? Minimum of 2 and Maximum of 6:\t'))
        while num_players < 2 or num_players > 6:
            num_players = int(input('Minimum of 2 and Maximum of 6. Please choose a valid number of players:\t'))
        
        # Sets buy-in amount
        buy_in_amount = int(input('How many chips will the buy-in be?:\t'))
        while buy_in_amount <= 0:
            buy_in_amount = int(input('Please choose a valid buy-in amount:\t'))
        
        # Sets big blind amount
        bb_amount = int(input('What will the big blind amount be?:\t'))
        while bb_amount <= 0 or bb_amount > buy_in_amount / 50 or bb_amount % 2 == 1:
            bb_amount = int(input('Big Blind Amount must be an EVEN number greater than 0 and less than 2% of the buy in amount.\nPlease choose again:\t'))
      
        # Sets player names
        for i in range(num_players):
            player_name = input("Please choose a name for Player " + str(i + 1) + ":\t")
            self.players.append(Player(player_name, buy_in_amount))

        original_players = self.players.copy() # Creates a copy to avoid skipping during looping and resetting

        continue_game = True
        
        # Re-initializes all variables at the start of every round
        while(continue_game):
            deck = Deck()
            self.reset()

            for player in self.players:
                player.return_to_game()
            
            self.players = self.players[1:] + [self.players[0]]
            original_players = self.players.copy()
            
            for i in range(len(self.players)):
                for j in range(2):
                    dealt_card = deck.deal()
                    self.players[i].add(dealt_card)

            
            if len(self.players) == 2:
                self.players[0].assign_position("Small Blind")
                self.players[1].assign_position("Big Blind")
            else:
                self.players[-1].assign_position("Dealer")
                self.players[0].assign_position("Small Blind")
                self.players[1].assign_position("Big Blind")
            
            self.bet_blinds(bb_amount)

            for game_state in Poker_Game.game_states:
                if game_state == 'Preflop':
                    # Sets up positions
                    utg = 2 % len(self.players)
                    temp_players = self.players[:]
                    self.players = self.players[utg:] + self.players[:utg]
                    
                    i = 0
                    last_actor = len(self.players)
                    previous_action = ''
                    
                    # Betting round for the preflop which is essentially the same as the original method, but with tweaks due to different positions
                    while i < last_actor:
                        os.system('cls')
                        print(previous_action)
                        current_player = self.players[i % len(self.players)]

                        if current_player.in_play():
                            if current_player.get_position() == 'Big Blind' and self.current_bet == 20:
                                check_only_bb = [player for player in temp_players if not player.folded]
                                if len(check_only_bb) == 1:
                                    break

                            only_desired_player = input("The current player is " + current_player.name + 
                                            ". All others leave the computer!\nWhen " + 
                                            current_player.name + " is the only one at the computer," +
                                            " please type in 'Here':\t").lower()
                            while only_desired_player != 'here':
                                only_desired_player = input("\nAll others leave!\nWhen " + current_player.name +
                                                " is the only one here, type 'Here':\t").lower()
                            
                            print(current_player.display_hand())
                            print("The Pot has " + str(self.pot) + " chips.")
                            temp = self.current_bet

                            if current_player.get_position() == 'Big Blind' and self.current_bet == 20:
                                choice = self.player_choice(True, current_player, True)
                                previous_action = choice[0]
                                self.current_bet = choice[1]
                            else:
                                choice = self.player_choice(True, current_player)
                                previous_action = choice[0]
                                self.current_bet = choice[1]
                            
                            if self.current_bet > temp:
                                last_actor = i + len(self.players) 

                        i += 1
                    
                    os.system('cls')
                    print(previous_action)
                    self.players = [player for player in temp_players if not player.folded]
                    preflop_end = self.end_game_state(deck, 3)
                    if preflop_end:
                        break
                
                elif game_state == 'Flop' or game_state == 'Turn':

                    playing = [player for player in self.players if not player.is_all_in()]  
                    if len(playing) != 1:
                        self.betting_round(0, len(self.players))
                        middlegame = self.end_game_state(deck, 1)
                        if middlegame:
                            break
                    else:
                        self.board.append(deck.deal())
                
                elif game_state == 'River':
                    print("\nThe Board is:")
                    for card in self.board:
                        print(card)

                    playing = [player for player in self.players if not player.is_all_in()]  
                    if len(playing) not in [0, 1]:
                        self.betting_round(0, len(self.players))
                        endgame = self.end_game_state(deck, 0)
                        if endgame:
                            break

                else:
                    os.system('cls')
                    best_hand = None
                    winners = []

                    # Evaluation of each hand and determining the winner
                    for player in self.players:
                        current_hand = player.display_hand().evaluate(self.board)
                        if best_hand is None or current_hand.compare(best_hand) == 1:
                            winners = [player]
                            best_hand = current_hand
                        elif current_hand.compare(best_hand) == 0:
                            winners.append(player)
                    
                    if len(winners) == 1:
                        print("\nCongratulations " + winners[0].name + ", you won the hand!")
                        print(best_hand)
                        winners[0].receive_chips(self.pot)
                        winners[0].win()
                        print(winners[0])
                    else:
                        split_amount = self.pot / len(winners)
                        for winner in winners:
                            print("\nCongratulations " + winner.name + ", you chopped the hand!")
                            print(best_hand)
                            winner.receive_chips(int(split_amount))
                            print(winners[0])
            
            self.players = original_players.copy()

            # Decides if players want to play a new round and deals with buy-ins and cash-outs
            new_game = input("Would all players like to play another game?" + 
                " Type 'True' or 'False':\t").lower()  # Convert input to lowercase
            
            while new_game not in ['true', 'false']:
                new_game = input("Please choose 'True' or 'False':\t").lower()  # Convert input to lowercase

            if new_game == 'false':
                continue_game = False
            else:
                self.buy_ins()
                self.cash_outs()
                if len(self.players) < 2:
                    print("Oh No! Too many people cashed out or lost!" +
                          " The game will end since there is not enough players!")
                    continue_game = False

      
        # A message is displayed after the game ends.
        print("Thanks for playing!")


class Player:

    def __init__(self, name, chips):
        self.cards = Hand(name)
        self.name = name
        self.chips = chips
        self.chips_in_pot = 0
        self.wins = 0
        self.folded = False
        self.all_in = False
        self.position = ''
   
    def get_chips(self):
        return self.chips
    
    def get_chips_in_pot(self):
        return self.chips_in_pot
    
    def reset_chips(self):
        self.chips_in_pot = 0
   
    def bet(self, amount, poker_game, all_in_call = False):
        adj_amount = amount - self.chips_in_pot
        if amount <= 0:
            print('Sorry ' + self.name + ', you must bet an amount greater than 0!')
            return -1
        elif self.chips < adj_amount:
            if all_in_call:
                self.chips_in_pot += self.chips
                poker_game.add_to_pot(self.chips)
                self.chips = 0
                self.all_in == True
                return amount
            print('Sorry ' + self.name + ', you must bet an amount less than or equal to your current chips.')
            return -1
        elif self.chips == adj_amount:
            self.chips -= adj_amount
            self.all_in = True
            self.chips_in_pot = amount
            poker_game.add_to_pot(adj_amount)
            return amount
        else:
            self.chips -= adj_amount
            self.chips_in_pot = amount
            poker_game.add_to_pot(adj_amount)
            return amount

    def raise_bet(self, amount, current_bet, poker_game):
        if amount < current_bet * 2:
           print('Sorry ' + self.name + ', you must raise at least twice the current bet!')
           return -1
        return self.bet(amount, poker_game)
    
    def buy_in(self, amount):
        print(self.name + ", you bought an additional " + str(amount) + " chips.")
        self.chips += amount
    
    def cash_out(self):
        print(self.name + ", you cashed out for " + str(self.chips) + " chips. Bye!")
        self.chips = 0
   
    def get_name(self):
        return self.name
   
    def is_all_in(self):
        return self.all_in
    
    def in_play(self):
        return not self.all_in and not self.folded
   
    def fold(self):
        self.folded = True
    
    def assign_position(self, position):
        self.position = position
    
    def get_position(self):
        return self.position
   
    def return_to_game(self):
        self.folded = False
        self.all_in = False
        self.cards.reset_hand()
   
    def win(self):
        self.wins += 1

    def receive_chips(self, amount):
        self.chips += amount 
   
    def get_wins(self):
        return self.wins

    def get_user_choice(self, currently_bet, bet_amount = 0, preflop_big = False):
        if preflop_big:
            response = input(self.name + ", the current bet is " + str(bet_amount) + 
                             " chips. Would you like to check or raise?\n").upper()
            while response != 'CHECK' and response != 'RAISE':
                response = input(self.name + ', please choose to either check or raise.\n').upper()
        elif currently_bet:
            response = input(self.name + ", the current bet is " + str(bet_amount) + 
                             " chips. Would you like to call, raise, or fold?\n").upper()
            while response != 'CALL' and response != 'RAISE' and response != 'FOLD':
                response = input(self.name + ', please choose to either call, raise, or fold.\n').upper()
        else:
            response = input(self.name + ", would you check or bet?\n").upper()
            while response != 'CHECK' and response != 'BET':
                response = input(self.name + ', please choose to either check or bet.\n').upper()
        return response

    def add(self, added_card):
        self.cards.add_card(added_card)
   
    def display_hand(self):
        return self.cards

    def __str__(self):
        info = ""
        info += self.name + ", you have " + str(self.wins) + " wins and " + str(self.chips) + " chips.\n"
        return info
    
class AI_Player(Player):
        
    ai_number = 1

    def __init__(self, chips):
        super().__init__("AI " + str(AI_Player.ai_number), chips)
        AI_Player.ai_number += 1
    
    def get_user_choice(self, currently_bet, bet_amount = 0, preflop_big = False):
        return

class Hand:
    hand_rankings = {1: "High Card", 2: "Pair", 3: "Two Pair", 4: "Three of a Kind", 5: "Straight",
                     6: "Flush", 7: "Full House", 8: "Four of a Kind", 9: "Straight Flush", 10: "Royal Flush"}

    def __init__(self, name):
        self.cards = []
        self.user = name

    def add_card(self, added_card):
        self.cards.append(added_card)

    def reset_hand(self):
        self.cards = []
   
    def evaluate(self, board):
        all_cards = board + self.cards
        all_combos = itertools.combinations(all_cards, 5)
        best_hand_rank = -1
        best_hand = None

        for combo in all_combos:
            current_combo = self.evaluate_five(combo)
            if current_combo > best_hand_rank:
                best_hand_rank = current_combo
                best_hand = combo
            elif current_combo == best_hand_rank:
                current_hand = Hand_Value(current_combo, combo, Hand.hand_rankings[current_combo])
                current_best = Hand_Value(best_hand_rank, best_hand, Hand.hand_rankings[best_hand_rank])
                if current_hand.compare(current_best) == 1:
                    best_hand_rank = current_combo
                    best_hand = combo
        
        return Hand_Value(best_hand_rank, best_hand, Hand.hand_rankings[best_hand_rank])
    
    def evaluate_five(self, five_cards):
        all_ranks = sorted([card.get_value() for card in five_cards])
        all_suits = sorted([card.get_suit() for card in five_cards])
        counts = [all_ranks.count(rank) for rank in all_ranks]

        if list(itertools.repeat(all_suits[0], 5)) == all_suits:
            if all_ranks == list(range(min(all_ranks), max(all_ranks) + 1)):
                if min(all_ranks) == 10:
                    return 10
                return 9
            elif all_ranks == [2, 3, 4, 5, 14]:
                return 9
            else:
                return 6
        elif all_ranks == list(range(min(all_ranks), max(all_ranks) + 1)) or all_ranks == [2, 3, 4, 5, 14]:
            return 5
        elif 4 in counts:
            return 8
        elif 3 in counts:
            if 2 in counts:
                return 7
            return 4
        elif 2 in counts:
            counted_counts = [counts.count(count) for count in counts]
            if 4 in counted_counts:
                return 3
            return 2
        return 1

    def get_hand(self):
        return self.cards
   
    def __str__(self):
        hand_info = "\n" + self.user + ", this is your hand:\n"
      
        for the_card in self.cards:
            hand_info += the_card.__str__() + "\n"
      
        return hand_info

class Deck:

   def __init__(self):
      self.cards = [Card(i, j) for j in range(1, 14) for i in range(4)]
      self.shuffle()

   def deal(self):
      dealt_card = self.cards.pop()
      return dealt_card

   def shuffle(self):
      for i in range(51, -1, -1):
         shuffled_card = int(random() * (i + 1))
         
         temp = self.cards[shuffled_card]
         self.cards[shuffled_card] = self.cards[i]
         self.cards[i] = temp

class Card:   
    suits = {0: "Spades", 1: "Hearts", 2: "Clubs", 3: "Diamonds"}
    ranks = {1: "Ace", 2: "Deuce", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 
            8: "Eight", 9: "Nine", 10: "Ten", 11: "Jack", 12: "Queen", 13: "King"}

    def __init__(self, card_suit, card_rank):
        self.suit = card_suit
        self.rank = card_rank
        self.actual_suit = Card.suits[self.suit]
        self.actual_rank = Card.ranks[self.rank]

    def get_value(self):
        if self.rank == 1:
            return 14
        else:
            return self.rank
    
    def get_rank(self):
        return self.rank
    
    def get_suit(self):
        return self.suit

    def __str__(self):
        return self.actual_rank + " of " + self.actual_suit

class Hand_Value:
    def __init__(self, hand_rank, hand_val, actual_rank):
        self.hand_rank = hand_rank
        self.hand_val = hand_val
        self.actual_rank = actual_rank
    
    def compare(self, villain):      
        if self.hand_rank > villain.hand_rank:
            return 1
        elif self.hand_rank < villain.hand_rank:
            return -1
        
        hero_vals = sorted([card.get_value() for card in self.hand_val])
        hero_counts = [hero_vals.count(val) for val in hero_vals]
        villain_vals = sorted([card.get_value() for card in villain.hand_val])  
        villain_counts = [villain_vals.count(val) for val in villain_vals]  

        if self.hand_rank in [1, 5, 6, 9, 10]:
            for i in range(4, -1, -1):
                if hero_vals[i] > villain_vals[i]:
                    return 1
                elif hero_vals[i] < villain_vals[i]:
                    return -1
            return 0
        elif self.hand_rank == 8:
            if hero_vals[2] > villain_vals[2]:
                return 1
            elif hero_vals[2] < villain_vals[2]:
                return -1
            elif hero_vals[hero_counts.index(1)] > villain_vals[villain_counts.index(1)]:
                return 1
            elif hero_vals[hero_counts.index(1)] < villain_vals[villain_counts.index(1)]:
                return -1
            return 0
        elif self.hand_rank == 7:
            hero_triplet = hero_vals[hero_counts.index(3)]
            hero_doublet = hero_vals[hero_counts.index(2)]
            villain_triplet = villain_vals[villain_counts.index(3)]
            villain_doublet = villain_vals[villain_counts.index(2)]

            if hero_triplet > villain_triplet:
                return 1
            elif hero_triplet < villain_triplet:
                return -1
            elif hero_doublet > villain_doublet:
                return 1
            elif hero_doublet < villain_doublet:
                return -1
            return 0
        elif self.hand_rank == 4:
            hero_triplet = hero_vals[hero_counts.index(3)]
            villain_triplet = villain_vals[villain_counts.index(3)]
            
            if hero_triplet > villain_triplet:
                return 1
            elif hero_triplet < villain_triplet:
                return -1
            
            hero_others = sorted([val for val in hero_vals if val != hero_triplet])
            villain_others = sorted([val for val in villain_vals if val != villain_triplet])

            for i in range(1, -1, -1):
                if hero_others[i] > villain_others[i]:
                    return 1
                elif hero_others[i] < villain_others[i]:
                    return -1
            return 0
        elif self.hand_rank == 3:
            hero_vals_copy = hero_vals[:]
            hero_vals_copy.remove(hero_vals[hero_counts.index(1)])
            hero_only_pairs = sorted(hero_vals_copy)
            
            villain_vals_copy = villain_vals[:]
            villain_vals_copy.remove(villain_vals[villain_counts.index(1)])
            villain_only_pairs = sorted(villain_vals_copy)

            hero_single = hero_vals[hero_counts.index(1)]
            villain_single = villain_vals[villain_counts.index(1)]
            
            if hero_only_pairs[2] > villain_only_pairs[2]:
                return 1
            elif hero_only_pairs[2] < villain_only_pairs[2]:
                return -1
            elif hero_only_pairs[0] > villain_only_pairs[0]:
                return 1
            elif hero_only_pairs[0] < villain_only_pairs[0]:
                return -1
            elif hero_single > villain_single:
                return 1
            elif hero_single < villain_single:
                return -1
            return 0
        else:
            hero_pair = hero_vals[hero_counts.index(2)]
            villain_pair = villain_vals[villain_counts.index(2)]
            
            if hero_pair > villain_pair:
                return 1
            elif hero_pair < villain_pair:
                return -1
            
            hero_others = sorted([val for val in hero_vals if val != hero_pair])
            villain_others = sorted([val for val in villain_vals if val != villain_pair])

            for i in range(2, -1, -1):
                if hero_others[i] > villain_others[i]:
                    return 1
                elif hero_others[i] < villain_others[i]:
                    return -1
            return 0
    
    def __str__(self):
        info = "You have a " + self.actual_rank + ":\n"
        for card in self.hand_val:
            info += card.__str__() + "\n"
        return info

Poker_Game()