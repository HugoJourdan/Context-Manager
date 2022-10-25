# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#
#	General Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/General%20Plugin
#
#
###########################################################################################################

import objc
import json
import os
import random

from datetime import datetime
from GlyphsApp import *
from GlyphsApp.plugins import *
from GlyphsApp.UI import GlyphView
from AppKit import NSColor
from vanilla import *

class findContext(GeneralPlugin):

	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({'en': 'Context Manager'})
		self.font = Glyphs.font
		self.jsonPath = os.path.expanduser("~/Library/Application Support/Glyphs 3/info/ContextManager.json")

		if not os.path.exists(os.path.expanduser("~/Library/Application Support/Glyphs 3/info")):
			os.makedirs(os.path.expanduser("~/Library/Application Support/Glyphs 3/info"))

		os.chdir(os.path.dirname(self.jsonPath))
		if not os.path.exists(self.jsonPath):
			with open('ContextManager.json', 'w') as f:
				json.dump({"ContextClass":{},"Glyph":{}}, f)

		# Load File

		with open(self.jsonPath, encoding='utf8') as json_file:
			self.jsonFile = json.load(json_file)


		wW, wH = 660, 450
		self.w = FloatingWindow((wW, wH), "Context Manager")
		self.w.tabs = Tabs((10, 10, -10, -40), ["Context Glyph", "Context Class"], sizeStyle='small', callback=self.switchTabCallback)
		tab1 = self.w.tabs[0]
		tab2 = self.w.tabs[1]

		#–––––––––––––––––––––––––––––––––––––––––––#
		# TAB 1 : CONTEXT GLYPH                     #
		#–––––––––––––––––––––––––––––––––––––––––––#

		#-------------------------------------------#
		# Draw Selected Glyph
		#-------------------------------------------#

		tab1.box = Box((10, 18, 170, 170), cornerRadius=6, fillColor=NSColor.colorWithRed_green_blue_alpha_(0, 0, 0, 0.05), borderColor=NSColor.colorWithRed_green_blue_alpha_(0, 0, 0, 0.1) )

		tab1.box.glyphView = GlyphView((0, 10, -10, -20), layer=None, backgroundColor=NSColor.clearColor())

		tab1.box.drawline = HorizontalLine((0, -18, -0, 1))

		tab1.box.drawGlyphName = TextBox((2,-12,170,20), "GlyphName", sizeStyle='mini')
		tab1.box.drawGlyphUnicode = TextBox((2,-12,-2,20), "Unicode", sizeStyle='mini', alignment="right")


		#-------------------------------------------#
		# Options
		#-------------------------------------------#

		tab1.optionText = TextBox((6, 206, 160, 17), "Context Filters", sizeStyle='small')
		tab1.optionText.getNSTextField().setToolTip_("Check options to restrict context drawn to specific sources")

		tab1.contextClassCheckBox = CheckBox((10, 226, -10, 20), "Class", callback=self.toggleOptionCallback, sizeStyle="small")
		tab1.smartContextCheckBox = CheckBox((100, 226, -10, 20), "Smart", callback=self.toggleOptionCallback, sizeStyle="small")
		tab1.contextWordsCheckBox = CheckBox((10, 244, -10, 20), "Words", callback=self.toggleOptionCallback, sizeStyle="small")
		tab1.spacingContextCheckBox = CheckBox((100, 244, -10, 20), "Spacing", callback=self.toggleOptionCallback, sizeStyle="small")
		tab1.contextStringCheckBox = CheckBox((10, 262, -10, 20), "Strings", callback=self.toggleOptionCallback, sizeStyle="small")

		tab1.sep2 = HorizontalLine((10, 289, 170, 1))

		tab1.startCheckBox = CheckBox((10, 296, -10, 20), "Start with", callback=self.toggleOptionCallback, sizeStyle="small")
		tab1.includeCheckBox = CheckBox((100, 296, -10, 20), "Include", callback=self.toggleOptionCallback, sizeStyle="small")

		tab1.sep3 = HorizontalLine((10, 323, 170, 1))

		tab1.lowercaseCheckBox = CheckBox((10, 330, -10, 20), "Lowercase", callback=self.toggleOptionCallback, sizeStyle="small")
		tab1.uppercaseCheckBox = CheckBox((100, 330, -10, 20), "Uppercase", callback=self.toggleOptionCallback, sizeStyle="small")


		#-------------------------------------------#
		# RIGHT PART TAB
		#-------------------------------------------#

		tab1.contextClassTitle = TextBox((200, 14, -10, 17), "Glyph Classes", sizeStyle='small')
		tab1.contextClassList = List((200, 32, -10, 70), items=([]), drawFocusRing=False, rowHeight=20,)

		tab1.contextWordsTitle = TextBox((200, 114, -10, 17), "Glyph Words", sizeStyle='small')
		tab1.contextWordEditor = TextEditor((200, 132, 140, -10),text="", callback=self.updateGlyphWordsCallback)

		tab1.contextStringsTitle = TextBox((350, 114, -10, 17), "Glyph Strings", sizeStyle='small')
		tab1.contextStringsEditor = TextEditor((350, 132, -10, -10), text="", callback=self.updateGlyphStringsCallback)



		#–––––––––––––––––––––––––––––––––––––––––––#
		# TAB 2 : CONTEXT CLASS                     #
		#–––––––––––––––––––––––––––––––––––––––––––#


		self.classList = list(self.jsonFile["ContextClass"].keys())

		tab2.listOfContextClassTitle = TextBox((10,14,-10,20), "Context Classes", sizeStyle="small")
		tab2.filterClass = EditText((110,10,100,20),sizeStyle="small", placeholder="🔎 Search Glyph", callback=self.filterClassCallback)
		tab2.listOfContextClass = List((10, 34, 200, -10), self.classList, selectionCallback=self.updateClassGlyphsCallback, doubleClickCallback=self.renameItem_contextClassCallBack, allowsMultipleSelection=False, drawFocusRing=False,rowHeight=20)
		tab2.add_remove_contextClass = SegmentedButton((166, -36, 40, 20), [dict(title="+"), dict(title="-")], callback=self.add_remove_contextClassCallBack, sizeStyle="small", selectionStyle="momentary")


		tab2.contextClassGlyphsTitle = TextBox((220,14,-10,20), "Class Glyphs", sizeStyle="small")
		tab2.contextClassGlyphs = List((220, 34, 80, -10), [], allowsMultipleSelection=True, drawFocusRing=False,rowHeight=20, enableDelete=True)
		tab2.add_remove_contextGlyph = SegmentedButton((254, -36, 40, 20), [dict(title="+"), dict(title="-")], callback=self.add_remove_contextGlyphCallBack, sizeStyle="small", selectionStyle="momentary")
		tab2.add_remove_contextGlyph.getNSSegmentedButton().setToolTip_("Add selected Glyph in FontView")




		tab2.contentContextClassTitle = TextBox((310,14,-10,20), "Class Strings", sizeStyle="small")
		tab2.contentContextClass = TextEditor((310, 34, -10, -10), "", callback=self.updateClassStringsCallback)


		#–––––––––––––––––––––––––––––––––––––––––––#
		# FOOTER                                    #
		#–––––––––––––––––––––––––––––––––––––––––––#

		# Save and Settings
		actionPopUpButtonitems = [
			dict(title="Reset all datas", callback=self.resetCallback),
			dict(title="Import Context File", callback=self.importCallback),
			dict(title="Merge with another Context File", callback=self.mergeCallback),
		]
		self.w.actionPopUpButton = ActionButton((wW-60, wH-28, -10, 18), actionPopUpButtonitems, sizeStyle='regular')

		self.w.makeKey()
		self.w.center()

	@objc.python_method
	def start(self):
		newMenuItem = NSMenuItem("Context Manager", self.openWindow_)
		Glyphs.menu[EDIT_MENU].append(newMenuItem)
		newMenuItem = NSMenuItem("Set Context...", self.openWindow_)
		Glyphs.menu[EDIT_MENU].append(newMenuItem)

		Glyphs.addCallback(self.update, UPDATEINTERFACE)

		if not Glyphs.defaults["com.HugoJourdan.CM_T"]:
			Glyphs.defaults["com.HugoJourdan.CM_T"] = current_time = datetime.now().strftime("%d/%m/%Y")




	@objc.python_method
	def __del__(self):
		Glyphs.removeCallback(self.update)

	@objc.python_method
	def update(self, sender):


		try:
			font = Glyphs.font
			if font.selectedLayers:
				if not Glyphs.defaults["com.HugoJourdan.findContext"]:
					Glyphs.defaults["com.HugoJourdan.findContext"] = font.glyphs["A"].name

				if font.selectedLayers:
					self.selectedChar = font.selectedLayers[0]
				else:
					self.selectedChar = font.glyphs["A"].layers[0]

				# If selected char changed :
				if self.selectedChar.parent.name != Glyphs.defaults["com.HugoJourdan.findContext"] and self.w.isVisible():
					Glyphs.defaults["com.HugoJourdan.findContext"] = self.selectedChar.parent.name
					self.updateWindow()
		except:pass

	@objc.python_method
	def updateWindow(self):
		tab1 = self.w.tabs[0]
		tab2 = self.w.tabs[1]

		if self.font:
			if self.font.selectedFontMaster:
				selectedMasterID = self.font.selectedFontMaster.id

			self.selectedChar = self.font.glyphs["A"].layers[0]
			if self.font.selectedLayers:
				self.selectedChar = self.font.selectedLayers[0]

			# Hide Glyphs not present in current font
			listFontGlyphs = []
			for glyph in self.font.glyphs:
				if "." in glyph.name:
					listFontGlyphs.append(glyph.name.split('.')[0])
				elif glyph.category and glyph.category != "Separator":
					listFontGlyphs.append(glyph.name)

			# Expand self.jsonFile if char in current font in not present in the list
			for glyph in self.font.glyphs:
				try:
					if glyph.category and glyph.category != "Separator":
						if "." in glyph.name:
							glyphName = glyph.name.split('.')[0]
							glyphString = self.font.glyphs[glyphName].string
						else:
							glyphString = glyph.string
						if glyphString not in self.jsonFile["Glyph"].keys():
							self.jsonFile["Glyph"][glyphString] = {"ContextClass":[], "ContextWords":[], "ContextStrings":[], }
				except:pass


			if selectedMasterID:
				LAYER = self.font.glyphs[self.selectedChar.parent.name].layers[selectedMasterID]
				if hasattr(tab1.box, "glyphView") : delattr(tab1.box, "glyphView")
				setattr(tab1.box, "glyphView", GlyphView((0, 0, -0, -20), layer=LAYER, backgroundColor=NSColor.clearColor()))
				tab1.box.drawGlyphName.set(self.selectedChar.parent.name)

			glyphUnicode = self.selectedChar.parent.unicode
			glyphUnicode = f"U{glyphUnicode}" if glyphUnicode else "No Unicode"
			tab1.box.drawGlyphUnicode.set(glyphUnicode)

			tab1.contextClassList.set(self.jsonFile["Glyph"][self.selectedChar.parent.string]["ContextClass"])
			tab1.contextWordEditor.set('\n'.join(self.jsonFile["Glyph"][self.selectedChar.parent.string]["ContextWords"]))
			tab1.contextStringsEditor.set('\n'.join(self.jsonFile["Glyph"][self.selectedChar.parent.string]["ContextStrings"]))
			tab2.listOfContextClass.set(self.jsonFile["ContextClass"])

		self.updateGlyphClass()

	@objc.python_method
	def updateGlyphClass(self):
		for CLASS in self.jsonFile["ContextClass"]:
			for GLYPH in self.jsonFile["ContextClass"][CLASS]["Glyphs"]:
				if GLYPH not in self.jsonFile["Glyph"]:
					self.jsonFile["Glyph"][GLYPH] = {"ContextClass":[],"ContextWords":[], "ContextStrings":[]}
				if CLASS not in self.jsonFile["Glyph"][GLYPH]["ContextClass"]:
					self.jsonFile["Glyph"][GLYPH]["ContextClass"].append(CLASS)
		self.w.tabs[0].contextClassList.set(self.jsonFile["Glyph"][self.selectedChar.parent.string]["ContextClass"])


	@objc.python_method
	def filterClassCallback(self, sender):
		if self.w.tabs[1].filterClass.get():
			input = self.w.tabs[1].filterClass.get()
			classShow = []
			for CLASS in self.jsonFile["ContextClass"]:
				if input in self.jsonFile["ContextClass"][CLASS]["Glyphs"]:
					classShow.append(CLASS)
			self.w.tabs[1].listOfContextClass.set(classShow)
			self.w.tabs[1].listOfContextClass.setSelection([0])
		else:
			self.w.tabs[1].listOfContextClass.set([CLASS for CLASS in self.jsonFile["ContextClass"]])
			self.w.tabs[1].listOfContextClass.setSelection([0])

	@objc.python_method
	def openWindow_(self, sender):

		t1 = datetime.strptime(Glyphs.defaults["com.HugoJourdan.CM_T"], "%d/%m/%Y")
		t2 = datetime.strptime(datetime.now().strftime("%d/%m/%Y"), "%d/%m/%Y")
		difference = t2 - t1

		if difference.days < 30:

			self.settings()
			self.updateWindow()
			self.w.open()

			if not self.LoadPreferences():
				print("Note: 'Context String Maker' could not load preferences. Will resort to defaults")
		else:
			Message("Your FindContext trial period is over\nTo buy a licence, visit\nwww.lience.com", title='Context Manager', OKButton=None)


	@objc.python_method
	def toggleOptionCallback(self, sender):

		Glyphs.defaults["com.HugoJourdan.ContextManager.contextClassCheckBox"] = self.w.tabs[0].contextClassCheckBox.get()
		Glyphs.defaults["com.HugoJourdan.ContextManager.contextWordsCheckBox"] = self.w.tabs[0].contextWordsCheckBox.get()
		Glyphs.defaults["com.HugoJourdan.ContextManager.contextStringCheckBox"] = self.w.tabs[0].contextStringCheckBox.get()
		Glyphs.defaults["com.HugoJourdan.ContextManager.smartContextCheckBox"] = self.w.tabs[0].smartContextCheckBox.get()
		Glyphs.defaults["com.HugoJourdan.ContextManager.spacingContextCheckBox"] = self.w.tabs[0].spacingContextCheckBox.get()
		Glyphs.defaults["com.HugoJourdan.ContextManager.lowercaseCheckBox"] = self.w.tabs[0].lowercaseCheckBox.get()
		Glyphs.defaults["com.HugoJourdan.ContextManager.uppercaseCheckBox"] = self.w.tabs[0].uppercaseCheckBox.get()
		Glyphs.defaults["com.HugoJourdan.ContextManager.startCheckBox"] = self.w.tabs[0].startCheckBox.get()
		Glyphs.defaults["com.HugoJourdan.ContextManager.includeCheckBox"] = self.w.tabs[0].includeCheckBox.get()

    # Select first Class of selected Glyph when switching to "Context Class" tab.
	@objc.python_method
	def switchTabCallback(self, sender):
		tabSelected = sender.get()
		try:
			if tabSelected == 1 :
				if self.jsonFile["Glyph"][self.selectedChar.parent.string]["ContextClass"]:
					if "." in self.selectedChar.parent.name:
						findGlyph = self.selectedChar.parent.name.split(".")[0].string
					else:
						findGlyph = self.selectedChar.parent.string
					className = self.jsonFile["Glyph"][findGlyph]["ContextClass"][0]
					i = list(self.jsonFile["ContextClass"]).index(className)
					self.w.tabs[1].listOfContextClass.setSelection([i])
			elif tabSelected == 0 :
				print("tab1")
				self.updateGlyphClass()
		except:pass

	# Update "Class Strings" in [Context Class] tab.
	@objc.python_method
	def updateClassStringsCallback(self, sender):

		classVisible = self.w.tabs[1].listOfContextClass.get()
		i = self.w.tabs[1].listOfContextClass.getSelection()[0]
		key = classVisible[i]

		editText = sender.get()
		editTextList = [x for x in editText.split("\n") if x]
		self.jsonFile["ContextClass"][key]["Context"] = editTextList


		with open(self.jsonPath, "w", encoding='utf8') as outfile:
			json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)

	# Update "Class Glyphs" in [Context Class] tab.
	@objc.python_method
	def updateClassGlyphsCallback(self, sender):
		if self.w.tabs[1].listOfContextClass.getSelection():

			classVisible = self.w.tabs[1].listOfContextClass.get()
			i = self.w.tabs[1].listOfContextClass.getSelection()[0]
			key = classVisible[i]

			contextClass = self.jsonFile["ContextClass"][key]["Context"]
			content = ""
			for context in contextClass:
				content += f"{context}\n"
			self.w.tabs[1].contentContextClass.set(content)



			contextGlyphs = self.jsonFile["ContextClass"][key]["Glyphs"]
			self.w.tabs[1].contextClassGlyphs.set(contextGlyphs)


		else:
			self.w.tabs[1].contentContextClass.set("")

	# Rename Item when double click on Context Class
	@objc.python_method
	def renameItem_contextClassCallBack(self, sender):

		i = self.w.tabs[1].listOfContextClass.getSelection()[0]
		keyName = list(self.jsonFile["ContextClass"].keys())[i]
		renameClassName = AskString("Rename Context Class", value=keyName,title="Glyphs", OKButton="Rename")
		if renameClassName:

			self.jsonFile["ContextClass"] = {key if key != keyName else renameClassName: value for key, value in self.jsonFile["ContextClass"].items()}
			self.w.tabs[1].listOfContextClass.set(list(self.jsonFile["ContextClass"].keys()))
			self.w.tabs[1].listOfContextClass.setSelection([i])

			with open(self.jsonPath, "w", encoding='utf8') as outfile:
				json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)
		else:
			pass

	# Add/remove callback button of Context Class
	@objc.python_method
	def add_remove_contextClassCallBack(self, sender):
		value = sender.get()


		# If (-) button is pressed
		if value == 1:

			if self.w.tabs[1].listOfContextClass.getSelection():
				visibleClass = self.w.tabs[1].listOfContextClass.get()

				i = self.w.tabs[1].listOfContextClass.getSelection()[0]
				self.w.tabs[1].listOfContextClass.setSelection([i-1])

				# Remove Deleted Item
				key = self.w.tabs[1].listOfContextClass.get()[i]
				self.jsonFile["ContextClass"].pop(key)
				self.w.tabs[1].listOfContextClass.set(list(self.jsonFile["ContextClass"].keys()))
				for GLYPH in self.jsonFile["Glyph"]:
					if key in self.jsonFile["Glyph"][GLYPH]["ContextClass"]:
						self.jsonFile["Glyph"][GLYPH]["ContextClass"].remove(key)
			self.w.tabs[1].filterClass.set("")



		# If (+) button is pressed
		elif value == 0:
			contextClassName = AskString("Type a Context Class name to add", placeholder="Context Class Name",title="Add Context Class", OKButton="Add")
			if contextClassName:

				self.classList.append(contextClassName)
				self.jsonFile["ContextClass"][contextClassName]={"Glyphs":[], "Context":[]}

				temp = {k: self.jsonFile["ContextClass"][k] for k in sorted(self.jsonFile["ContextClass"])}
				self.jsonFile["ContextClass"] = temp
				index = list(self.jsonFile["ContextClass"].keys()).index(contextClassName)

				with open(self.jsonPath, "w", encoding='utf8') as outfile:
					json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)


				self.w.tabs[1].listOfContextClass.set(list(self.jsonFile["ContextClass"].keys()))
				self.w.tabs[1].listOfContextClass.setSelection([index])


			else:
				pass

	# Add/remove callback button of Class Glyphs
	@objc.python_method
	def add_remove_contextGlyphCallBack(self, sender):
		value = sender.get()

		# If (-) button is pressed
		if value == 1:
			if self.w.tabs[1].contextClassGlyphs.getSelection():

				i = self.w.tabs[1].listOfContextClass.getSelection()[0]
				selectedClass = list(self.jsonFile["ContextClass"].keys())[i]

				i = self.w.tabs[1].contextClassGlyphs.getSelection()[0]
				self.w.tabs[1].contextClassGlyphs.setSelection([i-1])

				# Remove Deleted Item
				key = list(self.jsonFile["ContextClass"][selectedClass]["Glyphs"])[i]
				self.jsonFile["ContextClass"][selectedClass]["Glyphs"].remove(key)
				self.w.tabs[1].contextClassGlyphs.set(list(self.jsonFile["ContextClass"][selectedClass]["Glyphs"]))


				with open(self.jsonPath, "w", encoding='utf8') as outfile:
						json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)

				self.updateGlyphClass()

		# If (+) button is pressed
		elif value == 0:

			if self.font.selection:

				i = self.w.tabs[1].listOfContextClass.getSelection()[0]
				selectedClass = list(self.jsonFile["ContextClass"].keys())[i]

				for glyph in self.font.selection:
					addGlyph = glyph.string
					if addGlyph not in self.jsonFile["ContextClass"][selectedClass]["Glyphs"]:
						self.jsonFile["ContextClass"][selectedClass]["Glyphs"].append(addGlyph)

						#Sort A-Z Glyphs
						self.jsonFile["ContextClass"][selectedClass]["Glyphs"].sort()
						index = self.jsonFile["ContextClass"][selectedClass]["Glyphs"].index(str(addGlyph))

						self.w.tabs[1].contextClassGlyphs.set(self.jsonFile["ContextClass"][selectedClass]["Glyphs"])
						self.w.tabs[1].contextClassGlyphs.setSelection([index])

				with open(self.jsonPath, "w", encoding='utf8') as outfile:
					json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)

				self.updateGlyphClass()

			else:
				Message("No Glyph selected.\nSelect Glyphs in Font View,\n then press [+] button")


		# Order Calss Glyphs
		for CLASS in self.jsonFile["ContextClass"]:
			self.jsonFile["ContextClass"][CLASS]["Glyphs"].sort
		with open(self.jsonPath, "w", encoding='utf8') as outfile:
			json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)

	@objc.python_method
	def LoadPreferences(self):
		try:
			# register defaults:

			Glyphs.registerDefault("com.HugoJourdan.ContextManager.contextClassCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.contextWordsCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.contextStringCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.smartContextCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.spacingContextCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.lowercaseCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.uppercaseCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.startCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.includeCheckBox", 0)


			# load previously written prefs:
			self.w.tabs[0].spacingContextCheckBox.set(Glyphs.defaults["com.HugoJourdan.ContextManager.spacingContextCheckBox"])
			self.w.tabs[0].contextClassCheckBox.set(Glyphs.defaults["com.HugoJourdan.ContextManager.contextClassCheckBox"])
			self.w.tabs[0].contextWordsCheckBox.set(Glyphs.defaults["com.HugoJourdan.ContextManager.contextWordsCheckBox"])
			self.w.tabs[0].contextStringCheckBox.set(Glyphs.defaults["com.HugoJourdan.ContextManager.contextStringCheckBox"])
			self.w.tabs[0].smartContextCheckBox.set(Glyphs.defaults["com.HugoJourdan.ContextManager.smartContextCheckBox"])
			self.w.tabs[0].lowercaseCheckBox.set(Glyphs.defaults["com.HugoJourdan.ContextManager.lowercaseCheckBox"])
			self.w.tabs[0].uppercaseCheckBox.set(Glyphs.defaults["com.HugoJourdan.ContextManager.uppercaseCheckBox"])
			self.w.tabs[0].startCheckBox.set(Glyphs.defaults["com.HugoJourdan.ContextManager.startCheckBox"])
			self.w.tabs[0].includeCheckBox.set(Glyphs.defaults["com.HugoJourdan.ContextManager.includeCheckBox"])

			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	# Update "Glyph Words" in [Context Glyph] tab.
	@objc.python_method
	def updateGlyphWordsCallback(self, sender):

		input = self.selectedChar.parent.string
		editText = sender.get()
		editTextList = [x for x in editText.split("\n") if x]
		editTextList = list(dict.fromkeys(editTextList))
		self.jsonFile["Glyph"][input]["ContextWords"] = editTextList


		self.jsonFile["Glyph"][input]["ContextWords"].sort()

		with open(self.jsonPath, "w", encoding='utf8') as outfile:
			json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)

	# Update "Glyph Strings" in [Context Glyph] tab.
	@objc.python_method
	def updateGlyphStringsCallback(self, sender):
		input = self.selectedChar.parent.string
		editText = sender.get()
		editTextList = [x for x in editText.split("\n") if x]
		self.jsonFile["Glyph"][input]["ContextStrings"] = editTextList

		with open(self.jsonPath, "w", encoding='utf8') as outfile:
			json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)

	# Action button "Merge with another Context File" callback
	@objc.python_method
	def mergeCallback(self, sender):
		mergeFile = GetOpenFile(message="Select a .json file to merged",
								allowsMultipleSelection=False, filetypes=None, path=None)

		with open(mergeFile) as json_file:
			mergeFile = json.load(json_file)

		for CLASS in mergeFile["ContextClass"]:
			if CLASS not in self.jsonFile["ContextClass"]:
				self.jsonFile["ContextClass"][CLASS] = mergeFile["ContextClass"][CLASS]
				print(mergeFile["ContextClass"][CLASS])
			for word in mergeFile["ContextClass"][CLASS]["Glyphs"]:
				if word not in self.jsonFile["ContextClass"][CLASS]["Glyphs"]:
					self.jsonFile["ContextClass"][CLASS]["Glyphs "].append(word)

		for glyph in mergeFile["Glyph"]:
			if glyph not in self.jsonFile["Glyph"]:
				self.jsonFile["Glyph"][glyph] = mergeFile["Glyph"][glyph]
			for CLASS in mergeFile["Glyph"][glyph]["ContextClass"]:
				if CLASS not in self.jsonFile["Glyph"][glyph]["ContextClass"]:
					self.jsonFile["Glyph"][glyph]["ContextClass"].append(CLASS)
			for word in mergeFile["Glyph"][glyph]["ContextWords"]:
				if word not in self.jsonFile["Glyph"][glyph]["ContextWords"]:
					self.jsonFile["Glyph"][glyph]["ContextWords"].append(word)

		with open(self.jsonPath, "w", encoding='utf8') as outfile:
			json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)
		self.updateWindow()

	# Action button "Reset all data" callback
	@objc.python_method
	def resetCallback(self, sender):
		os.chdir(os.path.dirname(self.jsonPath))
		with open('ContextManager.json', 'w', encoding='utf8') as f:
			json.dump({"ContextClass":{},"Glyph":{}}, f, indent=4, ensure_ascii=False)

	# Action button "Import Context File"
	@objc.python_method
	def importCallback(self, sender):


		def importContextDataCallback(self):
			mergeFile = GetOpenFile(message="Select a .json file to import data",
								allowsMultipleSelection=False, filetypes=None, path=None)
			jsonPath = os.path.expanduser("~/Library/Application Support/Glyphs 3/info/ContextManager.json")

			with open(mergeFile) as json_file:
				mergeFile = json.load(json_file)
			with open(jsonPath) as json_file:
				jsonFile = json.load(json_file)

			if w.contextClassCheckBox.get() == True:
				for CLASS in mergeFile["ContextClass"]:
					if CLASS not in jsonFile["ContextClass"]:
						jsonFile["ContextClass"][CLASS] = {}
					for GLYPH in mergeFile["Glyph"]:
						if GLYPH not in jsonFile["Glyph"]:
							jsonFile["Glyph"][GLYPH] = {"ContextClass":[], "ContextWords":[], "ContextStrings":[]}
						if CLASS not in jsonFile["Glyph"][GLYPH]["ContextClass"]:
							jsonFile["Glyph"][GLYPH]["ContextClass"].append(CLASS)

			if w.contextClassGlyphsCheckBox.get() == True:
				for CLASS in mergeFile["ContextClass"]:
					if CLASS in jsonFile["ContextClass"]:
						jsonFile["ContextClass"][CLASS]["Glyphs"] = mergeFile["ContextClass"][CLASS]["Glyphs"]

			if w.contextClassContextCheckBox.get() == True:
				for CLASS in mergeFile["ContextClass"]:
					if CLASS in jsonFile["ContextClass"]:
						jsonFile["ContextClass"][CLASS]["Context"] = mergeFile["ContextClass"][CLASS]["Context"]

			if w.contextWordsCheckBox.get() == True:
				for GLYPH in mergeFile["Glyph"]:
					if not GLYPH in jsonFile["Glyph"]:
						jsonFile["Glyph"][GLYPH] = {"ContextClass":[], "ContextWords":[], "ContextStrings":[]}
					jsonFile["Glyph"][GLYPH]["ContextWords"] = mergeFile["Glyph"][GLYPH]["ContextWords"]

			if w.contextStringsCheckBox.get() == True:
				for GLYPH in mergeFile["Glyph"]:
					if not GLYPH in jsonFile["Glyph"]:
						jsonFile["Glyph"][GLYPH] = {"ContextClass":[], "ContextWords":[], "ContextStrings":[]}
					jsonFile["Glyph"][GLYPH]["ContextStrings"] = mergeFile["Glyph"][GLYPH]["ContextStrings"]
				print("contextStringsCheckBox")

			os.chdir(os.path.dirname(jsonPath))
			with open('ContextManager.json', 'w',  encoding='utf8') as f:
				json.dump(jsonFile, f, indent=4, ensure_ascii=False)



		wW, wH, linePos = 160, 180, 10
		w = FloatingWindow((wW, wH), "Import Context Data")
		w.importTitle = TextBox((10, -wH+linePos, -10,16), "Select Data to Import")
		linePos += 28
		w.contextClassCheckBox = CheckBox((10,-wH+linePos,-10,16), "Context Class", sizeStyle="small")
		linePos += 18
		w.contextClassGlyphsCheckBox = CheckBox((30,-wH+linePos,-10,16), " ↳ Glyphs", sizeStyle="small")
		linePos += 18
		w.contextClassContextCheckBox = CheckBox((30,-wH+linePos,-10,16), " ↳ Context", sizeStyle="small")
		w.sep2 = HorizontalLine((10,-wH+linePos+12,-10,16))
		linePos += 24
		w.contextWordsCheckBox = CheckBox((10,-wH+linePos,-10,16), "Context Words", sizeStyle="small")
		linePos += 18
		w.contextStringsCheckBox = CheckBox((10,-wH+linePos,-10,16), "Context Strings", sizeStyle="small")
		linePos += 24
		w.runButton = Button((6,-26,-6,16), "Load file", callback=importContextDataCallback)


		print(w.contextClassContextCheckBox.get())

		w.center()
		w.open()

		#@objc.python_method





	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
