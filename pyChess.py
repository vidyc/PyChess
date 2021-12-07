from board import Board

class PyChess():

	isGameOver = False

	def __init__(self):
		self.board = Board()
		self.startGame()

	def startGame(self):
		self.isGameOver = False
		restart = False

		while not restart:
			while not self.isGameOver:
				move = self.board.getNextMove()
				self.board.doMove(move)
				self.board.printBoard()

			restart = input("Restart game?: ")
			if restart:
				self.board.initialBoardState()
				self.isGameOver = False


if __name__ == "__main__":
	PyChess()