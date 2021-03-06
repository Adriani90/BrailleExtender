# coding: utf-8
# addonSettingsPanel.py
# Part of BrailleExtender addon for NVDA
# Copyright 2016-2018 André-Abush CLAUSE, released under GPL.

from __future__ import unicode_literals
import glob
import os
import gui
import wx
import addonHandler
import braille
import config
import controlTypes
import inputCore
import keyLabels
import queueHandler
import scriptHandler
import ui
addonHandler.initTranslation()

import configBE
import utils
from logHandler import log

instanceGP = None

class AddonSettingsPanel(gui.settingsDialogs.SettingsPanel):

	# Translators: title of a dialog.
	title = "Braille Extender"

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		bHelper1 = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		bHelper2 = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		self.generalBtn = bHelper1.addButton(self, wx.NewId(), "%s..." % _("&General"), wx.DefaultPosition)
		self.generalBtn.Bind(wx.EVT_BUTTON, self.onGeneralBtn)
		self.brailleTablesBtn = bHelper1.addButton(self, wx.NewId(), "%s..." % _("Braille &tables"), wx.DefaultPosition)
		self.brailleTablesBtn.Bind(wx.EVT_BUTTON, self.onBrailleTablesBtn)
		self.attributesBtn = bHelper1.addButton(self, wx.NewId(), "%s..." % _("Text &attributes"), wx.DefaultPosition)
		self.attributesBtn.Bind(wx.EVT_BUTTON, self.onAttributesBtn)
		self.quickLaunchesBtn = bHelper2.addButton(self, wx.NewId(), "%s..." % _("&Quick launches"), wx.DefaultPosition)
		self.quickLaunchesBtn.Bind(wx.EVT_BUTTON, self.onQuickLaunchesBtn)
		self.roleLabelsBtn = bHelper2.addButton(self, wx.NewId(), "%s..." % _("Role &labels"), wx.DefaultPosition)
		self.roleLabelsBtn.Bind(wx.EVT_BUTTON, self.onRoleLabelsBtn)
		self.profileEditorBtn = bHelper2.addButton(self, wx.NewId(), "%s... (%s)" % (_("&Profile editor"), _("feature in process")), wx.DefaultPosition)
		self.profileEditorBtn.Bind(wx.EVT_BUTTON, self.onProfileEditorBtn)
		sHelper.addItem(bHelper1)
		sHelper.addItem(bHelper2)

	def postInit(self): self.General.SetFocus()

	def onSave(self): pass

	def onGeneralBtn(self, evt):
		generalDlg = GeneralDlg(self, multiInstanceAllowed=True)
		generalDlg.ShowModal()

	def onBrailleTablesBtn(self, evt):
		brailleTablesDlg = BrailleTablesDlg(self, multiInstanceAllowed=True)
		brailleTablesDlg.ShowModal()

	def onAttributesBtn(self, evt):
		attribraDlg = AttribraDlg(self, multiInstanceAllowed=True)
		attribraDlg.ShowModal()

	def onQuickLaunchesBtn(self, evt):
		quickLaunchesDlg = QuickLaunchesDlg(self, multiInstanceAllowed=True)
		quickLaunchesDlg.ShowModal()

	def onRoleLabelsBtn(self, evt):
		roleLabelsDlg = RoleLabelsDlg(self, multiInstanceAllowed=True)
		roleLabelsDlg.ShowModal()

	def onProfileEditorBtn(self, evt):
		profileEditorDlg = ProfileEditorDlg(self, multiInstanceAllowed=True)
		profileEditorDlg.ShowModal()

