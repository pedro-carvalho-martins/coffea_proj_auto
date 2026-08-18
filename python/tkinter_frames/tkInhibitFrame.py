from tkinter_frames.ui_components import create_instruction_screen

## Função de criação do Frame de Inhibit

def createInhibitFrame(inhibitContainer):
    return create_instruction_screen(
        inhibitContainer,
        "Máquina\nem espera",
        "Aguarde a liberação para iniciar uma compra.",
    )
