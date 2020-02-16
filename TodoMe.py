"""



          JJJJJJJJJJJ          AAA         TTTTTTTTTTTTTTTTTTTTTTTPPPPPPPPPPPPPPPPP
          J:::::::::J         A:::A        T:::::::::::::::::::::TP::::::::::::::::P
          J:::::::::J        A:::::A       T:::::::::::::::::::::TP::::::PPPPPP:::::P
          JJ:::::::JJ       A:::::::A      T:::::TT:::::::TT:::::TPP:::::P     P:::::P
            J:::::J        A:::::::::A     TTTTTT  T:::::T  TTTTTT  P::::P     P:::::P
            J:::::J       A:::::A:::::A            T:::::T          P::::P     P:::::P
            J:::::J      A:::::A A:::::A           T:::::T          P::::PPPPPP:::::P
            J:::::j     A:::::A   A:::::A          T:::::T          P:::::::::::::PP
            J:::::J    A:::::A     A:::::A         T:::::T          P::::PPPPPPPPP
JJJJJJJ     J:::::J   A:::::AAAAAAAAA:::::A        T:::::T          P::::P
J:::::J     J:::::J  A:::::::::::::::::::::A       T:::::T          P::::P
J::::::J   J::::::J A:::::AAAAAAAAAAAAA:::::A      T:::::T          P::::P
J:::::::JJJ:::::::JA:::::A             A:::::A   TT:::::::TT      PP::::::PP
 JJ:::::::::::::JJA:::::A               A:::::A  T:::::::::T      P::::::::P
   JJ:::::::::JJ A:::::A                 A:::::A T:::::::::T      P::::::::P
     JJJJJJJJJ  AAAAAAA                   AAAAAAATTTTTTTTTTT      PPPPPPPPPP


@package Just Another Todo Plugin (JATP).
@author Sean Richards
@github http://github.com/Krytic/JATP

JATP is what it says on the tin. It is just another to-do plugin.
When bound to a keystroke, the plugin will search all open files in
all windows (excluding unbuffered files) and return anything that
looks like it contains a todo.

"Todo-strings" are defined as the following:
<any preceeding code><any amount of spaces><the language comment char><any amount of spaces>(todo)<comment>

Consequently, the following examples of python code will all be
picked up by the plugin:
- def init(): # todo: implement
- #todo: implement
-             # todo implement
- #TODO implement

Incidentally, if you run the plugin on *this file*, it will pick those
ztrings up as valid todos.

The following code will NOT (yet!) be picked up by the plugin:
- ##### Todo: implement
- #@todo implement
- I should probably mark this as todo: implement
- # a generic comment. Also, # todo: implement

"""

import sublime
import sublime_plugin


heading_string = """  _______        _         _      _     _
 |__   __|      | |       | |    (_)   | |
    | | ___   __| | ___   | |     _ ___| |_
    | |/ _ \\ / _` |/ _ \\  | |    | / __| __|
    | | (_) | (_| | (_) | | |____| \\__ \\ |_
    |_|\\___/ \\__,_|\\___/  |______|_|___/\\__|




"""

comment_characters = {"python": "#", "php": ["#", "//"]}

class TodomeCommand(sublime_plugin.TextCommand):
	"""
	Provides a simple todo interface.

	Scans all open files in all windows; will output a list of todos in a new view.

	Extends:
		sublime_plugin.TextCommand
	"""
	def run(self, edit):
		global heading_string

		window_manager = sublime.active_window()

		output_view = None

		views = [view for window in sublime.windows() for view in window.views()]

		for view in views:
			if view.name() == "Todo List":
				output_view = view
				output_view.erase(edit, sublime.Region(0, output_view.size()))

		if output_view == None:
			output_view = window_manager.new_file()
			output_view.set_name("Todo List")

		num_todos = 0

		output_string = heading_string

		for view in views:
			if view.file_name() == None:
				continue

			view_language = view.settings().get("syntax").split("/")[-1].split(".")[0].lower()
			if view_language not in comment_characters.keys():
				continue

			with open(view.file_name(), 'r') as f:
				output_string += (view.file_name() + "\n\n")
				contents = f.readlines()
				num_todos_in_file = 0

				for j in range(len(contents)):
					line = contents[j]
					if line.lstrip() == '':
						continue
					else:
						char_to_search_for = comment_characters[view_language]
						if type(char_to_search_for) == list:
							for char in char_to_search_for:
								bits = line.split(char, 1)
						else:
							bits = line.split(comment_characters[view_language], 1)

						if len(bits) < 2:
							# no comments, so ignore
							continue

						line = bits[1]
						if len(line.strip()) < 4:
							# may be comment with no text
							continue

						if "todo" == line.strip().lower()[:4]:
							stripped_line = line.lstrip().rstrip()[4:]
							if stripped_line[0] == ":":
								stripped_line = stripped_line[1:]
							stripped_line = stripped_line.lstrip()
							line_length = len("    " + stripped_line + "(line {})\n".format(j+1))
							num_spaces = 70 - line_length
							output_string += ("    " + stripped_line + " " * num_spaces + "(line {})\n".format(j+1))
							num_todos_in_file += 1

				if num_todos_in_file == 0:
					output_string += "    You're good!"

				num_todos += num_todos_in_file

				output_string += "\n\n"

		output_string += "{} todos.".format(num_todos)

		output_view.insert(edit, 0, output_string)
		window_manager.focus_view(output_view)