class GeneralDlg(gui.settingsDialogs.SettingsDialog):

	# Translators: title of a dialog.
	title = "Braille Extender - %s" % _("General")

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: label of a dialog.
		self.autoCheckUpdate = sHelper.addItem(wx.CheckBox(self, label=_("Check for &updates automatically")))
		self.autoCheckUpdate.SetValue(config.conf["brailleExtender"]["autoCheckUpdate"])

		# Translators: label of a dialog.
		self.updateChannel = sHelper.addLabeledControl(_("Add-on update channel"), wx.Choice, choices=configBE.updateChannels.values())
		if config.conf["brailleExtender"]["updateChannel"] in configBE.updateChannels.keys():
			itemToSelect = configBE.updateChannels.keys().index(config.conf["brailleExtender"]["updateChannel"])
		else: itemToSelect = config.conf["brailleExtender"]["updateChannel"].index(configBE.CHANNELSTABLE)
		self.updateChannel.SetSelection(itemToSelect)

		# Translators: label of a dialog.
		self.speakScroll = sHelper.addLabeledControl(_("Say current line while scrolling in"), wx.Choice, choices=configBE.focusOrReviewChoices.values())
		self.speakScroll.SetSelection(configBE.focusOrReviewChoices.keys().index(config.conf["brailleExtender"]["speakScroll"]))

		# Translators: label of a dialog.
		self.stopSpeechScroll = sHelper.addItem(wx.CheckBox(self, label=_("Speech interrupt when scrolling on same line")))
		self.stopSpeechScroll.SetValue(config.conf["brailleExtender"]["stopSpeechScroll"])

		# Translators: label of a dialog.
		self.stopSpeechUnknown = sHelper.addItem(wx.CheckBox(self, label=_("Speech interrupt for unknown gestures")))
		self.stopSpeechUnknown.SetValue(config.conf["brailleExtender"]["stopSpeechUnknown"])

		# Translators: label of a dialog.
		self.speakRoutingTo = sHelper.addItem(wx.CheckBox(self, label=_("Announce the character while moving with routing buttons")))
		self.speakRoutingTo.SetValue(config.conf["brailleExtender"]["speakRoutingTo"])

		# Translators: label of a dialog.
		self.hourDynamic = sHelper.addItem(wx.CheckBox(self, label=_("Display time and date infinitely")))
		self.hourDynamic.SetValue(config.conf["brailleExtender"]["hourDynamic"])

		# Translators: label of a dialog.
		self.volumeChangeFeedback = sHelper.addLabeledControl(_("Feedback for volume change in"), wx.Choice, choices=configBE.outputMessage.values())
		if config.conf["brailleExtender"]["volumeChangeFeedback"] in configBE.outputMessage:
			itemToSelect = configBE.outputMessage.keys().index(config.conf["brailleExtender"]["volumeChangeFeedback"]) 
		else:
			itemToSelect = configBE.outputMessage.keys().index(configBE.CHOICE_braille)
		self.volumeChangeFeedback.SetSelection(itemToSelect)

		# Translators: label of a dialog.
		self.modifierKeysFeedback = sHelper.addLabeledControl(_("Feedback for modifier keys in"), wx.Choice, choices=configBE.outputMessage.values())
		if config.conf["brailleExtender"]["modifierKeysFeedback"] in configBE.outputMessage:
			itemToSelect = configBE.outputMessage.keys().index(config.conf["brailleExtender"]["modifierKeysFeedback"]) 
		else:
			itemToSelect = configBE.outputMessage.keys().index(configBE.CHOICE_braille)

		# Translators: label of a dialog.
		self.modifierKeysFeedback.SetSelection(itemToSelect)
		self.rightMarginCells = sHelper.addLabeledControl(_("Right margin on cells")+" "+_("for the currrent braille display"), gui.nvdaControls.SelectOnFocusSpinCtrl, min=0, max=100, initial=config.conf["brailleExtender"]["rightMarginCells_%s" % configBE.curBD])
		if configBE.gesturesFileExists:
			lb = [k for k in instanceGP.getKeyboardLayouts()]
			# Translators: label of a dialog.
			self.KBMode = sHelper.addLabeledControl(_("Braille keyboard configuration"), wx.Choice, choices=lb)
			self.KBMode.SetSelection(self.getKeyboardLayout())

		# Translators: label of a dialog.
		self.reverseScrollBtns = sHelper.addItem(wx.CheckBox(self, label=_("Reverse forward scroll and back scroll buttons")))
		self.reverseScrollBtns.SetValue(config.conf["brailleExtender"]["reverseScrollBtns"])

		# Translators: label of a dialog.
		self.autoScrollDelay = sHelper.addLabeledControl(_("Autoscroll delay (ms)")+" "+_("for the currrent braille display"), gui.nvdaControls.SelectOnFocusSpinCtrl, min=125, max=42000, initial=config.conf["brailleExtender"]["autoScrollDelay_%s" % configBE.curBD])
		self.brailleDisplay1 = sHelper.addLabeledControl(_("First braille display preferred"), wx.Choice, choices=configBE.bds_v)
		self.brailleDisplay1.SetSelection(configBE.bds_k.index(config.conf["brailleExtender"]["brailleDisplay1"]))
		self.brailleDisplay2 = sHelper.addLabeledControl(_("Second braille display preferred"), wx.Choice, choices=configBE.bds_v)
		self.brailleDisplay2.SetSelection(configBE.bds_k.index(config.conf["brailleExtender"]["brailleDisplay2"]))

	def postInit(self): self.autoCheckUpdate.SetFocus()

	def onOk(self, evt):
		config.conf["brailleExtender"]["autoCheckUpdate"] = self.autoCheckUpdate.IsChecked()
		config.conf["brailleExtender"]["hourDynamic"] = self.hourDynamic.IsChecked()
		if self.reverseScrollBtns.IsChecked(): instanceGP.reverseScrollBtns()
		else: instanceGP.reverseScrollBtns(None, True)
		config.conf["brailleExtender"]["reverseScrollBtns"] = self.reverseScrollBtns.IsChecked()
		config.conf["brailleExtender"]["stopSpeechScroll"] = self.stopSpeechScroll.IsChecked()
		config.conf["brailleExtender"]["stopSpeechUnknown"] = self.stopSpeechUnknown.IsChecked()
		config.conf["brailleExtender"]["speakRoutingTo"] = self.speakRoutingTo.IsChecked()

		config.conf["brailleExtender"]["updateChannel"] = configBE.updateChannels.keys()[self.updateChannel.GetSelection()]
		config.conf["brailleExtender"]["speakScroll"] = configBE.focusOrReviewChoices.keys()[self.speakScroll.GetSelection()]

		config.conf["brailleExtender"]["autoScrollDelay_%s" % configBE.curBD] = self.autoScrollDelay.Value
		config.conf["brailleExtender"]["rightMarginCells_%s" % configBE.curBD] = self.rightMarginCells.Value
		config.conf["brailleExtender"]["brailleDisplay1"] = configBE.bds_k[self.brailleDisplay1.GetSelection()]
		config.conf["brailleExtender"]["brailleDisplay2"] = configBE.bds_k[self.brailleDisplay2.GetSelection()]
		if configBE.gesturesFileExists:
			config.conf["brailleExtender"]["keyboardLayout_%s" % configBE.curBD] = configBE.iniProfile["keyboardLayouts"].keys()[self.KBMode.GetSelection()]
		config.conf["brailleExtender"]["volumeChangeFeedback"] = configBE.outputMessage.keys()[self.volumeChangeFeedback.GetSelection()]
		config.conf["brailleExtender"]["modifierKeysFeedback"] = configBE.outputMessage.keys()[self.modifierKeysFeedback.GetSelection()]
		super(GeneralDlg, self).onOk(evt)

	def getKeyboardLayout(self):
		if (config.conf["brailleExtender"]["keyboardLayout_%s" % configBE.curBD] is not None
		and config.conf["brailleExtender"]["keyboardLayout_%s" % configBE.curBD] in configBE.iniProfile['keyboardLayouts'].keys()):
			return configBE.iniProfile['keyboardLayouts'].keys().index(config.conf["brailleExtender"]["keyboardLayout_%s" % configBE.curBD])
		else: return 0


