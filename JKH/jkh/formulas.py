def calculate_w_meter(tarif, value):
    """
    Расчет размера оплаты за услугу, для которой есть счетчик
    """
    return tarif.price * value


def calc_otopl_wo_meter(tarif, norm, square):
    """
    Расчет размера оплаты за отопление,
    если нет счетчика в квартире и общедомового счетчика
    """
    return tarif.price * norm.price * square


def calc_otopl_w_meter(tarif, value, square_house, square_apartment):
    """
    Расчет размера оплаты за отопление,
    при наличии общедомового счетчика
    value - показания общедомового счетчика
    square_house - площать всех жилых и нежилых помещений в доме
    square_square_apartment - площадь квартиры
    """
    return tarif.price * value * (square_apartment / square_house)


def calc_wo_meter(tarif, norm, human_count):
    """
    Расчет размера оплты за горячюю, холодную воду, канализацию и электричество,
    если отсутствует счетчик за услугу
    human_count - кодичество человек проживающих в помещении
    """
    return tarif.price * norm.price * human_count