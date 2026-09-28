"""
main.py
-------
Entry point for Chrona: Lost Time.

Manages the overall game state machine:
    MENU -> LEVEL_MAP -> DIALOGUE (intro) -> PLAYING -> DIALOGUE (outro)
    -> LEVEL_MAP (next level) ... -> WIN (after level 5)

Also handles: pausing, game over, saving/loading progress, and the HUD.

Run with:   python main.py
"""

import sys
import pygame

import settings
from src.save_system import load_save, new_save, update_progress
from src.menu import MainMenu, SettingsMenu, HowToPlay, draw_pause_overlay
from src.game_map import LevelMap
from src.dialogue import DialogueBox
from src import story

from levels import (
    level1_temple,
    level2_forest,
    level3_desert,
    level4_frozen,
    level5_castle,
)

LEVEL_MODULES = {
    1: level1_temple,
    2: level2_forest,
    3: level3_desert,
    4: level4_frozen,
    5: level5_castle,
}


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(settings.GAME_TITLE)
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = settings.STATE_MENU
        self.save_data = load_save()

        self.main_menu = MainMenu(has_save=self._has_real_save())
        self.settings_menu = SettingsMenu()
        self.level_map = None

        self.current_level_number = 1
        self.level = None
        self.player = None
        self.camera_x = 0

        self.dialogue_box = None
        self.pending_state_after_dialogue = None

        self.pause_selected = 0
        self.howto = None
        self.howto_after = None    # callable run when the help screen closes

        self.font_hud = pygame.font.SysFont("georgia", 22)
        self.font_big = pygame.font.SysFont("georgia", 54, bold=True)
        self.font_med = pygame.font.SysFont("georgia", 26)
        self.font_small = pygame.font.SysFont("georgia", 17)

    # ------------------------------------------------------------------
    def _has_real_save(self):
        from src.save_system import save_exists
        return save_exists()

    # ------------------------------------------------------------------
    def open_howto(self, after):
        self.howto = HowToPlay()
        self.howto_after = after
        self.state = settings.STATE_HOWTO

    def _back_to_menu(self):
        self.main_menu = MainMenu(has_save=self._has_real_save())
        self.state = settings.STATE_MENU

    def _back_to_pause(self):
        self.state = settings.STATE_PAUSE

    # ------------------------------------------------------------------
    # LEVEL LIFECYCLE
    # ------------------------------------------------------------------
    def start_level(self, level_number, with_intro=True):
        self.current_level_number = level_number
        module = LEVEL_MODULES[level_number]
        self.level = module.create_level()
        self.player = self.level.make_player()
        self.camera_x = 0

        # Persist that we are now "inside" this level so Continue Game
        # resumes here if the player quits or fails.
        self.save_data["current_level"] = level_number
        update_progress(self.save_data, level_number, completed=False, crystals_collected=0)

        if with_intro:
            intro_lines = story.get_intro(level_number)
            if intro_lines:
                self.dialogue_box = DialogueBox(intro_lines, on_finish=self._finish_intro)
                self.state = settings.STATE_DIALOGUE
                return
        self.state = settings.STATE_PLAYING

    def _finish_intro(self):
        self.state = settings.STATE_PLAYING

    def complete_level(self):
        crystals = self.level.crystals_collected_this_level
        self.level.completed = True
        update_progress(self.save_data, self.current_level_number,
                         completed=True, crystals_collected=crystals)

        outro_lines = story.get_outro(self.current_level_number)
        if outro_lines:
            self.dialogue_box = DialogueBox(outro_lines, on_finish=self._after_outro)
            self.state = settings.STATE_DIALOGUE
        else:
            self._after_outro()

    def _after_outro(self):
        if self.current_level_number >= settings.TOTAL_LEVELS:
            self.state = settings.STATE_WIN
        else:
            self.level_map = LevelMap(self.save_data)
            self.state = settings.STATE_LEVEL_MAP

    def fail_level(self):
        # Progress (current_level) is already saved; just return to the map.
        self.level_map = LevelMap(self.save_data)
        self.state = settings.STATE_LEVEL_MAP

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)

            self.update()
            self.draw()

            self.clock.tick(settings.FPS)

        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if self.state == settings.STATE_MENU:
            choice = self.main_menu.handle_event(event)
            if choice == "New Game":
                self.save_data = new_save()
                # Show the tutorial first, then begin Level 1
                self.open_howto(lambda: self.start_level(1))
            elif choice == "How to Play":
                self.open_howto(self._back_to_menu)
            elif choice == "Continue Game":
                self.save_data = load_save()
                self.start_level(self.save_data.get("current_level", 1))
            elif choice == "Level Map":
                self.level_map = LevelMap(self.save_data)
                self.state = settings.STATE_LEVEL_MAP
            elif choice == "Settings":
                self.state = settings.STATE_SETTINGS
            elif choice == "Exit":
                self.running = False

        elif self.state == settings.STATE_HOWTO:
            if self.howto.handle_event(event) == "done":
                after, self.howto_after = self.howto_after, None
                if after:
                    after()

        elif self.state == settings.STATE_SETTINGS:
            choice = self.settings_menu.handle_event(event)
            if choice == "back":
                self.state = settings.STATE_MENU

        elif self.state == settings.STATE_LEVEL_MAP:
            choice = self.level_map.handle_event(event)
            if choice == "back":
                self.main_menu = MainMenu(has_save=self._has_real_save())
                self.state = settings.STATE_MENU
            elif isinstance(choice, int):
                self.start_level(choice)

        elif self.state == settings.STATE_DIALOGUE:
            self.dialogue_box.handle_event(event)

        elif self.state == settings.STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                key = event.key
                p, lvl = self.player, self.level
                if key == settings.KEY_JUMP:
                    if p.on_ladder:
                        p.jump_off_ladder()
                    else:
                        p.request_jump()
                elif key in settings.KEYS_UP:
                    # UP climbs if a ladder is right here, otherwise it jumps
                    if not p.on_ladder and not p.try_grab_ladder(lvl.ladders, going_up=True):
                        p.request_jump()
                elif key in settings.KEYS_DOWN:
                    if not p.on_ladder:
                        p.try_grab_ladder(lvl.ladders, going_up=False)
                elif key == settings.KEY_ATTACK:
                    lvl.add_bolt(p.fire_bolt())
                elif key == settings.KEY_PAUSE:
                    self.pause_selected = 0
                    self.state = settings.STATE_PAUSE
                elif key == settings.KEY_HELP:
                    self.open_howto(self._resume_playing)
                elif key in settings.KEYS_ENTER_PORTAL:
                    if lvl.portal and lvl.portal.player_in_range(p):
                        self.complete_level()

        elif self.state == settings.STATE_PAUSE:
            if event.type == pygame.KEYDOWN:
                if event.key in settings.KEYS_UP:
                    self.pause_selected = (self.pause_selected - 1) % 3
                elif event.key in settings.KEYS_DOWN:
                    self.pause_selected = (self.pause_selected + 1) % 3
                elif event.key in (settings.KEY_INTERACT, settings.KEY_JUMP, pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.pause_selected == 0:
                        self.state = settings.STATE_PLAYING
                    elif self.pause_selected == 1:
                        self.open_howto(self._back_to_pause)
                    else:
                        self._back_to_menu()
                elif event.key == settings.KEY_PAUSE:
                    self.state = settings.STATE_PLAYING

        elif self.state == settings.STATE_GAME_OVER:
            if event.type == pygame.KEYDOWN:
                self.main_menu = MainMenu(has_save=self._has_real_save())
                self.state = settings.STATE_MENU

        elif self.state == settings.STATE_WIN:
            if event.type == pygame.KEYDOWN:
                self.main_menu = MainMenu(has_save=self._has_real_save())
                self.state = settings.STATE_MENU

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def update(self):
        if self.state == settings.STATE_PLAYING:
            keys = pygame.key.get_pressed()
            p = self.player
            p.handle_input(keys)
            # holding UP/DOWN while standing at a ladder also grabs it
            if not p.on_ladder:
                if any(keys[k] for k in settings.KEYS_UP):
                    p.try_grab_ladder(self.level.ladders, going_up=True)
                elif any(keys[k] for k in settings.KEYS_DOWN):
                    p.try_grab_ladder(self.level.ladders, going_up=False)
            if p.on_ladder:
                p.climb(keys)
            else:
                p.move_and_collide(self.level.platforms)
            self.player.update_timers()
            self.level.update(self.player, keys)
            self.camera_x = self.level.get_camera_x(self.player)

            # --- Boss fight orchestration (Level 5) ---
            if self.level.player_reached_boss_trigger(self.player):
                self.level.boss_intro_played = True
                lines = story.get_boss_intro(self.current_level_number)
                if lines:
                    self.dialogue_box = DialogueBox(lines, on_finish=self._activate_boss)
                    self.state = settings.STATE_DIALOGUE
                    return
                else:
                    self._activate_boss()

            if (self.level.boss and self.level.boss.defeated
                    and not self.level.boss_victory_played):
                self.level.boss_victory_played = True
                self.level.portal.active = True
                lines = story.get_boss_victory(self.current_level_number)
                if lines:
                    self.dialogue_box = DialogueBox(lines, on_finish=self._resume_playing)
                    self.state = settings.STATE_DIALOGUE
                    return

            # --- Rival prince duel orchestration (Levels 3 and 4) ---
            triggered_rival = self.level.check_rival_trigger(self.player)
            if triggered_rival:
                triggered_rival["intro_played"] = True
                lines = story.get_rival_dialogue(
                    self.current_level_number, triggered_rival["unit"].key, "intro")
                if lines:
                    self.dialogue_box = DialogueBox(
                        lines, on_finish=lambda r=triggered_rival: self._activate_rival(r))
                    self.state = settings.STATE_DIALOGUE
                    return
                else:
                    self._activate_rival(triggered_rival)

            won_rival = self.level.check_rival_victory()
            if won_rival:
                won_rival["victory_played"] = True
                lines = story.get_rival_dialogue(
                    self.current_level_number, won_rival["unit"].key, "victory")
                if lines:
                    self.dialogue_box = DialogueBox(lines, on_finish=self._resume_playing)
                    self.state = settings.STATE_DIALOGUE
                    return

            if not self.player.is_alive():
                self.state = settings.STATE_GAME_OVER

    def _activate_boss(self):
        self.level.boss_active = True
        self.state = settings.STATE_PLAYING

    def _activate_rival(self, rival):
        rival["active"] = True
        self.state = settings.STATE_PLAYING

    def _resume_playing(self):
        self.state = settings.STATE_PLAYING

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------
    def draw(self):
        if self.state == settings.STATE_MENU:
            self.main_menu.draw(self.screen)
        elif self.state == settings.STATE_HOWTO:
            self.howto.draw(self.screen)
        elif self.state == settings.STATE_SETTINGS:
            self.settings_menu.draw(self.screen)
        elif self.state == settings.STATE_LEVEL_MAP:
            self.level_map.draw(self.screen)
        elif self.state in (settings.STATE_PLAYING, settings.STATE_PAUSE, settings.STATE_DIALOGUE):
            self.draw_level_scene()
            if self.state == settings.STATE_PAUSE:
                draw_pause_overlay(self.screen, self.pause_selected)
            if self.state == settings.STATE_DIALOGUE and self.dialogue_box:
                self.dialogue_box.draw(self.screen)
        elif self.state == settings.STATE_GAME_OVER:
            self.draw_game_over()
        elif self.state == settings.STATE_WIN:
            self.draw_win_screen()

        pygame.display.flip()

    def draw_level_scene(self):
        self.level.draw(self.screen, self.camera_x)
        self.player.draw(self.screen, self.camera_x)
        self.draw_hud()

    def draw_hud(self):
        # Hearts (lives)
        for i in range(max(settings.PLAYER_START_LIVES, self.player.lives)):
            x = 20 + i * 30
            color = settings.RED if i < self.player.lives else settings.DARK_GRAY
            pygame.draw.circle(self.screen, color, (x, 20), 8)
            pygame.draw.circle(self.screen, color, (x + 10, 20), 8)
            pygame.draw.polygon(self.screen, color, [(x - 8, 24), (x + 18, 24), (x + 5, 40)])

        # Energy bar (fuels the X Energy Bolt)
        bx, by, bw, bh = 20, 46, 150, 14
        pygame.draw.rect(self.screen, settings.DARK_GRAY, (bx, by, bw, bh), border_radius=5)
        frac = self.player.energy / settings.MAX_ENERGY
        col = (90, 180, 255) if self.player.energy >= settings.BOLT_COST else (110, 110, 150)
        pygame.draw.rect(self.screen, col, (bx, by, int(bw * frac), bh), border_radius=5)
        pygame.draw.rect(self.screen, settings.GOLD, (bx, by, bw, bh), 2, border_radius=5)
        pygame.draw.line(self.screen, settings.GOLD,
                         (bx + bw * settings.BOLT_COST // settings.MAX_ENERGY, by),
                         (bx + bw * settings.BOLT_COST // settings.MAX_ENERGY, by + bh), 1)
        etxt = self.font_small.render(f"ENERGY  {int(self.player.energy)}", True, settings.WHITE)
        self.screen.blit(etxt, (bx + bw + 10, by - 2))

        # Time Crystals
        crystal_text = self.font_hud.render(
            f"Crystals: {self.level.crystals_collected_this_level}", True, settings.GOLD)
        self.screen.blit(crystal_text, (20, 66))

        # Level name
        level_text = self.font_hud.render(
            f"Level {self.current_level_number}: {self.level.name}", True, settings.WHITE)
        self.screen.blit(level_text, level_text.get_rect(topright=(settings.SCREEN_WIDTH - 20, 20)))

        # Boss HP bar while the fight is active
        if self.level.boss and self.level.boss_active and self.level.boss.alive:
            self.level.boss.draw_hp_bar(self.screen)

        # Rival duel HP bar while a duel is active
        for rival in self.level.rivals:
            if rival["active"] and rival["unit"].alive:
                rival["unit"].draw_hp_bar(self.screen)

        # Sealed-portal reminder while the boss still lives
        if (self.level.boss and self.level.boss_active and self.level.boss.alive
                and self.level.portal and not self.level.portal.active):
            hint = self.font_hud.render(
                "Defeat the Timewyrm to unseal the portal!", True, settings.VILLAIN_RED)
            self.screen.blit(hint, hint.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 60)))

        # Portal prompt (only once it's active/unsealed)
        if (self.level.portal and self.level.portal.active
                and self.level.portal.player_in_range(self.player)
                and self.state == settings.STATE_PLAYING):
            prompt = self.font_hud.render("Press ENTER (or E) to enter the portal", True, settings.GOLD)
            self.screen.blit(prompt, prompt.get_rect(center=(settings.SCREEN_WIDTH // 2, 80)))
        elif (self.state == settings.STATE_PLAYING and not self.player.on_ladder
                and self.player._ladder_at(self.level.ladders)):
            prompt = self.font_hud.render("Press UP / DOWN to climb the ladder", True, settings.LIGHT_VIOLET)
            self.screen.blit(prompt, prompt.get_rect(center=(settings.SCREEN_WIDTH // 2, 80)))

        # Controls reminder at the start of every level (or any time on H)
        if self.level.frame < 900 and self.state == settings.STATE_PLAYING:
            hint = ("Move: ARROWS / A D   Jump: SPACE / UP   Climb: UP DOWN   "
                    "Bolt: X   Portal: ENTER   Help: H")
            surf = self.font_small.render(hint, True, settings.WHITE)
            bar = pygame.Surface((surf.get_width() + 24, 28), pygame.SRCALPHA)
            bar.fill((10, 5, 25, 170))
            self.screen.blit(bar, bar.get_rect(midbottom=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 8)))
            self.screen.blit(surf, surf.get_rect(midbottom=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 12)))

    def draw_game_over(self):
        self.screen.fill(settings.DARK)
        title = self.font_big.render("GAME OVER", True, settings.RED)
        self.screen.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 220)))
        sub = self.font_med.render(
            f"Your progress up to Level {self.save_data.get('current_level', 1)} is saved.",
            True, settings.WHITE)
        self.screen.blit(sub, sub.get_rect(center=(settings.SCREEN_WIDTH // 2, 280)))
        hint = self.font_med.render("Press any key to return to the Main Menu", True, settings.LIGHT_VIOLET)
        self.screen.blit(hint, hint.get_rect(center=(settings.SCREEN_WIDTH // 2, 330)))

    def draw_win_screen(self):
        self.screen.fill(settings.DARK)
        title = self.font_big.render("TIME RESTORED", True, settings.GOLD)
        self.screen.blit(title, title.get_rect(center=(settings.SCREEN_WIDTH // 2, 200)))
        sub1 = self.font_med.render("Aria and Caleb mend the broken timeline together.", True, settings.WHITE)
        self.screen.blit(sub1, sub1.get_rect(center=(settings.SCREEN_WIDTH // 2, 260)))
        sub2 = self.font_med.render(
            f"Total Time Crystals collected: {self.save_data.get('time_crystals', 0)}",
            True, settings.LIGHT_VIOLET)
        self.screen.blit(sub2, sub2.get_rect(center=(settings.SCREEN_WIDTH // 2, 300)))
        hint = self.font_med.render("Press any key to return to the Main Menu", True, settings.GOLD)
        self.screen.blit(hint, hint.get_rect(center=(settings.SCREEN_WIDTH // 2, 360)))


if __name__ == "__main__":
    game = Game()
    game.run()