class AttribraDlg(gui.settingsDialogs.SettingsDialog):

	# Translators: title of a dialog.
	title = "Braille Extender - %s" % _("Attribra")

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.toggleAttribra = sHelper.addItem(wx.CheckBox(self, label=_("Enable Attribra")))
		self.toggleAttribra.SetValue(config.conf["brailleExtender"]["features"]["attributes"])
		self.spellingErrorsAttribute = sHelper.addLabeledControl(_("Show spelling errors with"), wx.Choice, choices=configBE.attributeChoices.values())
		self.spellingErrorsAttribute.SetSelection(self.getItemToSelect("invalid-spelling"))
		self.boldAttribute = sHelper.addLabeledControl(_("Show bold with"), wx.Choice, choices=configBE.attributeChoices.values())
		self.boldAttribute.SetSelection(self.getItemToSelect("bold"))
		self.italicAttribute = sHelper.addLabeledControl(_("Show italic with"), wx.Choice, choices=configBE.attributeChoices.values())
		self.italicAttribute.SetSelection(self.getItemToSelect("italic"))
		self.underlineAttribute = sHelper.addLabeledControl(_("Show underline with"), wx.Choice, choices=configBE.attributeChoices.values())
		self.underlineAttribute.SetSelection(self.getItemToSelect("underline"))

	def postInit(self): self.toggleAttribra.SetFocus()

	def onOk(self, evt):
		config.conf["brailleExtender"]["features"]["attributes"] = self.toggleAttribra.IsChecked()
		config.conf["brailleExtender"]["attributes"]["bold"] = configBE.attributeChoices.keys()[self.boldAttribute.GetSelection()]
		config.conf["brailleExtender"]["attributes"]["italic"] = configBE.attributeChoices.keys()[self.italicAttribute.GetSelection()]
		config.conf["brailleExtender"]["attributes"]["underline"] = configBE.attributeChoices.keys()[self.underlineAttribute.GetSelection()]
		config.conf["brailleExtender"]["attributes"]["invalid-spelling"] = configBE.attributeChoices.keys()[self.spellingErrorsAttribute.GetSelection()]
		super(AttribraDlg, self).onOk(evt)

	def getItemToSelect(self, attribute):
		try: idx = configBE.attributeChoices.keys().index(config.conf["brailleExtender"]["attributes"][attribute])
		except BaseException as err:
			log.error(err)
			idx = 0
		return idx

