import pygame
import time as t
import generate
from sudoku import *
import random
from thread import Threads
pygame.init()
font = pygame.font.SysFont(None, 70)

pad = 20
WIDTH = 1000
HEIGHT = 670
change = True

class Grid:
	
	def __init__(self, rows, cols, width, height):
		a = -1
		# assign a problem
		self.change = change
		if self.change:
			b = random.randint(1, 10)
			while a == b:
				b = random.randint(1, 10)
			a = b

			self.board = Sudoku("problems/" + str(a) + ".txt")
			creator= generate.SudokuCreater(self.board)
			self.solved_board= creator.solve()
			self.change = False

		self.rows = rows
		self.cols = cols
		self.cubes = [[Cube(self.board.structure[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
		self.width = width
		self.height = height
		self.model = None
		self.selected = None

	def update_model(self):
		self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

	def place(self, val):
		row, col = self.selected
		if self.cubes[row][col].value == 0:
			self.cubes[row][col].set(val)
			self.update_model()

			if (val == int(self.solved_board[Variable(row, col)])):
				return True
			else:
				self.cubes[row][col].set(0)
				self.cubes[row][col].set_temp(0)
				self.update_model()
				return False

	def sketch(self, val):
		row, col = self.selected
		self.cubes[row][col].set_temp(val)

	def draw(self, screen):
		# Outer Box
		pygame.draw.rect(screen, pygame.Color("black"), pygame.Rect(pad, pad, 630, 630), 6)
		# Draw Grid Lines
		gap = self.width / 9
		for i in range(self.rows+1):
			line_width = 4 if i % 3 == 0 and i != 0 else 1
			# vertical lines
			pygame.draw.line(screen, pygame.Color("black"), ((i * gap) + pad, pad), ((i * gap) + pad, (self.height) + pad), line_width)
			# Horizontal Zok Bach
			pygame.draw.line(screen, pygame.Color("black"), (pad, (i * gap) + pad), ((self.width) + pad, (i * gap) + pad), line_width)

		# Draw Cubes
		for i in range(self.rows):
			for j in range(self.cols):
				self.cubes[i][j].draw(screen)

	def select(self, row, col):
		# Reset all other
		for i in range(self.rows):
			for j in range(self.cols):
				self.cubes[i][j].selected = False

		self.cubes[row][col].selected = True
		self.selected = (row, col)

	def clear(self):
		row, col = self.selected
		if self.cubes[row][col].value == 0:
			self.cubes[row][col].set_temp(0)

	def click(self, pos):
		"""
		:param: pos
		:return: (row, col)
		"""
		if pos[0] < self.width and pos[1] < self.height:
			gap = self.width / 9
			x = (pos[0] - pad) // gap
			y = (pos[1] - pad) // gap
			return (int(y),int(x))
		else:
			return None

	def is_finished(self):
		for i in range(self.rows):
			for j in range(self.cols):
				if self.cubes[i][j].value == 0:
					return False
		return True

class Cube:
	rows = 9
	cols = 9

	def __init__(self, value, row, col, width ,height):
		self.value = int(value)
		self.temp = 0
		self.row = row
		self.col = col
		self.width = width
		self.height = height
		self.selected = False

	def draw(self, screen):
		fnt = pygame.font.SysFont(None, 40)
		gap = self.width / 9
		x = self.col * gap
		y = self.row * gap

		if self.temp != 0 and self.value == 0:
			text = fnt.render(str(self.temp), 1, (128,128,128))
			screen.blit(text, (x+5+pad, y+5+pad))
		elif self.value != 0:
			# print(str(self.value) + str(" solved"))
			text = fnt.render(str(self.value), 1, (0, 0, 0))
			screen.blit(text, (x + (gap/2 - text.get_width()/2) + pad, y + (gap/2 - text.get_height()/2) + pad))

		if self.selected:
			pygame.draw.rect(screen, (255,0,0), (x + pad, y + pad, gap, gap), 3)

	def set(self, val):
		self.value = val

	def set_temp(self, val):
		self.temp = val

class button():
	def __init__(self, color, x,y,width,height, textcolor, text=''):
		self.color = color
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.textcolor = textcolor
		self.text = text

	def draw(self,win,outline=None):
		#Call this method to draw the button on the screen
		if outline:
			pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
			
		pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
		
		if self.text != '':
			font = pygame.font.SysFont(None, 25)
			text = font.render(self.text, 1, self.textcolor)
			win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

	def isOver(self, pos):
		#Pos is the mouse position or a tuple of (x,y) coordinates
		if pos[0] > self.x and pos[0] < self.x + self.width:
			if pos[1] > self.y and pos[1] < self.y + self.height:
				return True
			
		return False

# play state
def redraw_screen(screen, board, time, mistakes):
	screen.fill(pygame.Color("white"))
	# Heading
	fnt = pygame.font.SysFont(None, 115)
	text = fnt.render("Sudoku!", 1, (0,0,0))
	screen.blit(text, (665, 30))
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Instructions:", 1, (0,0,0))
	screen.blit(text, (670, 140))
	# Draw rules
	fnt = pygame.font.SysFont(None, 28)
	text = fnt.render("-> Use mouse to select box.", 1, (0, 0, 0))
	screen.blit(text, (670, 170))
	text = fnt.render("-> Enter no. to fill temporarily.", 1, (0, 0, 0))
	screen.blit(text, (670, 210))
	text = fnt.render("-> Press Enter to fill permanently.", 1, (0, 0, 0))
	screen.blit(text, (670, 250))
	text = fnt.render("-> Press Backspace/Del to remove.", 1, (0, 0, 0))
	screen.blit(text, (670, 290))
	text = fnt.render("-> Press Escape to quit.", 1, (0, 0, 0))
	screen.blit(text, (670, 330))
	# Draw mistakes
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Mistakes: " + str(mistakes), 1, (150, 0, 0))
	screen.blit(text, (665, 630))
	# Draw time
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
	screen.blit(text, (870, 630))
	# Draw grid and board
	board.draw(screen)


# util function for formatting time in a string
def format_time(secs):
	sec = secs%60
	minute = secs//60

	if sec < 10:
		sec = "0" + str(sec)
	if minute < 10:
		minute = "0" + str(minute)

	et = " " + str(minute) + ":" + str(sec)
	return et

# gameover state
def draw_gameover(screen, board, time, mistakes):
	screen.fill(pygame.Color("white"))
	# Heading
	fnt = pygame.font.SysFont(None, 115)
	text = fnt.render("Sudoku!", 1, (0,0,0))
	screen.blit(text, (665, 30))
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Instructions:", 1, (0,0,0))
	screen.blit(text, (670, 140))
	# Draw rules
	fnt = pygame.font.SysFont(None, 28)
	text = fnt.render("-> Use mouse to select box.", 1, (0, 0, 0))
	screen.blit(text, (670, 170))
	text = fnt.render("-> Enter no. to fill temporarily.", 1, (0, 0, 0))
	screen.blit(text, (670, 210))
	text = fnt.render("-> Press Enter to fill permanently.", 1, (0, 0, 0))
	screen.blit(text, (670, 250))
	text = fnt.render("-> Press Backspace/Del to remove.", 1, (0, 0, 0))
	screen.blit(text, (670, 290))
	text = fnt.render("-> Press Escape to quit.", 1, (0, 0, 0))
	screen.blit(text, (670, 330))
	# Draw gameover text
	fnt = pygame.font.SysFont(None, 60)
	text = fnt.render("START GAME!", 1, (0, 0, 0))
	screen.blit(text, (675, 400))
	# Press any key to restart
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Press any key to restart.", 1, (0, 0, 0))
	screen.blit(text, (705, 480))

	# Results
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Your Score is given below:", 1, (0, 0, 0))
	screen.blit(text, (695, 590))
	# Draw mistakes
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Mistakes: " + str(mistakes), 1, (150, 0, 0))
	screen.blit(text, (665, 630))
	# Draw time
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
	screen.blit(text, (870, 630))
	# Draw grid and board
	board.draw(screen)
	pygame.display.flip()

	waiting = True
	while waiting:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				waiting = False

# solved state
def draw_solved(screen, board, time, mistakes):
	for i in range(board.rows):
		for j in range(board.cols):
			board.cubes[i][j].value = board.solved_board[Variable(i, j)]
	screen.fill(pygame.Color("white"))
	# Heading
	fnt = pygame.font.SysFont(None, 115)
	text = fnt.render("Sudoku!", 1, (0,0,0))
	screen.blit(text, (665, 30))
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Instructions:", 1, (0,0,0))
	screen.blit(text, (670, 140))
	# Draw rules
	fnt = pygame.font.SysFont(None, 28)
	text = fnt.render("-> Use mouse to select box.", 1, (0, 0, 0))
	screen.blit(text, (670, 170))
	text = fnt.render("-> Enter no. to fill temporarily.", 1, (0, 0, 0))
	screen.blit(text, (670, 210))
	text = fnt.render("-> Press Enter to fill permanently.", 1, (0, 0, 0))
	screen.blit(text, (670, 250))
	text = fnt.render("-> Press Backspace/Del to remove.", 1, (0, 0, 0))
	screen.blit(text, (670, 290))
	text = fnt.render("-> Press Escape to quit.", 1, (0, 0, 0))
	screen.blit(text, (670, 330))
	# Draw giveup text
	fnt = pygame.font.SysFont(None, 65)
	text = fnt.render("YOU GAVE UP!", 1, (0, 0, 0))
	screen.blit(text, (670, 405))
	# Press any key to restart
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Press any key to restart.", 1, (0, 0, 0))
	screen.blit(text, (705, 480))

	# Results
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Your Score is given below:", 1, (0, 0, 0))
	screen.blit(text, (695, 590))
	# Draw mistakes
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Mistakes: " + str(mistakes), 1, (150, 0, 0))
	screen.blit(text, (665, 630))
	# Draw time
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
	screen.blit(text, (870, 630))
	# Draw grid and board
	board.draw(screen)
	pygame.display.flip()

	waiting = True
	while waiting:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				waiting = False

# win state
def draw_won(screen, board, time, mistakes):
	screen.fill(pygame.Color("white"))
	# Heading
	fnt = pygame.font.SysFont(None, 115)
	text = fnt.render("Sudoku!", 1, (0,0,0))
	screen.blit(text, (665, 30))
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Instructions:", 1, (0,0,0))
	screen.blit(text, (670, 140))
	# Draw rules
	fnt = pygame.font.SysFont(None, 28)
	text = fnt.render("-> Use mouse to select box.", 1, (0, 0, 0))
	screen.blit(text, (670, 170))
	text = fnt.render("-> Enter no. to fill temporarily.", 1, (0, 0, 0))
	screen.blit(text, (670, 210))
	text = fnt.render("-> Press Enter to fill permanently.", 1, (0, 0, 0))
	screen.blit(text, (670, 250))
	text = fnt.render("-> Press Backspace/Del to remove.", 1, (0, 0, 0))
	screen.blit(text, (670, 290))
	text = fnt.render("-> Press Escape to quit.", 1, (0, 0, 0))
	screen.blit(text, (670, 330))
	# Draw winning text
	fnt = pygame.font.SysFont(None, 75)
	text = fnt.render("YOU WON!", 1, (0, 0, 0))
	screen.blit(text, (685, 400))
	# Press any key to restart
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Press any key to restart.", 1, (0, 0, 0))
	screen.blit(text, (705, 480))

	# Results
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Your Score is given below:", 1, (0, 0, 0))
	screen.blit(text, (695, 590))
	# Draw mistakes
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Mistakes: " + str(mistakes), 1, (150, 0, 0))
	screen.blit(text, (665, 630))
	# Draw time
	fnt = pygame.font.SysFont(None, 30)
	text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
	screen.blit(text, (870, 630))
	# Draw grid and board
	board.draw(screen)
	pygame.display.flip()

	waiting = True
	while waiting:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYDOWN:
				waiting = False

def main():
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("Multithreaded Sudoku!")
	solvebutton = button((200, 200, 200), 760, 530, 120, 50, (0, 0, 0), "Get Solution")
	resetbutton = button((200, 200, 200), 760, 460, 120, 50, (0, 0, 0), "Reset Game")
	board = Grid(9, 9, 630, 630)
	key = None
	# state variables
	run = True
	gameover = False
	getsolved = False
	win = False
	# score variables
	mistakes = 0
	start = t.time()
	play_time = 0
	while run:
		
		if gameover:
			draw_gameover(screen, board, play_time, mistakes)
			mistakes = 0
			board.change = False
			board = Grid(9, 9, 630, 630)
			start = t.time()
			gameover = False

		if getsolved:
			draw_solved(screen, board, play_time, mistakes)
			mistakes = 0
			board.change = True
			board = Grid(9, 9, 630, 630)
			start = t.time()
			getsolved = False

		if win:
			draw_won(screen, board, play_time, mistakes)
			mistakes = 0
			board.change = True
			board = Grid(9, 9, 630, 630)
			start = t.time()
			win = False

		play_time = round(t.time() - start)

		for event in pygame.event.get():
			pos = pygame.mouse.get_pos()
			if event.type == pygame.QUIT:
				run = False

			if event.type == pygame.MOUSEBUTTONDOWN:
				# if solve button is clicked
				if solvebutton.isOver(pos):
					getsolved = True
				# if reset button is clicked
				if resetbutton.isOver(pos):
					gameover = True

			# if user wins
			if board.is_finished():
				# win routine
				print("\nSHAH ANWAAR KHALID CED18I048\nSHUBHAM KARWA COE18B062\nASHISH CHOUDHARY CED18I061\nSUYASH CHOUDHARY COE18B054\nSHASHANK DOKANIA COE18B067")
				win = True

			# hover for solve button
			if event.type == pygame.MOUSEMOTION:
				if solvebutton.isOver(pos):
					solvebutton.color = (40, 40, 40)
					solvebutton.textcolor = (255, 255, 255)
				else:
					solvebutton.color = (200, 200, 200)
					solvebutton.textcolor = (0, 0, 0)
			# Hover for reset button
			if event.type == pygame.MOUSEMOTION:
				if resetbutton.isOver(pos):
					resetbutton.color = (40, 40, 40)
					resetbutton.textcolor = (255, 255, 255)
				else:
					resetbutton.color = (200, 200, 200)
					resetbutton.textcolor = (0, 0, 0)

			# keystrokes
			if event.type == pygame.KEYDOWN:
				# escape to quit
				if event.key == pygame.K_ESCAPE:
					run = False
				if event.key == pygame.K_1 or event.key == pygame.K_KP1:
					key = 1
				if event.key == pygame.K_2 or event.key == pygame.K_KP2:
					key = 2
				if event.key == pygame.K_3 or event.key == pygame.K_KP3:
					key = 3
				if event.key == pygame.K_4 or event.key == pygame.K_KP4:
					key = 4
				if event.key == pygame.K_5 or event.key == pygame.K_KP5:
					key = 5
				if event.key == pygame.K_6 or event.key == pygame.K_KP6:
					key = 6
				if event.key == pygame.K_7 or event.key == pygame.K_KP7:
					key = 7
				if event.key == pygame.K_8 or event.key == pygame.K_KP8:
					key = 8
				if event.key == pygame.K_9 or event.key == pygame.K_KP9:
					key = 9
				if event.key == pygame.K_DELETE  or event.key == pygame.K_BACKSPACE:
					board.clear()
					key = None
				if event.key == pygame.K_RETURN:
					i, j = board.selected
					if board.cubes[i][j].temp != 0:
						if board.place(board.cubes[i][j].temp):
							print(".", end = "")
						else:
							mistakes += 1
						key = None

			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				clicked = board.click(pos)
				if clicked:
					board.select(clicked[0], clicked[1])
					key = None

		if board.selected and key != None:
			board.sketch(key)

		redraw_screen(screen, board, play_time, mistakes)
		solvebutton.draw(screen, (0, 0, 0))
		resetbutton.draw(screen, (0, 0, 0))
		pygame.display.update()

main()
pygame.quit()
