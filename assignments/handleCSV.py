
def getIDFromCSV(headerRow:list[str], row:list[str]) -> int:
	for i in range(len(headerRow)):
		if headerRow[i] == "ID":
			return int(row[i])
	return None


def getNameFromCSV(headerRow:list[str], row:list[str]) -> str:
	for i in range(len(headerRow)):
		if headerRow[i] == "Name":
			if row[i] == "":
				return "MISSING NAME!"
			
			return row[i]
	
	return None

def getTeammatesFromCSV(headerRow:list[str], row:list[str]) -> str:
	teammates = [str, str, str, str, str]
	for i in range(len(headerRow)):
		if headerRow[i] == "1":
			teammates[0] = row[i]
		
		elif headerRow[i] == "2":
			teammates[1] = row[i]
		
		elif headerRow[i] == "3":
			teammates[2] = row[i]
		
		elif headerRow[i] == "4":
			teammates[3] = row[i]
		
		elif headerRow[i] == "5":
			teammates[4] = row[i]
		
	return teammates


def checkIfTeamValid(id: int, name: str, teammates:list[str]) -> bool:
	if id is None or name is None or teammates is None:
		return False
	
	if type(id) is not int:
		# print(f"(checkIfTeamValid) -> ID is not int")
		return False

	if len(name) == 0:
		# print(f"(checkIfTeamValid) -> Invalid name for team with ID of {id}")
		return False

	teammateCount = 0
	for teammate in teammates:
		if teammate != "":
			teammateCount += 1

	# DONT ALLOW MORE THAN 5 PEOPLE ON A TEAM
	if teammateCount > 5:
		# print(f"(checkIfTeamValid) -> Invalid number of teammates on team with ID of {id}")
		return False
	
	return True
