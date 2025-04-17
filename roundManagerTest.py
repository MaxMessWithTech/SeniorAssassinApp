
class Team:
	def __init__(self, id, size):
		self.id = id
		self.size = size
	
	# Get # of remaining participants
	def get_remaining_count(self) -> int:
		return self.size
	

	def __str__(self):
		return f"Team {self.id} of size {self.size}"
	
	def __repr__(self):
		return self.__str__()


# Returns the pairings it has chosen and if it is valid
def recursive_pairing(
		round, target_size:int, depth:int, 
		pairings:list, remaining:list
	) -> list | bool:
	MARGIN = 2

	# PRUNE IF DEPTH HAS REACHED AN EXCESSIVE NUMBER:
	if depth >= 50:
		return pairings
	
	if len(remaining) == 0:
		return pairings
	
	for i in range(len(remaining)):
		# Try adding it
		pass


def make_multi_pairings(round, num_pairings:int):
	"""
	Algorithm Rules
	1) 	A prosecuting team cannot have multiple targets of the same team
	2) 	Shoot for the same number of target participants 
		between the same number of targets
	"""

	teams = [
		Team(0, 4), 	Team(2, 4), 	Team(3, 1), 
		Team(6, 2), 	Team(8, 5), 	Team(10, 4), 
		Team(12, 5), 	Team(14, 5), 	Team(15, 3), 
		Team(17, 4), 	Team(18, 3), 	Team(19, 4), 
		Team(20, 3), 	Team(22, 4), 	Team(23, 2), 
		Team(24, 4), 	Team(25, 3), 	Team(29, 4), 
		Team(30, 5)
	]
	
	# Sort in order of remaining members using bubble sort
	for i in range(len(teams)):
		swapped = False

		for j in range(0, len(teams) - i - 1):

			if teams[j].get_remaining_count() > teams[j+1].get_remaining_count():
				teams[j], teams[j+1] = teams[j+1], teams[j]
				swapped = True
		if swapped is False:
			break
	
	print(teams)

	# Get count of all remaining members
	total_remaining = 0
	for team in teams:
		total_remaining += team.get_remaining_count()
	
	# The average number of people each team should target
	num_targets_avg = total_remaining / (len(teams) * num_pairings)

	# Create Targets


if __name__ == "__main__":
	make_multi_pairings(None, None)