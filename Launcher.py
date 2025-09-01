from Menu.menu import Menu, text, options, console

#-------Menu Principal-------
Menu_Principal = Menu(text, options, console)
Menu_Principal.show()
with keyboard.Listener(on_press=Menu_Principal.controll_keyboard) as listener:
    listener.join()

