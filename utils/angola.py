import re

PROVINCIAS = [
    'Bengo', 'Benguela', 'Bié', 'Cabinda', 'Cuando Cubango',
    'Cuanza Norte', 'Cuanza Sul', 'Cunene', 'Huambo', 'Huíla',
    'Luanda', 'Lunda Norte', 'Lunda Sul', 'Malanje', 'Moxico',
    'Namibe', 'Uíge', 'Zaire',
]

MUNICIPIOS = {
    'Bengo': ['Ambriz', 'Bula Atumba', 'Dande', 'Dembos', 'Nambuangongo', 'Pango Aluquém'],
    'Benguela': ['Baía Farta', 'Balombo', 'Benguela', 'Bocoio', 'Caimbambo', 'Catumbela', 'Chongoroi', 'Cubal', 'Ganda', 'Lobito'],
    'Bié': ['Andulo', 'Camacupa', 'Catabola', 'Chinguar', 'Chitembo', 'Cuemba', 'Cunhinga', 'Cuíto', 'Nharea'],
    'Cabinda': ['Belize', 'Buco Zau', 'Cabinda', 'Cacongo'],
    'Cuando Cubango': ['Calai', 'Cuangar', 'Cuchi', 'Cuito Cuanavale', 'Dirico', 'Mavinga', 'Menongue', 'Nancova', 'Rivungo'],
    'Cuanza Norte': ['Ambaca', 'Banga', 'Bolongongo', 'Cambambe', 'Cazengo', 'Golungo Alto', 'Gonguembo', 'Lucala', 'Quiculungo', 'Samba Caju'],
    'Cuanza Sul': ['Amboim', 'Cassongue', 'Cela', 'Conda', 'Ebo', 'Libolo', 'Mussende', 'Porto Amboim', 'Quibala', 'Quilenda', 'Seles', 'Sumbe'],
    'Cunene': ['Cahama', 'Cuanhama', 'Curoca', 'Cuvelai', 'Namacunde', 'Ombadja'],
    'Huambo': ['Bailundo', 'Caála', 'Ekunha', 'Huambo', 'Katchiungo', 'Londuimbali', 'Longonjo', 'Mungo', 'Chicala Cholohanga', 'Chinjenje', 'Ucuma'],
    'Huíla': ['Caconda', 'Caluquembe', 'Chiange', 'Chibia', 'Chicomba', 'Chipindo', 'Gambos', 'Humpata', 'Jamba', 'Lubango', 'Matala', 'Quilengues', 'Quipungo'],
    'Luanda': ['Belas', 'Cacuaco', 'Cazenga', 'Ícolo e Bengo', 'Luanda', 'Quilamba Quiaxi', 'Quissama', 'Talatona', 'Viana'],
    'Lunda Norte': ['Cambulo', 'Capenda Camulemba', 'Caungula', 'Chitato', 'Cuango', 'Cuilo', 'Lubalo', 'Lucapa', 'Xá Muteba'],
    'Lunda Sul': ['Cacolo', 'Dala', 'Muconda', 'Saurimo'],
    'Malanje': ['Cacuso', 'Calandula', 'Cambundi Catembo', 'Cangandala', 'Caombo', 'Cuaba Nzoji', 'Cunda Dia Baze', 'Luquembo', 'Malanje', 'Marimba', 'Massango', 'Mucari', 'Quela', 'Quirima'],
    'Moxico': ['Alto Zambeze', 'Bundas', 'Camanongue', 'Léua', 'Luau', 'Luacano', 'Luchazes', 'Moxico'],
    'Namibe': ['Bibala', 'Camucuio', 'Moçâmedes', 'Tômbua', 'Virei'],
    'Uíge': ['Alto Cauale', 'Ambuíla', 'Bembe', 'Buengas', 'Bungo', 'Damba', 'Macocola', 'Mucaba', 'Negage', 'Puri', 'Quimbele', 'Quitexe', 'Sanza Pombo', 'Songo', 'Uíge', 'Zombo'],
    'Zaire': ['Cuimba', 'Mabanza Congo', 'Nóqui', 'Nezeto', 'Soio', 'Tomboco'],
}

TELEFONE_PREFIXO = '+244'
MOEDA = 'Kz'
MOEDA_SIMBOLO = 'Kz'
LOCALE = 'pt-AO'
TIMEZONE = 'Africa/Luanda'


def format_kz(value):
    if value is None:
        value = 0
    try:
        formatted = f"{float(value):,.2f}"
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"{formatted} {MOEDA}"
    except (ValueError, TypeError):
        return f"0,00 {MOEDA}"


def validate_angolan_phone(phone):
    if not phone:
        return True
    pattern = r'^\+244\s?9\d{2}\s?\d{3}\s?\d{3}$'
    clean = phone.replace(' ', '')
    if clean.startswith('+244') and len(clean) == 13 and clean[1:].isdigit():
        return True
    if len(clean) == 9 and clean.isdigit() and clean.startswith('9'):
        return True
    return bool(re.match(pattern, phone))


def format_phone(phone):
    if not phone:
        return ''
    clean = phone.replace(' ', '').replace('+', '')
    if clean.startswith('244'):
        clean = clean[3:]
    if len(clean) == 9 and clean.startswith('9'):
        return f"+244 {clean[:3]} {clean[3:6]} {clean[6:]}"
    return phone
