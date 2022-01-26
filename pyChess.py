from distutils.util import execute
from turtle import pos
from board import Board
from piece import Piece
import pygame
from pgu import gui
import sys
import tkinter as tk
from tkinter import *

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

	PIECE_MOVE_ANIMATION_FRAMES = 5

	DISPLAY_COLOR = (25, 77, 0)

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

	PROMOTION_STR = { "bishop": Piece.BISHOP_ID,
					  "knight": Piece.KNIGHT_ID,
					  "rook":   Piece.ROOK_ID,
					  "queen":  Piece.QUEEN_ID
					}

	def __init__(self):
		self.gameDisplay.fill((255, 255, 255))
		self.gameDisplay.blit(self.BOARD_IMG, (0, 0))
		self.board = Board(self)
		pygame.display.update()
		self.startGame()

	def startGame(self):
		self.isGameOver = False
		self.restart = True

		self.handleMouseEvents = True
		self.handleKeyboardEvents = True

		self.handleUpdates = True

		self.handleRendering = True

		while self.restart:
			self.framecount = 0
			self.click_state = 0
			
			self.origin = (-1, -1)
			self.destination = (-1, -1)
			
			self.move = None
			self.legalMoves = []
			self.calculatedLegalMoves = False
			self.executeMove = False

			self.pieceAnimationPosition = None
			self.animateMove = False
			self.animationFrames = PyChess.PIECE_MOVE_ANIMATION_FRAMES
			self.posDelta = (PyChess.PIECE_WIDTH / self.animationFrames, PyChess.PIECE_HEIGHT / self.animationFrames)
			self.animationImg = None
			self.animationpieceId = ""

			self.promotion = False
			while not self.isGameOver:
				self.FPS_CLOCK.tick(180)

				######################################################
				################### EVENT HANDLING ###################
				######################################################
				for event in pygame.event.get():
					if self.handleMouseEvents and event.type == pygame.MOUSEBUTTONDOWN:
						self.mouseEvents()
					elif self.handleKeyboardEvents and event.type == pygame.KEYDOWN:
						self.keyboardEvents(event)
					elif event.type == pygame.QUIT:
						sys.exit("Quitting...")

				####################################################
				###################  UPDATE GAME ###################
				####################################################

				if self.handleUpdates and self.framecount % 4 == 0:
					if not self.calculatedLegalMoves:
						self.legalMoves = self.board.calculateLegalMoves()
						self.isGameOver = self.board.checkmate or self.board.stalemate
						self.calculatedLegalMoves = True
						if self.isGameOver:
							break

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
							self.executeMove = False
							self.promotion = True
							self.click_state = 0
							self.handleUpdates = False
							self.handleMouseEvents = False
	
					if self.executeMove:
						self.board.doMove(self.move)
						self.board.printBoard()
						self.board.displayBoard()

						self.click_state = 0
						
						self.origin = (-1, -1)
						self.destination = (-1, -1)
						
						self.legalMoves = []
						self.calculatedLegalMoves = False
						self.executeMove = False
				
				if self.handleRendering and self.framecount == 0:
					
					if self.animateMove and self.animationFrames > 0:
						self.pieceAnimationPosition = (self.pieceAnimationPosition[0] + self.posDelta[0],
													   self.pieceAnimationPosition[1] + self.posDelta[1])

						self.displayBoard()
						self.board.displayPieces(exclude=[self.animationpieceId])
						self.gameDisplay.blit(self.animationImg, (self.pieceAnimationPosition[0], self.pieceAnimationPosition[1],
							self.PIECE_WIDTH, self.PIECE_HEIGHT))
						
						self.animationFrames -= 1
					elif self.animationFrames == 0:
						self.animateMove = False
						self.pieceAnimationPosition = None

						self.handleKeyboardEvents = True
						self.handleMouseEvents = True
						self.handleUpdates = True				

					pygame.display.update()
				
				self.framecount = (self.framecount + 1) % 6

			restart_str = input("Restart game?: ").lower()
			accepted_strings = ["yes", "y", "true"]
			if restart_str in accepted_strings:
				self.restart = True
				self.board.initialBoardState()
				self.isGameOver = False
			else:
				self.restart = False

	def mouseEvents(self):
		left, middle, right = pygame.mouse.get_pressed()

		if left:
			mouseCoordinates = pygame.mouse.get_pos()
			i = int(mouseCoordinates[1] / self.PIECE_WIDTH)
			j = int(mouseCoordinates[0] / self.PIECE_HEIGHT)

			if self.board.enemyInPosition((i, j), (self.board.turn+1)%2)[0]:
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
			# si es el segundo click y la casilla es accesible para nuestro equipo
			elif self.click_state == 1 and self.board.accessiblePosition((i, j), self.board.turn%2):
				self.destination = (i, j)
				
				self.pieceAnimationPosition = (self.origin[1] * self.PIECE_WIDTH, self.origin[0] * self.PIECE_HEIGHT)
				self.animateMove = True
				self.animationFrames = PyChess.PIECE_MOVE_ANIMATION_FRAMES
				incY = i - self.origin[0]
				incX = j - self.origin[1]
				
				self.posDelta = (PyChess.PIECE_WIDTH / self.animationFrames, PyChess.PIECE_HEIGHT / self.animationFrames)
				self.posDelta = (self.posDelta[0] * incX, self.posDelta[1] * incY)

				pieceId = self.board.board[self.origin[0]][self.origin[1]]
				self.animationImg = PyChess.PIECE_IMAGES[(pieceId[0], pieceId[1])]
				self.animationpieceId = pieceId[2]

				self.handleUpdates = False
				self.handleKeyboardEvents = False
				self.handleMouseEvents = False

				self.click_state = 2
			else:
				self.click_state = 0	
				self.origin = (-1, -1)
				self.destination = (-1, -1)
				#self.board.displayBoard()

	def keyboardEvents(self, key):
		if self.promotion:
			if key == pygame.key.key_code("q"):
				self.move.promoted = Piece.QUEEN_ID
				self.promotion = False
				self.handleMouseEvents = True
				self.handleUpdates = True
				self.executeMove = True
			elif key == pygame.key.key_code("w"):
				self.move.promoted = Piece.ROOK_ID
				self.promotion = False
				self.handleMouseEvents = True
				self.handleUpdates = True
				self.executeMove = True
			elif key == pygame.key.key_code("e"):
				self.move.promoted = Piece.BISHOP_ID
				self.promotion = False
				self.handleMouseEvents = True
				self.handleUpdates = True
				self.executeMove = True
			elif key == pygame.key.key_code("r"):
				self.move.promoted = Piece.KNIGHT_ID
				self.promotion = False
				self.handleMouseEvents = True
				self.handleUpdates = True
				self.executeMove = True

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