import sys, pygame as pg

class Button:
    def __init__(self, text, position, size, font, bg_color, text_color):
        self.text = text
        self.position = position
        self.size = size
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.rect = pg.Rect(position, size)
        self.rendered_text = self.font.render(self.text, True, self.text_color)

    def draw(self, surface):
        pg.draw.rect(surface, self.bg_color, self.rect)
        text_rect = self.rendered_text.get_rect(center=self.rect.center)
        surface.blit(self.rendered_text, text_rect)

    def is_clicked(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def update_position(self, new_position):
        self.position = new_position
        self.rect.topleft = new_position
