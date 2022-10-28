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

class contextManager(GeneralPlugin):

	@objc.python_method
	def settings(self):	

		self.name = Glyphs.localize({'en': 'Context Manager'})
		self.font = Glyphs.font
		self.jsonPath = os.path.expanduser("~/Library/Application Support/Glyphs 3/info/ContextManager.json")

		os.chdir(os.path.dirname(self.jsonPath))
		if not os.path.exists(self.jsonPath):
			try:
				import shutil
				path = os.path.expanduser("~/Library/Application Support/Glyphs 3/Repositories/ContextManager/Context Manager.glyphsPlugin/Contents/Resources/ContextManager.json")
				shutil.copy(path, os.path.expanduser("~/Library/Application Support/Glyphs 3/info"))
			except:
				with open('ContextManager.json', 'w') as f:
					json.dump({"ContextClass":{},"Glyph":{}}, f)

		# Load File

		with open(self.jsonPath, encoding='utf8') as json_file:
			self.jsonFile = json.load(json_file)


		wW, wH = 760, 500
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

		tab1.sliderText = TextBox((10, 374, 170, 17), f"Show [x] context", sizeStyle='small')
		tab1.slider = Slider((10, 390, 170, 22),tickMarkCount=10, stopOnTickMarks=True, minValue=1, maxValue=10, callback=self.slideTextUpdateCallback, sizeStyle="small")
		


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
		tab2.contextClassGlyphs = List((220, 34, 180, -10), [], allowsMultipleSelection=True, drawFocusRing=False,rowHeight=20, enableDelete=True)
		tab2.add_remove_contextGlyph = SegmentedButton((354, -36, 40, 20), [dict(title="+"), dict(title="-")], callback=self.add_remove_contextGlyphCallBack, sizeStyle="small", selectionStyle="momentary")
		tab2.add_remove_contextGlyph.getNSSegmentedButton().setToolTip_("Add selected Glyph in FontView")


		tab2.contentContextClassTitle = TextBox((410,14,-10,20), "Class Strings", sizeStyle="small")
		tab2.contentContextClass = TextEditor((410, 34, -10, -10), "", callback=self.updateClassStringsCallback)


		#–––––––––––––––––––––––––––––––––––––––––––#
		# FOOTER                                    #
		#–––––––––––––––––––––––––––––––––––––––––––#

		# Save and Settings
		actionPopUpButtonitems = [
			dict(title="Reset all datas", callback=self.resetCallback),
			dict(title="Import Context File", callback=self.importCallback),
			dict(title="Merge with another Context File", callback=self.mergeCallback),
			"----",
			dict(title="Open Context Manager Documentation", callback=self.openDocumentationCallback),
		]
		self.w.actionPopUpButton = ActionButton((wW-60, wH-28, -10, 18), actionPopUpButtonitems, sizeStyle='regular')

		self.w.makeKey()
		self.w.center()

	@objc.python_method
	def slideTextUpdateCallback(self,sender):
		value = round(sender.get())
		Glyphs.defaults["com.HugoJourdan.ContextManager.slider"] = value
		
		self.w.tabs[0].sliderText.set(f"Show {value} context")

	@objc.python_method
	def start(self):
		newMenuItem = NSMenuItem("Context Manager", self.openWindow_)
		Glyphs.menu[EDIT_MENU].append(newMenuItem)
		newMenuItem = NSMenuItem("Set Context...", self.setContext_)
		Glyphs.menu[EDIT_MENU].append(newMenuItem)

		Glyphs.addCallback(self.update, UPDATEINTERFACE)

		self.LoadPreferences()

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
				if not Glyphs.defaults["com.HugoJourdan.contextManager"]:
					Glyphs.defaults["com.HugoJourdan.contextManager"] = font.glyphs["A"].name

				if font.selectedLayers:
					self.selectedChar = font.selectedLayers[0]
				else:
					self.selectedChar = font.glyphs["A"].layers[0]

				# If selected char changed :
				if self.selectedChar.parent.name != Glyphs.defaults["com.HugoJourdan.contextManager"] and self.w.isVisible():
					Glyphs.defaults["com.HugoJourdan.contextManager"] = self.selectedChar.parent.name
					self.updateWindow()
		except:pass

	@objc.python_method
	def setContext_(self, sender):			
		import random
		from datetime import datetime
		import os

		self.font = Glyphs.font

		t1 = datetime.strptime(Glyphs.defaults["com.HugoJourdan.CM_T"], "%d/%m/%Y")
		t2 = datetime.strptime(datetime.now().strftime("%d/%m/%Y"), "%d/%m/%Y")
		difference = t2 - t1

		if difference.days < 30:
			with open(self.jsonPath) as json_file:
				contextDic = json.load(json_file)

			# Use current selected Glyph EditView or FontView
			try:
				if self.font.selectedLayers:
					selectedChar = self.font.selectedLayers[0].parent

				c = selectedChar.name

				wordList = []
				if c in contextDic["Glyph"]:

					# If "Class" filter is checked
					if Glyphs.defaults["com.HugoJourdan.ContextManager.contextClassCheckBox"] == True:
						for CLASS in contextDic["ContextClass"]:
							if c in contextDic["ContextClass"][CLASS]["Glyphs"]:
								for item in contextDic["ContextClass"][CLASS]["Context"]:
									wordList.append(item)

								#wordList.append(glyphsString)

					# If "Context" filter is checked
					if Glyphs.defaults["com.HugoJourdan.ContextManager.contextWordsCheckBox"] == True:
						if c in contextDic["Glyph"]:
							for item in contextDic["Glyph"][c]["ContextWords"]:
								wordList.append(item)

					# If "String" filter is checked
					if Glyphs.defaults["com.HugoJourdan.ContextManager.contextStringCheckBox"] == True:
						if c in contextDic["Glyph"]:
							for item in contextDic["Glyph"][c]["ContextStrings"]:
								wordList.append(item)

					# If "Smart" filter is checked
					if Glyphs.defaults["com.HugoJourdan.ContextManager.smartContextCheckBox"] == True:
						addString = []
						classGlyphs = {}

						for CLASS in contextDic["ContextClass"]:
							if c in contextDic["ContextClass"][CLASS]["Glyphs"]:
								# addString = f"{c} "
								# for glyph in [glyph for glyph in contextDic["ContextClass"][CLASS]["Glyphs"]] :
								# 	if glyph != c:
								# 		addString += f"{glyph}{c}{glyph} "
								# wordList.append(addString)
								classGlyphs = ""
								for glyph in contextDic["ContextClass"][CLASS]["Glyphs"]:
										classGlyphs += glyph
								wordList.append(classGlyphs)

					# If "Spacing" filter is checked
					if Glyphs.defaults["com.HugoJourdan.ContextManager.spacingContextCheckBox"] == True:
						wordList.append(f"HH{c}HH{c}OO{c}OO{c}nn{c}nn{c}oo{c}oo")

					# If "Uppercase" filter is checked
					if Glyphs.defaults["com.HugoJourdan.ContextManager.uppercaseCheckBox"] == True:
						wordListCopy = []
						for word in wordList:
							wordCopy = ""
							for char in word:
								if char != selectedChar.string:
									wordCopy += char.upper()
								else:
									wordCopy += char
							wordListCopy.append(wordCopy)
						wordList = wordListCopy

					# If "Lowercase" filter is checked
					if Glyphs.defaults["com.HugoJourdan.ContextManager.lowercaseCheckBox"] == True:
						wordListCopy = []
						for word in wordList:
							wordCopy = ""
							for char in word:
								if char != selectedChar.string:
									wordCopy += char.lower()
								else:
									wordCopy += char
							wordListCopy.append(wordCopy)
						wordList = wordListCopy

					# If "Start" or "Include" filter are checked
					if Glyphs.defaults["com.HugoJourdan.ContextManager.startCheckBox"] == True and Glyphs.defaults["com.HugoJourdan.ContextManager.includeCheckBox"] == True:
						pass
					elif Glyphs.defaults["com.HugoJourdan.ContextManager.startCheckBox"] == True:
						tempList = wordList.copy()
						for word in tempList:
							if word[0] != selectedChar.string:
								wordList.remove(word)
					elif Glyphs.defaults["com.HugoJourdan.ContextManager.includeCheckBox"] == True:
						tempList = wordList.copy()
						for word in tempList:
							if word[0] == selectedChar.string:
								wordList.remove(word)

					if not wordList:
						Message(f"Check if you have set any context\n or selected filters.", title=f"No Context found\n for [{c}] glyph", OKButton=None)
						pass

					nbWords = Glyphs.defaults["com.HugoJourdan.ContextManager.slider"]
					showContext = []

					# Fix if "/" in context
					for word in wordList:
						if "/" in word:
							i = wordList.index(word)
							wordList[i] = word.replace("/", "//") 

					pickedWord = random.choice(wordList)

					if self.font.currentTab and len(wordList)>1 and nbWords == 1:
						currenTabText = self.font.currentTab.text
						# Pick again if word already in current tab /or/ if selected word contain char not in font /or/ selected char not in selected word
						while pickedWord == currenTabText or all(char in [glyph.string for glyph in self.font.glyphs] for char in [*pickedWord]) == False or selectedChar.string not in pickedWord :
							pickedWord = random.choice(wordList)

						showContext.append(pickedWord)

					elif len(wordList) > nbWords:
						for i in range (nbWords):
							while pickedWord in showContext:
								pickedWord = random.choice(wordList)
							showContext.append(pickedWord)
							
					

					tabText = ""
					for word in showContext:
						tabText += f"{word}\n"
							
					INDEX = tabText.find(selectedChar.string)
					if not self.font.currentTab:
						self.font.newTab(tabText)
					else:
						self.font.currentTab.text = tabText
					self.font.currentTab.textCursor = INDEX
				else:
					Message("Add context in selected filter\n or reduce Show context treshold", title=f'No enought context found\n for [{c}] glyph', OKButton=None)


			except:TypeError("Open a font or select a glyph")
		else:
			Message("Your FindContext trial period is over\nTo buy a licence, visit\nwww.lience.com", title='Context Manager', OKButton=None)

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

			# Expand self.jsonFile if char in current font in not present in the list
			for glyph in self.font.glyphs:
				try:
					if glyph.category and glyph.category != "Separator" or "Mark":
						if "." in glyph.name and not "locl" in glyph.name.split('.')[1] :
							glyphName = glyph.name.split('.')[0].name
						else:
							glyphName = glyph.name
						if glyphName not in self.jsonFile["Glyph"].keys():
							self.jsonFile["Glyph"][glyphName] = {"ContextClass":[], "ContextWords":[], "ContextStrings":[], }
				except:pass

			if selectedMasterID:
				LAYER = self.font.glyphs[self.selectedChar.parent.name].layers[selectedMasterID]
				if hasattr(tab1.box, "glyphView") : delattr(tab1.box, "glyphView")
				setattr(tab1.box, "glyphView", GlyphView((0, 0, -0, -20), layer=LAYER, backgroundColor=NSColor.clearColor()))

			if len(self.selectedChar.parent.name) > 16:
				tab1.box.drawGlyphName.set(self.selectedChar.parent.name[:16]+"...")
			else:
				tab1.box.drawGlyphName.set(self.selectedChar.parent.name)

			glyphUnicode = self.selectedChar.parent.unicode
			glyphUnicode = f"U{glyphUnicode}" if glyphUnicode else "No Unicode"
			tab1.box.drawGlyphUnicode.set(glyphUnicode)

			if ".locl" in self.selectedChar.parent.name:
				glyphName = self.selectedChar.parent.name.split(".locl")[0]
			elif "." in self.selectedChar.parent.name:
				glyphName = self.selectedChar.parent.name.split(".locl")[0]
			else:
				glyphName = self.selectedChar.parent.name
			

			tab1.contextClassList.set(self.jsonFile["Glyph"][glyphName]["ContextClass"])
			tab1.contextWordEditor.set('\n'.join(self.jsonFile["Glyph"][glyphName]["ContextWords"]))
			tab1.contextStringsEditor.set('\n'.join(self.jsonFile["Glyph"][glyphName]["ContextStrings"]))
			tab2.listOfContextClass.set(self.jsonFile["ContextClass"])

		self.w.tabs[0].slider.set(Glyphs.defaults["com.HugoJourdan.ContextManager.slider"])
		self.w.tabs[0].sliderText.set(f'Show {Glyphs.defaults["com.HugoJourdan.ContextManager.slider"]} context')
		self.updateGlyphClasses()

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
	def updateGlyphClasses(self):
		if self.font:
			allClass = [CLASS for CLASS in self.jsonFile["ContextClass"].keys()]
			for GLYPH in self.jsonFile["Glyph"]:
				for CLASS in self.jsonFile["Glyph"][GLYPH]["ContextClass"]:
					if GLYPH or font.glyphs[GLYPH].string not in self.jsonFile["ContextClass"][CLASS]:
						self.jsonFile["Glyph"][GLYPH]["ContextClass"].remove(CLASS)
						
			for CLASS in self.jsonFile["ContextClass"].keys():	
				for GLYPH in self.jsonFile["ContextClass"][CLASS]["Glyphs"]:
					try:
						glyphName = self.font.glyphs[GLYPH].name
						if CLASS not in self.jsonFile["Glyph"][glyphName]["ContextClass"]:
							self.jsonFile["Glyph"][glyphName]["ContextClass"].append(CLASS)
					except:pass
			with open(self.jsonPath, "w", encoding='utf8') as outfile:
				json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)
		self.w.tabs[0].contextClassList.set(self.jsonFile["Glyph"][self.selectedChar.parent.name]["ContextClass"])

	@objc.python_method
	def openWindow_(self, sender):
		# Fix possible not Context Class linked
				
		t1 = datetime.strptime(Glyphs.defaults["com.HugoJourdan.CM_T"], "%d/%m/%Y")
		t2 = datetime.strptime(datetime.now().strftime("%d/%m/%Y"), "%d/%m/%Y")
		difference = t2 - t1

		if difference.days < 30:
			try:
				self.settings()
				self.updateWindow()
				self.w.open()
			except:pass

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
				if self.jsonFile["Glyph"][self.selectedChar.parent.name]["ContextClass"]:
					if "." in self.selectedChar.parent.name :
						findGlyph = self.selectedChar.parent.name.split(".")[0].name
					else:
						findGlyph = self.selectedChar.parent.name
					className = self.jsonFile["Glyph"][findGlyph]["ContextClass"][0]
					i = list(self.jsonFile["ContextClass"]).index(className)
					self.w.tabs[1].listOfContextClass.setSelection([i])
			elif tabSelected == 0 :
				self.updateGlyphClasses()
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

				

				# Remove Selected Item
				removeGlyphs = []
				for item in self.w.tabs[1].contextClassGlyphs.getSelection():
					key = list(self.jsonFile["ContextClass"][selectedClass]["Glyphs"])[item]
					removeGlyphs.append(key)
				for glyph in removeGlyphs:
					self.jsonFile["ContextClass"][selectedClass]["Glyphs"].remove(glyph)
				self.w.tabs[1].contextClassGlyphs.set(list(self.jsonFile["ContextClass"][selectedClass]["Glyphs"]))


				with open(self.jsonPath, "w", encoding='utf8') as outfile:
						json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)

				self.w.tabs[1].contextClassGlyphs.setSelection([])
				self.updateGlyphClasses()

		# If (+) button is pressed
		elif value == 0:

			if self.font.selection:

				i = self.w.tabs[1].listOfContextClass.getSelection()[0]
				selectedClass = list(self.jsonFile["ContextClass"].keys())[i]

				for glyph in self.font.selection:
					if glyph.string:
						addGlyph = glyph.string
					if self.font.glyphs[glyph.name.split(".locl")[0]]:
						addGlyph = self.font.glyphs[glyph.name.split(".locl")[0]].string
					else:
						addGlyph = glyph.name
					if addGlyph not in self.jsonFile["ContextClass"][selectedClass]["Glyphs"]:
						self.jsonFile["ContextClass"][selectedClass]["Glyphs"].append(addGlyph)

						#Sort A-Z Glyphs
						self.jsonFile["ContextClass"][selectedClass]["Glyphs"].sort()
						index = self.jsonFile["ContextClass"][selectedClass]["Glyphs"].index(str(addGlyph))

						self.w.tabs[1].contextClassGlyphs.set(self.jsonFile["ContextClass"][selectedClass]["Glyphs"])
						self.w.tabs[1].contextClassGlyphs.setSelection([index])

				with open(self.jsonPath, "w", encoding='utf8') as outfile:
					json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)

				self.updateGlyphClasses()

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
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.contextWordsCheckBox", 1)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.contextStringCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.smartContextCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.spacingContextCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.lowercaseCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.uppercaseCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.startCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.includeCheckBox", 0)
			Glyphs.registerDefault("com.HugoJourdan.ContextManager.slider", 1)


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
			self.w.tabs[0].slider.set(Glyphs.defaults["com.HugoJourdan.ContextManager.slider"])

			return True
		except:
			return False

	# Update "Glyph Words" in [Context Glyph] tab.
	@objc.python_method
	def updateGlyphWordsCallback(self, sender):

		input = self.selectedChar.parent.name
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

		input = self.selectedChar.parent.name
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

		def importContextDataCallback(sender):
			mergeFile = GetOpenFile(message="Select a .json file to import data",
								allowsMultipleSelection=False, filetypes=None, path=None)

			with open(mergeFile, encoding='utf8') as json_file:
				mergeFile = json.load(json_file)
			with open(self.jsonPath, encoding='utf8') as json_file:
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
				for GLYPH in mergeFile["Glyph"].keys():
					glyphName = Glyphs.font.glyphs[GLYPH].name

					if not glyphName in jsonFile["Glyph"]:
						jsonFile["Glyph"][glyphName] = {"ContextClass":[], "ContextWords":[], "ContextStrings":[]}
					for word in mergeFile["Glyph"][GLYPH]["ContextWords"]:
						if word not in jsonFile["Glyph"][glyphName]["ContextWords"]:
							self.jsonFile["Glyph"][glyphName]["ContextWords"].append(word)

			if w.contextStringsCheckBox.get() == True:
				for GLYPH in mergeFile["Glyph"]:
					
					glyphName = self.font.glyphs[GLYPH].name
					if not glyphName in jsonFile["Glyph"]:
						jsonFile["Glyph"][glyphName] = {"ContextClass":[], "ContextWords":[], "ContextStrings":[]}
					
					jsonFile["Glyph"][glyphName]["ContextStrings"] = mergeFile["Glyph"][GLYPH]["ContextStrings"]

			os.chdir(os.path.dirname(self.jsonPath))
			with open(self.jsonPath, "w", encoding='utf8') as outfile:
				json.dump(self.jsonFile, outfile, indent=4, ensure_ascii=False)

			contextManager.updateWindow(self)
		

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



		w.center()
		w.open()

		#@objc.python_method

	@objc.python_method
	def openDocumentationCallback( self, sender ):
		URL = "https://github.com/HugoJourdan/Context-Manager"
		import webbrowser
		webbrowser.open(URL)


	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
