import numpy as np
import pickle
from msvcrt import getch
from colorama import init, Fore, Back
from time import sleep


class State:
    def __init__(self, player_1, player_2):
        self.board = np.zeros((3, 3))
        self.player_1 = player_1
        self.player_2 = player_2
        self.isEnd = False
        self.boardHash = None
        self.playerSymbol = 1

    def getHash(self):
        self.boardHash = str(self.board.reshape(9))
        return self.boardHash

    def winner(self):
        field = np.reshape(self.board, 9)
        for a, b, c in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
            if abs(field[a] + field[b] + field[c]) == 3:
                self.isEnd = True
                return (field[a] + field[b] + field[c]) / abs(field[a] + field[b] + field[c])
        if 0 not in field:
            self.isEnd = True
            return 0
        self.isEnd = False
        return None

    def availablePositions(self):
        positions = []
        for i in range(3):
            for j in range(3):
                if self.board[i, j] == 0:
                    positions.append((i, j))
        return positions

    def updateState(self, position):
        self.board[position] = self.playerSymbol
        self.playerSymbol = -self.playerSymbol

    def giveReward(self):
        result = self.winner()
        if result == 1:
            self.player_1.feedReward(1)
            self.player_2.feedReward(0)
        elif result == -1:
            self.player_1.feedReward(0)
            self.player_2.feedReward(1)
        else:
            self.player_1.feedReward(0.1)
            self.player_2.feedReward(0.5)

    def reset(self):
        self.board = np.zeros((3, 3))
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = 1

    def training(self, rounds=100):
        for i in range(rounds):
            if (i + 1) % 1000 == 0:
                print("...{} rounds done...".format(i + 1))
            while not self.isEnd:
                positions = self.availablePositions()
                player_1_action = self.player_1.chooseAction(positions, self.board, self.playerSymbol)
                self.updateState(player_1_action)
                board_hash = self.getHash()
                self.player_1.addState(board_hash)

                win = self.winner()
                if win is not None:
                    self.giveReward()
                    self.player_1.reset()
                    self.player_2.reset()
                    self.reset()
                    break

                else:
                    positions = self.availablePositions()
                    player_2_action = self.player_2.chooseAction(positions, self.board, self.playerSymbol)
                    self.updateState(player_2_action)
                    board_hash = self.getHash()
                    self.player_2.addState(board_hash)

                    win = self.winner()
                    if win is not None:
                        self.giveReward()
                        self.player_1.reset()
                        self.player_2.reset()
                        self.reset()
                        break

    def play(self):
        self.showBoard()
        while True:
            positions = self.availablePositions()
            player_1_action = self.player_1.chooseAction(positions, self.board, self.playerSymbol)
            if self.player_1.name == 'Computer':
                print(Back.RED + 'Computer turn: ', end='')
                sleep(0.75)
                print(str(player_1_action) + Back.RESET)
            self.updateState(player_1_action)
            self.showBoard()
            win = self.winner()
            if win is not None:
                print(Back.CYAN, end='')
                if win == 1:
                    print(self.player_1.name, "wins!")
                else:
                    print("Tie!")
                print(Back.RESET, end='')
                self.reset()

            else:
                positions = self.availablePositions()
                player_2_action = self.player_2.chooseAction(positions, self.board, self.playerSymbol)
                if self.player_2.name == 'Computer':
                    print(Back.RED + 'Computer turn: ', end='')
                    sleep(0.75)
                    print(str(player_2_action) + Back.RESET)
                self.updateState(player_2_action)
                self.showBoard()
                win = self.winner()
                if win is not None:
                    print(Back.CYAN, end='')
                    if win == -1:
                        print(self.player_2.name, "wins!")
                    else:
                        print("Tie!")
                    print(Back.RESET, end='')
                    self.reset()
            if win is not None:
                print('One more game? To continue, press 1...')
                if not getch().decode("utf-8") == '1':
                    print('...game session is over.')
                    break
                else:
                    self.showBoard()

    def showBoard(self):
        for i in range(0, 3):
            print(' --------- --------- --------- ')
            cols_splitter = '|         |         |         |'
            out = '|    '
            for j in range(0, 3):
                if self.board[i, j] == 1:
                    token = 'X'
                if self.board[i, j] == -1:
                    token = 'O'
                if self.board[i, j] == 0:
                    token = ' '
                out += token + '    |    '
            print(cols_splitter)
            print(out)
            print(cols_splitter)
        print(' --------- --------- --------- ')


class Player:
    def __init__(self, name, exp_rate=0.3):
        self.name = name
        self.states = []
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_value = {}

    def getHash(self, board):
        boardHash = str(board.reshape(9))
        return boardHash

    def chooseAction(self, positions, current_board, symbol):
        if np.random.uniform(0, 1) <= self.exp_rate:
            idx = np.random.choice(len(positions))
            action = positions[idx]
        else:
            value_max = -999
            for p in positions:
                next_board = current_board.copy()
                next_board[p] = symbol
                next_boardHash = self.getHash(next_board)
                value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)
                if value >= value_max:
                    value_max = value
                    action = p
        return action

    def addState(self, state):
        self.states.append(state)

    def feedReward(self, reward):
        for state in reversed(self.states):
            if self.states_value.get(state) is None:
                self.states_value[state] = 0
            self.states_value[state] += self.lr * (self.decay_gamma * reward - self.states_value[state])
            reward = self.states_value[state]

    def reset(self):
        self.states = []

    def savePolicy(self):
        with open('policy_' + str(self.name), 'wb') as policy_file:
            pickle.dump(self.states_value, policy_file)

    def loadPolicy(self, file):
        with open(file, 'rb') as policy_file:
            self.states_value = pickle.load(policy_file)


class HumanPlayer:
    def __init__(self, name):
        self.name = name
        self.keyboard_cells = [(2, 0), (2, 1), (2, 2), (1, 0), (1, 1), (1, 2), (0, 0), (0, 1), (0, 2)]

    def chooseAction(self, positions, _, __):
        print(Back.GREEN + 'Your turn: ', end='')
        while True:
            while True:
                try:
                    action = self.keyboard_cells[int(getch().decode("utf-8")) - 1]
                    break
                except:
                    pass
            if action in positions:
                print(str(action) + Back.RESET)
                return action

    def addState(self, state):
        pass

    def feedReward(self, reward):
        pass

    def reset(self):
        pass


def start_training(rounds):
    init()
    p1 = Player("p1")
    p2 = Player("p2")
    st = State(p1, p2)
    print("training...")
    st.training(rounds)
    p1.savePolicy()
    p2.savePolicy()
    print(Fore.LIGHTGREEN_EX + '...training session was successfully completed!' + Fore.RESET)


def start_play(player):
    init()
    if player == 0:
        p1 = HumanPlayer("Human")
        p2 = Player("Computer", exp_rate=0)
        p2.loadPolicy("policy_p2")
        st = State(p1, p2)
        st.play()
    elif player == 1:
        p1 = Player("Computer", exp_rate=0)
        p1.loadPolicy("policy_p1")
        p2 = HumanPlayer("Human")
        st = State(p1, p2)
        st.play()