class RoleLabelsDlg(gui.settingsDialogs.SettingsDialog):

	# Translators: title of a dialog.
	title = "Braille Extender - %s" % _("Role labels")

	def makeSettings(self, settingsSizer):
		self.roleLabels = config.conf["brailleExtender"]["roleLabels"].copy()
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.categories = sHelper.addLabeledControl(_("Role category"), wx.Choice, choices=[_("General"), _("Landmark"), _("Positive state"), _("Negative state")])
		self.categories.Bind(wx.EVT_CHOICE, self.onCategories)
		self.categories.SetSelection(0)
		sHelper2 = gui.guiHelper.BoxSizerHelper(self, orientation=wx.HORIZONTAL)
		self.labels = sHelper2.addLabeledControl(_("Role"), wx.Choice, choices=[controlTypes.roleLabels[int(k)] for k in braille.roleLabels.keys()])
		self.labels.Bind(wx.EVT_CHOICE, self.onLabels)
		self.label = sHelper2.addLabeledControl(_("Actual or new label"), wx.TextCtrl)
		self.label.Bind(wx.EVT_TEXT, self.onLabel)
		sHelper.addItem(sHelper2)
		self.onCategories(None)

	def onCategories(self, event):
		idCategory = self.categories.GetSelection()
		if idCategory == 0: self.labels.SetItems([controlTypes.roleLabels[int(k)] for k in braille.roleLabels.keys()])
		elif idCategory == 1: self.labels.SetItems(braille.landmarkLabels.keys())
		elif idCategory == 2: self.labels.SetItems([controlTypes.stateLabels[k] for k in braille.positiveStateLabels.keys()])
		elif idCategory == 3: self.labels.SetItems([controlTypes.stateLabels[k] for k in braille.negativeStateLabels.keys()])
		else: self.labels.SetItems([])
		if idCategory > -1 and idCategory < 4: self.labels.SetSelection(0)
		self.onLabels(None)

	def onLabels(self, event):
		idCategory = self.categories.GetSelection()
		idLabel = self.getIDFromIndex(idCategory, self.labels.GetSelection())
		key = "%d:%s" % (idCategory, idLabel)
		if key in self.roleLabels.keys(): self.label.SetValue(self.roleLabels[key])
		else: self.label.SetValue(self.getLabelFromID())

	def onLabel(self, evt):
		idCategory = self.categories.GetSelection()
		idLabel = self.labels.GetSelection()
		key = "%d:%s" % (idCategory, self.getIDFromIndex(idCategory, idLabel))
		label = self.label.GetValue()
		if idCategory >= 0 and idLabel >= 0:
			if self.getLabelFromID() == label:
				if key in self.roleLabels.keys(): log.info("%s deleted" % self.roleLabels.pop(key))
			else: self.roleLabels[key] = label

	def getIDFromIndex(self, idCategory, idLabel):
		try:
			if idCategory == 0: return braille.roleLabels.keys()[idLabel]
			elif idCategory == 1: return braille.landmarkLabels.keys()[idLabel]
			elif idCategory == 2: return braille.positiveStateLabels.keys()[idLabel]
			elif idCategory == 3: return braille.negativeStateLabels.keys()[idLabel]
			else: return -1
		except BaseException: return -1

	def getLabelFromID(self):
		idCategory = self.categories.GetSelection()
		idLabel = self.labels.GetSelection()
		if idCategory == 0:
			return braille.roleLabels[braille.roleLabels.keys()[idLabel]]
		elif idCategory == 1:
			return braille.landmarkLabels.values()[idLabel]
		elif idCategory == 2:
			return braille.positiveStateLabels[braille.positiveStateLabels.keys()[idLabel]]
		elif idCategory == 3:
			return braille.negativeStateLabels[braille.negativeStateLabels.keys()[idLabel]]

	def postInit(self):
		self.categories.SetFocus()

	def onOk(self, evt):
		config.conf["brailleExtender"]["roleLabels"] = self.roleLabels
		configBE.discardRoleLabels()
		configBE.loadRoleLabels(config.conf["brailleExtender"]["roleLabels"].copy())
		super(RoleLabelsDlg, self).onOk(evt)

