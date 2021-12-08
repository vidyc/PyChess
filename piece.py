import random, string

class Piece():

	EMPTY_PIECE_ID = (-1, -1)
	
	PAWN_ID = 0
	KNIGHT_ID = 1
	BISHOP_ID = 2
	ROOK_ID = 3
	QUEEN_ID = 4
	KING_ID = 5

	SLIDERS = [BISHOP_ID, ROOK_ID, QUEEN_ID]

	WHITE_ID = 0
	BLACK_ID = 1

	INITIAL_POSITIONS = { (WHITE_ID, PAWN_ID): list(zip([6]*8, list(range(8)))),
						(BLACK_ID, PAWN_ID): list(zip([1]*8, list(range(8)))),
						(WHITE_ID, KNIGHT_ID): [ (7, 1), (7, 6) ],
						(BLACK_ID, KNIGHT_ID): [ (0, 1), (0, 6) ],
						(WHITE_ID, BISHOP_ID): [ (7, 2), (7, 5) ],
						(BLACK_ID, BISHOP_ID): [ (0, 2), (0, 5) ],
						(WHITE_ID, ROOK_ID): [ (7, 0), (7, 7) ],
						(BLACK_ID, ROOK_ID): [ (0, 0), (0, 7) ],
						(WHITE_ID, QUEEN_ID): [ (7, 3) ], 
						(BLACK_ID, QUEEN_ID): [ (0, 3) ],
						(WHITE_ID, KING_ID): [ (7, 4) ],
						(BLACK_ID, KING_ID): [ (0, 4) ]
					    }

	KNIGHT_MOVES = [ (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2) ]
	KING_MOVES = list( zip( [-1]*3, list(range(-1, 2)) ) ) + [(0, -1), (0, 1)] + list( zip( [1]*3, list(range(-1, 2)) ) ) 

	def __init__(self, team, type):
		stringID = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
		self.id = (team, type, stringID)
		self.type = type
		self.team = team
		self.stringID = stringID