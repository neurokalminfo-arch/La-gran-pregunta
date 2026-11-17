PHASES = [
 ("city",    "¿Y si mañana se fuera la luz en todo el país?"),
 ("yapaso",  "No es una hipótesis. Ya pasó."),
 ("iberia",  "España y Portugal, abril de 2025: a oscuras en segundos."),
 ("chile",   "Chile, dos meses antes: casi todo el país a oscuras."),
 ("traffic", "Semáforos apagados."),
 ("train",   "Ciento dieciséis trenes parados en mitad de la vía."),
 ("shops",   "Y solo uno de cada diez comercios podía cobrar con tarjeta."),
 ("why",     "¿Por qué tan rápido?"),
 ("heart",   "La red eléctrica late cincuenta veces por segundo, como un corazón."),
 ("balance", "Lo que se produce y lo que se consume debe estar igualado en cada instante."),
 ("chain",   "Si algo la desequilibra de golpe, las centrales se desconectan... una detrás de otra."),
 ("eu",      "Por eso la Unión Europea pide tener en casa lo necesario para setenta y dos horas:"),
 ("kit",     "agua, comida sin cocinar, radio a pilas, linterna, efectivo, medicinas y una batería cargada."),
 ("days",    "Aquel apagón se arregló en un día. ¿Y si el próximo durara tres?"),
 ("comment", "¿Tú tienes tu kit? Dímelo en comentarios."),
 ("cta",     "Y si se apagara Internet un mes entero, lo tienes en nuestro canal: La Gran Pregunta."),
]
TEXT = ' '.join(s for _, s in PHASES)
if __name__ == '__main__': print(len(TEXT.split()), 'palabras')
