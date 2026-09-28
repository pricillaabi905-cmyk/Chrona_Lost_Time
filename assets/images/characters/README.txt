HOW TO ADD CHARACTER PICTURES
==============================

Drop image files into this folder using these exact names. The game
checks for them automatically every time it draws a character - if a
file isn't here yet, it just uses the built-in drawn art instead, so
nothing ever breaks. Add files whenever you have them, one at a time.

FILE NAMES (all optional):

  aria_sprite.png             Aria's in-level character (walking around)
  aria_portrait.png           Aria's face, used in dialogue boxes + menu

  caleb_sprite.png            Caleb's figure on the main menu
  caleb_portrait.png          Caleb's face, used in dialogue boxes

  idris_portrait.png          Idris the Shade's dialogue portrait
  rowan_portrait.png          Rowan of the Ice Court's dialogue portrait
  hollow_sovereign_portrait.png   The Hollow Sovereign's dialogue portrait

FORMAT:
  - PNG file, transparent background strongly recommended
  - Portraits: roughly SQUARE (e.g. 256x256, 512x512). Face/bust centered -
    it gets automatically cropped into a circle, so keep the important
    part (the face) near the middle.
  - Sprites: any size works, it gets scaled automatically. A tall,
    portrait-oriented crop (like a 3/4 or full-body shot) looks best
    since it's scaled to fit a roughly 34x52 px character box.

That's it - no code changes needed. Just save the file with the right
name in this folder and restart the game.
