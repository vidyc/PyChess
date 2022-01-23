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
		restart = True

		while restart:
			click_state = 0
			origin = (-1, -1)
			destination = (-1, -1)
			move = None
			legalMoves = []
			calculated = False
			promotion = False
			promotion_type = None
			while not self.isGameOver:
				self.FPS_CLOCK.tick(180)
				if not calculated:
					legalMoves = self.board.calculateLegalMoves()
					self.isGameOver = self.board.checkmate or self.board.stalemate
					calculated = True

				for event in pygame.event.get():
					if event.type == pygame.MOUSEBUTTONDOWN:
						left, middle, right = pygame.mouse.get_pressed()

						if left and not promotion:
							mouseCoordinates = pygame.mouse.get_pos()
							i = int(mouseCoordinates[1] / self.PIECE_WIDTH)
							j = int(mouseCoordinates[0] / self.PIECE_HEIGHT)
							print("click en coordenadas " + str(mouseCoordinates) + " " + str((i, j)))
							print(click_state)
							if self.board.enemyInPosition((i, j), (self.board.turn+1)%2)[0]:
								click_state = 1
								origin = (i, j)
								self.displayBoard()
								pygame.draw.rect(self.gameDisplay, (77, 166, 255), 
									(j*self.PIECE_WIDTH, i*self.PIECE_HEIGHT, self.PIECE_WIDTH, self.PIECE_HEIGHT))
								self.board.displayPieces()
								pygame.display.update()
							# si es el segundo click y la casilla es accesible para nuestro equipo
							elif click_state == 1 and self.board.accessiblePosition((i, j), self.board.turn%2):
								destination = (i, j)
								click_state = 2
							else:
								click_state = 0	
								origin = (-1, -1)
								destination = (-1, -1)
								self.board.displayBoard()
								pygame.display.update()	
					elif promotion and event.type == pygame.KEYDOWN:
						if event.key == pygame.key.key_code("q"):
							print("QUEEN")
							move.promoted = Piece.QUEEN_ID
							promotion = False
						elif event.key == pygame.key.key_code("w"):
							print("ROOK")
							move.promoted = Piece.ROOK_ID
							promotion = False
						elif event.key == pygame.key.key_code("e"):
							print("BISHOP")
							move.promoted = Piece.BISHOP_ID
							promotion = False
						elif event.key == pygame.key.key_code("r"):
							print("KNIGHT")
							move.promoted = Piece.KNIGHT_ID
							promotion = False
					elif event.type == pygame.QUIT:
						sys.exit("Quitting...")

				if click_state == 2 and not promotion:
					# check if the selected move is a legal move
					for m in legalMoves:
						if m.origin == origin and m.dest == destination:
							move = m
							move.print()
							break

					if move == None:
						click_state = 0
						origin = (-1, -1)
						destination = (-1, -1)
						self.board.displayBoard()
						pygame.display.update()	
					elif move.promoted != None:	
						promotion = True
						click_state = 0

				if move != None and not promotion:
					self.board.doMove(move)
					self.board.printBoard()
					self.board.displayBoard()
					
					move = None
					click_state = 0
					origin = (-1, -1)
					destination = (-1, -1)
					legalMoves = []
					calculated = False

			restart_str = input("Restart game?: ").lower()
			accepted_strings = ["yes", "y", "true"]
			if restart_str in accepted_strings:
				restart = True
				self.board.initialBoardState()
				self.isGameOver = False
			else:
				restart = False

	def displayBoard(self):
		self.gameDisplay.blit(self.BOARD_IMG, (0, 0))

	def displayPiece(self, team, type, x, y):
		self.gameDisplay.blit(self.PIECE_IMAGES[(team, type)], 
			(x*self.PIECE_WIDTH, y*self.PIECE_HEIGHT))

	def update(self):
		pygame.display.update()


if __name__ == "__main__":
	PyChess()