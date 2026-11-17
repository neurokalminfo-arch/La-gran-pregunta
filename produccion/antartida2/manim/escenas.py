from manim import *
config.background_color = "#0A0C10"
AMBER = "#FFB224"; RED_ = "#FF4B3A"; BLUE_ = "#2E8BFF"; INK = "#ECEAE4"; MUTED = "#8A8F98"; GREEN_ = "#38D996"
F = "Inter Display"

class Huella(Scene):
    """Huella gravitatoria: cambio del nivel del mar según la distancia al hielo (esquema cualitativo)."""
    def construct(self):
        ax = Axes(x_range=[0, 20, 5], y_range=[-1, 1.6, 0.5], x_length=12, y_length=5.6,
                  axis_config={"color": MUTED, "stroke_width": 3, "include_ticks": False}).shift(DOWN * .4)
        xl = Text("distancia a la Antártida →", font=F, weight=BOLD, color=MUTED).scale(.5).next_to(ax.x_axis, DOWN, buff=.3).align_to(ax.x_axis, RIGHT)
        yl = Text("subida del mar", font=F, weight=BOLD, color=MUTED).scale(.5).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=.25)
        tit = Text("¿Cuánto sube el mar en cada sitio?", font=F, weight=HEAVY, color=INK).scale(.8).to_edge(UP, buff=.5)
        self.play(FadeIn(tit, shift=DOWN * .3), Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)
        media = DashedLine(ax.c2p(0, 1), ax.c2p(20, 1), color=INK, stroke_width=3, dash_length=.15)
        ml = Text("media mundial", font=F, weight=BOLD, color=INK).scale(.45).next_to(media, UP, buff=.08).align_to(media, RIGHT)
        cero = ax.plot(lambda x: 0, x_range=[0, 20], color=MUTED, stroke_width=2)
        media_g = ax.plot(lambda x: 1, x_range=[0, 20], stroke_opacity=0)
        self.play(Create(media), FadeIn(ml), Create(cero), run_time=.8)
        f = lambda x: -0.9 + 2.2 * (1 - np.exp(-x / 2.6)) + 0.12 * (1 - np.exp(-x / 8))
        curva = ax.plot(f, x_range=[0, 20], color=BLUE_, stroke_width=8)
        self.play(Create(curva), run_time=2.6, rate_func=smooth)
        zona = ax.get_area(curva, x_range=[0, 1.35], color=RED_, opacity=.35, bounded_graph=cero)
        baja = Text("BAJA", font=F, weight=HEAVY, color=RED_).scale(.9).move_to(ax.c2p(3.2, -.6))
        self.play(FadeIn(zona), Write(baja), run_time=.9)
        tf = Dot(ax.c2p(1.0, f(1.0)), color=AMBER, radius=.12)
        tfl = Text("Tierra del Fuego", font=F, weight=BOLD, color=AMBER).scale(.5).next_to(tf, UR, buff=.15)
        self.play(GrowFromCenter(tf), FadeIn(tfl), run_time=.7)
        alto = ax.get_area(curva, x_range=[8, 20], color=BLUE_, opacity=.25, bounded_graph=media_g)
        mas = Text("↑ MÁS QUE LA MEDIA", font=F, weight=HEAVY, color=BLUE_).scale(.7).move_to(ax.c2p(14, .55))
        self.play(FadeIn(alto), Write(mas), run_time=1.0)
        nota = Text("esquema según Mitrovica et al. (2009), Science", font=F, color=MUTED).scale(.33).to_edge(DOWN, buff=.25).to_edge(RIGHT)
        self.play(FadeIn(nota), run_time=.4)
        self.wait(6)

class Grados(Scene):
    """Subida del mar a largo plazo por grado de calentamiento (Garbe et al. 2020)."""
    def construct(self):
        tit = Text("Cuánto sube el mar por cada grado", font=F, weight=HEAVY, color=INK).scale(.8).to_edge(UP, buff=.45)
        self.play(FadeIn(tit, shift=DOWN * .3), run_time=.8)
        rates = [1.3, 1.3, 2.4, 2.4, 2.4, 2.4, 10, 10, 10]
        cum = np.cumsum(rates); scale = 5.2 / cum[-1]
        base = DOWN * 2.6; bars = VGroup(); labels = VGroup()
        for i, c in enumerate(cum):
            colr = BLUE_ if rates[i] < 2 else (AMBER if rates[i] < 5 else RED_)
            b = Rectangle(width=1.0, height=max(c * scale, .02), fill_color=colr, fill_opacity=.95, stroke_width=0)
            b.move_to(LEFT * 5.6 + RIGHT * i * 1.4 + base, aligned_edge=DOWN)
            bars.add(b)
            labels.add(Text(f"+{i+1} °C", font=F, weight=BOLD, color=MUTED).scale(.42).next_to(b, DOWN, buff=.15))
        tags = {0: "1,3 m por grado", 2: "2,4 m por grado", 6: "10 m por grado"}
        for i, b in enumerate(bars):
            anims = [GrowFromEdge(b, DOWN), FadeIn(labels[i])]
            self.play(*anims, run_time=.55 if i < 6 else .8)
            if i in tags:
                tg = Text(tags[i], font=F, weight=HEAVY, color=b.get_fill_color()).scale(.55).next_to(b, UP, buff=.2)
                if i == 6:
                    tg.scale(1.3)
                    self.play(Write(tg), b.animate.set_fill(RED_), Flash(b.get_top(), color=RED_, flash_radius=.6), run_time=.8)
                else:
                    self.play(Write(tg), run_time=.5)
        nota = Text("Garbe et al. (2020), Nature · subida a largo plazo (siglos a milenios)", font=F, color=MUTED).scale(.33).to_edge(DOWN, buff=.2).to_edge(RIGHT)
        self.play(FadeIn(nota), run_time=.4)
        self.wait(8)
