from pathlib import Path

from textual.widgets import Label, Input
from textual.containers import Horizontal

def build(label_contents: str, placeholder_contents: str | None = None):
    # adicionar dois pontos no final do label
    if not label_contents.strip().endswith(':'):
        label_contents += ':'

    # criar o label
    input_label = Label(label_contents).add_class('input-label')
    input_field = Input()
    
    # adicionar o placeholder no input caso tenha sido passado pra função
    if placeholder_contents:
        input_field.placeholder = placeholder_contents

    # adicionar os widgets finais ao container horizontal
    # isso é o equivalente de with Horziontal(): yield Widget()
    # mas em vez de só criar os widgets dentro, insere eles com _add_child()
    container = Horizontal().add_class('input-container')
    container._add_child(input_label)
    container._add_child(input_field)

    return container, input_field