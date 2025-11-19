"""En este módulo se guardan las expresiones regulares para verificar campos """ 
import re

class Regex_01:

    @staticmethod
    def numero_hc_valido(valor: str) -> bool:
        patron = '^\d{1,6}$'
        return bool(re.match(patron, valor))
    
    def email_valido(self,):
        patron =  '^[a-zA-Z0-9. _%+-]+@[a-zA-Z0-9. -]+\\. [a-zA-Z]{2,}$.'
        return patron
    
