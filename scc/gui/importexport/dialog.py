#!/usr/bin/env python2
"""
SC-Controller - Import / Export Dialog
"""
from __future__ import unicode_literals
from scc.tools import _

from scc.gui.editor import Editor, ComboSetter
from scc.tools import find_profile, profile_is_default, profile_is_override
from export import Export
from import_vdf import ImportVdf
from import_sccprofile import ImportSccprofile

import sys, os, logging
log = logging.getLogger("IE.Dialog")

class Dialog(Editor, ComboSetter, Export, ImportVdf, ImportSccprofile):
	GLADE = "import_export.glade"
	
	def __init__(self, app):
		self.app = app
		self._back = []
		self._recursing = False
		self._next_callback = None
		self.setup_widgets()
		Export.__init__(self)
		ImportVdf.__init__(self)
		ImportSccprofile.__init__(self)
	
	
	@staticmethod
	def is_supported(filename):
		"""
		Returns True if passed file can be imported.
		"""
		# Currently decided base on extension
		return (filename.endswith(".sccprofile")
			or filename.endswith(".sccprofile.tar.gz")
			or filename.endswith(".vdf")
			or filename.endswith(".vdffz")
		)
	
	
	@staticmethod
	def check_name(name):
		if len(name.strip()) <= 0: return False
		if "/" in name: return False
		if find_profile(name):
			# Profile already exists
			if profile_is_default(name) and not profile_is_override(name):
				# Existing profile is default and has no override yet
				return True
			return False
		return True
	
	
	def import_file(self, filename):
		"""
		Attempts to import passed file.
		
		Switches to apropriate page automatically, or, if file cannot be
		imported, does nothing.
		"""
		if filename.endswith(".sccprofile"):
			self.import_scc(filename=filename)
		elif filename.endswith(".sccprofile.tar.gz"):
			self.import_scc_tar(filename=filename)
		elif filename.endswith(".vdf") or filename.endswith(".vdffz"):
			self.import_vdf(filename=filename)
	
	
	def next_page(self, page):
		stDialog = self.builder.get_object("stDialog")
		btBack = self.builder.get_object("btBack")
		self._back.append(stDialog.get_visible_child())
		stDialog.set_visible_child(page)
		btBack.set_visible(True)
		self._page_selected(page)
	
	
	def _page_selected(self, page):
		stDialog	= self.builder.get_object("stDialog")
		hbDialog	= self.builder.get_object("hbDialog")
		hbDialog.set_title(stDialog.child_get_property(page, "title"))
		hname = "on_%s_activated" % (page.get_name(),)
		if hasattr(self, hname):
			getattr(self, hname)()
	
	
	def enable_next(self, enabled=True, callback=None):
		"""
		Makes 'Next' button visible and assigns callback that will be
		called when button is clicked. 'Next' button is automatically hidden
		before callback is called.
		
		Returns 'Next' button widget.
		"""
		assert not enabled or callback
		btNext = self.builder.get_object("btNext")
		btNext.set_visible(enabled)
		btNext.set_use_stock(False)
		btNext.set_sensitive(True)
		btNext.set_label(_("Next"))
		self._next_callback = callback
		return btNext
	
	
	def on_btNext_clicked(self, *a):
		cb = self._next_callback
		self.enable_next(enabled=False)
		cb()
	
	
	def on_btBack_clicked(self, *a):
		btBack			= self.builder.get_object("btBack")
		stDialog		= self.builder.get_object("stDialog")
		btSaveAs		= self.builder.get_object("btSaveAs")
		btNext			= self.builder.get_object("btNext")
		page, self._back = self._back[-1], self._back[:-1]
		stDialog.set_visible_child(page)
		btNext.set_visible(False)
		btSaveAs.set_visible(False)
		btBack.set_visible(len(self._back) > 0)
		self._page_selected(page)
	
	
	def on_btExport_clicked(self, *a):
		grSelectProfile	= self.builder.get_object("grSelectProfile")
		self.next_page(grSelectProfile)
	
	
	def on_btImportVdf_clicked(self, *a):
		grVdfImport	= self.builder.get_object("grVdfImport")
		self.next_page(grVdfImport)
