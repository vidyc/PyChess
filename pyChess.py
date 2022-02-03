from distutils.util import execute
from board import Board
from piece import Piece
import pygame
import sys
import time

class PyChess():

	isGameOver = False

	WIDTH = 800
	HEIGHT = 800

	PIECE_WIDTH = WIDTH / 8
	PIECE_HEIGHT = HEIGHT / 8

	pygame.init()
	gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("PyChess")
	FPS_CLOCK = pygame.time.Clock()

	BOARD_IMG = pygame.transform.scale(pygame.image.load("assets/chessboard_gray.png"), (WIDTH, HEIGHT))

	BLACK_KING_IMG = pygame.transform.smoothscale(pygame.image.load("assets/black_king.png"), (PIECE_WIDTH, PIECE_HEIGHT))
	BLACK_QUEEN_IMG = pygame.transform.smoothscale(pygame.image.load("assets/black_queen.png"), (PIECE_WIDTH, PIECE_HEIGHT))
	BLACK_KNIGHT_IMG = pygame.transform.smoothscale(pygame.image.load("assets/black_knight.png"), (PIECE_WIDTH, PIECE_HEIGHT))
	BLACK_BISHOP_IMG = pygame.transform.smoothscale(pygame.image.load("assets/black_bishop.png"), (PIECE_WIDTH, PIECE_HEIGHT))
	BLACK_PAWN_IMG = pygame.transform.smoothscale(pygame.image.load("assets/black_pawn.png"), (PIECE_WIDTH, PIECE_HEIGHT))
	BLACK_ROOK_IMG = pygame.transform.smoothscale(pygame.image.load("assets/black_rook.png"), (PIECE_WIDTH, PIECE_HEIGHT))

	WHITE_KING_IMG = pygame.transform.smoothscale(pygame.image.load("assets/white_king.png"), (PIECE_WIDTH, PIECE_HEIGHT))
	WHITE_QUEEN_IMG = pygame.transform.smoothscale(pygame.image.load("assets/white_queen.png"), (PIECE_WIDTH, PIECE_HEIGHT))
	WHITE_KNIGHT_IMG = pygame.transform.smoothscale(pygame.image.load("assets/white_knight.png"), (PIECE_WIDTH, PIECE_HEIGHT))
	WHITE_BISHOP_IMG = pygame.transform.smoothscale(pygame.image.load("assets/white_bishop.png"), (PIECE_WIDTH, PIECE_HEIGHT))
	WHITE_PAWN_IMG = pygame.transform.smoothscale(pygame.image.load("assets/white_pawn.png"), (PIECE_WIDTH, PIECE_HEIGHT))
	WHITE_ROOK_IMG = pygame.transform.smoothscale(pygame.image.load("assets/white_rook.png"), (PIECE_WIDTH, PIECE_HEIGHT))

	PIECE_MOVE_ANIMATION_FRAMES = 8

	DISPLAY_COLOR = (25, 77, 0)
	CHECK_COLOR   = (180, 20, 20)
	POPUP_COLOR   = (200, 200, 200)

	PIECE_IMAGES = { (Piece.WHITE_ID, Piece.PAWN_ID):  WHITE_PAWN_IMG,
					(Piece.BLACK_ID, Piece.PAWN_ID):   BLACK_PAWN_IMG,
					(Piece.WHITE_ID, Piece.KNIGHT_ID): WHITE_KNIGHT_IMG,
					(Piece.BLACK_ID, Piece.KNIGHT_ID): BLACK_KNIGHT_IMG,
					(Piece.WHITE_ID, Piece.BISHOP_ID): WHITE_BISHOP_IMG,
					(Piece.BLACK_ID, Piece.BISHOP_ID): BLACK_BISHOP_IMG,
					(Piece.WHITE_ID, Piece.ROOK_ID):   WHITE_ROOK_IMG,
					(Piece.BLACK_ID, Piece.ROOK_ID):   BLACK_ROOK_IMG,
					(Piece.WHITE_ID, Piece.QUEEN_ID):  WHITE_QUEEN_IMG, 
					(Piece.BLACK_ID, Piece.QUEEN_ID):  BLACK_QUEEN_IMG,
					(Piece.WHITE_ID, Piece.KING_ID):   WHITE_KING_IMG,
					(Piece.BLACK_ID, Piece.KING_ID):   BLACK_KING_IMG
				    }

	PROMOTION_STR = { "queen":  Piece.QUEEN_ID, 
					  "knight": Piece.KNIGHT_ID,
					  "rook":   Piece.ROOK_ID,
					  "bishop": Piece.BISHOP_ID,
					}

	def __init__(self):
		self.gameDisplay.fill((255, 255, 255))
		self.gameDisplay.blit(self.BOARD_IMG, (0, 0))
		self.board = Board(self)
		pygame.display.update()
		self.startGame()

	def startGame(self):
		self.isGameOver = False

		self.handleMouseEvents = True
		self.handleKeyboardEvents = True
		self.handleUpdates = True
		self.handleRendering = True

		self.framecount = 0
		self.click_state = 0
		
		self.origin = (-1, -1)
		self.destination = (-1, -1)
		
		self.move = None
		self.legalMoves = []
		self.calculatedLegalMoves = False
		self.executeMove = False

		self.check = False
		self.checkedKingId  = ""
		self.checkedKingPos = None

		self.previous_time = time.time_ns()
		self.delta = 0

		self.pieceAnimationPosition = None
		self.animateMove = False
		self.animationFrames = PyChess.PIECE_MOVE_ANIMATION_FRAMES
		self.posDelta = (PyChess.PIECE_WIDTH / self.animationFrames, PyChess.PIECE_HEIGHT / self.animationFrames)
		self.animationImg = None
		self.animationpieceId = ""

		self.popUpAnimationFrames = PyChess.PIECE_MOVE_ANIMATION_FRAMES / 2
		self.animatePopUp = False
		self.popUpRect       = (0, 0, 0, 0)
		self.popUpWidthDelta = PyChess.PIECE_WIDTH / PyChess.PIECE_MOVE_ANIMATION_FRAMES
		self.popUpHeightDelta  = 4 * PyChess.PIECE_HEIGHT / PyChess.PIECE_MOVE_ANIMATION_FRAMES
		self.popUpPositions  = {}

		self.promotion = False
		while 1:
			self.FPS_CLOCK.tick(180)

			######################################################
			################### EVENT HANDLING ###################
			######################################################
			for event in pygame.event.get():
				if self.handleMouseEvents and event.type == pygame.MOUSEBUTTONDOWN:
					self.mouseEvents()
				elif self.handleKeyboardEvents and event.type == pygame.KEYDOWN:
					self.keyboardEvents(event.key)
				elif event.type == pygame.QUIT:
					sys.exit("Quitting...")

			#####################################################
			#################### UPDATE GAME ####################
			#####################################################

			if self.handleUpdates and self.framecount % 2 == 0:
				if not self.calculatedLegalMoves:
					self.legalMoves = self.board.calculateLegalMoves()
					self.isGameOver = self.board.checkmate or self.board.stalemate
					self.calculatedLegalMoves = True
					
					if self.board.check:
						self.check = True
						self.checkedKingPos = self.board.kingPositions[self.board.turn%2]
						self.checkedKingId  = self.board.board[self.checkedKingPos[0]][self.checkedKingPos[1]][2] 
						
						if self.isGameOver:
							self.handleUpdates = False
							self.handleKeyboardEvents = False
							self.handleMouseEvents = False


				if self.click_state == 2:
					# check if the selected move is a legal move
					for m in self.legalMoves:
						if m.origin == self.origin and m.dest == self.destination:
							self.executeMove = True
							self.move = m
							self.move.print()
							break

					if not self.executeMove:
						self.click_state = 0
						self.origin = (-1, -1)
						self.destination = (-1, -1)
						self.board.displayBoard()
					elif self.move.promoted != None:
						# we will block all events until the promotion pop-up window is drawn
						self.animatePopUp = True
						self.popUpAnimationFrames = PyChess.PIECE_MOVE_ANIMATION_FRAMES / 2
						self.popUpWidthDelta = PyChess.PIECE_WIDTH / self.popUpAnimationFrames
						self.popUpHeightDelta  = 4 * PyChess.PIECE_HEIGHT / self.popUpAnimationFrames

						yDest = self.destination[0]
						if self.board.turn % 2 == 1:
							yDest = self.destination[0] - 3
										
						self.popUpRect = (self.destination[1] * PyChess.PIECE_WIDTH, yDest * PyChess.PIECE_HEIGHT, 0, 0)	

						self.click_state = 3

						self.executeMove = False
						self.promotion = True
						self.handleUpdates = False
						self.handleKeyboardEvents = False
						self.handleMouseEvents = False

				if self.executeMove:
					self.board.doMove(self.move)
					self.board.printBoard()
					self.board.displayBoard()

					self.click_state = 0
					
					self.origin = (-1, -1)
					self.destination = (-1, -1)
					
					self.legalMoves = []
					self.check = False
					self.checkedKingId = ""
					self.checkedKingPos = None
					self.calculatedLegalMoves = False
					self.executeMove = False
			
			#####################################################
			#################### RENDER GAME ####################
			#####################################################

			if self.handleRendering and self.framecount == 0:
				
				if self.animateMove:
					if self.animationFrames > 0:
						self.pieceAnimationPosition = (self.pieceAnimationPosition[0] + self.posDelta[0],
													self.pieceAnimationPosition[1] + self.posDelta[1])

						self.displayBoard()
						self.board.displayPieces(exclude=[self.animationpieceId], invert=False)
						self.gameDisplay.blit(self.animationImg, (self.pieceAnimationPosition[0], self.pieceAnimationPosition[1],
							self.PIECE_WIDTH, self.PIECE_HEIGHT))
						
						self.animationFrames -= 1
					elif self.animationFrames == 0:
						self.animateMove = False
						self.pieceAnimationPosition = None

						self.handleKeyboardEvents = True
						self.handleMouseEvents = True
						self.handleUpdates = True
				elif self.animatePopUp:
					# idea: compute a rectangle each frame, growing deltaWidth and deltaHeight, then draw it
					# then detect mouseclicks on that rectangle and determine an action
					# maybe a good idea to build a class for it		
					if self.popUpAnimationFrames > 0:
						self.popUpRect = ( self.popUpRect[0], self.popUpRect[1], self.popUpRect[2] + self.popUpWidthDelta, self.popUpRect[3] + self.popUpHeightDelta )
						pygame.draw.rect(self.gameDisplay, PyChess.POPUP_COLOR, self.popUpRect)
						print(self.popUpRect)
						self.popUpAnimationFrames -= 1
					else:
						# draw the 4 possible promotion pieces
						team  = self.board.turn % 2
						types = list(PyChess.PROMOTION_STR.values())
						x = self.destination[1]
						y = self.destination[0]
						incY = 1 if team == 0 else -1
						for i in range(4):
							self.popUpPositions[(y, x)] = types[i]
							self.gameDisplay.blit(self.PIECE_IMAGES[(team, types[i])], 
								(x*self.PIECE_WIDTH, y*self.PIECE_HEIGHT))
							
							y += incY

						self.animatePopUp = False
						self.handleMouseEvents = True
						self.popUpRect = None
					print("popup")		
				elif self.check:
					pygame.draw.rect(self.gameDisplay, self.CHECK_COLOR, 
						(self.checkedKingPos[1]*self.PIECE_WIDTH, self.checkedKingPos[0]*self.PIECE_HEIGHT,
							self.PIECE_WIDTH, self.PIECE_HEIGHT))
					self.board.displayPieces(exclude=[self.checkedKingId], invert=True)
				
				pygame.display.update()
			
			self.framecount = (self.framecount + 1) % 3
			
			current_time = time.time_ns()
			self.delta = current_time - self.previous_time
			self.previous_time = current_time
			#print(self.delta / 1e6)

			#restart_str = input("Restart game?: ").lower()
			#accepted_strings = ["yes", "y", "true"]
			#if restart_str in accepted_strings:
			#	self.restart = True
			#	self.board.initialBoardState()
			#	self.isGameOver = False
			#else:
			#	self.restart = False

	def mouseEvents(self):
		mouseX, mouseY = pygame.mouse.get_pos()
		left, middle, right = pygame.mouse.get_pressed()

		if left:
			i = int(mouseY / self.PIECE_WIDTH)
			j = int(mouseX / self.PIECE_HEIGHT)

			print((i, j))

			# si es el segundo click y la casilla es accesible para nuestro equipo
			if self.click_state == 1 and self.board.accessiblePosition((i, j), self.board.turn%2):
				self.destination = (i, j)
				
				self.pieceAnimationPosition = (self.origin[1] * self.PIECE_WIDTH, self.origin[0] * self.PIECE_HEIGHT)
				self.animateMove = True
				self.animationFrames = PyChess.PIECE_MOVE_ANIMATION_FRAMES
				incY = i - self.origin[0]
				incX = j - self.origin[1]
				
				self.posDelta = (incX * PyChess.PIECE_WIDTH / self.animationFrames, incY * PyChess.PIECE_HEIGHT / self.animationFrames)

				pieceId = self.board.board[self.origin[0]][self.origin[1]]
				self.animationImg = PyChess.PIECE_IMAGES[(pieceId[0], pieceId[1])]
				self.animationpieceId = pieceId[2]

				self.handleUpdates = False
				self.handleKeyboardEvents = False
				self.handleMouseEvents = False

				self.click_state = 2
			elif self.click_state == 3 and (i, j) in self.popUpPositions:
				print("clicked inside popUp window")
				self.move.promoted = self.popUpPositions[(i, j)]
				
				self.promotion = False
				self.handleUpdates = True
				self.executeMove = True

				self.click_state = 0
				self.popUpPositions = {}
			elif self.board.enemyInPosition((i, j), (self.board.turn+1)%2)[0]:
				self.click_state = 1
				self.origin = (i, j)

				possible_moves = self.obtainPossibleMoves(self.origin)

				self.displayBoard()
				pygame.draw.rect(self.gameDisplay, self.DISPLAY_COLOR, 
					(j*self.PIECE_WIDTH, i*self.PIECE_HEIGHT, self.PIECE_WIDTH, self.PIECE_HEIGHT))

				for destination, capture in possible_moves:
					y = destination[0]
					x = destination[1]
					height = y * self.PIECE_HEIGHT
					width  = x * self.PIECE_WIDTH
					xInc = self.PIECE_WIDTH/5
					yInc = self.PIECE_HEIGHT/5
					if capture:
						pygame.draw.polygon(self.gameDisplay, self.DISPLAY_COLOR,
							points=[(width, height), (width + xInc, height), (width, height + yInc)])
						pygame.draw.polygon(self.gameDisplay, self.DISPLAY_COLOR,
							points=[(width+self.PIECE_WIDTH, height), (width+self.PIECE_WIDTH - xInc, height), (width + self.PIECE_WIDTH, height + yInc)])
						pygame.draw.polygon(self.gameDisplay, self.DISPLAY_COLOR,
							points=[(width, height+self.PIECE_HEIGHT), (width + xInc, height+self.PIECE_HEIGHT), (width, height + self.PIECE_HEIGHT - yInc)])
						pygame.draw.polygon(self.gameDisplay, self.DISPLAY_COLOR,
							points=[(width + self.PIECE_WIDTH, height + self.PIECE_HEIGHT), (width + self.PIECE_WIDTH - xInc, height + self.PIECE_HEIGHT),
									(width + self.PIECE_WIDTH, height + self.PIECE_HEIGHT - yInc)])
					else:
						pygame.draw.circle(self.gameDisplay, self.DISPLAY_COLOR, (x*self.PIECE_WIDTH + self.PIECE_WIDTH/2, 
										   y*self.PIECE_HEIGHT + self.PIECE_HEIGHT/2), self.PIECE_WIDTH/7)

				self.board.displayPieces()
				pygame.display.update()
			else:
				self.popUpPositions = {}

				self.click_state = 0	
				self.origin = (-1, -1)
				self.destination = (-1, -1)
				self.board.displayBoard()

	def keyboardEvents(self, key):
		if self.promotion:
			if key == pygame.key.key_code("q"):
				print("QUEEN")
				self.move.promoted = Piece.QUEEN_ID
				self.promotion = False
				self.handleMouseEvents = True
				self.handleUpdates = True
				self.executeMove = True
				self.handleRendering = True
			elif key == pygame.key.key_code("w"):
				self.move.promoted = Piece.ROOK_ID
				self.promotion = False
				self.handleMouseEvents = True
				self.handleUpdates = True
				self.executeMove = True
				self.handleRendering = True
			elif key == pygame.key.key_code("e"):
				self.move.promoted = Piece.BISHOP_ID
				self.promotion = False
				self.handleMouseEvents = True
				self.handleUpdates = True
				self.executeMove = True
				self.handleRendering = True
			elif key == pygame.key.key_code("r"):
				self.move.promoted = Piece.KNIGHT_ID
				self.promotion = False
				self.handleMouseEvents = True
				self.handleUpdates = True
				self.executeMove = True
				self.handleRendering = True

	def displayBoard(self):
		self.gameDisplay.blit(self.BOARD_IMG, (0, 0))

	def displayPiece(self, team, type, x, y):
		self.gameDisplay.blit(self.PIECE_IMAGES[(team, type)], 
			(x*self.PIECE_WIDTH, y*self.PIECE_HEIGHT))

	def update(self):
		pygame.display.update()
	
	# Returns a list containing tuples (destination, capture)
	def obtainPossibleMoves(self, origin):
		possible_moves = []
		for move in self.legalMoves:
			if move.origin == origin:
				possible_moves.append((move.dest, move.capture))
		
		return possible_moves


if __name__ == "__main__":
	PyChess()