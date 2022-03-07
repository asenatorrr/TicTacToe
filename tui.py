from re import match, search
from time import sleep
from main import start_play, start_training
from colorama import init, Fore


TITLE = '''
 ████████╗██╗░█████╗░░░░░░░████████╗░█████╗░░█████╗░░░░░░░████████╗░█████╗░███████╗
 ╚══██╔══╝██║██╔══██╗░░░░░░╚══██╔══╝██╔══██╗██╔══██╗░░░░░░╚══██╔══╝██╔══██╗██╔════╝
 ░░░██║░░░██║██║░░╚═╝█████╗░░░██║░░░███████║██║░░╚═╝█████╗░░░██║░░░██║░░██║█████╗░░
 ░░░██║░░░██║██║░░██╗╚════╝░░░██║░░░██╔══██║██║░░██╗╚════╝░░░██║░░░██║░░██║██╔══╝░░
 ░░░██║░░░██║╚█████╔╝░░░░░░░░░██║░░░██║░░██║╚█████╔╝░░░░░░░░░██║░░░╚█████╔╝███████╗
 ░░░╚═╝░░░╚═╝░╚════╝░░░░░░░░░░╚═╝░░░╚═╝░░╚═╝░╚════╝░░░░░░░░░░╚═╝░░░░╚════╝░╚══════╝'''

DESCRIPTION = '''\
 ==================================================================================
 Author: Senatorrr
 Version: 1.0.0
 © 2020-2021. Copying is forbidden for evil people
 
 Usage: training [options]
        --rounds <number> : number of rounds for new AI training
        
        play [options]
        --player <number> : use 0 to play for 'X' and 1 to play for 'O'
        
        exit
 ==================================================================================
'''


def slow_print(s):
    strings = s.split('\n')
    for string in strings:
        print(string)
        sleep(0.4)


if __name__ == '__main__':
    init()
    slow_print(Fore.CYAN + TITLE + Fore.RESET)
    sleep(0.5)
    print(Fore.LIGHTCYAN_EX + DESCRIPTION + Fore.RESET)
    while True:
        print(Fore.LIGHTWHITE_EX, end='')
        input_string = input('>>')
        if match(r'^training --rounds \d+$', input_string):
            rounds = int(search(r'\d+', input_string).group(0))
            start_training(rounds)
        if match(r'^play --player [0-1]$', input_string):
            player = int(search(r'[0-1]', input_string).group(0))
            start_play(player)
        if match(r'^exit$', input_string):
            exit(0)
