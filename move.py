

class Move():
	
	def __init__(self, team, origin, dest, capture=False, castling=None, passant=False, enPassantPos=None, promoted=None):
		# origin =   initial position
		# dest =     final position
		# captured = piece id that has been captured
		# castling = 0 -> kingside, 1 -> queenside
		# passant =  inidicates if it's an en passant capture
		# enPassantPos = indicates the position in which an en
		# passant capture will be possible for the opposing team
		# promoted = piece id to which our piece has been promoted

		self.notation = "si claro"
		self.team = team
		self.origin = origin
		self.dest = dest
		self.capture = capture
		self.castling = castling
		self.passant = passant
		self.enPassantPos = enPassantPos
		self.promoted = promoted

	def print(self):
		print(("Move(" + str(self.origin) + ", " + str(self.dest) + ", " + str(self.capture) 
			   + ", " + str(self.castling) + ", " + str(self.passant) + ", " + str(self.enPassantPos) 
			   + ", " + str(self.promoted)))