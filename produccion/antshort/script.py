PHASES = [
 ("globe",   "¿Qué pasaría si se derritiera toda la Antártida?"),
 ("rise",    "El mar subiría cincuenta y ocho metros. Como un edificio de veinte pisos."),
 ("cities",  "Madrid se salvaría. Buenos Aires, no."),
 ("twist",   "Y lo más raro: junto al hielo, el mar bajaría."),
 ("size",    "La Antártida es casi una Europa y media,"),
 ("thick",   "enterrada bajo un hielo de hasta casi cinco kilómetros."),
 ("ninety",  "Ahí está el noventa por ciento del hielo del planeta."),
 ("five",    "Con cinco metros más, Venecia y Miami se inundan."),
 ("spain",   "Con veinticinco, el mar entra en Sevilla y Valencia."),
 ("world",   "Con cincuenta y ocho, en Buenos Aires y Montevideo."),
 ("gravity", "¿Por qué bajaría? Porque esa montaña de hielo es tan enorme que su gravedad atrae el mar, como un imán."),
 ("escape",  "Sin hielo, el agua se escapa hacia el norte."),
 ("forest",  "Y no sería la primera vez: hace noventa millones de años, cerca del Polo Sur crecía una selva."),
 ("nasa",    "Hoy pierde unos ciento treinta y cinco mil millones de toneladas de hielo al año."),
 ("cta",     "¿Tu ciudad se salvaría? Dímelo en comentarios. El vídeo completo, en nuestro canal: La Gran Pregunta."),
]
TEXT = ' '.join(s for _, s in PHASES)
if __name__ == '__main__': print(len(TEXT.split()))