class BrailleTablesDlg(gui.settingsDialogs.SettingsDialog):

	# Translators: title of a dialog.
	title = "Braille Extender - %s" % _("braille tables")

	def makeSettings(self, settingsSizer):
		self.oTables = set(configBE.outputTables)
		self.iTables = set(configBE.inputTables)
		lt = [_('Use the current input table')]
		for table in configBE.tables:
			if table.output and not table.contracted: lt.append(table[1])
			if config.conf["brailleExtender"]["inputTableShortcuts"] in configBE.tablesUFN:
				iSht = configBE.tablesUFN.index(config.conf["brailleExtender"]["inputTableShortcuts"]) + 1
			else: iSht = 0
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.tables = sHelper.addLabeledControl(_("Prefered braille tables")+" (%s)" % ("press F1 for help"), wx.Choice, choices=self.getTablesWithSwitches())
		self.tables.SetSelection(0)
		self.tables.Bind(wx.EVT_CHAR, self.onTables)

		self.inputTableShortcuts = sHelper.addLabeledControl(_("Input braille table for keyboard shortcut keys"), wx.Choice, choices=lt)
		self.inputTableShortcuts.SetSelection(iSht)
		lt = [_('None')]
		for table in configBE.tables:
			if table.output: lt.append(table[1])
		self.postTable = sHelper.addLabeledControl(_("Secondary output table to use"), wx.Choice, choices=lt)
		self.postTable.SetSelection(configBE.tablesFN.index(config.conf["brailleExtender"]["postTable"]) if config.conf["brailleExtender"]["postTable"] in configBE.tablesFN else 0)

		# Translators: label of a dialog.
		self.tabSpace = sHelper.addItem(wx.CheckBox(self, label=_("Display tab signs as spaces")))
		self.tabSpace.SetValue(config.conf["brailleExtender"]["tabSpace"])

		# Translators: label of a dialog.
		self.tabSize = sHelper.addLabeledControl(_("Number of space for a tab sign")+" "+_("for the currrent braille display"), gui.nvdaControls.SelectOnFocusSpinCtrl, min=1, max=42, initial=config.conf["brailleExtender"]["tabSize_%s" % configBE.curBD])

	def postInit(self): self.tables.SetFocus()

	def onOk(self, evt):
		config.conf["brailleExtender"]["outputTables"] = ','.join(self.oTables)
		config.conf["brailleExtender"]["inputTables"] = ','.join(self.iTables)
		configBE.loadPreferedTables()
		config.conf["brailleExtender"]["inputTableShortcuts"] = configBE.tablesUFN[self.inputTableShortcuts.GetSelection()-1] if self.inputTableShortcuts.GetSelection()>0 else '?'
		postTableID = self.postTable.GetSelection()
		postTable = "None" if postTableID == 0 else configBE.tablesFN[postTableID]
		config.conf["brailleExtender"]["postTable"] = postTable
		configBE.loadPostTable()
		config.conf["brailleExtender"]["tabSpace"] = self.tabSpace.IsChecked()
		config.conf["brailleExtender"]["tabSize_%s" % configBE.curBD] = self.tabSize.Value
		configBE.loadPreTable()
		super(BrailleTablesDlg, self).onOk(evt)

	def getTablesWithSwitches(self):
		out = []
		for i, tbl in enumerate(configBE.tablesTR):
			out.append("%s%s: %s" % (tbl, configBE.sep, self.getInSwitchesText(configBE.tablesFN[i])))
		return out

	def getCurrentSelection(self):
		idx = self.tables.GetSelection()
		tbl = configBE.tablesFN[self.tables.GetSelection()]
		return idx, tbl

	def setCurrentSelection(self, tbl, newLoc):
		if newLoc == "io":
			self.iTables.add(tbl)
			self.oTables.add(tbl)
		elif newLoc == "i":
			self.iTables.add(tbl)
			self.oTables.discard(tbl)
		elif newLoc == "o":
			self.oTables.add(tbl)
			self.iTables.discard(tbl)
		elif newLoc == "n":
			self.iTables.discard(tbl)
			self.oTables.discard(tbl)

	def inSwitches(self, tbl):
		inp = True if tbl in self.iTables else False
		out = True if tbl in self.oTables else False
		return [inp, out]

	def getInSwitchesText(self, tbl):
		inS = self.inSwitches(tbl)
		if all(inS): inSt = _("input and output")
		elif not any(inS): inSt = _("none")
		elif inS[0]: inSt = _("input only")
		elif inS[1]: inSt = _("output only")
		return inSt

	def changeSwitch(self, tbl, direction = 1, loop = True):
		dirs = ['n', 'i', 'o', "io"]
		iCurDir = 0
		inS = self.inSwitches(tbl)
		if all(inS): iCurDir = dirs.index("io")
		elif not any(inS): iCurDir = dirs.index('n')
		elif inS[0]: iCurDir = dirs.index('i')
		elif inS[1]: iCurDir = dirs.index('o')

		if len(dirs)-1 == iCurDir and direction == 1 and loop: newDir = dirs[0]
		elif iCurDir == 0 and direction == 0 and loop: newDir = dirs[-1]
		elif iCurDir < len(dirs)-1 and direction == 1: newDir = dirs[iCurDir+1]
		elif iCurDir > 0 and iCurDir < len(dirs) and direction == 0: newDir = dirs[iCurDir-1]
		else: return
		self.setCurrentSelection(tbl, newDir)

	def onTables(self, evt):
		keycode = evt.GetKeyCode()
		if keycode in [ord(','), ord(';')]:
			idx, tbl = self.getCurrentSelection()
			if keycode == ord(','):
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, "%s" % tbl)
			else:
				ui.browseableMessage("Name: %s\nFile name: %s\nIn switches: %s" % (
					configBE.tablesTR[idx],
					tbl,
					self.getInSwitchesText(tbl)
				), "Infos about this table", False)
		if keycode == wx.WXK_F1:
			ui.browseableMessage(
				_("In this combo box, all tables are present. Press space bar, left or right arrow keys to include (or not) the selected table in switches")+".\n"+
			_("You can also press 'comma' key to get the file name of the selected table and 'semicolon' key to view miscellaneous infos on the selected table")+".",
			_("Contextual help"), False)
		if keycode in [wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_SPACE]:
			idx, tbl = self.getCurrentSelection()
			if keycode == wx.WXK_LEFT: self.changeSwitch(tbl, 0, False)
			elif keycode == wx.WXK_RIGHT: self.changeSwitch(tbl, 1, False)
			elif keycode == wx.WXK_SPACE: self.changeSwitch(tbl, 1, True)
			newSwitch = self.getInSwitchesText(tbl)
			self.tables.SetString(self.tables.GetSelection(), "%s%s: %s" % (configBE.tablesTR[idx], configBE.sep, newSwitch))
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, "%s" % newSwitch)
			utils.refreshBD()
		else: evt.Skip()

