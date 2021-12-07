import numpy as np
from gmpy2 import xmpz

from piece import Piece
from move import Move

class Board():
	
	BOARD_SIZE = 8

	UP = 0
	RIGHT = 1
	DOWN = 2
	LEFT = 3

	UP_LEFT = 4
	UP_RIGHT = 5
	DOWN_RIGHT = 6
	DOWN_LEFT = 7

	# board is a list of piece id
	board = [[(-1, -1)] * 8 for i in range(8)]

	# map that stores piece id as key and Piece as value
	# id = tuple (team, type) -> (-1, -1) if empty
	pieces = {}

	# 0 -> white, 1 -> black
	turn = 0

	numWhitePieces = 0
	numBlackPieces = 0

	whitePieces = {}
	blackPieces = {}

	castlingRights = [True] * 4

	enPassantPos = None

	def __init__(self):
		self.initialBoardState()

	def initialBoardState(self):
		self.board = [[(-1, -1)] * self.BOARD_SIZE for i in range(self.BOARD_SIZE)]

		for key, positions in Piece.INITIAL_POSITIONS.items():
			for pos in positions:
				# team = key[0], type = key[1], stringID = key[2]
				piece = Piece(key[0], key[1])
				
				if key[0] == Piece.WHITE_ID:
					self.whitePieces[piece.stringID] = pos
				else:
					self.blackPieces[piece.stringID] = pos

				self.board[pos[0]][pos[1]] = piece.id 

		self.numWhitePieces = 16
		self.numBlackPieces = 16
		self.turn = 0
		self.castlingRights = [True] * 4
		self.enPassantPos = None
		self.printBoard()

	def printBoard(self):
		for row in self.board:
			str = ""
			for piece in row:
				switch = {-1: 'o',0: 'p',1: 'n',2: 'b',3: 'r',4: 'q',5: 'k'}

				char = switch[piece[1]]
				if piece[0] == 0:
					str += (char + " ")
				else:
					str += (char.upper() + " ")

			print(str)


	def sumTuples(self, t1, t2):
		return (t1[0]+t2[0], t1[1]+t2[1])

	def legalPosition(self, pos):
		return pos[0] >= 0 and pos[0] < self.BOARD_SIZE and pos[1] >= 0 and pos[1] < self.BOARD_SIZE

	def accessiblePosition(self, pos, team):
		# determines if we can move to that position ( empty or enemy in it )
		return self.legalPosition(pos) and self.board[pos[0]][pos[1]][0] != team

	def enemyInPosition(self, pos, team):
		return self.legalPosition(pos) and self.board[pos[0]][pos[1]][0] != team and self.board[pos[0]][pos[1]][0] != -1

	def emptyPosition(self, pos):
		return self.legalPosition(pos) and self.board[pos[0]][pos[1]][0] == -1

	def slide(self, origin, dest, team, direction):

		# if dest is not specified, we will slide until we reach an edge of the board

		x = origin[1]
		y = origin[0]

		inc = (0, 0)
		switch = {
			self.UP:         (-1, 0),
			self.RIGHT:      (0, 1),
			self.DOWN:       (1, 0),
			self.LEFT:       (0, -1),
			self.UP_LEFT:    (-1, -1),
			self.UP_RIGHT:   (-1, 1),
			self.DOWN_RIGHT: (1, 1),
			self.DOWN_LEFT:  (1, -1),
		}
		inc = switch[direction]

		pos = (y + inc[0], x + inc[1])
		l = []
		stop = not self.legalPosition(pos)
		while not stop:
			targetTeam = self.board[pos[0]][pos[1]][0] 

			if targetTeam != team:
				l.append(pos)

			newPos = (pos[0] + inc[0], pos[1] + inc[1])

			if targetTeam != -1 or not self.legalPosition(newPos) or pos == dest:
				stop = True

			pos = newPos

		return l

	def calculateLegalMovesRook(self, pos, team):
		legalMoves = []
		legalMoves += self.slide(pos, None, team, self.UP)
		legalMoves += self.slide(pos, None, team, self.LEFT)
		legalMoves += self.slide(pos, None, team, self.DOWN)
		legalMoves += self.slide(pos, None, team, self.RIGHT)

		return legalMoves

	def calculateLegalMovesBishop(self, pos, team):
		legalMoves = []
		legalMoves += self.slide(pos, None, team, self.UP_LEFT)
		legalMoves += self.slide(pos, None, team, self.UP_RIGHT)
		legalMoves += self.slide(pos, None, team, self.DOWN_LEFT)
		legalMoves += self.slide(pos, None, team, self.DOWN_RIGHT)

		return legalMoves

	def calculateLegalMovesQueen(self, pos, team):
		legalMoves = self.calculateLegalMovesRook(pos, team) + self.calculateLegalMovesBishop(pos, team)

		return legalMoves

	def calculateLegalMovesKnight(self, pos, team):
		legalMoves = []
		for inc in Piece.KNIGHT_MOVES:
			targetPos = self.sumTuples(pos, inc)
			if self.accessiblePosition(targetPos, team):
				legalMoves.append(targetPos)

		return legalMoves

	def calculateLegalMovesPawn(self, pos, team):

		legalMoves = []
		incY = -1
		if team == Piece.BLACK_ID:
			incY = 1

		targetPos = (pos[0]+incY, pos[1])

		empty1 = self.emptyPosition(targetPos)
		# check if we can advance forward
		if empty1:
			legalMoves.append(targetPos)

		initialY = {Piece.WHITE_ID: 6, Piece.BLACK_ID: 1}
		if pos[0] == initialY[team]:
			targetPos = (pos[0] + incY*2, pos[1])
			if empty1 and self.emptyPosition(targetPos):
				legalMoves.append(targetPos)

				for incX in [-1, 1]:
					candidatePos = (targetPos[0], targetPos[1]+incX)
					if self.enemyInPosition(targetPos, team) and self.board[targetPos[0]][targetPos[1]].type == Piece.PAWN_ID:
						# indicate in this legalMove that enPassant would be set
						print("triggered en passant")

		# check if we can capture pieces
		for incX in [-1, 1]:
			targetPos = self.sumTuples(pos, (incY, incX))
			if self.enemyInPosition(targetPos, team):
				legalMoves.append(targetPos)

		# Lastly, check if we can capture en passant
		if self.enPassantPos != None:
			diff = -1
			if team == Piece.BLACK_ID:
				diff = 1

				if self.enPassantPos[0]-pos[0] == diff and abs(self.enPassantPos[1]-pos[1]) == 1:
					legalMoves.append(self.enPassantPos)

		return legalMoves


	def calculateLegalMoves(self):
		legalMoves = []
		attacked_squares = xmpz(0)
		king_danger_squares = xmpz(0)

		if self.turn % 2 == Piece.WHITE_ID:
			# compute attacked squares
			for key, pos in self.whitePieces.items():
				type = self.board[pos[0]][pos[1]][1]

				if type == Piece.ROOK_ID:
					moveList = self.calculateLegalMovesRook(pos, self.turn%2)
					print(moveList)
				elif type == Piece.BISHOP_ID:
					moveList = self.calculateLegalMovesBishop(pos, self.turn%2)
					print(moveList)
				elif type == Piece.QUEEN_ID:
					moveList = self.calculateLegalMovesQueen(pos, self.turn%2)
					print(moveList)
				elif type == Piece.KNIGHT_ID:
					moveList = self.calculateLegalMovesKnight(pos, self.turn%2)
					print("knight")
					print(moveList)
				elif type == Piece.PAWN_ID:
					moveList = self.calculateLegalMovesPawn(pos, self.turn%2)
					print("pawn")
					print(moveList)
		else:
			print("Si no")


	def getNextMove(self):

		legalMoves = self.calculateLegalMoves()
		move = None

		while True:
			origin = eval(input("Origin position: "))
			dest = eval(input("Destination position: "))
			team = self.turn % 2

			print(origin)

			originID = self.board[origin[0]][origin[1]]
			destID = self.board[dest[0]][dest[1]]
			captured = None
			if destID != Piece.EMPTY_PIECE_ID and destID[0] != originID[0]:
				captured = destID

			#if destID == self.enPassantPos:

			promoted = None
			if originID[1] == Piece.PAWN_ID and (dest[0] == 0 or dest[0] == 7):
				promoted = input("Select piece to promote: ") 

			move = Move(team, origin, dest, captured, None, promoted)
			if True: # move in legalMoves
				break

		return move

	# Asumimos que move es un movimiento legal
	def doMove(self, move):
		# move mueve una pieza de una posicion a otra
		# con la posibilidad de eliminar una pieza

		origin = move.origin
		dest = move.dest
		piece_id = self.board[origin[0]][origin[1]]
		self.board[origin[0]][origin[1]] = Piece.EMPTY_PIECE_ID
		self.board[dest[0]][dest[1]] = piece_id

		if move.team == Piece.WHITE_ID:
			self.whitePieces[piece_id[2]] = dest
		else:
			self.blackPieces[piece_id[2]] = dest

		if move.passant:
			if move.team == Piece.WHITE_ID:
				# si el equipo blanco come en passant:
				self.board[dest[0]+1][dest[1]] = Piece.EMPTY_PIECE_ID
			else:
				self.board[dest[0]-1][dest[1]] = Piece.EMPTY_PIECE_ID

		if move.team == Piece.WHITE_ID:
			self.numBlackPieces-=1
		else:
			self.numWhitePieces-=1
		



		