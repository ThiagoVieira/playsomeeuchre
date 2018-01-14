from euchre.game_controller import GameController
from euchre.data_model import CardDeck
from euchre.players.RandomPlayer import RandomPlayer
from euchre.players.CommandLinePlayer import CommandLinePlayer


if __name__ == '__main__':
    controller = GameController([RandomPlayer(0) for _ in range(3)] + [CommandLinePlayer()], CardDeck(0))
    controller.play()
