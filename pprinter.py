
class Pprinter:
    class __Pprinter:
        
        def pprinter(self, color, symbol, string, new_line=True):
            if not new_line:
                print('{0!s}{1!s} {2!s} \033[0m'.format(color,symbol,string), end=' ')
            else:
                print('{0!s}{1!s} {2!s} \033[0m'.format(color,symbol,string))

        def info(self, string):
            self.pprinter('\033[96m','[+]',string)
        
        def request(self, string):
            self.pprinter('\033[94m','[?]',string, False)

        def warning(self, string):
            self.pprinter('\033[93m','[!] WARNING -',string)  

        def error(self, string):
            self.pprinter('\033[91m','[x] ERROR -',string)

        def print_banner(self, color_code, string):
            print('\033[38;5;{0!s}m {1!s} \033[0m'.format(color_code,string))

        

    
    __instance = None
    def __init__(self):
        if self.__instance is None:
            self.__instance = self.__Pprinter()
    
    def getInstance(self):
        return self.__instance
