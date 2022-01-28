import numpy as np
import copy
import pygame

from piece import Piece
from move import Move

class Board():
	
	BOARD_SIZE = 8

	UP = 0
	RIGHT = 1
	DOWN = 2
	LEFT = 3
	ORTHOGONAL = [UP, RIGHT, DOWN, LEFT]

	UP_LEFT = 4
	UP_RIGHT = 5
	DOWN_RIGHT = 6
	DOWN_LEFT = 7
	DIAGONAL = [UP_LEFT, UP_RIGHT, DOWN_RIGHT, DOWN_LEFT]

	POSSIBLE_PROMOTION = [ Piece.KNIGHT_ID, Piece.BISHOP_ID, Piece.ROOK_ID, Piece.QUEEN_ID]

	# board is a list of piece id
	board = [[(-1, -1)] * 8 for i in range(8)]

	# map that stores piece id as key and Piece as value
	# id = tuple (team, type) -> (-1, -1) if empty
	pieces = {}

	# 0 -> white, 1 -> black
	turn = 0

	pyChess = None

	numWhitePieces = 0
	numBlackPieces = 0

	KINGSIDE_CASTLING = 0
	QUEENSIDE_CASTLING = 1

	def __init__(self, pyChess):
		self.pyChess = pyChess
		self.initialBoardState()

	def initialBoardState(self):
		self.board = [[(-1, -1)] * self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
		self.whitePieces = {}
		self.blackPieces = {}

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
		self.kingPositions = { Piece.WHITE_ID: Piece.INITIAL_POSITIONS[(Piece.WHITE_ID, Piece.KING_ID)][0],
					      Piece.BLACK_ID: Piece.INITIAL_POSITIONS[(Piece.BLACK_ID, Piece.KING_ID)][0] }
		self.check = False
		self.checkmate = False
		self.stalemate = False
		self.numCheckers = 0
		self.enPassantPos = None
		self.printBoard()
		self.displayBoard()

	def printBoard(self):
		print(self.castlingRights)
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

	def displayBoard(self):
		self.pyChess.displayBoard()
		self.displayPieces()

		self.pyChess.update()

	# exclude --> list of pieces to exclude
	# invert  --> exclude becomes the list of pieces to draw
	def displayPieces(self, exclude=[], invert=False):
		if invert:
			for (i, row) in enumerate(self.board):
				for (j, piece) in enumerate(row):
					if piece[0] != -1 and piece[2] in exclude:
						self.pyChess.displayPiece(piece[0], piece[1], j, i)
		else:
			for (i, row) in enumerate(self.board):
				for (j, piece) in enumerate(row):
					if piece[0] != -1 and not piece[2] in exclude:
						self.pyChess.displayPiece(piece[0], piece[1], j, i)

	def sumTuples(self, t1, t2):
		return (t1[0]+t2[0], t1[1]+t2[1])

	def getPieceInPosition(self, pos, team):
		if self.legalPosition(pos) and self.board[pos[0]][pos[1]][0] == team:
			return self.board[pos[0]][pos[1]][1]

		return None

	def legalPosition(self, pos):
		return pos[0] >= 0 and pos[0] < self.BOARD_SIZE and pos[1] >= 0 and pos[1] < self.BOARD_SIZE

	def accessiblePosition(self, pos, team):
		# determines if we can move to that position ( empty or enemy in it )
		return self.legalPosition(pos) and self.board[pos[0]][pos[1]][0] != team

	def enemyInPosition(self, pos, team):
		
		enemy = self.legalPosition(pos) and self.board[pos[0]][pos[1]][0] != team and self.board[pos[0]][pos[1]][0] != -1
		type = None
		if enemy:
			type = self.board[pos[0]][pos[1]][1]

		return enemy, type

	def emptyPosition(self, pos):
		return self.legalPosition(pos) and self.board[pos[0]][pos[1]][0] == -1

	def isPositionAttacked(self, pos, team):
		attacked = False
		numAttackers = 0
		for dir in (self.ORTHOGONAL+self.DIAGONAL):
			l, attack, attacker = self.slide(pos, None, team, dir)

			if attack:
				attacked = True
				numAttackers += 1

				if numAttackers == 2:
					break
		for inc in Piece.KNIGHT_MOVES:
			targetPos = self.sumTuples(pos, inc)
			enemy, type = self.enemyInPosition(targetPos, team)
			if enemy and type == Piece.KNIGHT_ID:
				attacked = True
				numAttackers+=1
				
				if numAttackers == 2:
					break

		return attacked, numAttackers

	def isKingInCheck(self, team):
		return self.isPositionAttacked(self.kingPositions[team] ,team)	

	def isMoveLegal(self, move, team):
		# check if our king will be in check after executing move 
		newBoard = copy.deepcopy(self, {id(self.pyChess): self.pyChess})
		newBoard.doMove(move)
		legal = not (newBoard.isKingInCheck(team)[0])
		#print(legal)
		#newBoard.printBoard()
		return legal

	def aptForCastlingPosition(self, pos, team):
		return self.emptyPosition(pos) and not self.isPositionAttacked(pos, team)[0]

	def slide(self, origin, dest, team, direction):

		# if dest is not specified, we will slide until we reach an edge of the board

		x = origin[1]
		y = origin[0]

		attacked = False
		attacker = None

		diff = 1 if team == Piece.WHITE_ID else -1

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
			targetType = self.board[pos[0]][pos[1]][1]

			if targetTeam != team:
				capture = False
				if targetTeam != -1:
					capture = True
				
				l.append(Move(team, origin, pos, capture=capture))

			newPos = (pos[0] + inc[0], pos[1] + inc[1])

			if targetTeam != -1 or not self.legalPosition(newPos) or pos == dest:
				stop = True

			if targetTeam != -1 and targetTeam != team:
				if (direction in self.ORTHOGONAL and 
				   (targetType == Piece.ROOK_ID or targetType == Piece.QUEEN_ID)):
					attacked = True
					attacker = targetType
				elif (direction in self.DIAGONAL and
					  (targetType == Piece.QUEEN_ID or targetType == Piece.BISHOP_ID)):
					attacked = True
					attacker = targetType
				elif (direction in self.DIAGONAL and targetType == Piece.PAWN_ID and
				       y - pos[0] == diff):
					attacked = True
					attacker = targetType

			pos = newPos

		return l, attacked, attacker

	def calculateLegalMovesRook(self, pos, team):
		legalMoves = []
		legalMoves += self.slide(pos, None, team, self.UP)[0]
		legalMoves += self.slide(pos, None, team, self.LEFT)[0]
		legalMoves += self.slide(pos, None, team, self.DOWN)[0]
		legalMoves += self.slide(pos, None, team, self.RIGHT)[0]

		return legalMoves

	def calculateLegalMovesBishop(self, pos, team):
		legalMoves = []
		legalMoves += self.slide(pos, None, team, self.UP_LEFT)[0]
		legalMoves += self.slide(pos, None, team, self.UP_RIGHT)[0]
		legalMoves += self.slide(pos, None, team, self.DOWN_LEFT)[0]
		legalMoves += self.slide(pos, None, team, self.DOWN_RIGHT)[0]

		return legalMoves

	def calculateLegalMovesQueen(self, pos, team):
		legalMoves = self.calculateLegalMovesRook(pos, team) + self.calculateLegalMovesBishop(pos, team)

		return legalMoves

	def calculateLegalMovesKnight(self, pos, team):
		legalMoves = []
		for inc in Piece.KNIGHT_MOVES:
			targetPos = self.sumTuples(pos, inc)
			if self.accessiblePosition(targetPos, team):
				enemy, _ = self.enemyInPosition(targetPos, team)
				legalMoves.append(Move(team, pos, targetPos, capture=enemy))

		return legalMoves

	def calculateLegalMovesPawn(self, pos, team):

		legalMoves = []
		incY = -1
		if team == Piece.BLACK_ID:
			incY = 1

		targetPos = (pos[0]+incY, pos[1])

		empty1 = self.emptyPosition(targetPos)
		finalY = {Piece.WHITE_ID:0, Piece.BLACK_ID:7}
		# check if we can advance forward
		if empty1:
			if targetPos[0] == finalY[team]:
				for type in self.POSSIBLE_PROMOTION:
					legalMoves.append(Move(team, pos, targetPos, promoted=type))
			else:
				legalMoves.append(Move(team, pos, targetPos, promoted=None))

		initialY = {Piece.WHITE_ID: 6, Piece.BLACK_ID: 1}
		if pos[0] == initialY[team]:
			targetPos = (pos[0] + incY*2, pos[1])
			if empty1 and self.emptyPosition(targetPos):
				enPassantPos = None

				for incX in [-1, 1]:
					candidatePos = (targetPos[0], targetPos[1]+incX)
					enemy, type = self.enemyInPosition(candidatePos, team)
					if enemy and type == Piece.PAWN_ID:
						# indicate in this legalMove that enPassant would be set
						print("triggered en passant")
						enPassantPos = self.sumTuples(targetPos, (-incY, 0))
						break

				legalMoves.append(Move(team, pos, targetPos, enPassantPos=enPassantPos))



		# check if we can capture pieces
		for incX in [-1, 1]:
			targetPos = self.sumTuples(pos, (incY, incX))
			if self.enemyInPosition(targetPos, team)[0]:
				promoted = None
				if targetPos[0] == finalY[team]:
					for type in self.POSSIBLE_PROMOTION:
						legalMoves.append(Move(team, pos, targetPos, capture=True, promoted=type))
				else:
					legalMoves.append(Move(team, pos, targetPos, capture=True, promoted=None))

		# Lastly, check if we can capture en passant
		if self.enPassantPos != None:
			diff = -1
			if team == Piece.BLACK_ID:
				diff = 1

			print(self.enPassantPos)

			if self.enPassantPos[0]-pos[0] == diff and abs(self.enPassantPos[1]-pos[1]) == 1:
				legalMoves.append(Move(team, pos, self.enPassantPos, capture=True, passant=True))
				m = Move(team, pos, self.enPassantPos, capture=True, passant=True)
				m.print()

		return legalMoves

	def calculateLegalMovesKing(self, pos, team):
		legalMoves = []
		for inc in Piece.KING_MOVES:
			targetPos = self.sumTuples(pos, inc)
			if self.accessiblePosition(targetPos, team):
				enemy, _ = self.enemyInPosition(targetPos, team)
				legalMoves.append(Move(team, pos, targetPos, capture=enemy))

		ind = 0 if team == Piece.WHITE_ID else 2

		if (self.castlingRights[ind] and 
		    self.aptForCastlingPosition(self.sumTuples(self.kingPositions[team], (0, 1)), team) and
		 	self.aptForCastlingPosition(self.sumTuples(self.kingPositions[team], (0, 2)), team) ):
			targetPos = self.sumTuples(pos, (0, 2))
			m = Move(team, pos, targetPos, castling=Board.KINGSIDE_CASTLING)
			legalMoves.append(m)

		if (self.castlingRights[ind+1] and
	    	self.aptForCastlingPosition(self.sumTuples(self.kingPositions[team], (0, -1)), team) and
	 		self.aptForCastlingPosition(self.sumTuples(self.kingPositions[team], (0, -2)), team) and 
	 		self.aptForCastlingPosition(self.sumTuples(self.kingPositions[team], (0, -3)), team) ):
			targetPos = self.sumTuples(pos, (0, -2))
			legalMoves.append(Move(team, pos, targetPos, castling=Board.QUEENSIDE_CASTLING))

		return legalMoves

	def calculateLegalMoves(self):
		legalMoves = []
		#attacked_squares = xmpz(0)
		#king_danger_squares = xmpz(0)

		team = self.turn % 2
		pieces = self.whitePieces
		if team == Piece.BLACK_ID:
			pieces = self.blackPieces

		moveList = []
		if self.numCheckers <= 1:
			for key, pos in pieces.items():
				type = self.board[pos[0]][pos[1]][1]

				if type == Piece.ROOK_ID:
					moveList += self.calculateLegalMovesRook(pos, team)
				elif type == Piece.BISHOP_ID:
					moveList += self.calculateLegalMovesBishop(pos, team)
				elif type == Piece.QUEEN_ID:
					moveList += self.calculateLegalMovesQueen(pos, team)
				elif type == Piece.KNIGHT_ID:
					moveList += self.calculateLegalMovesKnight(pos, team)
				elif type == Piece.PAWN_ID:
					moveList += self.calculateLegalMovesPawn(pos, team)
				elif type == Piece.KING_ID:
					moveList += self.calculateLegalMovesKing(pos, team)
		else:
			# more than 1 checker => we can only move the king
			moveList += self.calculateLegalMovesKing(self.kingPositions[team], team)

		# after getting all the possible moves, we will eliminate those that leave our king in check

		moveList = [ move for move in moveList if self.isMoveLegal(move, team) ]

		#for move in moveList:
		#	move.print()

		if not moveList:
			self.checkmate = self.check
			self.stalemate = not self.check

		if self.checkmate:
			print("CHECKMATE!")
		elif self.stalemate:
			print("STALEMATE!")

		return moveList

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
				promoted = Piece.QUEEN_ID

			move = Move(team, origin, dest, capture=True, promoted=promoted)
			if True: # move in legalMoves
				break

		return move

	# Asumimos que move es un movimiento legal
	def doMove(self, move):
		# move mueve una pieza de una posicion a otra
		# con la posibilidad de eliminar una pieza

		self.enPassantPos = None
		origin = move.origin
		dest = move.dest
		piece_id = self.board[origin[0]][origin[1]]
		dest_piece_id = self.board[dest[0]][dest[1]]
		if move.passant:
			inc = 1 if move.team == Piece.WHITE_ID else -1
			dest_piece_id = self.board[dest[0]+inc][dest[1]]
		
		if move.promoted != None:
			print("Promotion")
			piece_id = (piece_id[0], move.promoted, piece_id[2])

		self.board[origin[0]][origin[1]] = Piece.EMPTY_PIECE_ID
		self.board[dest[0]][dest[1]] = piece_id

		ind = 0 if move.team == Piece.WHITE_ID else 2
		if piece_id[1] == Piece.KING_ID:
			self.kingPositions[move.team] = dest
			self.castlingRights[ind] = False
			self.castlingRights[ind+1] = False
		elif piece_id[1] == Piece.ROOK_ID:
			if origin[1] == 7:
				self.castlingRights[ind] = False
			elif origin[1] == 0:
				self.castlingRights[ind+1] = False

		if move.castling != None:
			origin2 = (origin[0], dest[1]+1)
			dest2 = (origin[0], origin[1]+1)
				
			print(origin2)
			print(dest2)

			if move.castling == self.QUEENSIDE_CASTLING:
				origin2 = (origin[0], dest[1]-2)
				dest2 = (origin[0], origin[1]-1)

			piece_id2 = self.board[origin2[0]][origin2[1]]
			self.board[origin2[0]][origin2[1]] = Piece.EMPTY_PIECE_ID
			self.board[dest2[0]][dest2[1]] = piece_id2

			if move.team == Piece.WHITE_ID:
				self.whitePieces[piece_id2[2]] = dest2
			else:
				self.blackPieces[piece_id2[2]] = dest2

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

		if move.enPassantPos:
			self.enPassantPos = move.enPassantPos

		if move.capture:
			if move.team == Piece.WHITE_ID:
				self.numBlackPieces-=1
				self.blackPieces.pop(dest_piece_id[2], None)
			else:
				self.numWhitePieces-=1
				self.whitePieces.pop(dest_piece_id[2], None)

		self.turn += 1

		self.check, self.numCheckers = self.isKingInCheck(self.turn%2)		