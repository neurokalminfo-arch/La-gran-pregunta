# -*- coding: utf-8 -*-
"""Vídeo 1 · Biología Oculta · «Lo que pasa en tu cuerpo si caminas 10 min al despertar».
Cada bloque se locuta de una vez; cada beat es una frase con su escena (kind + parámetros).
kw = palabras clave que aparecen en pantalla con efecto rotulador cuando la voz las dice.
src = fuente que se muestra abajo a la izquierda."""

BLOCKS = [
# ───────────── 0 · HOOK ─────────────
("hook", [
 ("Imagina a dos personas que desayunan exactamente lo mismo.", "two_breakfast", {}),
 ("Las mismas calorías. La misma hora. Una vida parecida.", "equal_cards", {"items": ["MISMAS CALORÍAS", "MISMA HORA", "MISMA VIDA"]}),
 ("Pero a las once de la mañana, una está agotada, con hambre y pensando en algo dulce...", "person_graph", {"mood": "tired", "graph": "roller", "clock": "11:00"}),
 ("y la otra ni se acuerda de comer.", "person_graph", {"mood": "calm", "graph": "flat", "clock": "11:00"}),
 ("La diferencia no está en el desayuno. Ni en la genética. Ni en la fuerza de voluntad.", "cross_list", {"items": ["DESAYUNO", "GENÉTICA", "FUERZA DE VOLUNTAD"]}),
 ("Una de las razones puede haber ocurrido antes de desayunar. En solo diez minutos. Y casi nadie lo hace.", "clock_window", {"from": 7.0, "to": 7.17, "kw": "10 MINUTOS"}),
 ("Quédate hasta el final, porque te voy a contar un experimento en el que un grupo de hombres quemó el doble de grasa... y no adelgazó más que los demás.", "paradox_tease", {}),
 ("Esa paradoja es la clave de todo este vídeo.", "big_question", {"text": "¿CÓMO ES POSIBLE?"}),
]),
# ───────────── 1 · QUÉ NO ES / LA SEÑAL ─────────────
("senal", [
 ("Empecemos por lo que no es.", "doctor_intro", {}),
 ("No es una dieta. No es un suplemento. No es meterse en agua helada, ni pagar un gimnasio.", "icon_cross", {"icons": ["plate", "pills", "ice", "dumbbell"]}),
 ("Es caminar. Despacio. Diez minutos, nada más levantarte.", "walk_sunrise", {"kw": "CAMINAR DESPACIO"}),
 ("Sé lo que estás pensando: caminar despacio no sirve para nada.", "skeptic", {}),
 ("Y si lo miras en calorías, tienes razón. Diez minutos de paseo tranquilo gastan unas treinta o cuarenta calorías. Más o menos, una galleta.", "kcal_cookie", {"value": 35}),
 ("Pero... ¿y si esos diez minutos no tuvieran nada que ver con quemar calorías?", "big_question", {"text": "¿Y SI NO FUERA POR LAS CALORÍAS?"}),
 ("¿Y si fueran un mensaje? Una instrucción que le das a tu cuerpo sobre qué hacer con la energía durante las horas siguientes.", "signal_body", {"kw": "UNA SEÑAL"}),
 ("Para entender ese mensaje, hay que ver qué pasa dentro de ti en el momento exacto en que abres los ojos.", "eye_open", {}),
]),
# ───────────── 2 · EL DESPERTAR ─────────────
("despertar", [
 ("Cuando suena el despertador, tu cuerpo no arranca de cero. Lleva horas preparándose.", "alarm", {}),
 ("Lo primero: el cortisol. Sí, la famosa hormona del estrés.", "hormone_tag", {"name": "CORTISOL", "color": "red"}),
 ("En los primeros treinta minutos después de despertar, sube de media un cincuenta por ciento. Lo midieron en más de quinientos adultos.", "cortisol_chart", {"src": "Wüst et al., Noise & Health, 2000 (509 adultos)"}),
 ("No es estrés. Es tu alarma interna: le dice al cuerpo que ha llegado la hora de moverse.", "inner_alarm", {}),
 ("Al mismo tiempo, tu hígado empieza a soltar glucosa a la sangre, para que el cerebro y los músculos tengan combustible desde el primer minuto.", "liver_release", {"kw": "GLUCOSA"}),
 ("Y la insulina, la hormona que guarda, está baja.", "insulin_gauge", {"level": 0.2}),
 ("Combustible en la sangre. Insulina baja. Señal de ponerse en marcha.", "three_stack", {"items": ["COMBUSTIBLE EN LA SANGRE", "INSULINA BAJA", "SEÑAL: ¡EN MARCHA!"]}),
 ("Es como un coche con el depósito lleno y el motor encendido... pero aparcado.", "car_parked", {}),
 ("La pregunta es: ¿qué pasa con esa gasolina si el coche no se mueve?", "big_question", {"text": "¿Y SI NO TE MUEVES?"}),
 ("Si te gusta entender lo que hace tu cuerpo mientras no miras, suscríbete. De eso va este canal.", "subscribe", {}),
]),
# ───────────── 3 · EL RELOJ ─────────────
("reloj", [
 ("Piénsalo desde la historia. Durante casi toda la existencia humana, despertarse significaba moverse.", "caveman_dawn", {}),
 ("Ir a por agua, buscar comida, cambiar de sitio. Nadie se despertaba para quedarse quieto, mirando una pantalla.", "then_now", {}),
 ("Tu metabolismo funciona con un reloj interno, el ritmo circadiano, que coordina el cerebro, el hígado y los músculos a lo largo del día.", "circadian_clock", {"kw": "RITMO CIRCADIANO"}),
 ("Y ese reloj se ajusta con señales: la luz, la comida... y el movimiento.", "three_icons", {"icons": ["sun", "plate", "walk"], "labels": ["LUZ", "COMIDA", "MOVIMIENTO"]}),
 ("El primer movimiento del día es una de esas señales. Y ahora viene lo interesante: qué hace exactamente.", "zoom_muscle", {}),
]),
# ───────────── 4 · GLUT-4 ─────────────
("glut4", [
 ("Dentro de tus músculos hay unas puertas para la glucosa. Se llaman GLUT-4.", "cell_doors", {"state": "closed", "kw": "GLUT-4"}),
 ("Normalmente, para abrirlas hace falta una llave: la insulina.", "cell_doors", {"state": "key"}),
 ("Imagina una discoteca con un portero. Sin invitación, la glucosa se queda en la calle.", "club", {}),
 ("Pero hay algo que muy poca gente sabe: cuando el músculo se contrae, esas puertas se abren solas.", "cell_doors", {"state": "contract"}),
 ("Sin llave. Sin portero. Es una puerta trasera.", "backdoor", {"kw": "PUERTA TRASERA"}),
 ("Y no es una teoría de internet: funciona incluso en personas con diabetes tipo dos, a las que la llave de la insulina les funciona peor.", "evidence_card", {"text": "Funciona incluso con diabetes tipo 2", "src": "Stanford y Goodyear, Adv Physiol Educ, 2014"}),
 ("Así que vuelve al coche aparcado. Si te quedas quieto al despertar, esa glucosa se queda dando vueltas por la sangre, esperando.", "vessel_idle", {}),
 ("Si te mueves, tus músculos empiezan a tirar de ella. Desde el primer paso.", "vessel_walk", {}),
 ("Y por eso bastan diez minutos: no buscas cansarte. Buscas abrir las puertas.", "scale_compare", {"left": "ESFUERZO", "right": "SEÑAL"}),
 ("Hay datos. En dos mil veintidós, investigadores de la Universidad de Limerick, en Irlanda, revisaron siete estudios.", "study_intro", {"n": 7, "src": "Buffey et al., Sports Medicine, 2022"}),
 ("Caminar suave solo de dos a cinco minutos después de comer ya bajaba el azúcar y la insulina en sangre.", "glucose_curves", {"src": "Buffey et al., Sports Medicine, 2022"}),
 ("Y pequeños paseos repartidos durante el día reducían la glucosa de media un diecisiete por ciento frente a estar sentado.", "bars_17", {"src": "Buffey et al., Sports Medicine, 2022"}),
 ("Esos estudios midieron paseos después de comer. La mañana usa el mismo mecanismo, solo que antes del desayuno.", "same_mechanism", {"kw": "MISMO MECANISMO"}),
 ("Por cierto: ¿qué es lo primero que haces tú al despertarte? ¿El móvil? ¿El café? Cuéntamelo en los comentarios.", "comment_ask", {}),
]),
# ───────────── 5 · LA PARADOJA ─────────────
("paradoja", [
 ("Y ahora, la paradoja del principio.", "big_question", {"text": "LA PARADOJA"}),
 ("En dos mil diecinueve, las universidades de Bath y Birmingham, en Reino Unido, siguieron durante seis semanas a treinta hombres con sobrepeso.", "thirty_men", {"src": "Edinburgh et al., J Clin Endocrinol Metab, 2019"}),
 ("Unos hacían ejercicio después de desayunar. Otros, antes.", "two_groups", {}),
 ("Los que se movían en ayunas quemaron el doble de grasa durante el ejercicio.", "counter_big", {"text": "×2", "label": "GRASA QUEMADA", "color": "amber", "src": "Edinburgh et al., J Clin Endocrinol Metab, 2019"}),
 ("Y sin embargo... no adelgazaron más que los otros.", "scale_equal", {}),
 ("Entonces, ¿para qué sirvió?", "big_question", {"text": "¿PARA QUÉ SIRVIÓ?"}),
 ("Para esto: sus músculos empezaron a responder mucho mejor a la insulina. Su cuerpo gestionaba mejor el azúcar.", "cell_doors", {"state": "many", "kw": "MEJOR RESPUESTA A LA INSULINA"}),
 ("Esa es la clave: el beneficio no se ve en la báscula. Se ve en cómo tu cuerpo maneja la energía.", "scale_vs_graph", {}),
 ("Ojo: en ese estudio pedaleaban a intensidad moderada, no paseaban. El paseo de diez minutos es la versión suave de la misma idea: moverse antes de comer, con la insulina baja.", "honest_note", {}),
 ("Y esto importa más de lo que parece. En España, uno de cada siete adultos tiene diabetes, según la Federación Internacional de Diabetes.", "country_stat", {"country": "es", "num": 1, "den": 7, "src": "IDF Diabetes Atlas, 2021"}),
 ("En México, la encuesta nacional de salud de dos mil veintidós encontró diabetes en el dieciocho por ciento de los adultos, y prediabetes en otro veintidós.", "country_stat", {"country": "mx", "pcts": [18, 22], "src": "ENSANUT 2022 · Basto-Abreu et al., Salud Pública Méx, 2023"}),
 ("Casi cuatro de cada diez. Y muchos, sin saberlo.", "four_in_ten", {}),
 ("Si este dato te ha sorprendido, dale a me gusta. Así YouTube se lo enseña a más gente.", "like", {}),
]),
# ───────────── 6 · ERRORES ─────────────
("errores", [
 ("Ahora, los tres errores que lo estropean todo.", "three_signs", {}),
 ("Error uno: convertirlo en un entrenamiento. Correr, subir cuestas, ir con prisa.", "mistake_run", {}),
 ("Cuanto más intenso es el ejercicio, más sube el cortisol. Y lo que buscabas era una señal de calma, no de alarma.", "cortisol_gauge", {}),
 ("Error dos: la taza gigante de café nada más abrir los ojos. La cafeína también sube el cortisol, y sumarla justo en su pico es echar leña al fuego.", "mistake_coffee", {}),
 ("Error tres: subirte a la báscula al día siguiente esperando un milagro. Ya has visto lo que pasó en Bath: lo que cambia no es el peso, es cómo tu cuerpo usa la energía.", "mistake_scale", {}),
 ("Y una nota importante: si tomas insulina u otros medicamentos para el azúcar, habla antes con tu médico. Moverte en ayunas puede bajarte la glucosa más de la cuenta.", "doctor_warning", {}),
]),
# ───────────── 6b · CÓMO HACERLO BIEN ─────────────
("como", [
 ("Entonces, ¿cómo se hace bien? Es más sencillo de lo que crees.", "doctor_intro", {"text": "CÓMO HACERLO BIEN"}),
 ("Primero, el momento: dentro de la primera hora después de levantarte, y antes de desayunar.", "clock_window", {"from": 7.0, "to": 8.0, "kw": "ANTES DE DESAYUNAR"}),
 ("Segundo, el ritmo: tienes que poder hablar sin jadear. Si no podrías mantener una conversación, vas demasiado rápido.", "talk_test", {}),
 ("Tercero: si puedes, sal fuera. La luz de la mañana es la señal más potente que existe para poner en hora tu reloj interno. Así juntas dos señales en un solo paseo.", "light_walk", {"kw": "LUZ + MOVIMIENTO"}),
 ("En Madrid, en pleno invierno, el sol sale pasadas las ocho y media. En Ciudad de México, hacia las siete. Si todavía es de noche, caminar por casa también cuenta: tus músculos no saben dónde estás.", "sunrise_cities", {}),
 ("Y cuarto: hazlo todos los días. A este reloj no le impresiona un día heroico. Le convence la repetición.", "calendar7", {"streak": True}),
]),
# ───────────── 7 · CIERRE ─────────────
("cierre", [
 ("Tres cosas que hoy sabes y ayer no.", "recap", {"n": 0}),
 ("Al despertar, tu cuerpo ya tiene combustible en la sangre y la insulina baja.", "recap", {"n": 1}),
 ("Tus músculos tienen una puerta trasera que se abre solo con moverte.", "recap", {"n": 2}),
 ("Y el beneficio no está en las calorías que quemas, sino en cómo tu cuerpo aprende a usar la energía.", "recap", {"n": 3}),
 ("Un último dato. En un estudio, unas estudiantes se echaron una siesta por la tarde. Al despertar, su cortisol no subió: bajó. Tu cuerpo distingue perfectamente una siesta de una mañana.", "nap_fact", {"src": "Federenko et al., Psychoneuroendocrinology, 2004"}),
 ("Así que haz la prueba. Siete días. Diez minutos caminando nada más levantarte. Sin contar calorías y sin pesarte. Solo fíjate en cómo te sientes a las once.", "calendar7", {}),
 ("Y cuéntamelo en los comentarios el día siete.", "comment_ask", {"short": True}),
 ("La próxima pregunta ya está en marcha: ¿por qué la grasa de la barriga es siempre la última en irse? Suscríbete para no perdértelo.", "next_video", {}),
]),
]

TITLE = "Lo que pasa en tu cuerpo si caminas 10 min al despertar"
