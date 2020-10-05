#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# License: GPLv2

import argparse
import base64
import fcntl
import gobject
import gtk
import os
import struct
import sys
import time
import zlib

iconSize = 22


def readDesktopEntry(path):
  entry = {}
  with open(path, "r") as f:
    lines = f.read().split("\n")
    inside = False
    for line in lines:
      if line.startswith("["):
        inside = line == "[Desktop Entry]"
        continue
      if inside:
        if "=" in line:
          k, v = line.split("=", 1)
          entry[k] = v
  entry["_path"] = path
  return entry


def getSettingLocations():
  locations = ["/usr/share", "/usr/local/share", os.path.expanduser("~/.local/share")]
  if "XDG_DATA_DIRS" in os.environ:
    dirs = os.environ["XDG_DATA_DIRS"]
    if dirs:
      dirs = dirs.split(":")
      for d in dirs:
        while d.endswith("/"):
          d = d[:-1]
        if d not in locations:
          locations.append(d)
  return locations


def loadCategories():
  categories = {}
  for d in getSettingLocations():
    d = d + "/desktop-directories/"
    for (dirpath, dirnames, filenames) in os.walk(d):
      for filename in filenames:
        entry = readDesktopEntry(os.path.join(dirpath, filename))
        if "Name" in entry:
          categories[entry["Name"]] = entry
  if "Other" not in categories:
    categories["Other"] = {"Name": "Other", "Icon": "applications-other", "_path": "auto-generated"}
  return categories


def normalizeCategory(c):
  if c == "Network":
     return [c, "Internet"]
  if c == "Game":
     return [c, "Games"]
  if c == "Utility":
     return [c, "Accessories", "Utilities"]
  if c == "AudioVideo" or c == "Player" or c == "Audio" or c == "Video":
    return [c, "Multimedia", "Sound & Video"]
  if c == "Settings":
     return [c, "Settings", "Preferences"]
  return [c]


def suggestCategories(appName):
  appName = appName.lower()
  if "network" in appName or "google" in appName or "cisco" in appName or "mail" in appName or "youtube" in appName:
    return normalizeCategory("Network")
  return ["Other"]


def loadApplications():
  categories = loadCategories()
  menu = {}
  for d in getSettingLocations():
    d = d + "/applications/"
    for (dirpath, dirnames, filenames) in os.walk(d):
      for filename in filenames:
        entry = readDesktopEntry(os.path.join(dirpath, filename))
        if "Type" in entry and entry["Type"] == "Application":
          if "Name" not in entry:
            entry["Name"] = filename.replace(".desktop", "")
            entry["Name"] = entry["Name"][:1].upper() + entry["Name"][1:]
          appCategories = []
          if "Categories" in entry:
            appCategories = [s.strip() for s in entry["Categories"].split(";") if s.strip()]
          appCategories.append("")
          added = False
          for c in appCategories:
            options = []
            if c:
              if c not in categories:
                options = normalizeCategory(c)
              else:
                options = [c]
            else:
              options = suggestCategories(entry["Name"])
            for o in options:
              if o in categories:
                if o not in menu:
                  menu[o] = []
                menu[o].append(entry)
                added = True
                break
            if added:
              break
  for c in menu:
    menu[c] = sorted(menu[c], key=lambda item: item["Name"])
  return menu, categories


def destroy(object):
  sys.exit(0)


def activate(object, app):
  if "Exec" in app:
    cmd = "("
    if "Path" in app and app["Path"]:
      cmd += "cd " + app["Path"] + ";"
    exe = ""
    percent = False
    for c in app["Exec"]:
      if not percent:
        if c == "%":
          percent = True
        else:
          exe += c
      else:
        if c == "%":
          exe += c
          percent = False
        else:
          pass
    cmd += exe + "&)"
    print("Executing: " + cmd)
    os.system(cmd)
  pass


def loadImage(name):
  image = gtk.Image()
  if "/" in name:
    if os.path.isfile(name):
      pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(name, iconSize, iconSize)
      image.set_from_pixbuf(pixbuf)
      return image
  image.set_from_icon_name(name, gtk.ICON_SIZE_DND)
  image.set_pixel_size(iconSize)
  return image


def createMenu():
  tree, categories = loadApplications()
  menu = gtk.Menu()
  menu.connect("destroy", destroy)
  for c in sorted(tree):
    category = categories[c]
    group = gtk.ImageMenuItem()
    group.set_label(category["Name"])
    tooltip = (category["Comment"] if "Comment" in category else category["Name"]) + "\n\n" + "Loaded from: " + category["_path"]
    group.set_tooltip_text(tooltip)
    if "Icon" in category:
      image = loadImage(category["Icon"])
      group.set_image(image)
      group.set_always_show_image(True)
    submenu = gtk.Menu()
    for app in tree[c]:
      item = gtk.ImageMenuItem()
      item.set_label(app["Name"])
      tooltip = app["Comment"] if "Comment" in app else app["GenericName"] if "GenericName" in app else app["Name"]
      tooltip += "\n\n" + "Loaded from: " + app["_path"]
      tooltip += "\n" + "Executes: " + app["Exec"] if "Exec" in app else ""
      if "Path" in app and app["Path"]:
        tooltip += " in " + app["Path"]
      item.set_tooltip_text(tooltip)
      if "Icon" in app:
        image = loadImage(app["Icon"])
        item.set_image(image)
        item.set_always_show_image(True)
      item.connect("activate", activate, app)
      submenu.append(item)
    group.set_submenu(submenu)
    menu.append(group)
  menu.show_all()
  menu.popup(None, None, None, 0, 0)


if __name__ == '__main__':
  createMenu()
  gtk.main()

