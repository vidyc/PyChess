

class Move():
	
	def __init__(self, team, origin, dest, captured, passant, promoted):
		# origin =   initial position
		# dest =     final position
		# captured = piece id that has been captured
		# passant =  inidicates if it's an en passant capture
		# promoted = piece id to which our piece has been promoted

		self.id = "si claro"
		self.team = team
		self.origin = origin
		self.dest = dest
		self.captured = captured 
		self.passant = passant
		self.promoted = promoted
