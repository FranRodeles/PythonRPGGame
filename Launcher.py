from Menu.menu import Menu, text_menu, options, console, keyboard



#-------Menu Principal-------
Menu_Principal = Menu(text_menu, options, console)
Menu_Principal.show()


with keyboard.Listener(on_press=Menu_Principal.controll_keyboard) as listener:
    listener.join()

