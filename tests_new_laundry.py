import urllib.request


class Laundry:
	# links = {"3": "http://classic.laundryview.com/laundry_room.php?lr=1364826", "5", "6", "7", "8"}
	html = str(urllib.request.urlopen("http://classic.laundryview.com/laundry_room.php?lr=136484").read())
	nums = [1, 2, 3, 4, 5, 6, 7, 8, 9]
	washers_text = []
	dryers_text = []

	def __init__(self):
		# TO DO: add floor-getting information
		print()

	def craft_floor(self, location):
		response = ""
		try:
			int(location[0])
			response += "On the %s floor, " % location
		except ValueError:
			response += "In %s, " % location

		self.get_laundry(self.html)
		washers = self.check_available(self.washers_text)
		dryers = self.check_available(self.dryers_text)

		# ensures correct grammar
		if washers[0] == 1:
			response += "%d washer and " % (washers[0])
		else:
			response += "%d washers and " % (washers[0])
		if dryers[0] == 1:
			response += "%d dryer are available." % (dryers[0])
		else:
			response += "%d dryers are available." % (dryers[0])

		# checks for machines that are almost done
		if washers[0] == 0 and len(washers[1]) > 0:
			response += " The next available washer will be ready in %d" % (washers[1][0])
			if washers[1][0] == 1:
				response += " minute."
			else:
				response += " minutes."
		if dryers[0] == 0 and len(dryers[1]) > 0:
			response += " The next available dryer will be ready in %d" % (dryers[1][0])
			if dryers[1][0] == 1:
				response += " minute."
			else:
				response += " minutes."

		return response

	def get_laundry(self, string):
		try:
			times = string[string.index("<span class=\"stat\">")+40:]
			end = times.index("\\t")
			try:
				times.index("<td align=\"right\" valign=\"top\"")
				self.washers_text.append(times[:end])
			except:
				self.dryers_text.append(times[:end])
			self.get_laundry(times)
		except ValueError:
			pass

	@staticmethod
	def check_available(machines):
		available_counter = 0
		times_remaining = []
		for machine in machines:
			if " ended" in machine or "ble" in machine:
				available_counter += 1
			else:
				try:
					time = int(machine[:machine.index("min")].split()[-1])
					times_remaining.append(time)
				except ValueError:
					pass
		return available_counter, sorted(times_remaining)

laundry = Laundry()
print(laundry.craft_floor("Baker"))