class QuickLaunchesDlg(gui.settingsDialogs.SettingsDialog):

	# Translators: title of a dialog.
	title = "Braille Extender - %s" % _("Quick launches")
	quickLaunchGestures = []
	quickLaunchLocations = []

	def makeSettings(self, settingsSizer):
		self.quickLaunchGestures = config.conf["brailleExtender"]["quickLaunches"].copy().keys()
		self.quickLaunchLocations = config.conf["brailleExtender"]["quickLaunches"].copy().values()
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		bHelper1 = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		self.quickKeys = sHelper.addLabeledControl(_("&Gestures"), wx.Choice, choices=self.getQuickLaunchList())
		self.quickKeys.SetSelection(0)
		self.quickKeys.Bind(wx.EVT_CHOICE, self.onQuickKeys)
		self.target = sHelper.addLabeledControl(_("Location"), wx.TextCtrl, value=self.quickLaunchLocations[0] if self.quickLaunchLocations != [] else '')
		self.target.Bind(wx.EVT_TEXT, self.onTarget)
		self.browseBtn = bHelper1.addButton(self, wx.NewId(), "%s..." % _("&Browse"), wx.DefaultPosition)
		self.removeGestureBtn = bHelper1.addButton(self, wx.NewId(), _("&Remove this gesture"), wx.DefaultPosition)
		self.addGestureBtn = bHelper1.addButton(self, wx.NewId(), _("&Add a quick launch"), wx.DefaultPosition)
		self.browseBtn.Bind(wx.EVT_BUTTON, self.onBrowseBtn)
		self.removeGestureBtn.Bind(wx.EVT_BUTTON, self.onRemoveGestureBtn)
		self.addGestureBtn.Bind(wx.EVT_BUTTON, self.onAddGestureBtn)
		sHelper.addItem(bHelper1)

	def postInit(self): self.quickKeys.SetFocus()

	def onOk(self, evt):
		config.conf["brailleExtender"]["quickLaunches"] = {}
		for gesture, location in zip(self.quickLaunchGestures, self.quickLaunchLocations):
			config.conf["brailleExtender"]["quickLaunches"][gesture] = location
		instanceGP.loadQuickLaunchesGes()
		super(QuickLaunchesDlg, self).onOk(evt)

	def captureNow(self):
		def getCaptured(gesture):
			if gesture.isModifier: return False
			if scriptHandler.findScript(gesture) is not None:
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Unable to associate this gesture. Please enter another, now"))
				return False
			if gesture.normalizedIdentifiers[0].startswith("kb") and ":escape" not in gesture.normalizedIdentifiers[0]:
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Please enter a gesture from your {NAME_BRAILLE_DISPLAY} braille display. Press Escape to cancel.".format(NAME_BRAILLE_DISPLAY=configBE.curBD)))
				return False
			if ':escape' not in gesture.normalizedIdentifiers[0]:
				self.quickLaunchGestures.append(gesture.normalizedIdentifiers[0])
				self.quickLaunchLocations.append('')
				self.quickKeys.SetItems(self.getQuickLaunchList())
				self.quickKeys.SetSelection(len(self.quickLaunchGestures)-1)
				self.onQuickKeys(None)
				self.quickKeys.SetFocus()
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("OK. The gesture captured is %s") % gesture.normalizedIdentifiers[0])
				inputCore.manager._captureFunc = None
		inputCore.manager._captureFunc = getCaptured

	def getQuickLaunchList(s):
		return ['%s%s: %s' % (utils.beautifulSht(s.quickLaunchGestures[i]), configBE.sep, s.quickLaunchLocations[i]) for i, v in enumerate(s.quickLaunchLocations)]

	def onRemoveGestureBtn(self, event):
		def askConfirmation():
			choice = gui.messageBox(_("Are you sure to want to delete this shorcut?"), '%s – %s' % (configBE._addonName, _("Confirmation")), wx.YES_NO|wx.ICON_QUESTION)
			if choice == wx.YES: confirmed()
		def confirmed():
			i = self.quickKeys.GetSelection()
			g = self.quickLaunchGestures.pop(i)
			self.quickLaunchLocations.pop(i)
			self.quickKeys.SetItems(self.getQuickLaunchList())
			self.quickKeys.SetSelection(i-1 if i > 0 else 0)
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _('{BRAILLEGESTURE} removed'.format(BRAILLEGESTURE=g)))
			self.onQuickKeys(None)
		wx.CallAfter(askConfirmation)
		self.quickKeys.SetFocus()

	def onAddGestureBtn(self, event):
		self.captureNow()
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _('Please enter the desired gesture for this command, now'))
		return

	def onTarget(self, event):
		oldS = self.quickKeys.GetSelection()
		self.quickLaunchLocations[self.quickKeys.GetSelection()] = self.target.GetValue()
		self.quickKeys.SetItems(self.getQuickLaunchList())
		self.quickKeys.SetSelection(oldS)

	def onQuickKeys(self, event):
		if not self.quickKeys.GetStringSelection().strip().startswith(':'):
			self.target.SetValue(self.quickKeys.GetStringSelection().split(': ')[1])
		else: self.target.SetValue('')
		return

	def onBrowseBtn(self, event):
		oldS = self.quickKeys.GetSelection()
		dlg = wx.FileDialog(None, _("Choose a file for {0}".format(self.quickLaunchGestures[self.quickKeys.GetSelection()])), "%PROGRAMFILES%", "", "*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return self.quickKeys.SetFocus()
		self.target.SetValue(dlg.GetDirectory() + '\\' + dlg.GetFilename())
		self.quickLaunchLocations[self.quickKeys.GetSelection()] = dlg.GetDirectory() + '\\' + dlg.GetFilename()
		self.quickKeys.SetItems(self.getQuickLaunchList())
		self.quickKeys.SetSelection(oldS)
		dlg.Destroy()
		return self.quickKeys.SetFocus()

class ProfileEditorDlg(gui.settingsDialogs.SettingsDialog):
	title = _("Profiles editor") + " (%s)" % configBE.curBD
	profilesList = []
	addonGesturesPrfofile = None
	generalGesturesProfile = None
	keyLabelsList = sorted([(t[1], t[0]) for t in keyLabels.localizedKeyLabels.items()])+[('f%d' %i, 'f%d' %i) for i in range(1, 13)]

	def makeSettings(self, settingsSizer):
		if configBE.curBD == 'noBraille':
			self.Destroy()
			wx.CallAfter(gui.messageBox, _("You must have a braille display to editing a profile"), self.title, wx.OK|wx.ICON_ERROR)

		if not os.path.exists(configBE.profilesDir):
			self.Destroy()
			wx.CallAfter(gui.messageBox, _("Profiles directory is not present or accessible. Unable to edit profiles"), self.title, wx.OK|wx.ICON_ERROR)

		self.profilesList = self.getListProfiles()

		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		labelText = _("Profile to edit")
		self.profiles = sHelper.addLabeledControl(labelText, wx.Choice, choices=self.profilesList)
		self.profiles.SetSelection(0)
		self.profiles.Bind(wx.EVT_CHOICE, self.onProfiles)

		sHelper2 = gui.guiHelper.BoxSizerHelper(self, orientation=wx.HORIZONTAL)
		labelText = _('Gestures category')
		categoriesList = [_("Single keys"), _("Modifier keys"), _("Practical shortcuts"), _("NVDA commands"), _("Addon features")]
		self.categories = sHelper2.addLabeledControl(labelText, wx.Choice, choices=categoriesList)
		self.categories.SetSelection(0)
		self.categories.Bind(wx.EVT_CHOICE, self.refreshGestures)
		labelText = _('Gestures list')
		self.gestures = sHelper2.addLabeledControl(labelText, wx.Choice, choices=[])
		self.gestures.Bind(wx.EVT_CHOICE, self.onGesture)

		sHelper.addItem(sHelper2)

		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)

		addGestureButtonID = wx.NewId()
		self.addGestureButton = bHelper.addButton(self, addGestureButtonID, _("Add gesture"), wx.DefaultPosition)

		self.removeGestureButton = bHelper.addButton(self, addGestureButtonID, _("Remove this gesture"), wx.DefaultPosition)

		assignGestureButtonID = wx.NewId()
		self.assignGestureButton = bHelper.addButton(self, assignGestureButtonID, _("Assign a braille gesture"), wx.DefaultPosition)

		sHelper.addItem(bHelper)

		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)

		removeProfileButtonID = wx.NewId()
		self.removeProfileButton = bHelper.addButton(self, removeProfileButtonID, _("Remove this profile"), wx.DefaultPosition)

		addProfileButtonID = wx.NewId()
		self.addProfileButton = bHelper.addButton(self, addProfileButtonID, _("Add a profile"), wx.DefaultPosition)
		self.addProfileButton.Bind(wx.EVT_BUTTON, self.onAddProfileButton)

		sHelper.addItem(bHelper)

		edHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.HORIZONTAL)
		labelText = _('Name for the new profile')
		self.newProfileName = edHelper.addLabeledControl(labelText, wx.TextCtrl)
		sHelper.addItem(edHelper)

		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		validNewProfileNameButtonID = wx.NewId()
		self.validNewProfileNameButton = bHelper.addButton(self, validNewProfileNameButtonID, _('Create'))

		sHelper.addItem(bHelper)

	def postInit(self):
		self.hideNewProfileSection()
		self.refreshGestures()
		if len(self.profilesList)>0:
			self.profiles.SetSelection(self.profilesList.index(config.conf["brailleExtender"]["profile_%s" % configBE.curBD]))
		self.onProfiles()
		self.profiles.SetFocus()

	def refreshGestures(self, evt = None):
		category = self.categories.GetSelection()
		items = []
		ALT = keyLabels.localizedKeyLabels['alt'].capitalize()
		CTRL = keyLabels.localizedKeyLabels['control'].capitalize()
		SHIFT = keyLabels.localizedKeyLabels['shift'].capitalize()
		WIN = keyLabels.localizedKeyLabels['windows'].capitalize()
		if category == 0: items = [k[0].capitalize() for k in self.keyLabelsList]
		elif category == 1:
			items = [ALT, CTRL, SHIFT, WIN, "NVDA",
			'%s+%s' % (ALT, CTRL),
			'%s+%s' % (ALT, SHIFT),
			'%s+%s' % (ALT, WIN),
			'%s+%s+%s' % (ALT, CTRL, SHIFT),
			'%s+%s+%s+%s' % (ALT, CTRL, SHIFT, WIN),
			'%s+%s+%s' % (ALT, CTRL, WIN),
			'%s+%s' % (CTRL, SHIFT),
			'%s+%s' % (CTRL, WIN),
				'%s+%s+%s' % (CTRL, SHIFT, WIN),
			'%s+%s' % (SHIFT, WIN)
			]
		elif category == 2:
			items = sorted([
				'%s+F4' % ALT,
				'%s+Tab' % ALT,
				'%s+Tab' % SHIFT,
			])
		self.gestures.SetItems(items)
		self.gestures.SetSelection(0)
		self.gestures.SetSelection(0)
		if category<2:
			self.addGestureButton.Disable()
			self.removeGestureButton.Disable()
		else:
			self.addGestureButton.Enable()
			self.removeGestureButton.Enable()

	def onProfiles(self, evt = None):
		if len(self.profilesList) == 0: return
		curProfile = self.profilesList[self.profiles.GetSelection()]
		self.addonGesturesPrfofile = config.ConfigObj('%s/baum/%s/profile.ini' % (configBE.profilesDir, curProfile), encoding="UTF-8")
		self.generalGesturesProfile = config.ConfigObj('%s/baum/%s/gestures.ini' % (configBE.profilesDir, curProfile), encoding="UTF-8")
		if self.addonGesturesPrfofile == {}:
			wx.CallAfter(gui.messageBox, _("Unable to load this profile. Malformed or inaccessible file"), self.title, wx.OK|wx.ICON_ERROR)

	def getListProfiles(self):
		profilesDir = '%s\%s' %(configBE.profilesDir, configBE.curBD)
		res = []
		ls = glob.glob(profilesDir+'\\*')  
		for e in ls:
			if os.path.isdir(e) and os.path.exists('%s\%s' %(e, 'profile.ini')): res.append(e.split('\\')[-1])
		return res

	def switchProfile(self, evt = None):
		self.refreshGestures()

	def onGesture(self, evt = None):
		category = self.categories.GetSelection()
		gesture = self.gestures.GetSelection()
		gestureName = self.keyLabelsList[gesture][1]

	def onAddProfileButton(self, evt = None):
		if not self.addProfileButton.IsEnabled():
			self.hideNewProfileSection()
			self.addProfileButton.Enable()
		else:
			self.newProfileName.Enable()
			self.validNewProfileNameButton.Enable()
			self.addProfileButton.Disable()

	def hideNewProfileSection(self, evt = None):
		self.validNewProfileNameButton.Disable()
		self.newProfileName.Disable()
