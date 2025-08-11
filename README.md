# Divine Light

Divine Ligth es un RPG programado en python y ejecutado a través de la terminal. 
La caracteristica principal del juego es la toma de decisiones respecto a la historia, teniendo muchos caminos posibles para que cada partida se sienta diferente. Dentro de cada partida hay encuentros con diferentes enemigos, un sistema de niveles y diferentes personajes jugables, cada uno con sus caracteristicas.

## Historia
- - 

## Caracteristicas 

- Toma de decisiones
- Combate contra varios enemigos y por turnos
- Distintos personajes jugables
- Mejorar niveles
- Graficos ASCII a través de consola
- Mapas aleatorios
- Gran interaccion del usuario con el juego a través de la consola

 ## Como funciona

 DIvine ligth utiliza una estructura de árboles para cargar la historia y la toma de decisiones, las mismas se cargan a través de un JSON donde cada hijo es una decisión posible. Dentro de cada nodo existe la posibilidad de encontrar un enemigo y que se muestre un mapa en la consola. 
 El menu y la interacción con el mismo esta realizado con la biblioteca rich terminal y pyunput respectivamente. EL resto se utilizan ciertos métodos para mejorar la inmersión y simular mecánicas propias de los RPG.

 ## Posibles features
 - Agregar un inventario de personaje
 - Tienda para comprar objetos
 - Más personajes y enemigos
 - Mejor creación de mapas